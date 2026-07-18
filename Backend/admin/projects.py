from flask import Blueprint, current_app, flash, redirect, render_template, request, url_for

from Backend.admin import current_user_id, login_required
from Backend.admin.upload import upload_image
from model import delete_entity, get_entity, list_entities, save_entity

admin_projects_bp = Blueprint("admin_projects", __name__, url_prefix="/admin")


@admin_projects_bp.route("/projects", methods=["GET", "POST"])
@login_required
def projects():
    user_id = current_user_id()
    edit_id = request.args.get("edit", type=int)
    edit_item = get_entity("projects", edit_id, user_id) if edit_id else None
    if request.method == "POST":
        item_id = request.form.get("id", type=int)
        existing = (
            get_entity("projects", item_id, user_id) if item_id else None
        )
        data = {
            "judul": request.form.get("judul", "").strip(),
            "deskripsi": request.form.get("deskripsi", "").strip(),
            "gambar_url": request.form.get("gambar_url", "").strip(),
            "link_project": request.form.get("link_project", "").strip(),
        }
        if not data["judul"]:
            flash("Judul proyek wajib diisi.", "danger")
        else:
            try:
                uploaded = upload_image(request.files.get("gambar"), "projects")
                if uploaded:
                    data["gambar_url"] = uploaded
                elif not data["gambar_url"] and existing:
                    data["gambar_url"] = existing.get("gambar_url")
                save_entity("projects", user_id, data, item_id)
                flash("Proyek berhasil disimpan.", "success")
                return redirect(url_for("admin_projects.projects"))
            except (ValueError, RuntimeError) as exc:
                flash(str(exc), "danger")
            except Exception:
                current_app.logger.exception("Gagal menyimpan proyek")
                flash("Proyek gagal disimpan.", "danger")
    return render_template(
        "admin/projects.html",
        items=list_entities("projects", user_id),
        edit_item=edit_item,
    )


@admin_projects_bp.post("/projects/<int:item_id>/delete")
@login_required
def delete_project(item_id: int):
    delete_entity("projects", item_id, current_user_id())
    flash("Proyek berhasil dihapus.", "success")
    return redirect(url_for("admin_projects.projects"))
