#!/usr/bin/env python3
"""BWD Editorial Visual composer — 6 newsroom templates, 1080x1350.

Usage:  python3 tools/compose.py spec.json out.png
Spec (JSON):
  template   breaking | figure | budget | accountability | explainer | data
  category   label kategori (mis. "Politik Nasional")
  badge      opsional, label status merah-kuning (mis. "Belum Terverifikasi")
  headline   judul; *kata* = sorot kuning
  deck       opsional, 1 kalimat pendukung (maks ~18 kata)
  figures    [{slug, name, role}] maks 3 — HANYA tokoh yang namanya disebut di headline; foto dari tokoh/<slug>/
  show_names opsional true → tampilkan label nama/jabatan di foto tokoh (default: tidak; papan nama tokoh TANPA foto tetap tampil)
  graphic    opsional {type, label} — grafis editorial simbolik yang menjelaskan headline
             (type: kursi-kosong, penyadapan, gedung, uang, palu, dokumen, perisai, jaringan, karhutla, dana-karhutla)
  facts      [{icon, label, value}] maks 3 (icon: status police gov money calendar doc chart gavel people mic globe)
  bignum     {value, label}            (budget)
  meter      opsional {pct, label, left, right} (budget) — bar serapan/realisasi di samping bignum; pct HARUS angka bersumber
  points     ["...", "...", "..."]       (explainer, maks 3)
  bars       [{label, value, display}]  (data, maks 5)
  timeline   [{date, text}]            (data/explainer, maks 4)
  date, sources, photo_credit
  bg         opsional path latar foto (gedung/suasana) yang dipasok user
Foto tokoh: tokoh/<slug>/cutout.png (dibuat otomatis dari photo.jpg bila belum ada).
Tokoh tanpa foto → hanya papan nama (tanpa wajah buatan). Daftar yang hilang dicetak ke stdout.
"""
import json, sys, re, html, pathlib
from playwright.sync_api import sync_playwright
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import graphics

ROOT = pathlib.Path(__file__).resolve().parent.parent
NAVY, RED, YEL, WHITE = "#071B3A", "#E51E2A", "#FFD43B", "#F7F8FA"

ICONS = {  # 24x24 stroke icons
 "status": '<circle cx="12" cy="12" r="9"/><path d="M12 7v6M12 16.5v.5"/>',
 "police": '<path d="M12 3l7 3v5c0 5-3 8-7 10-4-2-7-5-7-10V6z"/><path d="M9 12l2 2 4-4"/>',
 "gov": '<path d="M3 21h18M5 21V10M19 21V10M9 21V10M15 21V10M2 10l10-6 10 6z"/>',
 "money": '<rect x="2" y="6" width="20" height="12" rx="2"/><circle cx="12" cy="12" r="3"/>',
 "calendar": '<rect x="3" y="5" width="18" height="16" rx="2"/><path d="M3 10h18M8 3v4M16 3v4"/>',
 "doc": '<path d="M6 2h9l5 5v15H6z"/><path d="M14 2v6h6M9 13h8M9 17h8"/>',
 "chart": '<path d="M4 20V10M10 20V4M16 20v-7M22 20H2"/>',
 "gavel": '<path d="M14 4l6 6M11 7l6 6M12.5 5.5l-6 6M3 21l7-7"/><path d="M8 9l7 7"/>',
 "people": '<circle cx="9" cy="8" r="3.5"/><path d="M2 21c0-4 3-6.5 7-6.5s7 2.5 7 6.5"/><circle cx="17.5" cy="9" r="2.5"/><path d="M17 14.5c3 0 5 2 5 5"/>',
 "mic": '<rect x="9" y="2" width="6" height="12" rx="3"/><path d="M5 11a7 7 0 0014 0M12 18v4"/>',
 "globe": '<circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3c3 3 3 15 0 18M12 3c-3 3-3 15 0 18"/>',
}

def icon(name, size=30, color=YEL):
    p = ICONS.get(name, ICONS["doc"])
    return f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">{p}</svg>'

def hl(s):
    s = html.escape(s)
    return re.sub(r"\*(.+?)\*", r'<em>\1</em>', s)

def cutout(slug):
    d = ROOT / "tokoh" / slug
    c = d / "cutout.png"
    if c.exists():
        return c
    src = next((p for p in [d / "photo.jpg", d / "photo.png", d / "photo.jpeg", d / "photo.webp"] if p.exists()), None)
    if not src:
        return None
    from rembg import remove, new_session
    from PIL import Image
    im = Image.open(src).convert("RGB")
    out = remove(im, session=new_session("u2net_human_seg"))
    bb = out.getbbox()
    if bb:
        out = out.crop(bb)
    out.save(c)
    return c

CSS = f"""
*{{margin:0;padding:0;box-sizing:border-box}}
html,body{{width:1080px;height:1350px;overflow:hidden;background:{NAVY}}}
.c{{position:relative;width:1080px;height:1350px;overflow:hidden;font-family:'Inter','Poppins',sans-serif;color:{WHITE};
  background:radial-gradient(900px 700px at 78% 28%,rgba(229,30,42,.38),transparent 62%),
             radial-gradient(700px 600px at 10% 90%,rgba(40,90,170,.25),transparent 60%),
             linear-gradient(180deg,#0A2450 0%,{NAVY} 55%,#040F22 100%)}}
.grid{{position:absolute;inset:0;background-image:linear-gradient(rgba(255,255,255,.035) 1px,transparent 1px),linear-gradient(90deg,rgba(255,255,255,.035) 1px,transparent 1px);background-size:54px 54px;mask-image:linear-gradient(180deg,#000 0%,transparent 70%)}}
.bgphoto{{position:absolute;inset:0;background-size:cover;background-position:center;opacity:.35;filter:grayscale(.3)}}
.brand{{position:absolute;top:52px;left:60px;display:flex;align-items:center;gap:14px;z-index:9}}
.brand i{{display:block;width:8px;height:44px;background:{RED}}}
.brand b{{font:900 30px 'Inter';letter-spacing:.04em}}
.cat{{display:inline-block;background:{RED};color:#fff;font:800 24px 'Inter';letter-spacing:.06em;text-transform:uppercase;padding:9px 18px;border-radius:6px}}
.badge{{display:inline-block;margin-left:12px;border:2px solid {YEL};color:{YEL};font:800 20px 'Inter';letter-spacing:.06em;text-transform:uppercase;padding:7px 14px;border-radius:6px;vertical-align:top}}
h1{{font:900 var(--fs,92px)/1.02 'Inter';letter-spacing:-.025em;text-wrap:balance;text-shadow:0 4px 24px rgba(0,0,0,.45)}}
h1 em{{font-style:normal;color:{YEL}}}
.deck{{margin-top:18px;font:600 28px/1.3 'Inter';color:rgba(247,248,250,.85);max-width:900px}}
.figs{{position:absolute;z-index:2}}
.fig{{position:absolute;bottom:0}}
.fig img{{display:block;width:100%;height:100%;object-fit:contain;object-position:bottom center;filter:drop-shadow(0 20px 40px rgba(0,0,0,.55));-webkit-mask-image:linear-gradient(180deg,#000 72%,transparent 100%);mask-image:linear-gradient(180deg,#000 72%,transparent 100%)}}
.plate{{position:absolute;z-index:6;background:rgba(7,27,58,.92);border-left:6px solid {RED};padding:10px 16px}}
.plate b{{display:block;font:800 26px 'Inter'}}
.plate span{{display:block;font:600 19px 'Inter';color:rgba(247,248,250,.75)}}
.chips{{display:flex;gap:10px;margin-bottom:18px;flex-wrap:wrap}}
.chip{{background:rgba(7,27,58,.9);border-left:5px solid {RED};padding:7px 12px}}
.chip b{{display:block;font:800 21px 'Inter'}}
.chip span{{display:block;font:600 15px 'Inter';color:rgba(247,248,250,.72)}}
.gfx{{position:absolute;z-index:2}}
.gfx svg{{display:block;filter:drop-shadow(0 18px 30px rgba(0,0,0,.5))}}
.glabel{{position:absolute;left:50%;bottom:18px;transform:translateX(-50%);white-space:nowrap;background:{YEL};color:{NAVY};font:900 22px 'Inter';letter-spacing:.06em;text-transform:uppercase;padding:8px 16px;border-radius:6px;z-index:6}}
.noface{{position:absolute;z-index:6;display:flex;align-items:center;gap:14px;background:rgba(255,255,255,.06);border:2px dashed rgba(255,255,255,.25);border-radius:12px;padding:16px 20px}}
.noface .ini{{width:64px;height:64px;border-radius:50%;background:{RED};display:grid;place-items:center;font:900 28px 'Inter'}}
.text{{position:absolute;left:60px;right:60px;z-index:7}}
.shade{{position:absolute;left:0;right:0;bottom:0;height:62%;z-index:3;background:linear-gradient(180deg,transparent 0%,rgba(4,15,34,.88) 38%,#040F22 100%)}}
.facts{{display:flex;gap:0;margin-top:30px;border:2px solid rgba(255,255,255,.18);border-radius:16px;background:rgba(7,27,58,.7)}}
.fact{{flex:1;padding:18px 22px;border-left:2px solid rgba(255,255,255,.14)}}
.fact:first-child{{border-left:0}}
.fact .l{{display:flex;align-items:center;gap:10px;font:600 20px 'Inter';color:rgba(247,248,250,.8)}}
.fact .v{{margin-top:8px;font:800 28px/1.12 'Inter';color:{YEL}}}
.foot{{position:absolute;left:60px;right:60px;bottom:40px;z-index:8;display:flex;justify-content:space-between;gap:24px;padding-top:16px;border-top:2px solid rgba(255,255,255,.2);font:500 20px 'Inter';color:rgba(247,248,250,.72)}}
.foot span:last-child{{text-align:right}}
.credit{{position:absolute;z-index:8;right:60px;font:500 15px 'Inter';color:rgba(247,248,250,.55)}}
.big{{display:inline-block;background:{YEL};color:{NAVY};border-radius:14px;padding:16px 26px;margin-top:26px}}
.big b{{display:block;font:900 84px/1 'Inter';letter-spacing:-.03em}}
.big span{{display:block;margin-top:6px;font:700 22px 'Inter'}}
.bigrow{{display:flex;align-items:stretch;gap:24px;margin-top:26px}}.bigrow .big{{margin-top:0}}
.meter{{flex:1;display:flex;flex-direction:column;justify-content:center;background:rgba(255,255,255,.05);border:2px solid rgba(255,255,255,.14);border-radius:14px;padding:16px 22px}}
.meter .ml{{font:700 21px 'Inter';color:#C9D2E0}}.meter .bar{{position:relative;height:34px;margin:12px 0 8px;background:rgba(255,255,255,.12);border-radius:17px;overflow:hidden}}
.meter .bar i{{position:absolute;left:0;top:0;bottom:0;background:{YEL};border-radius:17px}}.meter .ends{{display:flex;justify-content:space-between;font:800 21px 'Inter'}}.meter .ends b{{color:{YEL}}}
.pts{{margin-top:26px;display:grid;gap:14px}}
.pt{{display:flex;gap:18px;align-items:flex-start;background:rgba(255,255,255,.05);border-radius:12px;padding:16px 20px}}
.pt i{{flex:none;width:46px;height:46px;border-radius:50%;background:{YEL};color:{NAVY};display:grid;place-items:center;font:900 24px 'Inter';font-style:normal}}
.pt p{{font:600 30px/1.3 'Inter'}}
.bars{{margin-top:26px;display:grid;gap:14px}}
.bar{{display:grid;grid-template-columns:230px 1fr 170px;align-items:center;gap:16px;font:700 27px 'Inter'}}
.bar .t{{height:44px}}
.bar .t{{height:34px;background:rgba(255,255,255,.08);border-radius:6px;overflow:hidden}}
.bar .t div{{height:100%;background:linear-gradient(90deg,{RED},#ff5a3c);border-radius:6px}}
.bar .t div.hi{{background:{YEL}}}
.bar .d{{text-align:right;color:{YEL}}}
.tl{{margin-top:26px;display:flex;gap:0;position:relative}}
.tl:before{{content:"";position:absolute;left:0;right:0;top:15px;height:3px;background:rgba(255,255,255,.25)}}
.tli{{flex:1;position:relative;padding-top:42px;padding-right:14px}}
.tli:before{{content:"";position:absolute;top:6px;left:0;width:22px;height:22px;border-radius:50%;background:{RED};border:4px solid {NAVY}}}
.tli b{{display:block;font:800 22px 'Inter';color:{YEL}}}
.tli span{{display:block;margin-top:6px;font:600 20px/1.3 'Inter'}}
"""

def figures_html(figs, box, missing, sizes=None):
    """box=(left, top, width, height) area for figures."""
    L, T, W, H = box
    have = []
    for f in figs[:3]:
        c = cutout(f["slug"]) if f.get("slug") else None
        if c: have.append((f, c))
        else: missing.append(f.get("name") or f.get("slug"))
    out, plates = [], []
    n = len(have)
    if n == 1:
        lay = [(0.0, 1.0, 1.0, 3)]
    elif n == 2:
        lay = [(0.0, 0.58, 1.0, 4), (0.42, 0.58, 0.9, 3)]  # tokoh pertama (utama) di depan & lebih besar
    elif n == 3:
        # tokoh pertama = tokoh utama: tengah, paling besar, paling depan; dua lainnya di belakang kiri/kanan
        lay = [(0.22, 0.56, 1.0, 5), (0.0, 0.40, 0.74, 3), (0.60, 0.40, 0.74, 3)]
    else:
        lay = []
    for (f, c), (x, w, h, z) in zip(have, lay):
        fx, fw, fh = L + x * W, w * W, h * H
        out.append(f'<div class="fig" style="left:{fx:.0f}px;width:{fw:.0f}px;height:{fh:.0f}px;top:{T + H - fh:.0f}px;z-index:{z}"><img src="{c.as_uri()}"></div>')
        plates.append((f, fx, fw))
    return "\n".join(out), plates, [f for f in figs[:3] if (f.get("name") or f.get("slug")) in missing]

def plates_html(plates, y):
    s = []
    for f, fx, fw in plates:
        if not f.get("name"): continue
        s.append(f'<div class="plate" style="left:{max(40, fx + fw*0.08):.0f}px;top:{y}px"><b>{html.escape(f["name"])}</b><span>{html.escape(f.get("role",""))}</span></div>')
    return "\n".join(s)

def noface_html(nf, x, y):
    s = []
    for i, f in enumerate(nf):
        name = f.get("name") or f.get("slug")
        ini = "".join(w[0] for w in name.split()[:2]).upper()
        s.append(f'<div class="noface" style="left:{x}px;top:{y + i*110}px"><div class="ini">{ini}</div><div><b style="font:800 26px Inter">{html.escape(name)}</b><br><span style="font:600 19px Inter;opacity:.75">{html.escape(f.get("role",""))}</span></div></div>')
    return "\n".join(s)

def facts_html(facts):
    if not facts: return ""
    return '<div class="facts">' + "".join(
        f'<div class="fact"><div class="l">{icon(f.get("icon","doc"),26)}{html.escape(f["label"])}</div><div class="v">{html.escape(f["value"])}</div></div>'
        for f in facts[:3]) + "</div>"

def head_html(s):
    b = f'<span class="badge">{html.escape(s["badge"])}</span>' if s.get("badge") else ""
    deck = f'<div class="deck">{html.escape(s["deck"])}</div>' if s.get("deck") else ""
    return f'<div><span class="cat">{html.escape(s.get("category",""))}</span>{b}</div><h1 id="hl" style="margin-top:22px">{hl(s["headline"])}</h1>{deck}'

def build(s, missing):
    t = s.get("template", "breaking")
    figs = s.get("figures", [])
    parts = []
    if s.get("bg"):
        parts.append(f'<div class="bgphoto" style="background-image:url({pathlib.Path(s["bg"]).resolve().as_uri()})"></div>')
    parts.append('<div class="grid"></div><div class="brand"><i></i><b>BALAI WARGA DIGITAL</b></div>')
    textbottom = 120  # space for footer
    if t in ("breaking", "accountability", "figure"):
        nphoto = sum(1 for f in figs[:3] if f.get("slug") and ((ROOT/"tokoh"/f["slug"]/"cutout.png").exists() or any((ROOT/"tokoh"/f["slug"]).glob("photo.*"))))
        g = s.get("graphic") or {}
        area = (440, 120, 640, 760) if t != "figure" else (300, 110, 780, 820)
        if g.get("type") and nphoto == 1: area = (470, 110, 610, 790)
        if nphoto == 2: area = (60, 130, 960, 720)
        if nphoto >= 3: area = (40, 110, 1000, 760)
        fh, plates, nf = figures_html(figs, area, missing)
        if g.get("type") and nphoto <= 1:
            gx, gy, gs = (30, 150, 470) if nphoto == 1 else (300, 130, 480)
            lab = f'<div class="glabel">{html.escape(g.get("label",""))}</div>' if g.get("label") else ""
            parts.append(f'<div class="gfx" style="left:{gx}px;top:{gy}px;width:{gs}px">{graphics.svg(g["type"], gs)}{lab}</div>')
        parts.append(f'<div class="figs">{fh}</div><div class="shade"></div>')
        # Default: TANPA label nama untuk tokoh berfoto (nama sudah ada di headline). Aktifkan dengan "show_names": true.
        show = s.get("show_names", False)
        if show and t == "figure": parts.append(plates_html(plates[:1], 640))
        elif show and len(plates) == 1: parts.append(plates_html(plates, 580))
        elif show and len(plates) == 2: parts.append(plates_html(plates, 560))
        chips = ""
        if show and len(plates) >= 3:
            chips = '<div class="chips">' + "".join(f'<div class="chip"><b>{html.escape(f["name"])}</b><span>{html.escape(f.get("role",""))}</span></div>' for f, _, _ in sorted(plates, key=lambda q: q[1]) if f.get("name")) + '</div>'
        parts.append(noface_html(nf, 60, 180))
        body = (chips if t != "figure" else "") + head_html(s) + facts_html(s.get("facts"))
        parts.append(f'<div class="text" style="bottom:{textbottom}px">{body}</div>')
    elif t == "budget":
        fh, plates, nf = figures_html(figs[:1], (560, 140, 520, 640), missing)
        bn = s.get("bignum")
        big = f'<div class="big"><b>{html.escape(bn["value"])}</b><span>{html.escape(bn["label"])}</span></div>' if bn else ""
        m = s.get("meter")
        if m and big:
            big = (f'<div class="bigrow">{big}<div class="meter"><div class="ml">{html.escape(m.get("label",""))}</div>'
                   f'<div class="bar"><i style="width:{float(m["pct"]):.1f}%"></i></div>'
                   f'<div class="ends"><b>{html.escape(m.get("left",""))}</b><span>{html.escape(m.get("right",""))}</span></div></div></div>')
        g = s.get("graphic") or {}
        if g.get("type"):
            gx, gy, gs = (30, 150, 470) if fh else (300, 130, 480)
            lab = f'<div class="glabel">{html.escape(g.get("label",""))}</div>' if g.get("label") else ""
            gfx = f'<div class="gfx" style="left:{gx}px;top:{gy}px;width:{gs}px;z-index:4">{graphics.svg(g["type"], gs)}{lab}</div>'
        else:
            gfx = ""
        parts.append(f'<div class="figs">{fh}</div><div class="shade"></div>{gfx}')
        parts.append(noface_html(nf, 60, 180))
        parts.append(f'<div class="text" style="bottom:{textbottom}px">{head_html(s)}{big}{facts_html(s.get("facts"))}</div>')
    elif t == "explainer":
        fh, plates, nf = figures_html(figs[:1], (700, 110, 380, 470), missing)
        pts = "".join(f'<div class="pt"><i>{i+1}</i><p>{html.escape(p)}</p></div>' for i, p in enumerate(s.get("points", [])[:3]))
        tl = timeline_html(s.get("timeline"))
        parts.append(f'<div class="figs">{fh}</div>')
        parts.append(f'<div class="text" style="top:190px;bottom:{textbottom}px;display:flex;flex-direction:column;justify-content:space-evenly"><div style="margin-right:{330 if fh else 0}px">{head_html(s)}</div><div class="pts">{pts}</div>{tl}</div>')
    elif t == "data":
        fh, plates, nf = figures_html(figs[:1], (760, 110, 320, 400), missing)
        bars = s.get("bars", [])[:5]
        mx = max([b["value"] for b in bars] or [1])
        bh = "".join(f'<div class="bar"><span>{html.escape(b["label"])}</span><div class="t"><div class="{"hi" if b.get("highlight") else ""}" style="width:{100*b["value"]/mx:.1f}%"></div></div><span class="d">{html.escape(b.get("display", str(b["value"])))}</span></div>' for b in bars)
        parts.append(f'<div class="figs">{fh}</div>')
        parts.append(f'<div class="text" style="top:190px;bottom:{textbottom}px;display:flex;flex-direction:column;justify-content:space-evenly"><div style="margin-right:{300 if fh else 0}px">{head_html(s)}</div><div class="bars">{bh}</div><div>{timeline_html(s.get("timeline"))}</div></div>')
    foot = f'<div class="foot"><span>{html.escape(s.get("date",""))}</span><span>Sumber: {html.escape(s.get("sources",""))}</span></div>'
    cred = f'<div class="credit" style="bottom:12px">{html.escape(s["photo_credit"])}</div>' if s.get("photo_credit") else ""
    return f'<!doctype html><html><head><meta charset="utf-8"><style>{CSS}</style></head><body><div class="c">{"".join(parts)}{foot}{cred}</div></body></html>'

def timeline_html(tl):
    if not tl: return ""
    return '<div class="tl">' + "".join(f'<div class="tli"><b>{html.escape(x["date"])}</b><span>{html.escape(x["text"])}</span></div>' for x in tl[:4]) + "</div>"

def main():
    spec = json.load(open(sys.argv[1])); out = sys.argv[2]
    missing = []
    page = build(spec, missing)
    tmp = pathlib.Path(out).with_suffix(".html"); tmp.write_text(page, encoding="utf-8")
    with sync_playwright() as p:
        b = p.chromium.launch(); pg = b.new_page(viewport={"width": 1080, "height": 1350})
        pg.goto(tmp.resolve().as_uri())
        # shrink headline until text block fits below the brand bar and doesn't exceed 4 lines
        pg.evaluate("""()=>{const h=document.getElementById('hl');if(!h)return;let fs=92;
          const ok=()=>{const r=h.getBoundingClientRect();const blocks=[...document.querySelectorAll('.text')];
            const top=Math.min(...blocks.map(x=>x.getBoundingClientRect().top));
            const bot=Math.max(...blocks.map(x=>x.getBoundingClientRect().bottom));
            const minTop=document.querySelector('.plate,.glabel')?600:130;
            return r.height<=fs*1.02*4.1 && top>=minTop && bot<=1236 && h.scrollWidth<=h.clientWidth};
          while(!ok()&&fs>54){fs-=2;h.style.setProperty('--fs',fs+'px')}
          // baris papan nama + label grafis selalu tepat di atas blok teks (tidak menimpa kategori/badge/headline)
          const t=document.querySelector('.text');if(!t)return;const row=t.getBoundingClientRect().top-16;
          document.querySelectorAll('.plate').forEach(pl=>{pl.style.top=(row-pl.offsetHeight)+'px'});
          const g=document.querySelector('.gfx');if(g){const lab=g.querySelector('.glabel');const gs=g.offsetWidth;
            let top=lab?row-gs+18:row-gs;const minT=120;
            if(top<minT){const sc=(gs-(minT-top))/gs;const sv=g.querySelector('svg');sv.style.transformOrigin='bottom center';sv.style.transform='scale('+sc+')';}
            g.style.top=top+'px'}}""")
        pg.wait_for_timeout(250); pg.screenshot(path=out); b.close()
    tmp.unlink()
    print(json.dumps({"out": out, "missing_photos": missing}))

if __name__ == "__main__":
    main()
