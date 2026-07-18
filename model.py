from __future__ import annotations

from pathlib import Path
from typing import Any, Iterable

import certifi
import pymysql
from flask import current_app, g


ENTITY_CONFIG = {
    "skills": {
        "table": "skills",
        "fields": ("nama_skill", "icon_class"),
    },
    "experiences": {
        "table": "experiences",
        "fields": ("posisi", "perusahaan", "durasi", "deskripsi"),
    },
    "projects": {
        "table": "projects",
        "fields": ("judul", "deskripsi", "gambar_url", "link_project"),
    },
}

PROFILE_FIELDS = (
    "nama_lengkap",
    "nama_panggilan",
    "tempat_lahir",
    "tanggal_lahir",
    "email",
    "telepon",
    "universitas",
    "fakultas",
    "prodi",
    "semester",
    "alamat",
    "foto_url",
)


def get_db():
    if "db_connection" not in g:
        required = ("DB_HOST", "DB_USER", "DB_PASSWORD", "DB_NAME")
        missing = [key for key in required if not current_app.config.get(key)]
        if missing:
            raise RuntimeError(
                "Konfigurasi TiDB belum lengkap. Isi variabel: " + ", ".join(missing)
            )

        configured_ca = current_app.config.get("DB_CA_PATH")
        ca_path = (
            configured_ca
            if configured_ca and Path(configured_ca).is_file()
            else certifi.where()
        )
        g.db_connection = pymysql.connect(
            host=current_app.config["DB_HOST"],
            port=current_app.config["DB_PORT"],
            user=current_app.config["DB_USER"],
            password=current_app.config["DB_PASSWORD"],
            database=current_app.config["DB_NAME"],
            cursorclass=pymysql.cursors.DictCursor,
            charset="utf8mb4",
            autocommit=False,
            ssl={"ca": ca_path},
            connect_timeout=15,
            read_timeout=20,
            write_timeout=20,
        )
    return g.db_connection


def close_db(_error: BaseException | None = None) -> None:
    connection = g.pop("db_connection", None)
    if connection is not None:
        connection.close()


def fetch_all(query: str, params: Iterable[Any] = ()) -> list[dict[str, Any]]:
    connection = get_db()
    with connection.cursor() as cursor:
        cursor.execute(query, tuple(params))
        return list(cursor.fetchall())


def fetch_one(query: str, params: Iterable[Any] = ()) -> dict[str, Any] | None:
    connection = get_db()
    with connection.cursor() as cursor:
        cursor.execute(query, tuple(params))
        return cursor.fetchone()


def execute(query: str, params: Iterable[Any] = ()) -> int:
    connection = get_db()
    try:
        with connection.cursor() as cursor:
            cursor.execute(query, tuple(params))
            last_id = int(cursor.lastrowid or 0)
        connection.commit()
        return last_id
    except Exception:
        connection.rollback()
        raise


# users
def get_user_by_username(username: str):
    return fetch_one("SELECT * FROM users WHERE username = %s", (username,))


def get_admin_user():
    return fetch_one(
        "SELECT * FROM users WHERE role = 'admin' ORDER BY id ASC LIMIT 1"
    )


def get_user(user_id: int):
    return fetch_one("SELECT * FROM users WHERE id = %s", (user_id,))


def create_admin(username: str, password_hash: str) -> int:
    connection = get_db()
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO users (username, password_hash, role)
                VALUES (%s, %s, 'admin')
                """,
                (username, password_hash),
            )
            user_id = int(cursor.lastrowid)
            cursor.execute(
                """
                INSERT INTO profiles (
                    user_id, nama_lengkap, nama_panggilan, universitas,
                    prodi, semester, alamat
                ) VALUES (%s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    user_id,
                    "Vanessa Ruth Walingkas",
                    "Vanessa",
                    "Isi nama universitas melalui halaman Admin",
                    "Sistem Informasi",
                    "Isi semester",
                    "Isi alamat dan ringkasan diri melalui halaman Admin.",
                ),
            )
        connection.commit()
        return user_id
    except Exception:
        connection.rollback()
        raise


def update_user_account(
    user_id: int, username: str, password_hash: str | None = None
) -> None:
    if password_hash:
        execute(
            "UPDATE users SET username = %s, password_hash = %s WHERE id = %s",
            (username, password_hash, user_id),
        )
    else:
        execute(
            "UPDATE users SET username = %s WHERE id = %s",
            (username, user_id),
        )


# profiles
def get_profile(user_id: int):
    return fetch_one("SELECT * FROM profiles WHERE user_id = %s", (user_id,))


def upsert_profile(user_id: int, data: dict[str, Any]) -> None:
    values = [data.get(field) or None for field in PROFILE_FIELDS]
    if get_profile(user_id):
        assignments = ", ".join(f"{field} = %s" for field in PROFILE_FIELDS)
        execute(
            f"UPDATE profiles SET {assignments} WHERE user_id = %s",
            (*values, user_id),
        )
        return

    columns = ", ".join(("user_id", *PROFILE_FIELDS))
    placeholders = ", ".join("%s" for _ in range(len(PROFILE_FIELDS) + 1))
    execute(
        f"INSERT INTO profiles ({columns}) VALUES ({placeholders})",
        (user_id, *values),
    )


# skills, experiences, projects
def list_entities(entity: str, user_id: int):
    table = ENTITY_CONFIG[entity]["table"]
    return fetch_all(
        f"SELECT * FROM {table} WHERE user_id = %s ORDER BY id DESC",
        (user_id,),
    )


def get_entity(entity: str, item_id: int, user_id: int):
    table = ENTITY_CONFIG[entity]["table"]
    return fetch_one(
        f"SELECT * FROM {table} WHERE id = %s AND user_id = %s",
        (item_id, user_id),
    )


def save_entity(
    entity: str,
    user_id: int,
    data: dict[str, Any],
    item_id: int | None = None,
) -> int:
    config = ENTITY_CONFIG[entity]
    fields = config["fields"]
    values = [data.get(field) or None for field in fields]
    if item_id:
        assignments = ", ".join(f"{field} = %s" for field in fields)
        execute(
            f"UPDATE {config['table']} SET {assignments} "
            "WHERE id = %s AND user_id = %s",
            (*values, item_id, user_id),
        )
        return item_id

    columns = ", ".join(("user_id", *fields))
    placeholders = ", ".join("%s" for _ in range(len(fields) + 1))
    return execute(
        f"INSERT INTO {config['table']} ({columns}) VALUES ({placeholders})",
        (user_id, *values),
    )


def delete_entity(entity: str, item_id: int, user_id: int) -> None:
    table = ENTITY_CONFIG[entity]["table"]
    execute(
        f"DELETE FROM {table} WHERE id = %s AND user_id = %s",
        (item_id, user_id),
    )


# contact_messages
def dashboard_counts(user_id: int) -> dict[str, int]:
    return {
        "skills": fetch_one(
            "SELECT COUNT(*) AS total FROM skills WHERE user_id = %s", (user_id,)
        )["total"],
        "experiences": fetch_one(
            "SELECT COUNT(*) AS total FROM experiences WHERE user_id = %s",
            (user_id,),
        )["total"],
        "projects": fetch_one(
            "SELECT COUNT(*) AS total FROM projects WHERE user_id = %s", (user_id,)
        )["total"],
        "messages": fetch_one(
            "SELECT COUNT(*) AS total FROM contact_messages WHERE status = 'baru'"
        )["total"],
    }


def list_messages(limit: int | None = None):
    query = "SELECT * FROM contact_messages ORDER BY id DESC"
    if limit is not None:
        query += " LIMIT %s"
        return fetch_all(query, (limit,))
    return fetch_all(query)


def toggle_message_status(item_id: int) -> None:
    item = fetch_one(
        "SELECT status FROM contact_messages WHERE id = %s", (item_id,)
    )
    if item:
        new_status = "dibaca" if item["status"] == "baru" else "baru"
        execute(
            "UPDATE contact_messages SET status = %s WHERE id = %s",
            (new_status, item_id),
        )


def delete_message(item_id: int) -> None:
    execute("DELETE FROM contact_messages WHERE id = %s", (item_id,))


def create_contact_message(
    name: str, email: str, subject: str | None, message: str
) -> int:
    return execute(
        """
        INSERT INTO contact_messages (nama, email, subjek, pesan, status)
        VALUES (%s, %s, %s, %s, 'baru')
        """,
        (name, email, subject, message),
    )


def public_portfolio(user_id: int) -> dict[str, Any]:
    return {
        "profile": get_profile(user_id),
        "skills": list_entities("skills", user_id),
        "experiences": list_entities("experiences", user_id),
        "projects": list_entities("projects", user_id),
    }
