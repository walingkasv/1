from __future__ import annotations

import secrets
from pathlib import Path

from flask import Flask, abort, request, session
from jinja2 import ChoiceLoader, FileSystemLoader

from Backend.admin.dashboard import admin_dashboard_bp
from Backend.admin.experience import admin_experience_bp
from Backend.admin.login import admin_login_bp
from Backend.admin.profiles import admin_profiles_bp
from Backend.admin.projects import admin_projects_bp
from Backend.admin.skills import admin_skills_bp
from Backend.utama.utama import public_bp
from config import Config
from model import close_db


def create_app(config_object=Config) -> Flask:
    app = Flask(
        __name__,
        template_folder="Frontend",
        static_folder="Frontend",
    )
    app.config.from_object(config_object)
    app.config.update(
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE="Lax",
        MAX_CONTENT_LENGTH=6 * 1024 * 1024,
    )

    # index.html wajib berada di root, sedangkan template admin berada di Frontend.
    frontend_loader = app.jinja_loader
    app.jinja_loader = ChoiceLoader(
        [FileSystemLoader(Path(app.root_path)), frontend_loader]
    )

    app.register_blueprint(public_bp)
    app.register_blueprint(admin_login_bp)
    app.register_blueprint(admin_dashboard_bp)
    app.register_blueprint(admin_profiles_bp)
    app.register_blueprint(admin_skills_bp)
    app.register_blueprint(admin_experience_bp)
    app.register_blueprint(admin_projects_bp)

    @app.before_request
    def csrf_protection() -> None:
        if "csrf_token" not in session:
            session["csrf_token"] = secrets.token_urlsafe(32)
        if request.method == "POST" and request.path.startswith("/admin"):
            token = request.form.get("csrf_token") or request.headers.get("X-CSRF-Token")
            if not token or not secrets.compare_digest(token, session["csrf_token"]):
                abort(400, description="Token CSRF tidak valid.")

    @app.context_processor
    def inject_globals() -> dict[str, str]:
        return {"csrf_token": session.get("csrf_token", "")}

    app.teardown_appcontext(close_db)
    return app


app = create_app()


if __name__ == "__main__":
    app.run(debug=True)
