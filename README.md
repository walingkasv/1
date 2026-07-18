# Web Portofolio — Vanessa Ruth Walingkas

Project portofolio Flask untuk:

- Nama: Vanessa Ruth Walingkas
- NIM: 682024101
- Program Studi: Sistem Informasi
- Database: `portfolio_vanessa`

## Fitur

- Halaman portofolio dinamis.
- Login dan session admin dengan password hash.
- CRUD profil, skill, pengalaman, dan proyek.
- Pengelolaan pesan kontak.
- Upload foto profil dan gambar proyek ke Cloudinary.
- Penyimpanan pesan ke TiDB dan pengiriman email melalui Resend.
- Validasi CSRF untuk form admin dan validasi upload maksimal 5 MB.

## Cara menjalankan

1. Buka terminal pada folder project.

2. Instal dependency:

   ```bash
   python3 -m pip install -r requirements.txt
   ```

   Pada Windows:

   ```powershell
   python -m pip install -r requirements.txt
   ```

3. Salin file konfigurasi:

   ```bash
   cp .env.example .env
   ```

   Pada Windows:

   ```powershell
   copy .env.example .env
   ```

4. Isi `.env` dengan konfigurasi TiDB, Cloudinary, dan Resend. Jangan unggah
   `.env` ke Git atau memasukkannya ke ZIP pengumpulan.

5. Jalankan `DB_682024101_VANESSA_RUTH_WALINGKAS.sql` melalui TiDB SQL Editor.

6. Jalankan aplikasi:

   ```bash
   python3 app.py
   ```

   atau pada Windows:

   ```powershell
   python app.py
   ```

7. Buka `http://127.0.0.1:5000`.

8. Buka halaman admin di `http://127.0.0.1:5000/admin/login`.

   Login awal:

   - Username: `admin`
   - Password: `admin123`

Akun awal dibuat ketika login pertama dilakukan pada database yang tabelnya
sudah disiapkan. Segera ubah username atau password melalui menu Akun.

## Konfigurasi TiDB

Aplikasi hanya menggunakan TiDB. `DB_CA_PATH` boleh dikosongkan agar aplikasi
menggunakan CA bundle dari `certifi`, atau diisi dengan path file CA yang
disediakan oleh TiDB.

Seluruh query nilai pengguna menggunakan parameter query. Credential database
dibaca dari environment variable dan tidak ditulis di source code.

## Cloudinary

Isi `CLOUDINARY_CLOUD_NAME`, `CLOUDINARY_API_KEY`, dan
`CLOUDINARY_API_SECRET`. Upload tersedia pada halaman Profil dan Proyek. Hanya
JPG, JPEG, PNG, dan WEBP dengan ukuran maksimal 5 MB yang diterima.

## Resend

Isi `RESEND_API_KEY`, `RESEND_FROM_EMAIL`, dan `CONTACT_TO_EMAIL`. Pesan kontak
tetap disimpan ke TiDB jika layanan email sedang gagal.

## Screenshot pengumpulan

Petunjuk bukti screenshot tersedia di folder `screenshots`. Screenshot
Cloudinary dan Resend harus berasal dari layanan asli; project ini tidak
menyertakan bukti palsu.

## Catatan keamanan

- Jangan membagikan isi `.env`.
- Ganti password admin setelah login pertama.
- Jangan menaruh credential asli di `.env.example`, SQL, README, atau source.
