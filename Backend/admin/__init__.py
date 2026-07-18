from functools import wraps

from flask import flash, redirect, session, url_for


def current_user_id() -> int:
    return int(session["user_id"])


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get("user_id"):
            flash("Silakan login terlebih dahulu.", "warning")
            return redirect(url_for("admin_login.login"))
        return view(*args, **kwargs)

    return wrapped
