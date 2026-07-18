import html
import re

import resend
from flask import Blueprint, current_app, jsonify, render_template, request, send_from_directory

from model import (
    create_contact_message,
    get_admin_user,
    public_portfolio,
)

public_bp = Blueprint("public", __name__)
EMAIL_PATTERN = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")


def email_configured() -> bool:
    return bool(
        current_app.config.get("RESEND_API_KEY")
        and current_app.config.get("CONTACT_TO_EMAIL")
        and current_app.config.get("RESEND_FROM_EMAIL")
    )


def send_contact_email(
    name: str, sender_email: str, subject: str, message: str
) -> str | None:
    if not email_configured():
        return None

    resend.api_key = current_app.config["RESEND_API_KEY"]
    response = resend.Emails.send(
        {
            "from": current_app.config["RESEND_FROM_EMAIL"],
            "to": [current_app.config["CONTACT_TO_EMAIL"]],
            "reply_to": sender_email,
            "subject": f"Portofolio Vanessa: {subject or 'Pesan baru'}",
            "html": (
                "<h2>Pesan baru dari website portofolio</h2>"
                f"<p><strong>Nama:</strong> {html.escape(name)}</p>"
                f"<p><strong>Email:</strong> {html.escape(sender_email)}</p>"
                f"<p><strong>Subjek:</strong> {html.escape(subject or 'Tanpa subjek')}</p>"
                f"<p><strong>Pesan:</strong><br>"
                f"{html.escape(message).replace(chr(10), '<br>')}</p>"
            ),
        }
    )
    return response.get("id") if isinstance(response, dict) else None


@public_bp.get("/")
def home():
    return render_template("index.html")


@public_bp.get("/favicon.ico")
def favicon():
    return send_from_directory(current_app.root_path, "favicon.ico")


@public_bp.get("/api/health")
def health():
    return jsonify({"status": "ok", "database": current_app.config["DB_DRIVER"]})


@public_bp.get("/api/portfolio")
def portfolio():
    user = get_admin_user()
    if not user:
        return jsonify({"error": "Data admin belum tersedia."}), 404
    return jsonify(public_portfolio(user["id"]))


@public_bp.post("/api/contact")
def contact():
    payload = request.get_json(silent=True) or request.form.to_dict()
    if payload.get("website"):
        return jsonify({"message": "Pesan diterima."}), 200

    name = str(payload.get("name", "")).strip()
    email = str(payload.get("email", "")).strip().lower()
    subject = str(payload.get("subject", "")).strip()
    message = str(payload.get("message", "")).strip()

    errors = []
    if not 2 <= len(name) <= 100:
        errors.append("Nama harus 2–100 karakter.")
    if not EMAIL_PATTERN.match(email) or len(email) > 100:
        errors.append("Alamat email tidak valid.")
    if len(subject) > 150:
        errors.append("Subjek maksimal 150 karakter.")
    if not 5 <= len(message) <= 4000:
        errors.append("Pesan harus 5–4000 karakter.")
    if errors:
        return jsonify({"error": " ".join(errors)}), 400

    message_id = create_contact_message(
        name, email, subject or None, message
    )
    email_id = None
    try:
        email_id = send_contact_email(name, email, subject, message)
    except Exception:
        current_app.logger.exception("Pesan tersimpan, tetapi email gagal dikirim")

    return (
        jsonify(
            {
                "message": (
                    "Pesan berhasil disimpan dan dikirim."
                    if email_id
                    else "Pesan berhasil disimpan."
                ),
                "id": message_id,
                "email_sent": bool(email_id),
                "email_service_configured": email_configured(),
            }
        ),
        201,
    )
