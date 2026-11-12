# bwd-assets

Aset produksi visual Balai Warga Digital.

- `tools/compose.py` — engine 6 template editorial (1080x1350).
- `tools/add_photo.py` — tambah foto tokoh ke Photo Bank.
- `tools/render.py`, `tools/bg_nophoto.py` — template headline lama (bwd-headline-post).
- `tokoh/<slug>/` — Photo Bank: photo.jpg, cutout.png, meta.json (sumber & lisensi). `tokoh/index.json` daftar tokoh.
- `foto/BWD-<ID>.jpg` — foto khusus per berita (opsional, dipasok pemilik akun).
- `posts/YYYY-MM/` — visual final yang dipakai Notion & Publer.

Foto tokoh hanya dari pemilik akun. Kredit dan lisensi wajib tercatat di meta.json.
