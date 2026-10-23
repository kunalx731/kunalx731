"""Render the animated hero for the profile README (light and dark).

Inter is subset to the glyphs each image uses and embedded, so the type renders
identically on every OS. The live stats strip is served by the
github-readme-stats deployment (/api/profile) in the same style.

    pip install fonttools brotli
    python scripts/profile_art.py dist
"""
import base64
import io
import sys
from html import escape
from pathlib import Path

from fontTools import subset
from fontTools.ttLib import TTFont
from fontTools.varLib import instancer

FONT_FILE = Path(__file__).parent / "fonts" / "Inter.woff2"  # SIL OFL 1.1, see fonts/OFL.txt
W, H = 1200, 600
EASE = "cubic-bezier(.16,1,.3,1)"
SIRI = ["#0894ff", "#c959dd", "#ff2e54", "#ff9004", "#0894ff"]

EYEBROW = "Krishna Kunal"
LINE_1 = "Data that thinks."
LINE_2 = "Models that ship."
COPY = "Data scientist. Speech, language and road-safety AI — from notebook to production."

THEMES = {
    "dark": dict(bg="#000000", text="#f5f5f7", sub="#86868b", glow=0.85, edge=0.9),
    "light": dict(bg="#ffffff", text="#1d1d1f", sub="#6e6e73", glow=0.55, edge=0.7),
}


def font_face(weight, text):
    """Inter at one weight, cut down to the characters in `text`, as an @font-face rule."""
    font = instancer.instantiateVariableFont(TTFont(FONT_FILE), {"wght": weight})
    opts = subset.Options()
    opts.flavor = "woff2"
    opts.layout_features = ["kern", "liga", "calt"]
    sub = subset.Subsetter(opts)
    sub.populate(text=text)
    sub.subset(font)
    buf = io.BytesIO()
    font.flavor = "woff2"
    font.save(buf)
    data = base64.b64encode(buf.getvalue()).decode()
    return (f"@font-face {{ font-family: 'Inter KK'; font-weight: {weight}; "
            f"src: url(data:font/woff2;base64,{data}) format('woff2'); }}")


def stops(colors):
    return "".join(f'<stop offset="{i / (len(colors) - 1):.2f}" stop-color="{c}"/>' for i, c in enumerate(colors))


def hero(t, fonts):
    cx, cy = W / 2, H / 2
    css = f"""
{fonts}
text {{ font-family: 'Inter KK', -apple-system, 'SF Pro Display', 'Segoe UI', sans-serif; }}
.in {{ opacity: 0; animation: in 1.4s {EASE} forwards; }}
@keyframes in {{ from {{ opacity: 0; transform: translateY(24px); filter: blur(12px); }}
                to {{ opacity: 1; transform: none; filter: blur(0); }} }}
.glow {{ opacity: 0; animation: glowin 2.4s ease-out forwards, breathe 6s ease-in-out 2.4s infinite alternate; }}
@keyframes glowin {{ to {{ opacity: {t['glow']}; }} }}
@keyframes breathe {{ from {{ opacity: {t['glow']}; }} to {{ opacity: {t['glow'] * .6:.2f}; }} }}
@media (prefers-reduced-motion: reduce) {{
  .in {{ animation: none !important; opacity: 1 !important; }}
  .glow {{ animation: none !important; opacity: {t['glow']} !important; }}
}}
"""
    body = f"""
<defs>
  <clipPath id="card"><rect width="{W}" height="{H}" rx="36"/></clipPath>
  <linearGradient id="siri" gradientUnits="userSpaceOnUse" x1="0" y1="0" x2="{W}" y2="{H}">
    {stops(SIRI)}
    <animateTransform attributeName="gradientTransform" type="rotate" from="0 {cx} {cy}" to="360 {cx} {cy}" dur="8s" repeatCount="indefinite"/>
  </linearGradient>
  <linearGradient id="ink" gradientUnits="userSpaceOnUse" x1="0" y1="0" x2="760" y2="0" spreadMethod="reflect">
    {stops(SIRI[:4])}
    <animateTransform attributeName="gradientTransform" type="translate" from="220 0" to="980 0" dur="10s" repeatCount="indefinite"/>
  </linearGradient>
  <filter id="blur" x="-10%" y="-10%" width="120%" height="120%"><feGaussianBlur stdDeviation="26"/></filter>
</defs>
<g clip-path="url(#card)">
  <rect width="{W}" height="{H}" fill="{t['bg']}"/>
  <rect class="glow" x="0" y="0" width="{W}" height="{H}" rx="36" stroke="url(#siri)" stroke-width="36" filter="url(#blur)"/>
</g>
<rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="35" stroke="url(#siri)" stroke-width="2" opacity="{t['edge']}"/>
<text class="in" x="{cx}" y="190" text-anchor="middle" font-size="22" font-weight="600" fill="{t['sub']}" style="animation-delay:.3s">{escape(EYEBROW)}</text>
<text class="in" x="{cx}" y="294" text-anchor="middle" font-size="92" font-weight="600" letter-spacing="-3.4" fill="{t['text']}" style="animation-delay:.45s">{escape(LINE_1)}</text>
<text class="in" x="{cx}" y="396" text-anchor="middle" font-size="92" font-weight="600" letter-spacing="-3.4" fill="url(#ink)" style="animation-delay:.65s">{escape(LINE_2)}</text>
<text class="in" x="{cx}" y="470" text-anchor="middle" font-size="22" font-weight="400" fill="{t['sub']}" style="animation-delay:.9s">{escape(COPY)}</text>
"""
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" fill="none" '
            f'role="img" aria-label="{escape(EYEBROW)} — {escape(LINE_1)} {escape(LINE_2)} {escape(COPY)}">'
            f"<style>{css}</style>{body}</svg>")


def main():
    out = Path(sys.argv[1] if len(sys.argv) > 1 else "dist")
    out.mkdir(parents=True, exist_ok=True)
    fonts = font_face(600, EYEBROW + LINE_1 + LINE_2) + font_face(400, COPY)
    for mode, t in THEMES.items():
        (out / f"hero-{mode}.svg").write_text(hero(t, fonts), encoding="utf-8")


if __name__ == "__main__":
    main()
