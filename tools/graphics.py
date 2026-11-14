"""Grafis editorial BWD (SVG, palet brand) untuk memperjelas headline.

Dipakai compose.py lewat spec "graphic": {"type": "<nama>", "label": "TEKS SINGKAT"}.
Semua grafis = ilustrasi simbolik (benda/ikon), BUKAN orang. Tidak pernah menggambar wajah.
"""
NAVY, RED, YEL, WHITE = "#071B3A", "#E51E2A", "#FFD43B", "#F7F8FA"

_DEFS = f'''<defs>
<radialGradient id="glow" cx="50%" cy="50%" r="50%"><stop offset="0" stop-color="{RED}" stop-opacity=".55"/><stop offset="1" stop-color="{RED}" stop-opacity="0"/></radialGradient>
<linearGradient id="beam" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{YEL}" stop-opacity=".35"/><stop offset="1" stop-color="{YEL}" stop-opacity="0"/></linearGradient>
<linearGradient id="metal" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#2A4A7F"/><stop offset="1" stop-color="#0E2A55"/></linearGradient>
</defs>'''

def _ring():
    return (f'<circle cx="220" cy="220" r="200" fill="url(#glow)"/>'
            f'<circle cx="220" cy="220" r="190" fill="none" stroke="{WHITE}" stroke-opacity=".12" stroke-width="2" stroke-dasharray="4 10"/>'
            f'<circle cx="220" cy="220" r="150" fill="none" stroke="{WHITE}" stroke-opacity=".08" stroke-width="1.5"/>')

def kursi_kosong():
    # kursi pejabat kosong di bawah sorot lampu
    return f'''{_ring()}
<polygon points="170,0 270,0 360,420 80,420" fill="url(#beam)"/>
<ellipse cx="220" cy="392" rx="140" ry="20" fill="#000" opacity=".45"/>
<g stroke="{YEL}" stroke-width="7" stroke-linejoin="round" stroke-linecap="round" fill="url(#metal)">
 <path d="M140 110 Q220 70 300 110 L300 250 L140 250 Z"/>
 <path d="M118 250 L322 250 L330 290 L110 290 Z"/>
 <path d="M110 200 L138 200 L138 290 M330 200 L302 200 L302 290" fill="none"/>
 <path d="M128 290 L120 385 M312 290 L320 385 M175 290 L170 360 M265 290 L270 360" fill="none"/>
</g>
<rect x="175" y="140" width="90" height="34" rx="6" fill="{RED}"/>
<text x="220" y="164" text-anchor="middle" font-family="Inter" font-weight="900" font-size="20" fill="{WHITE}">WAPRES</text>
<path d="M190 205 h60" stroke="{WHITE}" stroke-opacity=".35" stroke-width="5" stroke-dasharray="8 8"/>'''

def penyadapan():
    # headset + gelombang suara + sinyal dari ponsel, titik REC
    bars = "".join(f'<rect x="{60+i*16}" y="{300-h/2}" width="9" height="{h}" rx="4" fill="{YEL if 7<=i<=13 else WHITE}" opacity="{1 if 7<=i<=13 else .55}"/>'
                   for i, h in enumerate([18,30,22,46,34,70,52,96,120,84,140,100,72,110,58,40,62,28,36,20]))
    return f'''{_ring()}
<g fill="none" stroke="{WHITE}" stroke-width="12" stroke-linecap="round"><path d="M120 200 Q120 70 220 70 Q320 70 320 200"/></g>
<rect x="92" y="180" width="56" height="92" rx="22" fill="url(#metal)" stroke="{YEL}" stroke-width="6"/>
<rect x="292" y="180" width="56" height="92" rx="22" fill="url(#metal)" stroke="{YEL}" stroke-width="6"/>
{bars}
<g transform="translate(300 330)"><rect x="0" y="0" width="70" height="104" rx="12" fill="url(#metal)" stroke="{WHITE}" stroke-width="5"/>
<path d="M85 25 q14 25 0 50 M100 12 q26 38 0 76" fill="none" stroke="{RED}" stroke-width="6" stroke-linecap="round"/></g>
<circle cx="88" cy="96" r="12" fill="{RED}"/><text x="108" y="104" font-family="Inter" font-weight="900" font-size="24" fill="{RED}">REC</text>'''

def gedung():
    # gedung parlemen/negara: kubah + kolom + tangga
    cols = "".join(f'<rect x="{112+i*44}" y="240" width="20" height="110" rx="3" fill="{WHITE}" opacity=".9"/>' for i in range(5))
    return f'''{_ring()}
<path d="M110 205 Q220 70 330 205 Z" fill="url(#metal)" stroke="{YEL}" stroke-width="7" stroke-linejoin="round"/>
<path d="M150 205 Q220 120 290 205" fill="none" stroke="{YEL}" stroke-opacity=".5" stroke-width="4"/>
<rect x="85" y="205" width="270" height="32" rx="4" fill="{YEL}"/>
{cols}
<rect x="80" y="350" width="280" height="18" fill="{WHITE}" opacity=".8"/><rect x="65" y="368" width="310" height="18" fill="{WHITE}" opacity=".6"/>
<path d="M220 70 v-38 l40 12 l-40 12" fill="{RED}" stroke="{RED}" stroke-width="4" stroke-linejoin="round"/>'''

def uang():
    notes = "".join(f'<g transform="translate({90+i*8} {170+i*-26}) rotate({-8+i*5} 130 60)"><rect width="250" height="120" rx="10" fill="#1F7A4D" stroke="{WHITE}" stroke-opacity=".7" stroke-width="4"/>'
                    f'<circle cx="125" cy="60" r="30" fill="none" stroke="{WHITE}" stroke-opacity=".6" stroke-width="4"/><text x="125" y="70" text-anchor="middle" font-family="Inter" font-weight="900" font-size="28" fill="{WHITE}" opacity=".8">Rp</text></g>' for i in range(3))
    coins = "".join(f'<ellipse cx="{300+i*0}" cy="{360-i*16}" rx="58" ry="18" fill="{YEL}" stroke="#B8860B" stroke-width="4"/>' for i in range(5))
    return f'''{_ring()}{notes}{coins}<text x="300" y="300" text-anchor="middle" font-family="Inter" font-weight="900" font-size="26" fill="{NAVY}">Rp</text>'''

def palu():
    return f'''{_ring()}
<ellipse cx="220" cy="370" rx="150" ry="26" fill="#000" opacity=".4"/>
<rect x="120" y="320" width="200" height="44" rx="10" fill="url(#metal)" stroke="{YEL}" stroke-width="6"/>
<g transform="rotate(-35 220 200)">
 <rect x="130" y="130" width="180" height="76" rx="18" fill="url(#metal)" stroke="{YEL}" stroke-width="7"/>
 <rect x="150" y="130" width="16" height="76" fill="{YEL}" opacity=".7"/><rect x="274" y="130" width="16" height="76" fill="{YEL}" opacity=".7"/>
 <rect x="208" y="200" width="24" height="170" rx="10" fill="{WHITE}"/>
</g>
<path d="M330 120 l22 -22 M345 150 l32 -6 M312 95 l-6 -30" stroke="{RED}" stroke-width="7" stroke-linecap="round"/>'''

def dokumen():
    lines = "".join(f'<rect x="150" y="{150+i*34}" width="{150 if i%3 else 110}" height="12" rx="6" fill="{WHITE}" opacity=".55"/>' for i in range(6))
    return f'''{_ring()}
<path d="M120 80 h150 l60 60 v250 h-210 z" fill="url(#metal)" stroke="{YEL}" stroke-width="7" stroke-linejoin="round"/>
<path d="M270 80 v60 h60" fill="none" stroke="{YEL}" stroke-width="7" stroke-linejoin="round"/>
{lines}
<g transform="rotate(-14 280 320)"><circle cx="280" cy="320" r="62" fill="none" stroke="{RED}" stroke-width="9"/>
<text x="280" y="330" text-anchor="middle" font-family="Inter" font-weight="900" font-size="26" fill="{RED}">RESMI</text></g>'''

def perisai():
    # lembaga keamanan/penegak hukum: perisai generik (bukan lambang resmi)
    return f'''{_ring()}
<path d="M220 70 L340 115 V215 Q340 320 220 375 Q100 320 100 215 V115 Z" fill="url(#metal)" stroke="{YEL}" stroke-width="8" stroke-linejoin="round"/>
<path d="M220 150 l22 46 50 6 -37 34 10 50 -45 -25 -45 25 10 -50 -37 -34 50 -6z" fill="{YEL}"/>
<circle cx="340" cy="110" r="26" fill="{RED}"/><path d="M340 98 v14 M340 120 v2" stroke="{WHITE}" stroke-width="6" stroke-linecap="round"/>'''

def jaringan():
    pts = [(220,110),(110,190),(330,190),(150,320),(290,320),(220,220)]
    edges = [(0,5),(1,5),(2,5),(3,5),(4,5),(0,1),(0,2),(1,3),(2,4),(3,4)]
    e = "".join(f'<line x1="{pts[a][0]}" y1="{pts[a][1]}" x2="{pts[b][0]}" y2="{pts[b][1]}" stroke="{WHITE}" stroke-opacity=".5" stroke-width="4"/>' for a, b in edges)
    n = "".join(f'<circle cx="{x}" cy="{y}" r="{34 if i==5 else 24}" fill="{RED if i==5 else "#123A73"}" stroke="{YEL}" stroke-width="6"/>' for i, (x, y) in enumerate(pts))
    return f'{_ring()}{e}{n}<text x="220" y="230" text-anchor="middle" font-family="Inter" font-weight="900" font-size="28" fill="{WHITE}">Rp</text>'

def karhutla():
    # kebakaran hutan & lahan: siluet pepohonan, api, asap (simbolik, tanpa orang)
    def tree(x, y, h, c):
        return (f'<path d="M{x} {y-h} L{x+h*.32} {y-h*.45} L{x+h*.16} {y-h*.45} L{x+h*.4} {y} L{x-h*.4} {y} '
                f'L{x-h*.16} {y-h*.45} L{x-h*.32} {y-h*.45} Z" fill="{c}"/><rect x="{x-6}" y="{y}" width="12" height="22" fill="{c}"/>')
    back = "".join(tree(x, 330, h, "#123A73") for x, h in [(95,150),(175,190),(265,170),(345,140)])
    smoke = "".join(f'<circle cx="{x}" cy="{y}" r="{r}" fill="#9AA6B8" opacity="{o}"/>' for x, y, r, o in
                    [(190,150,46,.35),(240,115,56,.3),(300,80,48,.22),(150,105,34,.22),(345,45,40,.15)])
    flame = lambda x, y, s, c: (f'<path transform="translate({x} {y}) scale({s})" d="M0 0 C-48 -10 -58 -70 -22 -110 C-26 -78 -6 -66 0 -82 '
                                f'C6 -120 34 -140 40 -170 C70 -120 76 -50 46 -14 C36 -2 18 2 0 0 Z" fill="{c}"/>')
    flames = (flame(150,360,1.15,RED) + flame(255,365,1.35,RED) + flame(330,362,1.0,RED)
              + flame(158,360,.7,"#FF8A1F") + flame(262,364,.85,"#FF8A1F") + flame(336,362,.6,"#FF8A1F")
              + flame(165,358,.38,YEL) + flame(268,362,.48,YEL) + flame(340,360,.32,YEL))
    front = tree(70, 360, 120, "#0B2246") + tree(392, 360, 110, "#0B2246")
    return f'''{_ring()}{smoke}{back}{flames}{front}
<rect x="40" y="378" width="360" height="16" rx="8" fill="#3B2A1A"/>
<ellipse cx="220" cy="398" rx="170" ry="14" fill="#000" opacity=".35"/>'''

def dana_karhutla():
    # anggaran karhutla: hutan terbakar (latar) + tumpukan uang Rp (depan); simbolik, tanpa orang
    def tree(x, y, h, c):
        return (f'<path d="M{x} {y-h} L{x+h*.32} {y-h*.45} L{x+h*.16} {y-h*.45} L{x+h*.4} {y} L{x-h*.4} {y} '
                f'L{x-h*.16} {y-h*.45} L{x-h*.32} {y-h*.45} Z" fill="{c}"/><rect x="{x-5}" y="{y}" width="10" height="18" fill="{c}"/>')
    smoke = "".join(f'<circle cx="{x}" cy="{y}" r="{r}" fill="#9AA6B8" opacity="{o}"/>' for x, y, r, o in
                    [(150,120,40,.32),(205,88,50,.28),(265,60,42,.2),(115,80,30,.2),(310,32,34,.14)])
    back = "".join(tree(x, 280, h, "#1A4A8A") for x, h in [(40,120),(95,150),(150,130),(210,165),(270,140),(330,155),(395,125)])
    mid = "".join(tree(x, 300, h, "#123A73") for x, h in [(65,110),(125,135),(185,120),(245,130),(305,115),(370,120)])
    flame = lambda x, y, s, c: (f'<path transform="translate({x} {y}) scale({s})" d="M0 0 C-48 -10 -58 -70 -22 -110 C-26 -78 -6 -66 0 -82 '
                                f'C6 -120 34 -140 40 -170 C70 -120 76 -50 46 -14 C36 -2 18 2 0 0 Z" fill="{c}"/>')
    flames = "".join(flame(x, 302, sc, RED) + flame(x+6, 302, sc*.62, "#FF8A1F") + flame(x+10, 300, sc*.33, YEL)
                     for x, sc in [(80,.95),(165,1.25),(255,1.1),(335,.9)])
    front = tree(30, 318, 105, "#0B2246") + tree(410, 318, 95, "#0B2246")
    ground = '<rect x="10" y="316" width="420" height="14" rx="7" fill="#3B2A1A"/>'
    notes = "".join(f'<g transform="translate({214+i*6} {282-i*22}) rotate({-6+i*4} 90 40)"><rect width="180" height="84" rx="8" fill="#1F7A4D" stroke="{WHITE}" stroke-opacity=".8" stroke-width="4"/>'
                    f'<circle cx="90" cy="42" r="22" fill="none" stroke="{WHITE}" stroke-opacity=".65" stroke-width="3.5"/><text x="90" y="51" text-anchor="middle" font-family="Inter" font-weight="900" font-size="22" fill="{WHITE}" opacity=".9">Rp</text></g>' for i in range(3))
    coins = "".join(f'<ellipse cx="110" cy="{372-i*15}" rx="52" ry="16" fill="{YEL}" stroke="#B8860B" stroke-width="4"/>' for i in range(5))
    shadow = '<ellipse cx="250" cy="386" rx="190" ry="16" fill="#000" opacity=".4"/>'
    rp = f'<text x="110" y="318" text-anchor="middle" font-family="Inter" font-weight="900" font-size="22" fill="{NAVY}">Rp</text>'
    return _ring() + smoke + back + mid + flames + front + ground + shadow + notes + coins + rp

GRAPHICS = {"kursi-kosong": kursi_kosong, "penyadapan": penyadapan, "gedung": gedung, "uang": uang,
            "palu": palu, "dokumen": dokumen, "perisai": perisai, "jaringan": jaringan, "karhutla": karhutla,
            "dana-karhutla": dana_karhutla}

def svg(name, size=440):
    fn = GRAPHICS.get(name)
    if not fn: return ""
    return f'<svg width="{size}" height="{size}" viewBox="0 0 440 440" xmlns="http://www.w3.org/2000/svg">{_DEFS}{fn()}</svg>'
