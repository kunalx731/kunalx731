"""Render the animated SVG artwork for the profile README.

Writes light and dark variants of the hero, toolbox and contact pills into an
output directory. The live activity panel is served by the github-readme-stats
deployment (/api/profile) and shares this visual language.

    python scripts/profile_art.py dist
"""
import sys
from html import escape
from pathlib import Path

NAME = "Krishna Kunal"
W = 1200
PAD = 56

FONT = ("-apple-system, BlinkMacSystemFont, 'SF Pro Display', 'Segoe UI Variable Display', "
        "'Segoe UI', 'Helvetica Neue', Inter, Arial, sans-serif")
EASE = "cubic-bezier(.16,1,.3,1)"
SPECTRUM = ["#0a84ff", "#5e5ce6", "#bf5af2", "#ff375f", "#ff9f0a", "#0a84ff"]

THEMES = {
    "dark": dict(card="#000000", raised="#111214", border="rgba(255,255,255,0.10)", text="#f5f5f7",
                 sub="#86868b", chip="#1c1c1e", halo=0.42, edge=0.9),
    "light": dict(card="#fbfbfd", raised="#ffffff", border="rgba(0,0,0,0.08)", text="#1d1d1f",
                  sub="#6e6e73", chip="#f2f2f5", halo=0.20, edge=0.75),
}

BASE_CSS = f"""
text {{ font-family: {FONT}; }}
.in {{ opacity: 0; animation: in 1.2s {EASE} forwards; }}
@keyframes in {{ from {{ opacity: 0; transform: translateY(16px); filter: blur(8px); }}
                to {{ opacity: 1; transform: none; filter: blur(0); }} }}
@media (prefers-reduced-motion: reduce) {{
  .in {{ animation: none !important; opacity: 1 !important; }}
  .loop {{ animation: none !important; }}
}}
"""


def svg(w, h, body, css="", label=""):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
            f'role="img" aria-label="{escape(label)}" fill="none">'
            f"<style>{BASE_CSS}{css}</style>{body}</svg>")


def at(seconds):
    return f'style="animation-delay:{seconds:.2f}s"'


def spectrum_stops():
    return "".join(f'<stop offset="{i / (len(SPECTRUM) - 1):.2f}" stop-color="{c}"/>' for i, c in enumerate(SPECTRUM))


# --------------------------------------------------------------------------- hero

def hero(t):
    h = 380
    cx, cy = W / 2, h / 2
    css = """
.halo { transform-box: fill-box; transform-origin: center; animation: breathe 9s ease-in-out infinite alternate; }
@keyframes breathe { from { transform: scale(.92); opacity: .75; } to { transform: scale(1.06); opacity: 1; } }
"""
    body = f"""
<defs>
  <clipPath id="card"><rect width="{W}" height="{h}" rx="28"/></clipPath>
  <linearGradient id="edge" gradientUnits="userSpaceOnUse" x1="0" y1="0" x2="{W}" y2="{h}">
    {spectrum_stops()}
    <animateTransform attributeName="gradientTransform" type="rotate" from="0 {cx} {cy}" to="360 {cx} {cy}" dur="12s" repeatCount="indefinite"/>
  </linearGradient>
  <linearGradient id="ink" gradientUnits="userSpaceOnUse" x1="330" y1="0" x2="870" y2="0">
    <stop offset="0" stop-color="#0a84ff"/><stop offset=".45" stop-color="#bf5af2"/><stop offset="1" stop-color="#ff375f"/>
  </linearGradient>
  <filter id="soft" x="-30%" y="-30%" width="160%" height="160%"><feGaussianBlur stdDeviation="70"/></filter>
  <filter id="glow" x="-5%" y="-10%" width="110%" height="120%"><feGaussianBlur stdDeviation="9"/></filter>
</defs>
<g clip-path="url(#card)">
  <rect width="{W}" height="{h}" fill="{t['card']}"/>
  <ellipse class="halo loop" cx="{cx}" cy="{h + 40}" rx="460" ry="120" fill="url(#edge)" opacity="{t['halo']}" filter="url(#soft)"/>
</g>
<rect x="1.5" y="1.5" width="{W - 3}" height="{h - 3}" rx="27" stroke="url(#edge)" stroke-width="6" opacity="{t['edge'] * .45:.2f}" filter="url(#glow)"/>
<rect x="1" y="1" width="{W - 2}" height="{h - 2}" rx="27" stroke="url(#edge)" stroke-width="1.5" opacity="{t['edge']}"/>
<text class="in" x="{cx}" y="112" text-anchor="middle" font-size="17" font-weight="600" fill="{t['sub']}" {at(.1)}>Data Scientist</text>
<text class="in" x="{cx}" y="200" text-anchor="middle" font-size="92" font-weight="600" letter-spacing="-3.2" fill="{t['text']}" {at(.25)}>{NAME}</text>
<text class="in" x="{cx}" y="262" text-anchor="middle" font-size="42" font-weight="600" letter-spacing="-1.2" fill="url(#ink)" {at(.5)}>Machine learning that ships.</text>
<text class="in" x="{cx}" y="318" text-anchor="middle" font-size="17" fill="{t['sub']}" {at(.75)}>Speech AI  ·  NLP  ·  Applied ML systems  ·  Road-safety analytics</text>
"""
    return svg(W, h, body, css, f"{NAME} — Data Scientist. Machine learning that ships.")


# --------------------------------------------------------------------------- toolbox

GLYPHS = {
    # monoline, 24px box centred on the origin
    "spark": '<path d="M0 -11 C1.2 -3.5 3.5 -1.2 11 0 C3.5 1.2 1.2 3.5 0 11 C-1.2 3.5 -3.5 1.2 -11 0 C-3.5 -1.2 -1.2 -3.5 0 -11Z"/>',
    "stack": '<ellipse cx="0" cy="-7" rx="9" ry="3.5"/><path d="M-9 -7 V7 C-9 9 -5 10.5 0 10.5 C5 10.5 9 9 9 7 V-7"/><path d="M-9 0 C-9 2 -5 3.5 0 3.5 C5 3.5 9 2 9 0"/>',
    "ship": '<path d="M0 -11 L9.5 -5.5 V5.5 L0 11 L-9.5 5.5 V-5.5 Z"/><path d="M-9.5 -5.5 L0 0 L9.5 -5.5 M0 0 V11"/>',
}

TOOLBOX = [
    ("spark", "Machine learning", ["Python", "PyTorch", "TensorFlow", "scikit-learn", "NVIDIA NeMo", "LightGBM", "OpenCV", "pandas"]),
    ("stack", "Data & backend", ["FastAPI", "PostgreSQL", "MongoDB", "MySQL", "Node.js", "ONNX", "Supabase"]),
    ("ship", "Ship", ["Docker", "Kubernetes", "AWS", "Vercel", "Next.js", "React", "TypeScript", "Git"]),
]


def chip_width(label):
    return 30 + sum(9.6 if c.isupper() else 4.6 if c in "il.-" else 8.6 for c in label)


def toolbox(t):
    gap = 40
    col_w = (W - 2 * PAD - 2 * gap) / 3
    top = 196
    chip_h, chip_gap = 36, 10
    cols, bottom, n = [], top, 0
    for c, (glyph, title, tools) in enumerate(TOOLBOX):
        x0 = PAD + c * (col_w + gap)
        head = (f'<g transform="translate({x0 + 12:.0f},{top - 58})" stroke="{t["text"]}" stroke-width="1.6" '
                f'stroke-linejoin="round" stroke-linecap="round">{GLYPHS[glyph]}</g>'
                f'<text x="{x0:.0f}" y="{top - 10}" font-size="19" font-weight="600" fill="{t["text"]}">{escape(title)}</text>')
        chips = []
        x, y = 0.0, top + 12
        for tool in tools:
            w = chip_width(tool)
            if x and x + w > col_w:
                x, y = 0.0, y + chip_h + chip_gap
            chips.append(f'<g class="in" {at(.45 + n * .035)}><rect x="{x0 + x:.1f}" y="{y}" width="{w:.1f}" height="{chip_h}" '
                         f'rx="{chip_h / 2}" fill="{t["chip"]}" stroke="{t["border"]}"/>'
                         f'<text x="{x0 + x + w / 2:.1f}" y="{y + 23.5}" text-anchor="middle" font-size="15" '
                         f'font-weight="500" fill="{t["text"]}">{escape(tool)}</text></g>')
            x += w + chip_gap
            n += 1
        bottom = max(bottom, y + chip_h)
        cols.append(f'<g class="in" {at(.2 + c * .1)}>{head}</g>' + "".join(chips))
    h = int(bottom + PAD)
    body = (f'<rect x=".5" y=".5" width="{W - 1}" height="{h - 1}" rx="28" fill="{t["raised"]}" stroke="{t["border"]}"/>'
            f'<text class="in" x="{PAD}" y="80" font-size="34" font-weight="600" letter-spacing="-.8" fill="{t["text"]}">'
            f'Toolbox.<tspan fill="{t["sub"]}"> From notebook to production.</tspan></text>'
            + "".join(cols))
    return svg(W, h, body, label="Toolbox: " + ", ".join(tool for _, _, tools in TOOLBOX for tool in tools))


# --------------------------------------------------------------------------- contact pills

ICONS = {
    "Email": '<rect x="-10" y="-7.5" width="20" height="15" rx="3.5"/><path d="M-9 -5 L0 1.5 L9 -5"/>',
    "LinkedIn": '<rect x="-9.5" y="-9.5" width="19" height="19" rx="4.5"/><path d="M-4.5 -1 V5 M-4.5 -4.6 V-4.4 M-1 5 V-1 M-1 1.5 C-1 -0.5 4.5 -1.5 4.5 2 V5"/>',
    "X": '<path d="M-7.5 -8.5 L7.5 8.5 M7.5 -8.5 L-7.5 8.5"/>',
    "Instagram": '<rect x="-9.5" y="-9.5" width="19" height="19" rx="5.5"/><circle r="4.3"/><path d="M5.2 -5.4 V-5.2"/>',
}


def pill(name, t):
    w, h = 200, 56
    body = (f'<rect x=".5" y=".5" width="{w - 1}" height="{h - 1}" rx="{h / 2}" fill="{t["raised"]}" stroke="{t["border"]}"/>'
            f'<g transform="translate(34,28)" stroke="{t["text"]}" stroke-width="1.7" stroke-linecap="round" '
            f'stroke-linejoin="round">{ICONS[name]}</g>'
            f'<text x="58" y="34" font-size="17" font-weight="600" fill="{t["text"]}">{name}</text>'
            f'<path d="M166 34 L176 24 M168.5 23.5 H176.5 V31.5" stroke="{t["sub"]}" stroke-width="1.7" '
            f'stroke-linecap="round" stroke-linejoin="round"/>')
    return svg(w, h, f'<g class="in">{body}</g>', label=name)


# --------------------------------------------------------------------------- main

def main():
    out = Path(sys.argv[1] if len(sys.argv) > 1 else "dist")
    out.mkdir(parents=True, exist_ok=True)
    for mode, t in THEMES.items():
        files = {"hero": hero(t), "toolbox": toolbox(t), **{f"pill-{n.lower()}": pill(n, t) for n in ICONS}}
        for name, content in files.items():
            (out / f"{name}-{mode}.svg").write_text(content, encoding="utf-8")


if __name__ == "__main__":
    main()
