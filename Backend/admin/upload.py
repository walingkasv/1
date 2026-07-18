from pathlib import Path
from uuid import uuid4

import cloudinary
import cloudinary.uploader
from flask import current_app
from werkzeug.datastructures import FileStorage

ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png", "webp"}
MAX_FILE_SIZE = 5 * 1024 * 1024


def cloudinary_configured() -> bool:
    return all(
        current_app.config.get(key)
        for key in (
            "CLOUDINARY_CLOUD_NAME",
            "CLOUDINARY_API_KEY",
            "CLOUDINARY_API_SECRET",
        )
    )


def upload_image(file: FileStorage | None, subfolder: str) -> str | None:
    if not file or not file.filename:
        return None

    extension = Path(file.filename).suffix.lower().lstrip(".")
    if extension not in ALLOWED_EXTENSIONS:
        raise ValueError("Format gambar harus JPG, JPEG, PNG, atau WEBP.")
    if file.mimetype and file.mimetype not in {
        "image/jpeg",
        "image/png",
        "image/webp",
    }:
        raise ValueError("Tipe file gambar tidak valid.")

    file.stream.seek(0, 2)
    size = file.stream.tell()
    file.stream.seek(0)
    if size > MAX_FILE_SIZE:
        raise ValueError("Ukuran gambar maksimal 5 MB.")
    if not cloudinary_configured():
        raise RuntimeError("Konfigurasi Cloudinary belum diisi pada file .env.")

    cloudinary.config(
        cloud_name=current_app.config["CLOUDINARY_CLOUD_NAME"],
        api_key=current_app.config["CLOUDINARY_API_KEY"],
        api_secret=current_app.config["CLOUDINARY_API_SECRET"],
        secure=True,
    )
    result = cloudinary.uploader.upload(
        file,
        folder=f"portfolio_vanessa/{subfolder}",
        public_id=str(uuid4()),
        overwrite=False,
        resource_type="image",
        transformation=[{"quality": "auto", "fetch_format": "auto"}],
    )
    secure_url = result.get("secure_url")
    if not secure_url:
        raise RuntimeError("Cloudinary tidak mengembalikan secure_url.")
    return secure_url
