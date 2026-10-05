"""Builds assets/header-rice.svg: a tiling-WM desktop over The Starry Night listing my featured projects.

Run from the repo root after changing the lists below: python assets/build-header.py
"""
import base64
from pathlib import Path

root = Path(__file__).resolve().parent.parent
wallpaper = 'data:image/avif;base64,' + base64.b64encode((root / 'De_sterrennacht.avif').read_bytes()).decode()
out = root / 'assets' / 'header-rice.svg'

INK, PANEL, LINE, DIM, TEXT = '#0b1426', '#1c2b4d', '#2a3a5c', '#8193b5', '#dfe6f3'
GOLD, BLUE, GREEN, CREAM, RUST = '#f2c14e', '#5b8fd6', '#7fb89a', '#e9dca4', '#c8553d'


def esc(s):
    return s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')


# Workspaces in the bar: one per kind of project. "web" is active, it's where most of the work is.
tags = ['1 db', '2 algo', '3 oop', '4 web', '5 ai']
bar, x = [], 12.0
for i, t in enumerate(tags):
    w = 14 + 7.2 * len(t)
    active = t == '4 web'
    bar.append(
        f'<rect x="{x:.1f}" y="6" width="{w:.1f}" height="18" rx="9" fill="{GOLD if active else PANEL}"/>'
        f'<text x="{x + w / 2:.1f}" y="19" font-size="11" text-anchor="middle" fill="{INK if active else TEXT}">{t}</text>'
    )
    x += w + 6

fetch = [
    ('OS', 'Computer Science · Ceulp/ULBRA'),
    ('Host', 'EGEFAZ · IT intern, full stack'),
    ('Kernel', 'Python · TypeScript · JavaScript · SQL'),
    ('Packages', '8 featured projects'),
    ('Shell', 'Linux · Docker Compose · Vite'),
    ('DE', 'Django · DRF · React'),
    ('WM', 'PostgreSQL · Redis'),
    ('Deploy', 'Vercel · GitHub Pages'),
    ('AI', 'Claude Code · Ollama · Whisper'),
    ('Theme', 'Starry Night (Van Gogh, 1889)'),
    ('Locale', 'pt-BR · en (C1) · es (A2)'),
]
left = []
for i, (k, v) in enumerate(fetch):
    y = 144 + 22 * i
    left.append(
        f'<text class="in" style="animation-delay:{0.33 + 0.09 * i:.2f}s" x="30" y="{y}" font-size="13">'
        f'<tspan fill="{BLUE}" font-weight="700">{k}</tspan><tspan x="114" fill="{TEXT}">{esc(v)}</tspan></text>'
    )
palette_delay = 0.33 + 0.09 * len(fetch) + 0.1
palette = ''.join(
    f'<rect x="{30 + 20 * i}" y="380" width="16" height="16" rx="3" fill="{c}"/>'
    for i, c in enumerate([INK, '#2b4c8c', BLUE, '#3d6b4f', GOLD, CREAM, RUST, TEXT])
)

projects = [
    ('web', GREEN, 'portfolio/', 'live ↗'),
    ('web', GREEN, 'contrato-facil/', 'Django+React'),
    ('web', GREEN, 'cafe-verde/', 'WebSockets'),
    ('web', GREEN, 'dublacon/', 'DRF+React'),
    ('ai', RUST, 'akira-assistant/', 'local LLM'),
    ('web', GREEN, 'ConverteAqui/', 'Django+React'),
    ('db', BLUE, 'boardgame-library-db/', 'PostgreSQL'),
    ('web', GREEN, 'PlanejaMes/', 'live ↗'),
]
rows = []
for i, (tag, color, name, note) in enumerate(projects):
    y = 116 + 18 * i
    rows.append(
        f'<text class="in" style="animation-delay:{0.50 + 0.07 * i:.2f}s" x="466" y="{y}" font-size="12">'
        f'<tspan fill="{DIM}">drwxr-xr-x</tspan><tspan x="556" fill="{color}">{tag}</tspan>'
        f'<tspan x="600" fill="{TEXT}">{name}</tspan><tspan x="872" text-anchor="end" fill="{DIM}">{note}</tspan></text>'
    )
more = '+ more on the way'
more_y = 116 + 18 * len(projects) + 6
more_delay = 0.50 + 0.07 * len(projects)

# Share of bytes per language across the eight repos above (GitHub language stats, Oct 2026).
langs = [
    ('Python', 48.3, BLUE),
    ('JavaScript', 25.4, GOLD),
    ('TypeScript', 15.4, CREAM),
    ('CSS', 9.6, GREEN),
    ('Other', 1.4, DIM),
]
bar_y, bx, bw = 324, 466.0, 406.0
segs, legend = [], []
for i, (n, p, c) in enumerate(langs):
    w = bw * p / 100
    segs.append(
        f'<rect class="in" style="animation-delay:{1.0 + 0.1 * i:.2f}s" x="{bx:.1f}" y="{bar_y}" width="{w:.1f}" height="14" fill="{c}"/>'
    )
    bx += w
    col, row = i % 3, i // 3
    lx, ly = (466, 604, 742)[col], 366 + 26 * row
    legend.append(
        f'<g class="in" style="animation-delay:{1.3 + 0.1 * i:.2f}s"><circle cx="{lx + 6}" cy="{ly - 4}" r="5" fill="{c}"/>'
        f'<text x="{lx + 18}" y="{ly}" font-size="12" fill="{TEXT}">{n}</text>'
        f'<text x="{lx + 18 + 7.3 * len(n) + 8:.0f}" y="{ly}" font-size="12" fill="{DIM}">{p}%</text></g>'
    )

parts = [
    '<svg xmlns="http://www.w3.org/2000/svg" width="900" height="420" viewBox="0 0 900 420" role="img" '
    'aria-label="Desktop with The Starry Night as wallpaper: fastfetch, my 8 featured public projects and their languages">',
    '<style>',
    "  text { font-family: ui-monospace, SFMono-Regular, 'JetBrains Mono', Menlo, Consolas, monospace; }",
    '  .in { opacity: 0; animation: in .35s ease-out forwards; }',
    '  @keyframes in { from { opacity: 0; transform: translateX(-4px); } to { opacity: 1; transform: none; } }',
    '  .cur { animation: pisca 1s steps(1) infinite; }',
    '  @keyframes pisca { 50% { opacity: 0; } }',
    '  @media (prefers-reduced-motion: reduce) { .in { animation: none; opacity: 1; } .cur { animation: none; } }',
    '</style>',
    f'<defs><clipPath id="tela"><rect width="900" height="420" rx="14"/></clipPath>'
    f'<clipPath id="barra"><rect x="466" y="{bar_y}" width="406" height="14" rx="7"/></clipPath></defs>',
    '<g clip-path="url(#tela)">',
    f'<image href="{wallpaper}" x="0" y="0" width="900" height="420" preserveAspectRatio="xMidYMid slice"/>',
    f'<rect width="900" height="420" fill="{INK}" fill-opacity="0.18"/>',
    f'<rect width="900" height="30" fill="{INK}" fill-opacity="0.9"/>' + ''.join(bar)
    + f'<text x="450.0" y="20" font-size="12" text-anchor="middle" fill="{CREAM}">Yourdevdaniel</text>'
    + f'<text x="886" y="20" font-size="12" text-anchor="end" fill="{TEXT}">Palmas, TO  ·  open to work  ·  ●</text>',
    # fastfetch
    f'<rect x="12" y="42" width="426" height="366" rx="10" fill="{INK}" fill-opacity="0.92" stroke="{GOLD}" stroke-width="2"/>'
    f'<text x="26" y="64" font-size="12" fill="{DIM}">~ — fastfetch</text><line x1="12" y1="74" x2="438" y2="74" stroke="{LINE}"/>'
    f'<text class="in" style="animation-delay:0.15s" x="30" y="100" font-size="14" font-weight="700">'
    f'<tspan fill="{GOLD}">daniel</tspan><tspan fill="{DIM}">@</tspan><tspan fill="{BLUE}">egefaz</tspan></text>',
    f'<text class="in" style="animation-delay:0.24s" x="30" y="122" font-size="13" fill="{DIM}">──────────────────────</text>',
    *left,
    f'<g class="in" style="animation-delay:{palette_delay:.2f}s">{palette}</g>',
    # ls -l
    f'<rect x="450" y="42" width="438" height="230" rx="10" fill="{INK}" fill-opacity="0.92" stroke="{LINE}" stroke-width="1.2"/>'
    f'<text x="464" y="64" font-size="12" fill="{DIM}">~/projects — ls -l</text><line x1="450" y1="74" x2="888" y2="74" stroke="{LINE}"/>'
    f'<text x="466" y="94" font-size="12" fill="{BLUE}">$ ls -l ~/projects</text>',
    *rows,
    f'<text class="in" style="animation-delay:{more_delay:.2f}s" x="466" y="{more_y}" font-size="12" fill="{GOLD}">{more}</text>'
    f'<rect class="cur" x="{466 + 7.2 * len(more) + 4:.1f}" y="{more_y - 11}" width="7" height="14" fill="{GOLD}"/>',
    # onefetch
    f'<rect x="450" y="284" width="438" height="124" rx="10" fill="{INK}" fill-opacity="0.92" stroke="{LINE}" stroke-width="1.2"/>'
    f'<text x="464" y="304" font-size="12" fill="{DIM}">~ — onefetch --languages</text><line x1="450" y1="313" x2="888" y2="313" stroke="{LINE}"/>'
    f'<g clip-path="url(#barra)">{"".join(segs)}</g>' + ''.join(legend),
    '</g>',
    '</svg>',
]
svg = '\n'.join(parts) + '\n'
out.write_text(svg, encoding='utf-8', newline='\n')
print(f'wrote {out.relative_to(root)} ({len(svg):,} bytes)')
