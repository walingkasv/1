from flask import Blueprint, flash, redirect, render_template, url_for

from Backend.admin import current_user_id, login_required
from model import (
    dashboard_counts,
    delete_message,
    list_messages,
    toggle_message_status,
)

admin_dashboard_bp = Blueprint("admin_dashboard", __name__, url_prefix="/admin")


@admin_dashboard_bp.get("")
@admin_dashboard_bp.get("/")
@admin_dashboard_bp.get("/dashboard")
@login_required
def dashboard():
    user_id = current_user_id()
    return render_template(
        "admin/dashboard.html",
        counts=dashboard_counts(user_id),
        recent_messages=list_messages(limit=5),
    )


@admin_dashboard_bp.get("/messages")
@login_required
def messages():
    return render_template("admin/messages.html", items=list_messages())


@admin_dashboard_bp.post("/messages/<int:item_id>/toggle")
@login_required
def toggle_message(item_id: int):
    toggle_message_status(item_id)
    return redirect(url_for("admin_dashboard.messages"))


@admin_dashboard_bp.post("/messages/<int:item_id>/delete")
@login_required
def remove_message(item_id: int):
    delete_message(item_id)
    flash("Pesan berhasil dihapus.", "success")
    return redirect(url_for("admin_dashboard.messages"))
