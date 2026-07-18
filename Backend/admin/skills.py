from flask import Blueprint, flash, redirect, render_template, request, url_for

from Backend.admin import current_user_id, login_required
from model import delete_entity, get_entity, list_entities, save_entity

admin_skills_bp = Blueprint("admin_skills", __name__, url_prefix="/admin")


@admin_skills_bp.route("/skills", methods=["GET", "POST"])
@login_required
def skills():
    user_id = current_user_id()
    edit_id = request.args.get("edit", type=int)
    edit_item = get_entity("skills", edit_id, user_id) if edit_id else None
    if request.method == "POST":
        item_id = request.form.get("id", type=int)
        data = {
            "nama_skill": request.form.get("nama_skill", "").strip(),
            "icon_class": request.form.get("icon_class", "").strip(),
        }
        if not data["nama_skill"]:
            flash("Nama skill wajib diisi.", "danger")
        else:
            save_entity("skills", user_id, data, item_id)
            flash("Skill berhasil disimpan.", "success")
            return redirect(url_for("admin_skills.skills"))
    return render_template(
        "admin/skills.html",
        items=list_entities("skills", user_id),
        edit_item=edit_item,
    )


@admin_skills_bp.post("/skills/<int:item_id>/delete")
@login_required
def delete_skill(item_id: int):
    delete_entity("skills", item_id, current_user_id())
    flash("Skill berhasil dihapus.", "success")
    return redirect(url_for("admin_skills.skills"))
