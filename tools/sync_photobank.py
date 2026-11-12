#!/usr/bin/env python3
"""Sinkronkan Photo Bank v2 (folder laptop pemilik akun) ke tokoh/ di repo.

Usage: python3 tools/sync_photobank.py <staged_root> <listing.json> [--plan | --apply]
  staged_root   folder hasil device_stage_files (…/uploads/balai_warga_photo_bank_v2)
  listing.json  hasil device_list_dir (recursive) folder laptop — dipakai untuk mtime
  --plan        cetak JSON {"stage": [...relpath...], "slugs": [...]} : file yang perlu di-stage
  --apply       proses file yang sudah di-stage, tulis tokoh/<slug>/ + index + manifest, cetak laporan JSON

Aturan pemilihan per tokoh:
  1. approved/<slug>.<ext> (atau approved/<slug>_*.<ext>) → dipakai, verified=true (sudah disetujui pemilik akun).
  2. Selain itu, kandidat terbaik di candidates/<slug>/ berdasar metadata (judul Commons cocok nama, potret, resolusi,
     bukan foto grup/acara) → verified=true (pemilik akun menyatakan semua foto di folder sudah disetujui, 13 Nov 2026).
  Semua perubahan di folder pemilik akun sudah disetujui: bila kandidat terbaik sebuah tokoh berubah (file baru/diperbarui),
  foto tokoh itu diganti — termasuk tokoh yang sudah ada. approved/ tetap diprioritaskan di atas candidates/.
  Kolom review_status di downloaded_candidates.csv bernilai APPROVED/REJECTED dihormati.
Slug bertanda "REJECTED:..." (mtime = mtime file saat ditolak) dicoba lagi hanya bila ada file yang lebih baru atau ada file di approved/.
Manifest: tokoh/_sync_manifest.json menyimpan sumber + mtime per slug supaya hanya perubahan yang diproses.
"""
import csv, json, re, sys, datetime, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
T = ROOT / "tokoh"
MAN = T / "_sync_manifest.json"
IMG = (".jpg", ".jpeg", ".png", ".webp")
BAD = re.compile(r"(logo|signature|seal|lambang|map|flag|bendera|family|group|bersama|with |dan |&| and |meeting|rapat|visit|kunjungan|pelantikan|serah terima|formasi|dinner|welcomes|upacara|menghadiri|grave|makam)", re.I)

def tok(s): return [t for t in re.findall(r"[a-z]+", s.lower()) if len(t) > 2]

def load(staged):
    S = pathlib.Path(staged)
    rows = list(csv.DictReader(open(S / "metadata/downloaded_candidates.csv", encoding="utf-8-sig"))) if (S / "metadata/downloaded_candidates.csv").exists() else []
    roster = {r["filename_slug"]: r for r in csv.DictReader(open(S / "metadata/master_roster.csv", encoding="utf-8-sig"))} if (S / "metadata/master_roster.csv").exists() else {}
    return S, rows, roster

def score(r):
    w, h = int(r.get("width") or 0), int(r.get("height") or 0)
    t = r.get("commons_file_title", ""); nt = tok(r.get("display_name", ""))
    hit = sum(1 for x in nt if x in t.lower()) / max(1, len(nt))
    s = hit * 3 + (1 if h >= w else 0) + min(w, 2000) / 1000 + (0.5 if re.search("official|resmi|portrait|potret", t, re.I) else 0)
    if BAD.search(t): s -= 3
    if w and w < 300: s -= 1.5
    if (r.get("review_status") or "").upper().startswith("REJECT"): s -= 100
    if (r.get("review_status") or "").upper() == "APPROVED": s += 50
    return s

def files_from_listing(listing):
    d = json.load(open(listing))
    return {e["name"]: e.get("mtimeMs", 0) for e in d.get("entries", []) if e.get("type") == "file"}

def canon_of(slug, man):
    return next((k for k, v in man.items() if slug in v.get("aliases", [])), slug)

def decide(files, rows, man):
    """Kembalikan [(slug_kanonik, relpath, row)] yang perlu diproses.
    Sebuah tokoh diproses bila (a) belum pernah disinkron, atau (b) ada file di folder
    candidates/<slug>/ atau approved/<slug>* yang lebih baru dari 'seen' di manifest.
    Untuk (b), file terbaru yang berubah lebih diutamakan (itu yang baru ditambahkan pemilik akun)."""
    by_slug = {}
    for rel, mt in files.items():
        if not rel.lower().endswith(IMG): continue
        if rel.startswith("approved/"):
            sl = re.split(r"[_.]", pathlib.Path(rel).stem)[0].lower()
        elif rel.startswith("candidates/"):
            sl = rel.split("/")[-2]  # folder yang langsung berisi file (juga menangani folder tokoh yang terselip di folder lain)
        else: continue
        by_slug.setdefault(canon_of(sl, man), []).append((rel, mt, sl))
    rowmap = {r["candidate_path"]: r for r in rows}
    out = []
    for slug, fl in by_slug.items():
        m = man.get(slug, {}); seen = m.get("seen", 0)
        newer = [f for f in fl if f[1] > seen]
        if m and not newer: continue
        pool = newer if m else fl
        appr = [f for f in pool if f[0].startswith("approved/")]
        if appr:
            rel = max(appr, key=lambda f: f[1])[0]; out.append((slug, rel, {}, True)); continue
        scored = []
        for rel, mt, sl in pool:
            r = rowmap.get(rel)
            sc = score(r) if r else 2.5  # file tanpa baris metadata: tetap dipakai (folder sudah disetujui)
            scored.append((sc, mt, rel, r or {}))
        scored.sort(key=lambda x: (-x[0], -x[1]))
        if not scored or scored[0][0] < 2:
            if m: out.append((slug, None, {}, False))  # hanya perbarui 'seen'
            continue
        out.append((slug, scored[0][2], scored[0][3], True))
    return out, by_slug

def plan(staged, listing):
    files = files_from_listing(listing)
    man = json.loads(MAN.read_text()) if MAN.exists() else {}
    S = pathlib.Path(staged)
    rows = list(csv.DictReader(open(S / "metadata/downloaded_candidates.csv", encoding="utf-8-sig"))) if (S / "metadata/downloaded_candidates.csv").exists() else []
    todo, _ = decide(files, rows, man)
    stage = ["metadata/downloaded_candidates.csv", "metadata/master_roster.csv"] + [t[1] for t in todo if t[1]]
    print(json.dumps({"stage": stage, "slugs": sorted(t[0] for t in todo if t[1])}, ensure_ascii=False))

def apply(staged, listing):
    from PIL import Image, ImageOps
    from rembg import remove, new_session
    Image.MAX_IMAGE_PIXELS = None
    S, rows, roster = load(staged)
    files = files_from_listing(listing)
    by_path = {r["candidate_path"]: r for r in rows}
    man = json.loads(MAN.read_text()) if MAN.exists() else {}
    idx = json.loads((T / "index.json").read_text()) if (T / "index.json").exists() else {}
    sess = new_session("u2net_human_seg"); report = []
    decided, by_slug = decide(files, rows, man)
    todo = []
    for slug, rel, r, verified in decided:
        seen = max(f[1] for f in by_slug[slug])
        if rel is None:
            man.setdefault(slug, {})["seen"] = seen; continue
        if not (S / rel).exists():
            print(json.dumps({"warning": "belum di-stage", "file": rel})); continue
        todo.append((slug, rel, verified, r, seen))
    for slug, rel, verified, r, seen in todo:
        ro = roster.get(slug, {})
        d = T / slug; d.mkdir(parents=True, exist_ok=True)
        im = ImageOps.exif_transpose(Image.open(S / rel)).convert("RGB"); im.thumbnail((1600, 1600), Image.LANCZOS)
        im.save(d / "photo.jpg", quality=92)
        cut = remove(im, session=sess); bb = cut.getbbox(); cut = cut.crop(bb) if bb else cut; cut.save(d / "cutout.png")
        old = json.loads((d / "meta.json").read_text()) if (d / "meta.json").exists() else {}
        meta = {"slug": slug, "name": r.get("display_name") or ro.get("display_name") or old.get("name") or slug.replace("-", " ").title(),
                "role": ro.get("role_context") or old.get("role", ""), "aliases": old.get("aliases", []),
                "credit": (r.get("author") or r.get("credit") or old.get("credit") or ro.get("photographer_credit") or "dok. pemberitaan").strip(),
                "license": r.get("license") or ro.get("license") or old.get("license", "Belum dicek"),
                "license_url": r.get("license_url", ""), "source_page": r.get("source_page") or ro.get("source_page_url", ""),
                "commons_title": r.get("commons_file_title", ""), "role_verified": ro.get("last_role_verified", ""),
                "verified": verified, "verified_date": datetime.date.today().isoformat() if verified else "",
                "review": ("Disetujui pemilik akun (folder approved/)" if rel.startswith("approved/") else "Dari folder pemilik akun; semua isi folder sudah disetujui pemilik akun"),
                "width": im.width, "added": old.get("added") or datetime.date.today().isoformat(), "updated": datetime.date.today().isoformat(),
                "source": "Photo Bank v2 milik pemilik akun"}
        (d / "meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2))
        idx[slug] = {"name": meta["name"], "role": meta["role"], "aliases": meta["aliases"]}
        man[slug] = {"source": rel, "mtime": files[rel], "seen": seen, "aliases": meta["aliases"]}
        report.append({"slug": slug, "name": meta["name"], "verified": verified, "width": im.width, "low_res": im.width < 600, "new": not old})
    (T / "index.json").write_text(json.dumps(dict(sorted(idx.items())), ensure_ascii=False, indent=2))
    MAN.write_text(json.dumps(dict(sorted(man.items())), ensure_ascii=False, indent=2))
    print(json.dumps(report, ensure_ascii=False))

if __name__ == "__main__":
    staged, listing, mode = sys.argv[1], sys.argv[2], (sys.argv[3] if len(sys.argv) > 3 else "--plan")
    (apply if mode == "--apply" else plan)(staged, listing)
