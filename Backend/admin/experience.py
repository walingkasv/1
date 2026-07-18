from flask import Blueprint, flash, redirect, render_template, request, url_for

from Backend.admin import current_user_id, login_required
from model import delete_entity, get_entity, list_entities, save_entity

admin_experience_bp = Blueprint(
    "admin_experience", __name__, url_prefix="/admin"
)


@admin_experience_bp.route("/experiences", methods=["GET", "POST"])
@login_required
def experiences():
    user_id = current_user_id()
    edit_id = request.args.get("edit", type=int)
    edit_item = get_entity("experiences", edit_id, user_id) if edit_id else None
    if request.method == "POST":
        item_id = request.form.get("id", type=int)
        data = {
            "posisi": request.form.get("posisi", "").strip(),
            "perusahaan": request.form.get("perusahaan", "").strip(),
            "durasi": request.form.get("durasi", "").strip(),
            "deskripsi": request.form.get("deskripsi", "").strip(),
        }
        if not data["posisi"] or not data["perusahaan"]:
            flash("Posisi dan perusahaan/organisasi wajib diisi.", "danger")
        else:
            save_entity("experiences", user_id, data, item_id)
            flash("Pengalaman berhasil disimpan.", "success")
            return redirect(url_for("admin_experience.experiences"))
    return render_template(
        "admin/experience.html",
        items=list_entities("experiences", user_id),
        edit_item=edit_item,
    )


@admin_experience_bp.post("/experiences/<int:item_id>/delete")
@login_required
def delete_experience(item_id: int):
    delete_entity("experiences", item_id, current_user_id())
    flash("Pengalaman berhasil dihapus.", "success")
    return redirect(url_for("admin_experience.experiences"))
