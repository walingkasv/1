from flask import (
    Blueprint,
    current_app,
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from werkzeug.security import check_password_hash, generate_password_hash

from Backend.admin import current_user_id, login_required
from model import (
    create_admin,
    get_user,
    get_user_by_username,
    update_user_account,
)

admin_login_bp = Blueprint("admin_login", __name__, url_prefix="/admin")


@admin_login_bp.route("/login", methods=["GET", "POST"])
def login():
    if session.get("user_id"):
        return redirect(url_for("admin_dashboard.dashboard"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        user = get_user_by_username(username)

        if (
            user is None
            and username == current_app.config["ADMIN_USERNAME"]
            and password == current_app.config["ADMIN_PASSWORD"]
        ):
            user_id = create_admin(username, generate_password_hash(password))
            user = get_user(user_id)

        if (
            user
            and user.get("role") == "admin"
            and check_password_hash(user["password_hash"], password)
        ):
            session.clear()
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            flash("Login berhasil. Selamat datang!", "success")
            return redirect(url_for("admin_dashboard.dashboard"))
        flash("Username atau password salah.", "danger")

    return render_template("admin/login.html")


@admin_login_bp.route("/logout", methods=["GET", "POST"])
@login_required
def logout():
    session.clear()
    flash("Anda sudah logout.", "success")
    return redirect(url_for("admin_login.login"))


@admin_login_bp.route("/account", methods=["GET", "POST"])
@login_required
def account():
    user = get_user(current_user_id())
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        old_password = request.form.get("old_password", "")
        new_password = request.form.get("new_password", "")
        existing = get_user_by_username(username) if username else None

        if not username:
            flash("Username wajib diisi.", "danger")
        elif existing and existing["id"] != user["id"]:
            flash("Username sudah digunakan.", "danger")
        elif new_password and not check_password_hash(
            user["password_hash"], old_password
        ):
            flash("Password lama tidak sesuai.", "danger")
        elif new_password and len(new_password) < 6:
            flash("Password baru minimal 6 karakter.", "danger")
        else:
            password_hash = (
                generate_password_hash(new_password) if new_password else None
            )
            update_user_account(user["id"], username, password_hash)
            session["username"] = username
            flash("Akun berhasil diperbarui.", "success")
            return redirect(url_for("admin_login.account"))
    return render_template("admin/account.html", user=user)
