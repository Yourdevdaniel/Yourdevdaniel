"""Builds the ink-wash (sumi-e) images of my profile README:

  assets/title.svg         a sword cut through "Akira"
  assets/header-rice.svg   a tiling-WM desktop with one fastfetch window over an ink landscape
  assets/ronin.svg         a ronin on a cliff in the wind, closing the page
  assets/cards/{en,pt}/    one card per project, with the screenshot from my portfolio

Needs fonttools and pillow (pip install fonttools pillow). Run from anywhere: python assets/build-header.py
The brush font (Ma Shan Zheng, OFL) is downloaded once and its glyphs go into the SVGs as paths,
so the calligraphy looks the same on machines without Chinese fonts. Screenshots in assets/shots come from my portfolio repo.
"""
import base64
import io
import math
import random
import tempfile
import urllib.request
from pathlib import Path

from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont
from PIL import Image

root = Path(__file__).resolve().parent.parent
cache = Path(tempfile.gettempdir())


def fetch(url, name):
    path = cache / name
    if not path.exists():
        urllib.request.urlretrieve(url, path)
    return path


font = TTFont(fetch('https://github.com/google/fonts/raw/main/ofl/mashanzheng/MaShanZheng-Regular.ttf', 'MaShanZheng-Regular.ttf'))
cmap, glyphs = font.getBestCmap(), font.getGlyphSet()
EM = font['head'].unitsPerEm

PAPER, MIST, GREY, SUMI, SEAL = '#f1e9d8', '#c9c0b0', '#6f665d', '#1d1a17', '#b8312f'
INK, PANEL, LINE, DIM, TEXT = '#1d1a17', '#332e29', '#4a433c', '#a39785', '#efe6d2'
OCHRE, CELADON, JADE, CREAM, CINNABAR = '#c9a25a', '#8fb3ab', '#93b07f', '#e8dcbf', '#d9573f'
INK_TEXT = '#3b342e'  # small text on paper: darker than GREY so it reads like ink, not pencil
MONO = "font-family=\"ui-monospace, SFMono-Regular, 'JetBrains Mono', Menlo, Consolas, monospace\""
SERIF = "font-family=\"Georgia, 'Times New Roman', serif\""


def esc(s):
    return s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')


def brush(s, x, y, size, vertical=False):
    """Brush-script text as one SVG path. (x, y) is the first baseline; vertical stacks the glyphs downwards."""
    k = size / EM
    pen = SVGPathPen(glyphs)
    for ch in s:
        name = cmap[ord(ch)]
        glyphs[name].draw(TransformPen(pen, (k, 0, 0, -k, x, y)))
        if vertical:
            y += size
        else:
            x += font['hmtx'][name][0] * k
    return pen.getCommands()


def ridge(rng, peaks, base, w, h, step=5):
    """A mountain silhouette: sharp bumps over a baseline, closed below the bottom of the canvas."""
    pts = []
    for x in range(0, w + step, step):
        top = sum(p * math.exp(-((x - c) / s) ** 2) for c, p, s in peaks)
        pts.append((x, base - top + rng.uniform(-1.5, 1.5)))
    return 'M' + ' L'.join(f'{x},{y:.1f}' for x, y in pts) + f' L{w},{h + 30} L0,{h + 30} Z'


def seal(ch, x, y, size, angle=-3):
    return (f'<g transform="rotate({angle} {x + size / 2} {y + size / 2})"><rect x="{x}" y="{y}" width="{size}" height="{size}" rx="{size / 9:.1f}" '
            f'fill="{SEAL}" filter="url(#brush-soft)"/><path d="{brush(ch, x + size * 0.05, y + size * 0.86, size * 0.9)}" fill="{PAPER}"/></g>')


def image_uri(path, width):
    im = Image.open(path).convert('RGB')
    im = im.resize((width, round(im.height * width / im.width)), Image.LANCZOS)
    buf = io.BytesIO()
    im.save(buf, 'WEBP', quality=80)
    return 'data:image/webp;base64,' + base64.b64encode(buf.getvalue()).decode()


DEFS = (
    '<filter id="grain" x="0" y="0" width="100%" height="100%"><feTurbulence type="fractalNoise" baseFrequency=".9" numOctaves="2" seed="3"/>'
    '<feColorMatrix values="0 0 0 0 .35  0 0 0 0 .28  0 0 0 0 .2  0 0 0 .09 0"/></filter>'
    '<filter id="brush" x="-5%" y="-10%" width="110%" height="120%"><feTurbulence type="fractalNoise" baseFrequency=".035 .09" numOctaves="3" seed="11"/>'
    '<feDisplacementMap in="SourceGraphic" scale="9"/></filter>'
    # ink: a slight bleed on small text, like a brush on rice paper
    '<filter id="ink"><feTurbulence type="fractalNoise" baseFrequency=".6" numOctaves="2" seed="8"/><feDisplacementMap in="SourceGraphic" scale="1.4"/></filter>'
    '<filter id="brush-soft"><feTurbulence baseFrequency=".2" numOctaves="2" seed="5"/><feDisplacementMap in="SourceGraphic" scale="3"/></filter>'
    '<filter id="blur" x="-50%" y="-400%" width="200%" height="900%"><feGaussianBlur stdDeviation="14"/></filter>'
    f'<radialGradient id="sun"><stop offset=".75" stop-color="{SEAL}" stop-opacity=".85"/><stop offset="1" stop-color="{SEAL}" stop-opacity="0"/></radialGradient>'
    f'<linearGradient id="far" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{MIST}"/><stop offset=".55" stop-color="{MIST}" stop-opacity="0"/></linearGradient>'
    f'<linearGradient id="mid" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{GREY}"/><stop offset=".6" stop-color="{GREY}" stop-opacity="0"/></linearGradient>'
    f'<linearGradient id="near" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{SUMI}"/><stop offset=".6" stop-color="{SUMI}" stop-opacity=".7"/>'
    f'<stop offset="1" stop-color="{SUMI}" stop-opacity=".25"/></linearGradient>'
)
MOTION = '''  .mist { animation: drift 24s ease-in-out infinite alternate; }
  @keyframes drift { from { transform: translateX(-45px); } to { transform: translateX(45px); } }
  .birds { animation: fly 40s linear infinite; }
  @keyframes fly { from { transform: translate(-60px,110px); } to { transform: translate(1060px,30px); } }
  .leaf { transform-box: fill-box; transform-origin: center; animation: fall 11s linear infinite; }
  @keyframes fall { from { transform: translate(0,-20px) rotate(0); } to { transform: translate(-150px,340px) rotate(540deg); } }
  @media (prefers-reduced-motion: reduce) { .mist, .birds, .in, .cur { animation: none; } .in { opacity: 1; } .leaf { display: none; } .birds { transform: translate(560px,70px); } }'''
BIRDS = '<g class="birds">' + ''.join(
    f'<path d="M0,0 q6,-6 12,0 q6,-6 12,0" transform="translate({dx},{dy}) scale({s})" fill="none" stroke="{SUMI}" stroke-width="1.6" stroke-linecap="round"/>'
    for dx, dy, s in [(0, 0, 1), (30, 14, 0.8), (-22, 20, 0.7)]
) + '</g>'


def leaves(seed, w):
    rng = random.Random(seed)
    return ''.join(
        f'<g transform="translate({rng.uniform(80, w):.0f},0)"><path class="leaf" style="animation-delay:-{rng.uniform(0, 11):.1f}s;'
        f'animation-duration:{rng.uniform(9, 13):.1f}s" d="M0,0 q4,-6 9,0 q-5,6 -9,0 Z" fill="{c}"/></g>'
        for c in [SEAL, OCHRE, SEAL, CINNABAR, SEAL, OCHRE]
    )


def svg(w, h, label, style, body, pad=0):
    """pad adds a transparent margin around the card: GitHub strips CSS, so this is how cards side by side get a gap."""
    ow, oh = w + 2 * pad, h + 2 * pad
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{ow}" height="{oh}" viewBox="0 0 {ow} {oh}" role="img" aria-label="{esc(label)}">\n'
            f'<style>\n{style}\n</style>\n<defs>{DEFS}<clipPath id="card"><rect width="{w}" height="{h}" rx="12"/></clipPath></defs>\n'
            f'<g transform="translate({pad},{pad})" clip-path="url(#card)">\n{body}\n<rect width="{w}" height="{h}" filter="url(#grain)"/>\n</g>\n</svg>\n')


out = {}

# ---- Title: a red sword cut crosses "Akira", the halves slide back together, rest, fade, repeat.
TW, TH = 1000, 170
cut_l, cut_r = 98, 74
akira = brush('Akira', 56, 122, 112)
out['title.svg'] = svg(TW, TH, 'Akira, Daniel Bernardes, full-stack developer: a sword cut slices the name in brush script', '''  .cut { stroke-dasharray: 1100; animation: cut 9s cubic-bezier(.7,0,.2,1) infinite; }
  @keyframes cut { 0% { stroke-dashoffset: 1100; opacity: 1; } 6% { stroke-dashoffset: 0; opacity: 1; } 16%, 100% { opacity: 0; } }
  .top { animation: top 9s ease-out infinite; }
  .bot { animation: bot 9s ease-out infinite; }
  @keyframes top { 0%, 6% { transform: translate(-14px,-4px); opacity: .35; } 18%, 88% { transform: none; opacity: 1; } 100% { opacity: 0; } }
  @keyframes bot { 0%, 6% { transform: translate(14px,4px); opacity: .35; } 18%, 88% { transform: none; opacity: 1; } 100% { opacity: 0; } }
  .sub { opacity: 0; animation: sub 9s ease-out infinite; }
  @keyframes sub { 0%, 14% { opacity: 0; transform: translateY(6px); } 24%, 88% { opacity: 1; transform: none; } 100% { opacity: 0; } }
  @media (prefers-reduced-motion: reduce) { .cut { animation: none; opacity: 0; } .top, .bot, .sub { animation: none; opacity: 1; transform: none; } }''',
    f'''<clipPath id="above"><path d="M0,0 H{TW} V{cut_r} L0,{cut_l} Z"/></clipPath><clipPath id="below"><path d="M0,{cut_l} L{TW},{cut_r} V{TH} H0 Z"/></clipPath>
<rect width="{TW}" height="{TH}" fill="{PAPER}"/>
<g class="top"><path clip-path="url(#above)" d="{akira}" fill="{SUMI}"/></g>
<g class="bot"><path clip-path="url(#below)" d="{akira}" fill="{SUMI}"/></g>
<path class="cut" d="M20,{cut_l + 1} L{TW - 20},{cut_r - 1}" stroke="{SEAL}" stroke-width="3" stroke-linecap="round" filter="url(#brush-soft)"/>
<g class="sub">{seal("明", 336, 58, 46)}
<text x="410" y="74" {SERIF} font-size="28" fill="{SUMI}" filter="url(#ink)">Daniel Bernardes</text>
<text x="410" y="102" {SERIF} font-size="16" font-style="italic" fill="{INK_TEXT}" filter="url(#ink)">full-stack developer · Django · React · TypeScript</text>
<text x="411" y="128" {SERIF} font-size="11" letter-spacing="3" fill="{SEAL}" filter="url(#ink)">OPEN TO INTERNSHIPS AND JUNIOR ROLES</text></g>''')

# ---- Header: one fastfetch window, the rest is landscape.
W, H = 1000, 340
rng = random.Random(7)
mountains = ''.join(
    f'<path d="{ridge(rng, peaks, base, W, H)}" fill="url(#{g})" filter="url(#brush)"/>'
    for peaks, base, g in [
        ([(520, 60, 70), (640, 110, 50), (760, 90, 60), (880, 130, 45)], 230, 'far'),
        ([(480, 70, 40), (600, 160, 34), (640, 120, 28), (780, 120, 40), (950, 200, 30)], 290, 'mid'),
        ([(460, 50, 80), (700, 100, 55), (900, 120, 50)], 350, 'near'),
    ]
)
fetch_lines = [
    ('Study', 'Computer Science · Ceulp/ULBRA'),
    ('Work', 'EGEFAZ · IT intern, full stack'),
    ('Stack', 'Django · DRF · React · TypeScript'),
    ('Data', 'PostgreSQL · Redis'),
    ('AI', 'Claude Code · Ollama · Whisper'),
    ('Locale', 'pt-BR · en (C1) · es (A2)'),
]
# Share of bytes per language across my featured repos (GitHub language stats, Oct 2026).
langs = [('Python', 48.3, CELADON), ('JavaScript', 25.4, OCHRE), ('TypeScript', 15.4, CREAM), ('CSS', 9.6, JADE), ('Other', 1.4, DIM)]
rows = ''.join(
    f'<text class="in" style="animation-delay:{0.3 + 0.1 * i:.1f}s" x="44" y="{150 + 24 * i}" font-size="13">'
    f'<tspan fill="{CINNABAR}" font-weight="700">{k}</tspan><tspan x="112" fill="{TEXT}">{esc(v)}</tspan></text>'
    for i, (k, v) in enumerate(fetch_lines)
)
segs, bx = [], 44.0
for n, p, c in langs:
    segs.append(f'<rect x="{bx:.1f}" y="300" width="{392 * p / 100:.1f}" height="8" fill="{c}"/>')
    bx += 392 * p / 100
legend = '  '.join(f'{n} {round(p)}%' for n, p, _ in langs[:4])
tags = ''
x = 12.0
for t in ['1 db', '2 algo', '3 oop', '4 web', '5 ai']:
    w = 14 + 7.2 * len(t)
    tags += (f'<rect x="{x:.1f}" y="6" width="{w:.1f}" height="18" rx="9" fill="{SEAL if t == "4 web" else PANEL}"/>'
             f'<text x="{x + w / 2:.1f}" y="19" font-size="11" text-anchor="middle" fill="{TEXT}">{t}</text>')
    x += w + 6
out['header-rice.svg'] = svg(W, H, 'A tiling-WM desktop over an ink-wash landscape: fastfetch with my studies, work, stack and languages', f'''  text {{ font-family: ui-monospace, SFMono-Regular, 'JetBrains Mono', Menlo, Consolas, monospace; }}
  .in {{ opacity: 0; animation: in .35s ease-out forwards; }}
  @keyframes in {{ from {{ opacity: 0; transform: translateX(-4px); }} to {{ opacity: 1; transform: none; }} }}
  .cur {{ animation: blink 1s steps(1) infinite; }}
  @keyframes blink {{ 50% {{ opacity: 0; }} }}
{MOTION}''', f'''<rect width="{W}" height="{H}" fill="{PAPER}"/>
<circle cx="760" cy="96" r="34" fill="url(#sun)"/>
{mountains}
<g class="mist"><ellipse cx="700" cy="280" rx="360" ry="16" fill="{PAPER}" opacity=".9" filter="url(#blur)"/></g>
{BIRDS}
<path d="{brush("二天一流", 912, 110, 46, vertical=True)}" fill="{SUMI}" opacity=".9"/>
{seal("明", 913, 272, 44)}
<rect width="{W}" height="30" fill="{INK}" fill-opacity=".92"/>{tags}
<text x="500" y="20" font-size="12" text-anchor="middle" fill="{CREAM}">Yourdevdaniel</text>
<text x="986" y="20" font-size="12" text-anchor="end" fill="{TEXT}">Brazil  ·  open to work  ·  <tspan fill="{CINNABAR}">●</tspan></text>
<rect x="24" y="50" width="440" height="276" rx="10" fill="{INK}" fill-opacity=".9" stroke="{SEAL}" stroke-width="2"/>
<text x="38" y="72" font-size="12" fill="{DIM}">~ — fastfetch</text><line x1="24" y1="82" x2="464" y2="82" stroke="{LINE}"/>
<text class="in" style="animation-delay:.1s" x="44" y="108" font-size="15" font-weight="700"><tspan fill="{OCHRE}">akira</tspan><tspan fill="{DIM}">@</tspan><tspan fill="{CINNABAR}">egefaz</tspan></text>
<text class="in" style="animation-delay:.2s" x="44" y="126" font-size="13" fill="{DIM}">────────────────</text>
{rows}
<g class="in" style="animation-delay:1s">{"".join(segs)}<text x="44" y="320" font-size="10.5" fill="{DIM}">{legend}</text></g>
<rect class="cur" x="160" y="96" width="8" height="15" fill="{OCHRE}"/>''')

# ---- Closing scene: a ronin on a cliff in the wind, a pine, a red sun.
# 明镜止水, "clear mirror, still water": the calm mind of the swordsman, and 明 is Akira.
SW, SH = 1000, 300
feet_x, feet_y, k = 770, 238, 0.85
scarf = ['M8,-80 C30,-84 50,-74 72,-82 C60,-76 34,-74 8,-76 Z',
         'M8,-80 C30,-92 52,-88 76,-96 C58,-84 32,-78 8,-76 Z',
         'M8,-80 C28,-78 50,-68 70,-70 C58,-70 34,-72 8,-76 Z']
cloak = ['M13,-80 C28,-70 38,-52 46,-42 C34,-44 24,-46 16,-46 Z',
         'M13,-80 C32,-72 46,-58 58,-50 C40,-48 26,-48 16,-46 Z',
         'M13,-80 C26,-66 34,-48 40,-38 C30,-42 22,-46 16,-46 Z']


def sway(frames, dur):
    loop = ';'.join(frames + frames[:1])
    return f'<animate attributeName="d" dur="{dur}s" repeatCount="indefinite" values="{loop}" calcMode="spline" keySplines="{";".join([".45 0 .55 1"] * len(frames))}"/>'


stroke = f'fill="none" stroke="{SUMI}" stroke-linecap="round" stroke-linejoin="round"'
ronin = (
    f'<g transform="translate({feet_x},{feet_y}) scale({k})" fill="{SUMI}" filter="url(#brush-soft)">'
    f'<path d="{scarf[0]}" fill="{SEAL}">{sway(scarf, 2.4)}</path>'
    f'<path d="{cloak[0]}">{sway(cloak, 3.1)}</path>'
    f'<path d="M-6,-48 L52,-68" {stroke} stroke-width="3.5"/><path d="M-4,-44 L38,-55" {stroke} stroke-width="2.6"/>'
    '<path d="M-15,-46 L15,-46 C20,-30 26,-14 30,0 L10,0 L2,-24 L-6,0 L-28,0 C-24,-16 -20,-30 -15,-46 Z"/>'
    '<path d="M-11,-84 C-4,-88 4,-88 11,-84 L17,-46 L-17,-46 Z"/>'
    f'<path d="M-17,-52 L17,-52 L17,-46 L-17,-46 Z" fill="{SEAL}"/>'
    '<path d="M-11,-82 C-22,-70 -22,-58 -16,-52 L-6,-58 C-8,-66 -8,-74 -6,-80 Z"/>'
    f'<path d="M-9,-78 C-14,-68 -12,-58 -4,-52" {stroke} stroke-width="5.5"/>'
    f'<path d="M10,-78 C14,-70 15,-62 16,-56" {stroke} stroke-width="6"/>'
    '<circle cx="0" cy="-89" r="6.5"/>'
    '<path d="M-30,-93 Q-6,-112 0,-117 Q6,-112 30,-93 Q0,-99 -30,-93 Z"/></g>'
)
pine = (
    f'<g {stroke} filter="url(#brush-soft)">'
    '<path d="M912,252 C904,214 922,186 896,156 C878,134 884,114 862,98" stroke-width="9"/>'
    '<path d="M898,160 C916,150 930,150 948,140 M884,122 C868,124 852,128 836,126 M906,196 C924,192 936,184 952,182" stroke-width="4"/></g>'
    f'<g fill="{SUMI}" filter="url(#brush)" opacity=".9"><ellipse cx="860" cy="94" rx="40" ry="10"/><ellipse cx="946" cy="136" rx="30" ry="9"/>'
    '<ellipse cx="832" cy="122" rx="24" ry="8"/><ellipse cx="952" cy="178" rx="26" ry="8"/></g>'
)
far_scene = ridge(random.Random(5), [(120, 70, 60), (300, 120, 45), (420, 80, 70), (560, 100, 50)], 250, SW, SH)
cliff = f'M590,{SH + 20} L630,268 L655,250 L690,240 L720,{feet_y + 1} L860,{feet_y - 1} L900,250 L950,256 L1000,252 L1000,{SH + 20} Z'
out['ronin.svg'] = svg(SW, SH, 'Ink-wash scene: a ronin stands on a cliff in the wind beside a pine, red leaves falling; calligraphy reads 明镜止水, clear mirror, still water', MOTION, f'''<rect width="{SW}" height="{SH}" fill="{PAPER}"/>
<circle cx="640" cy="78" r="30" fill="url(#sun)"/>
<path d="{far_scene}" fill="url(#far)" filter="url(#brush)"/>
<g class="mist"><ellipse cx="380" cy="262" rx="360" ry="16" fill="{PAPER}" opacity=".9" filter="url(#blur)"/></g>
<path d="{cliff}" fill="url(#near)" filter="url(#brush)"/>
{pine}
{ronin}
{leaves(3, SW)}
<path d="{brush("明镜止水", 46, 74, 44, vertical=True)}" fill="{SUMI}" opacity=".88"/>
{seal("明", 50, 252, 34, angle=4)}''')

# ---- Project cards: the screenshot from my portfolio on top, an ink label below.
SHOTS = root / 'assets' / 'shots'  # copied from Yourdevdaniel/portfolio (public/og.png, public/work/*.webp)
KIND = {'web': '剑', 'ai': '智', 'db': '卷'}  # sword, wisdom, scroll
PROJECTS = [
    # name, kind, screenshot, stack, (en, pt)
    ('contrato-facil', 'web', 'contrato-facil.webp', 'Django · React · PostgreSQL',
     ('Guided contracts, signed in order, SHA-256 audit trail', 'Contrato guiado, assinatura em ordem, auditoria SHA-256')),
    ('cafe-verde', 'web', 'cafe-verde.webp', 'Django Channels · Redis · React',
     ('Order from the table; the kitchen updates live', 'Pedido pela mesa; a cozinha atualiza ao vivo')),
    ('dublacon', 'web', 'dublacon.webp', 'DRF · React · PostgreSQL',
     ('Where voice actors and artists team up on projects', 'Onde dubladores e artistas se juntam em projetos')),
    ('ConverteAqui', 'web', 'converteaqui.webp', 'Django · React · Docker',
     ('Raw lead sheets in, clean scored Excel and PDF out', 'Planilha de leads crua entra, Excel e PDF limpos saem')),
    ('PlanejaMes', 'web', 'planejames.webp', 'React · Three.js · GSAP',
     ('Monthly budget with the 50/30/20 rule and a 3D scene', 'Orçamento mensal 50/30/20 com cena 3D')),
    ('akira-assistant', 'ai', None, 'Python · Ollama · Whisper · Kokoro',
     ('Telegram assistant on my PC, voice in, voice out', 'Assistente no Telegram no meu PC, por voz')),
    ('boardgame-library-db', 'db', None, 'PostgreSQL · Python · pytest',
     ('A race condition, closed by a partial unique index', 'Condição de corrida fechada com índice único parcial')),
]
CW, CH, IH = 480, 290, 196


def picture(name, shot):
    """The top of a card: the real screenshot, or an ink panel for projects that have no screen."""
    if shot:
        return f'<image href="{image_uri(SHOTS / shot, CW)}" width="{CW}" height="{IH}" preserveAspectRatio="xMidYMin slice"/>'
    if name == 'akira-assistant':
        lines = [(TEXT, '$ akira test --phrases'), (JADE, '✓ "me lembra de pagar a luz amanhã"'), (JADE, '✓ "o que tem na agenda hoje?"'),
                 (DIM, '  ...'), (OCHRE, '41 / 41 passed · local model, no cloud')]
        body = ''.join(f'<text x="28" y="{50 + 26 * i}" {MONO} font-size="13" fill="{c}">{esc(t)}</text>' for i, (c, t) in enumerate(lines))
        return f'<rect width="{CW}" height="{IH}" fill="{INK}"/>{body}'
    return (f'<rect width="{CW}" height="{IH}" fill="{INK}"/><path d="{brush("800x", 30, 128, 96)}" fill="{CINNABAR}"/>'
            f'<text x="34" y="166" {MONO} font-size="13" fill="{TEXT}">slower without the FK index. now it has one.</text>')


def card(name, kind, shot, stack, blurb):
    return svg(CW, CH, f'{name}: {blurb}', '', f'''<rect width="{CW}" height="{CH}" fill="{PAPER}"/>
{picture(name, shot)}
<path d="M0,{IH} C120,{IH - 6} 360,{IH + 5} {CW},{IH - 2} V{IH + 4} C360,{IH + 9} 120,{IH} 0,{IH + 5} Z" fill="{SUMI}" filter="url(#brush-soft)"/>
{seal(KIND[kind], 18, 214, 40)}
<text x="74" y="232" {SERIF} font-size="21" font-weight="700" fill="{SUMI}" filter="url(#ink)">{name}</text>
<text x="74" y="254" {SERIF} font-size="13.5" font-style="italic" fill="{INK_TEXT}" filter="url(#ink)">{esc(blurb)}</text>
<text x="74" y="276" {MONO} font-size="11" fill="{SEAL}" filter="url(#ink)">{esc(stack)}</text>
<text x="462" y="232" {SERIF} font-size="20" text-anchor="end" fill="{SEAL}" filter="url(#ink)">›</text>''', pad=12)


def portfolio_card(lang):
    head, line1, line2, cta = {
        'en': ('my portfolio', 'A name that widens and folds as you scroll, cards that stack,',
               'real screen recordings. Two languages, light and dark.', 'ENTER THE DOJO  ›'),
        'pt': ('meu portfólio', 'Um nome que se alarga e se dobra com a rolagem, cards que',
               'se empilham, gravações reais de tela. Dois idiomas, claro e escuro.', 'ENTRE NO DOJO  ›'),
    }[lang]
    pw, ph, iw = 1000, 300, 571
    return svg(pw, ph, f'bernardes.dev, {head}', '', f'''<rect width="{pw}" height="{ph}" fill="{PAPER}"/>
<image href="{image_uri(SHOTS / "og.png", 800)}" width="{iw}" height="{ph}" preserveAspectRatio="xMidYMid slice"/>
<path d="M{iw},0 C{iw - 8},100 {iw + 6},200 {iw - 2},{ph} L{iw + 5},{ph} C{iw + 11},200 {iw - 2},100 {iw + 4},0 Z" fill="{SUMI}" filter="url(#brush-soft)"/>
<text x="612" y="62" {SERIF} font-size="12" letter-spacing="3" fill="{INK_TEXT}" filter="url(#ink)">{head.upper()}</text>
<path d="{brush("bernardes.dev", 608, 128, 58)}" fill="{SUMI}" filter="url(#ink)"/>
<text x="612" y="170" {SERIF} font-size="13" font-style="italic" fill="{INK_TEXT}" filter="url(#ink)">{esc(line1)}</text>
<text x="612" y="190" {SERIF} font-size="13" font-style="italic" fill="{INK_TEXT}" filter="url(#ink)">{esc(line2)}</text>
<text x="612" y="216" {MONO} font-size="11.5" fill="{SEAL}" filter="url(#ink)">React · TypeScript · GSAP</text>
<rect x="612" y="236" width="196" height="38" rx="4" fill="{SEAL}" filter="url(#brush-soft)"/>
<text x="710" y="260" {SERIF} font-size="13" letter-spacing="2" text-anchor="middle" fill="{PAPER}">{cta}</text>
{seal("明", 930, 236, 40)}''')


for i, lang in enumerate(['en', 'pt']):
    out[f'cards/{lang}/portfolio.svg'] = portfolio_card(lang)
    for name, kind, shot, stack, blurbs in PROJECTS:
        out[f'cards/{lang}/{name}.svg'] = card(name, kind, shot, stack, blurbs[i])

for file, text in out.items():
    path = root / 'assets' / file
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding='utf-8', newline='\n')
    print(f'wrote assets/{file} ({len(text):,} bytes)')
