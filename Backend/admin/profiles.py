from flask import Blueprint, current_app, flash, redirect, render_template, request, url_for

from Backend.admin import current_user_id, login_required
from Backend.admin.upload import upload_image
from model import PROFILE_FIELDS, get_profile, upsert_profile

admin_profiles_bp = Blueprint("admin_profiles", __name__, url_prefix="/admin")

@admin_profiles_bp.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    user_id = current_user_id()
    profile_data = get_profile(user_id) or {}
    if request.method == "POST":
        data = {
            key: request.form.get(key, "").strip() for key in PROFILE_FIELDS
        }
        if not data["nama_lengkap"]:
            flash("Nama lengkap wajib diisi.", "danger")
            return render_template("admin/profiles.html", profile=profile_data)
        try:
            uploaded = upload_image(request.files.get("foto"), "profile")
            if uploaded:
                data["foto_url"] = uploaded
            elif not data["foto_url"]:
                data["foto_url"] = profile_data.get("foto_url")
            upsert_profile(user_id, data)
            flash("Profil berhasil diperbarui.", "success")
            return redirect(url_for("admin_profiles.profile"))
        except (ValueError, RuntimeError) as exc:
            flash(str(exc), "danger")
        except Exception:
            current_app.logger.exception("Gagal memperbarui profil")
            flash("Profil gagal disimpan.", "danger")
    return render_template("admin/profiles.html", profile=profile_data)
