"""Render the animated SVG artwork for the profile README.

Writes light and dark variants of every image into an output directory:
hero, section header, contact pills. The live activity panel is
served by the github-readme-stats deployment (/api/profile).

    python scripts/profile_art.py dist
"""
import sys
from html import escape
from pathlib import Path

NAME = "Krishna Kunal"

FONT = ("-apple-system, BlinkMacSystemFont, 'SF Pro Display', 'Segoe UI Variable Display', "
        "'Segoe UI', 'Helvetica Neue', Inter, Arial, sans-serif")

THEMES = {
    "dark": dict(stage="#000000", tile="#161617", stroke="rgba(255,255,255,0.08)",
                 text="#f5f5f7", sub="#86868b", accent="#2997ff",
                 glow=0.42),
    "light": dict(stage="#fbfbfd", tile="#f5f5f7", stroke="rgba(0,0,0,0.06)",
                  text="#1d1d1f", sub="#6e6e73", accent="#0071e3",
                  glow=0.22),
}
SPECTRUM = ["#0894ff", "#c959dd", "#ff2e54", "#ff9004", "#0894ff"]

BASE_CSS = f"""
text {{ font-family: {FONT}; }}
.rise {{ opacity: 0; animation: rise .9s cubic-bezier(.2,.8,.2,1) forwards; }}
@keyframes rise {{ from {{ opacity: 0; transform: translateY(18px); }} to {{ opacity: 1; transform: none; }} }}
@media (prefers-reduced-motion: reduce) {{
  .rise, .cell {{ animation: none !important; opacity: 1 !important; }}
  .blob, .wave {{ animation: none !important; }}
  .bar {{ animation: none !important; transform: none !important; }}
  .focus {{ animation: none !important; }}
  .f0 {{ opacity: 1 !important; }}
}}
"""


def svg(w, h, body, css="", label=""):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
            f'role="img" aria-label="{escape(label)}" fill="none">'
            f"<style>{BASE_CSS}{css}</style>{body}</svg>")


def delay(seconds):
    return f'style="animation-delay:{seconds:.2f}s"'


# --------------------------------------------------------------------------- hero

FOCUS = ["Speech recognition", "Natural language processing", "Applied ML systems", "Road-safety analytics"]


def hero(t):
    w, h = 1200, 330
    blobs = [(130, 20, 160, "#0a84ff", 17), (1090, 10, 150, "#bf5af2", 21),
             (600, 420, 200, "#ff375f", 19), (1150, 340, 120, "#ff9f0a", 23), (40, 340, 110, "#30d158", 25)]
    blob_svg = "".join(
        f'<circle class="blob b{i}" cx="{x}" cy="{y}" r="{r}" fill="{c}"/>' for i, (x, y, r, c, _) in enumerate(blobs))
    blob_css = "".join(
        f".b{i}{{animation: drift{i % 2} {s}s ease-in-out {-i * 3}s infinite alternate;}}"
        for i, (*_, s) in enumerate(blobs))

    stops = "".join(f'<stop offset="{i / (len(SPECTRUM) - 1):.2f}" stop-color="{c}"/>' for i, c in enumerate(SPECTRUM))
    period, n = 3.2, len(FOCUS)
    focus = "".join(
        f'<text class="focus f{i}" x="600" y="262" text-anchor="middle" font-size="20" font-weight="600" '
        f'fill="{t["accent"]}" style="animation-delay:{1.4 + i * period:.1f}s">{escape(word)}</text>'
        for i, word in enumerate(FOCUS))
    cycle = period * n
    show = period / cycle * 100

    css = f"""
.blob {{ opacity: {t['glow']}; transform-box: fill-box; transform-origin: center; }}
@keyframes drift0 {{ from {{ transform: translate(-50px,-20px) scale(1); }} to {{ transform: translate(60px,40px) scale(1.18); }} }}
@keyframes drift1 {{ from {{ transform: translate(40px,30px) scale(1.1); }} to {{ transform: translate(-60px,-30px) scale(.92); }} }}
.focus {{ opacity: 0; animation: focus {cycle:.1f}s ease-in-out infinite; }}
@keyframes focus {{
  0% {{ opacity: 0; transform: translateY(10px); }}
  {show * .15:.2f}% {{ opacity: 1; transform: none; }}
  {show * .85:.2f}% {{ opacity: 1; transform: none; }}
  {show:.2f}%, 100% {{ opacity: 0; transform: translateY(-10px); }}
}}
{blob_css}
"""
    body = f"""
<defs>
  <clipPath id="stage"><rect width="{w}" height="{h}" rx="32"/></clipPath>
  <filter id="soft" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="70"/></filter>
  <linearGradient id="spectrum" gradientUnits="userSpaceOnUse" x1="0" y1="0" x2="900" y2="0" spreadMethod="repeat">
    {stops}
    <animateTransform attributeName="gradientTransform" type="translate" from="0 0" to="900 0" dur="9s" repeatCount="indefinite"/>
  </linearGradient>
</defs>
<g clip-path="url(#stage)">
  <rect width="{w}" height="{h}" fill="{t['stage']}"/>
  <g filter="url(#soft)">{blob_svg}</g>
</g>
<rect x=".5" y=".5" width="{w - 1}" height="{h - 1}" rx="32" stroke="{t['stroke']}"/>
<text class="rise" x="600" y="92" text-anchor="middle" font-size="14" font-weight="600" letter-spacing="6" fill="{t['sub']}" {delay(.1)}>HELLO, I'M</text>
<text class="rise" x="600" y="172" text-anchor="middle" font-size="84" font-weight="700" letter-spacing="-2.6" fill="url(#spectrum)" {delay(.3)}>{NAME}</text>
<text class="rise" x="600" y="220" text-anchor="middle" font-size="24" font-weight="500" fill="{t['text']}" {delay(.6)}>Data scientist. Building machine learning that ships.</text>
{focus}
<text class="rise" x="600" y="300" text-anchor="middle" font-size="15" fill="{t['sub']}" {delay(1)}>It works — don’t ask how.</text>
"""
    return svg(w, h, body, css, f"{NAME} — Data Scientist")


# --------------------------------------------------------------------------- small pieces

def header(title, subtitle, t):
    body = (f'<text class="rise" x="600" y="40" text-anchor="middle" font-size="34" font-weight="700" '
            f'letter-spacing="-1.5" fill="{t["text"]}">{escape(title)}</text>'
            f'<text class="rise" x="600" y="70" text-anchor="middle" font-size="17" fill="{t["sub"]}" {delay(.15)}>'
            f'{escape(subtitle)}</text>')
    return svg(1200, 84, body, label=title)


ICONS = {
    "Email": '<rect x="-11" y="-8" width="22" height="16" rx="3.5" stroke="{c}" stroke-width="2"/>'
             '<path d="M-10 -6 L0 2 L10 -6" stroke="{c}" stroke-width="2" stroke-linejoin="round"/>',
    "LinkedIn": '<rect x="-10" y="-10" width="20" height="20" rx="4.5" fill="{c}"/>'
                '<text x="0" y="5.5" text-anchor="middle" font-size="13" font-weight="800" fill="{bg}">in</text>',
    "X": '<path d="M-8 -9 L8 9 M8 -9 L-8 9" stroke="{c}" stroke-width="2.6" stroke-linecap="round"/>',
    "Instagram": '<rect x="-10" y="-10" width="20" height="20" rx="6" stroke="{c}" stroke-width="2"/>'
                 '<circle r="4.6" stroke="{c}" stroke-width="2"/><circle cx="5.5" cy="-5.5" r="1.4" fill="{c}"/>',
}


def pill(name, t):
    w, h = 190, 52
    icon = ICONS[name].format(c=t["text"], bg=t["tile"])
    body = (f'<rect x=".5" y=".5" width="{w - 1}" height="{h - 1}" rx="26" fill="{t["tile"]}" stroke="{t["stroke"]}"/>'
            f'<g transform="translate(40,26)">{icon}</g>'
            f'<text x="64" y="32" font-size="17" font-weight="600" fill="{t["text"]}">{name}</text>'
            f'<path d="M160 21 l5 5 -5 5" stroke="{t["sub"]}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>')
    return svg(w, h, body, label=name)


# --------------------------------------------------------------------------- main

def main():
    out = Path(sys.argv[1] if len(sys.argv) > 1 else "dist")
    out.mkdir(parents=True, exist_ok=True)
    for mode, t in THEMES.items():
        files = {
            "hero": hero(t),
            "toolbox": header("Toolbox.", "What I reach for, from notebook to production — and how to reach me.", t),
            **{f"pill-{n.lower()}": pill(n, t) for n in ICONS},
        }
        for name, content in files.items():
            (out / f"{name}-{mode}.svg").write_text(content, encoding="utf-8")


if __name__ == "__main__":
    main()
