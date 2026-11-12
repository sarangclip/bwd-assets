#!/usr/bin/env python3
"""Tambah foto tokoh ke Photo Bank BWD.

Usage: python3 tools/add_photo.py <foto> <slug> "<Nama Lengkap>" "<Jabatan>" "<Sumber/kredit>" [--license "<lisensi>"] [--date YYYY-MM-DD]
Membuat tokoh/<slug>/photo.jpg (maks 1600 px), cutout.png (latar transparan), dan meta.json.
"""
import sys, json, argparse, pathlib, datetime
from PIL import Image

ROOT = pathlib.Path(__file__).resolve().parent.parent
ap = argparse.ArgumentParser()
ap.add_argument("src"); ap.add_argument("slug"); ap.add_argument("name"); ap.add_argument("role"); ap.add_argument("credit")
ap.add_argument("--license", default="Belum dicek"); ap.add_argument("--date", default="")
a = ap.parse_args()

d = ROOT / "tokoh" / a.slug
d.mkdir(parents=True, exist_ok=True)
im = Image.open(a.src).convert("RGB")
im.thumbnail((1600, 1600), Image.LANCZOS)
im.save(d / "photo.jpg", quality=92)
if im.width < 500:
    print(f"PERINGATAN: resolusi rendah ({im.width}px) — hasil bisa kurang tajam")

from rembg import remove, new_session
out = remove(im, session=new_session("u2net_human_seg"))
bb = out.getbbox()
if bb: out = out.crop(bb)
out.save(d / "cutout.png")

meta = {"slug": a.slug, "name": a.name, "role": a.role, "credit": a.credit, "license": a.license,
        "photo_date": a.date, "added": datetime.date.today().isoformat(), "source": "dikirim pemilik akun"}
(d / "meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2))

idx = ROOT / "tokoh" / "index.json"
data = json.loads(idx.read_text()) if idx.exists() else {}
data[a.slug] = {"name": a.name, "role": a.role, "aliases": []}
idx.write_text(json.dumps(dict(sorted(data.items())), ensure_ascii=False, indent=2))
print(json.dumps(meta, ensure_ascii=False))
