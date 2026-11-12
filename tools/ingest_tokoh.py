#!/usr/bin/env python3
"""Proses foto tokoh yang di-upload langsung ke folder tokoh/ lewat GitHub.

Pemilik akun cukup meng-upload file seperti tokoh/gibran-rakabuming.jpg.
Skrip ini mengubahnya menjadi tokoh/<slug>/{photo.jpg,cutout.png,meta.json} dan memperbarui tokoh/index.json.
Kredit opsional di tokoh/kredit.txt, satu baris per tokoh:  gibran-rakabuming: BPMI Setpres
Nama tampil opsional di tokoh/nama.txt:                      gibran-rakabuming: Gibran Rakabuming Raka | Wakil Presiden
Usage: python3 tools/ingest_tokoh.py   (cetak JSON daftar yang diproses)
"""
import json, re, pathlib, datetime
from PIL import Image

ROOT = pathlib.Path(__file__).resolve().parent.parent
T = ROOT / "tokoh"

def kv(name):
    p = T / name
    out = {}
    if p.exists():
        for line in p.read_text(encoding="utf-8").splitlines():
            if ":" in line and not line.lstrip().startswith("#"):
                k, v = line.split(":", 1)
                out[slugify(k)] = v.strip()
    return out

def slugify(s):
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")

def main():
    credits, names = kv("kredit.txt"), kv("nama.txt")
    idx_p = T / "index.json"
    idx = json.loads(idx_p.read_text()) if idx_p.exists() else {}
    done = []
    files = [p for p in T.iterdir() if p.is_file() and p.suffix.lower() in (".jpg", ".jpeg", ".png", ".webp")]
    session = None
    for f in sorted(files):
        slug = slugify(f.stem)
        d = T / slug
        d.mkdir(exist_ok=True)
        im = Image.open(f).convert("RGB")
        im.thumbnail((1600, 1600), Image.LANCZOS)
        im.save(d / "photo.jpg", quality=92)
        if session is None:
            from rembg import new_session
            session = new_session("u2net_human_seg")
        from rembg import remove
        cut = remove(im, session=session)
        bb = cut.getbbox()
        if bb: cut = cut.crop(bb)
        cut.save(d / "cutout.png")
        nm, role = (names.get(slug, "") + "|").split("|")[:2]
        nm = nm.strip() or " ".join(w.capitalize() for w in slug.split("-"))
        meta = {"slug": slug, "name": nm, "role": role.strip(), "credit": credits.get(slug, "dok. pemberitaan"),
                "license": "Belum dicek", "added": datetime.date.today().isoformat(),
                "source": "di-upload pemilik akun ke GitHub", "width": im.width}
        (d / "meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2))
        idx[slug] = {"name": nm, "role": role.strip(), "aliases": []}
        f.unlink()
        done.append({"slug": slug, "name": nm, "width": im.width, "low_res": im.width < 600})
    # apply later edits to kredit/nama for existing entries
    for slug, cr in credits.items():
        m = T / slug / "meta.json"
        if m.exists():
            meta = json.loads(m.read_text()); meta["credit"] = cr; m.write_text(json.dumps(meta, ensure_ascii=False, indent=2))
    for slug, v in names.items():
        if slug in idx:
            nm, role = (v + "|").split("|")[:2]
            idx[slug].update({"name": nm.strip() or idx[slug]["name"], "role": role.strip() or idx[slug]["role"]})
            m = T / slug / "meta.json"
            if m.exists():
                meta = json.loads(m.read_text()); meta.update({"name": idx[slug]["name"], "role": idx[slug]["role"]}); m.write_text(json.dumps(meta, ensure_ascii=False, indent=2))
    idx_p.write_text(json.dumps(dict(sorted(idx.items())), ensure_ascii=False, indent=2))
    print(json.dumps(done, ensure_ascii=False))

if __name__ == "__main__":
    main()
