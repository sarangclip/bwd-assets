"""Motion reel BWD 1080x1920, 8 detik, 30 fps (bagian D skill bwd-editorial-visual-intelligence).

Usage: python3 tools/motion_reel.py spec.json out.mp4 [--frames-dir DIR] [--still 2.6,7.0]

Spec JSON:
{
  "category": "Politik Nasional",           # pill merah
  "badge": "Belum Terverifikasi",           # opsional, pill outline
  "headline": "Teks dengan *kata sorotan*\\nbaris berikutnya",   # \\n = <br>
  "deck": "maks ~18 kata",                  # opsional
  "date": "Senin, 23 November 2026",
  "sources": "Suara.com, Antara News",
  "card": {
     "photos": ["hasto-kristiyanto", "jokowi"],   # slug Photo Bank; hanya tokoh di headline
     "graphic": {"type": "kursi-kosong"},          # opsional (tidak dipakai bila 2 foto)
     "bignum": {"value": "Rp945", "unit": "triliun"}, # opsional (menggantikan grafis)
     "label": "BELUM DIKONFIRMASI"                 # strip kuning di tepi bawah kartu
  },
  "facts": [{"label": "Proses", "value": "Penyidikan"}, ...]   # maks 3
}
"""
import html
import json
import os
import re
import shutil
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import graphics  # noqa: E402

W, H, FPS, DUR = 1080, 1920, 30, 8.0


def esc(s):
    return html.escape(s or "", quote=False)


def headline_html(s):
    s = esc(s)
    s = re.sub(r"\*(.+?)\*", r'<span class="y">\1</span>', s)
    return s.replace("\n", "<br>")


def photo_info(slug):
    d = os.path.join(ROOT, "tokoh", slug)
    meta = json.load(open(os.path.join(d, "meta.json"), encoding="utf-8"))
    photo = os.path.join(d, "photo.jpg")
    if not os.path.exists(photo):
        raise FileNotFoundError(f"foto tidak ada: {slug}")
    return {
        "src": "file://" + photo,
        "credit": html.unescape(meta.get("credit", "")),
        "name": meta.get("name", slug),
    }


def build_html(spec, out_html):
    card = spec.get("card", {})
    photos = [photo_info(s) for s in card.get("photos", [])][:2]
    credits = []
    for p in photos:
        if p["credit"] and p["credit"] not in credits:
            credits.append(p["credit"])
    credit_line = ("Foto: " + " / ".join(credits)) if credits else ""

    # --- isi kartu
    card_html = ""
    if photos and len(photos) == 2:
        card_html = (
            f'<div class="ph" style="left:60px;top:30px;width:290px;height:380px;background-image:url({photos[0]["src"]})"></div>'
            f'<div class="ph" style="left:410px;top:30px;width:290px;height:380px;background-image:url({photos[1]["src"]})"></div>'
        )
    elif photos:
        card_html = (
            f'<div class="ph" style="left:40px;top:30px;width:290px;height:380px;background-image:url({photos[0]["src"]})"></div>'
        )
        g = card.get("graphic")
        if g:
            card_html += f'<div class="gfx" style="left:370px;top:70px;width:340px;height:340px">{graphics.svg(g["type"], 340)}</div>'
    elif card.get("bignum"):
        b = card["bignum"]
        card_html = (
            f'<div class="big"><div class="bv">{esc(b["value"])}</div>'
            f'<div class="bu">{esc(b.get("unit", ""))}</div></div>'
        )
        g = card.get("graphic")
        if g:
            card_html += f'<div class="gfx" style="left:420px;top:70px;width:300px;height:300px">{graphics.svg(g["type"], 300)}</div>'
        if g:
            card_html = card_html.replace('class="big"', 'class="big" style="width:400px"')
    elif card.get("graphic"):
        g = card["graphic"]
        card_html = f'<div class="gfx" style="left:180px;top:40px;width:400px;height:400px">{graphics.svg(g["type"], 400)}</div>'

    credit_html = f'<div class="cr">{esc(credit_line)}</div>' if credit_line else ""
    label = esc(card.get("label", ""))
    label_html = f'<div class="strip">{label}</div>' if label else ""

    hl = spec["headline"]
    plain_len = len(re.sub(r"\*", "", hl))
    hl_size, hl_lh = (96, 88) if plain_len <= 36 else ((84, 78) if plain_len <= 56 else (72, 70))

    facts = spec.get("facts", [])[:3]
    fact_cells = "".join(
        f'<div class="cell"><div class="fl">{esc(f["label"])}</div><div class="fv">{esc(f["value"])}</div></div>'
        for f in facts
    )
    badge = spec.get("badge")
    badge_html = f'<div class="badge">{esc(badge)}</div>' if badge else ""

    page = f"""<!doctype html>
<html lang="id"><head><meta charset="utf-8">
<style>
*{{box-sizing:border-box;margin:0;padding:0}}
html,body{{width:{W}px;height:{H}px;overflow:hidden;background:#050F24}}
body{{font-family:Inter,"Helvetica Neue",Arial,sans-serif;color:#F7F8FA}}
#stage{{position:absolute;left:0;top:0;width:{W}px;height:{H}px;overflow:hidden;
 background:linear-gradient(180deg,#0E2A5A 0%,#081E42 55%,#050F24 100%)}}
#grid{{position:absolute;inset:0;background-image:linear-gradient(rgba(255,255,255,.035) 1px,transparent 1px),linear-gradient(90deg,rgba(255,255,255,.035) 1px,transparent 1px);background-size:60px 60px}}
#glow{{position:absolute;left:640px;top:900px;width:900px;height:900px;margin:-450px 0 0 -450px;border-radius:50%;
 background:radial-gradient(circle,rgba(229,30,42,.55) 0%,rgba(229,30,42,0) 65%)}}
.abs{{position:absolute}}
#logo-bar{{left:60px;top:250px;width:8px;height:50px;background:#E51E2A}}
#logo{{left:86px;top:250px;font-size:36px;font-weight:800;line-height:50px;letter-spacing:1px}}
#meta{{left:60px;top:318px;font-size:26px;color:rgba(247,248,250,.6);white-space:nowrap}}
#card{{left:160px;top:356px;width:760px;height:500px;border-radius:28px;border:2px solid rgba(255,255,255,.18);
 background:linear-gradient(160deg,rgba(40,90,170,.42),rgba(12,40,90,.55))}}
.ph{{position:absolute;border-radius:18px;background-size:cover;background-position:center 20%;border:2px solid rgba(255,255,255,.18)}}
.gfx{{position:absolute}}
.gfx svg{{display:block}}
.big{{position:absolute;left:0;top:60px;width:760px;text-align:center}}
.bv{{font-size:140px;font-weight:900;color:#FFD43B;line-height:150px;letter-spacing:-3px;white-space:nowrap}}
.bu{{font-size:28px;font-weight:700;color:rgba(247,248,250,.9);margin-top:8px;line-height:34px}}
.strip{{position:absolute;left:140px;top:480px;width:480px;height:52px;background:#FFD43B;color:#071B3A;
 font-size:26px;font-weight:900;line-height:52px;text-align:center;border-radius:6px;letter-spacing:.5px}}
.cr{{position:absolute;right:18px;top:8px;font-size:18px;color:rgba(247,248,250,.72);white-space:nowrap}}
#pills{{left:60px;top:926px;height:48px;display:flex;gap:14px;align-items:center}}
.pill{{height:48px;line-height:48px;padding:0 22px;background:#E51E2A;font-size:28px;font-weight:800;letter-spacing:2px;border-radius:6px;white-space:nowrap}}
.badge{{height:48px;line-height:46px;padding:0 20px;border:2px solid #FFD43B;color:#FFD43B;font-size:24px;font-weight:800;border-radius:6px;white-space:nowrap}}
#hl{{left:60px;top:996px;width:960px;font-size:{hl_size}px;font-weight:900;line-height:{hl_lh}px;letter-spacing:-2px}}
.y{{color:#FFD43B}}
#deck{{left:60px;top:1368px;width:960px;font-size:32px;font-weight:500;line-height:42px;color:rgba(247,248,250,.86)}}
#facts{{left:60px;top:1472px;width:960px;height:70px;border-radius:16px;border:2px solid rgba(255,255,255,.14);display:flex;overflow:hidden}}
.cell{{flex:1;padding:10px 18px;border-right:2px solid rgba(255,255,255,.14)}}
.cell:last-child{{border-right:none}}
.fl{{font-size:20px;color:rgba(247,248,250,.7);line-height:24px}}
.fv{{font-size:27px;font-weight:800;color:#FFD43B;line-height:34px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}}
#sweep{{left:0;top:-200px;width:260px;height:2400px;background:linear-gradient(90deg,rgba(255,255,255,0),rgba(255,255,255,.16),rgba(255,255,255,0));transform:rotate(16deg);opacity:0}}
#brand-foot{{left:60px;top:1600px;font-size:22px;color:rgba(247,248,250,.45);white-space:nowrap}}
</style></head>
<body>
<div id="stage">
 <div id="grid" class="abs"></div>
 <div id="glow" class="abs"></div>
 <div id="logo-bar" class="abs"></div>
 <div id="logo" class="abs">BALAI WARGA DIGITAL</div>
 <div id="meta" class="abs">{esc(spec.get("date",""))} · Sumber: {esc(spec.get("sources",""))}</div>
 <div id="card" class="abs">{card_html}{credit_html}{label_html}</div>
 <div id="pills" class="abs"><div class="pill">{esc(spec.get("category","").upper())}</div>{badge_html}</div>
 <div id="hl" class="abs">{headline_html(hl)}</div>
 <div id="deck" class="abs">{esc(spec.get("deck",""))}</div>
 <div id="facts" class="abs">{fact_cells}</div>
 <div id="sweep" class="abs"></div>
</div>
<script>
function E(t,a,b){{ if(t<=a) return 0; if(t>=b) return 1; const x=(t-a)/(b-a); return x*x*(3-2*x); }}
function S(id,o){{ const el=document.getElementById(id); if(el) el.style.opacity=o; }}
function T(id,y,o){{ const el=document.getElementById(id); if(el){{ el.style.transform='translateY('+y+'px)'; el.style.opacity=o; }} }}
function render(t){{
  document.getElementById('stage').style.opacity = E(t,0,0.35);
  const g = 0.85 + 0.15*Math.sin(2*Math.PI*t/2.4);
  document.getElementById('glow').style.opacity = g;
  S('logo', E(t,0.05,0.45)); S('logo-bar', E(t,0.05,0.45)); S('meta', E(t,0.05,0.45));
  const cE = E(t,0.2,0.8);
  document.getElementById('card').style.transform = 'translateY('+((1-cE)*40)+'px)';
  document.getElementById('card').style.opacity = cE;
  S('pills', E(t,0.4,0.8));
  const hE = E(t,0.5,1.1);
  document.getElementById('hl').style.transform = 'translateY('+((1-hE)*24)+'px)';
  document.getElementById('hl').style.opacity = hE;
  S('deck', E(t,3.5,4.0));
  S('facts', E(t,3.9,4.4));
  const sw = t>=5.2 && t<=7.4 ? (t-5.2)/2.2 : -1;
  const sweep = document.getElementById('sweep');
  if (sw>=0) {{ sweep.style.opacity = 1; sweep.style.transform = 'translateX('+(-300 + sw*1500)+'px) rotate(16deg)'; }}
  else {{ sweep.style.opacity = 0; }}
  S('brand-foot', 0);
}}
document.fonts.ready.then(()=>render(0));
</script>
</body></html>"""
    open(out_html, "w", encoding="utf-8").write(page)


def render_frames(html_path, frames_dir, stills=None):
    from playwright.sync_api import sync_playwright
    os.makedirs(frames_dir, exist_ok=True)
    n = int(DUR * FPS)
    with sync_playwright() as p:
        b = p.chromium.launch(executable_path="/usr/bin/google-chrome", args=["--no-sandbox"])
        pg = b.new_page(viewport={"width": W, "height": H}, device_scale_factor=1)
        pg.goto("file://" + html_path)
        pg.evaluate("document.fonts.ready")
        if stills:
            for ts in stills:
                pg.evaluate(f"render({ts})")
                pg.screenshot(path=os.path.join(frames_dir, f"still_{ts}.png"))
        if stills:
            b.close()
            return
        for f in range(n):
            pg.evaluate(f"render({f / FPS})")
            pg.screenshot(path=os.path.join(frames_dir, f"f_{f:04d}.png"))
        b.close()


def encode(frames_dir, out_mp4):
    tmp = out_mp4 + ".tmp.mp4"
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(FPS), "-i",
           os.path.join(frames_dir, "f_%04d.png"), "-c:v", "libx264", "-crf", "18",
           "-preset", "veryfast", "-pix_fmt", "yuv420p", "-movflags", "+faststart", tmp]
    r = subprocess.run(cmd)
    if r.returncode != 0:
        raise SystemExit("ffmpeg gagal")
    os.replace(tmp, out_mp4)


def main():
    spec = json.load(open(sys.argv[1], encoding="utf-8"))
    out = sys.argv[2]
    stills = None
    if "--still" in sys.argv:
        stills = [float(x) for x in sys.argv[sys.argv.index("--still") + 1].split(",")]
    scratch = os.environ.get("BWD_SCRATCH", "/tmp/bwd-motion")
    work = os.path.join(scratch, os.path.splitext(os.path.basename(out))[0])
    shutil.rmtree(work, ignore_errors=True)
    os.makedirs(work)
    html_path = os.path.join(work, "scene.html")
    build_html(spec, html_path)
    frames = os.path.join(work, "frames")
    render_frames(html_path, frames, stills)
    if not stills:
        encode(frames, out)
    print(json.dumps({"out": out, "frames": frames}))


if __name__ == "__main__":
    main()
