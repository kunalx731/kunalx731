"""Render the animated SVG artwork for the profile README.

Writes light and dark variants of every image into an output directory:
hero, bento (live GitHub stats), section headers, contact pills, footer.

    GITHUB_TOKEN=... python scripts/profile_art.py dist
"""
import datetime as dt
import json
import os
import sys
import urllib.request
from html import escape
from pathlib import Path

LOGIN = "kunalx731"
NAME = "Krishna Kunal"
EXCLUDE_REPOS = {"nhai_nhidcl", "co_dashboard"}  # committed virtualenvs
HIDE_LANGS = {"HTML", "CSS"}

FONT = ("-apple-system, BlinkMacSystemFont, 'SF Pro Display', 'Segoe UI Variable Display', "
        "'Segoe UI', 'Helvetica Neue', Inter, Arial, sans-serif")

THEMES = {
    "dark": dict(stage="#000000", tile="#161617", stroke="rgba(255,255,255,0.08)",
                 text="#f5f5f7", sub="#86868b", accent="#2997ff", track="#2c2c2e",
                 glow=0.42, heat=["#202023", "#0b3a66", "#0062c4", "#0a84ff", "#64d2ff"]),
    "light": dict(stage="#fbfbfd", tile="#f5f5f7", stroke="rgba(0,0,0,0.06)",
                  text="#1d1d1f", sub="#6e6e73", accent="#0071e3", track="#e5e5ea",
                  glow=0.22, heat=["#e8e8ed", "#b3d7ff", "#5eb0ff", "#0a84ff", "#0058b9"]),
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


# --------------------------------------------------------------------------- data

QUERY = """
query($login: String!) {
  user(login: $login) {
    pullRequests { totalCount }
    issues { totalCount }
    repositories(ownerAffiliations: OWNER, isFork: false, first: 100) {
      totalCount
      nodes {
        name
        stargazerCount
        languages(first: 10, orderBy: {field: SIZE, direction: DESC}) {
          edges { size node { name color } }
        }
      }
    }
    contributionsCollection {
      contributionCalendar {
        totalContributions
        weeks { contributionDays { date contributionCount weekday } }
      }
    }
  }
}
"""


def fetch(token):
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": QUERY, "variables": {"login": LOGIN}}).encode(),
        headers={"Authorization": f"bearer {token}", "User-Agent": LOGIN},
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        payload = json.load(resp)
    if "errors" in payload:
        raise RuntimeError(payload["errors"])
    return payload["data"]["user"]


def summarize(user):
    cal = user["contributionsCollection"]["contributionCalendar"]
    weeks = [w["contributionDays"] for w in cal["weeks"]]
    days = [d for w in weeks for d in w]

    longest = run = 0
    for d in days:
        run = run + 1 if d["contributionCount"] else 0
        longest = max(longest, run)
    current = 0
    tail = days[::-1]
    if tail and not tail[0]["contributionCount"]:
        tail = tail[1:]  # today isn't over yet
    for d in tail:
        if not d["contributionCount"]:
            break
        current += 1

    sizes, colors = {}, {}
    for repo in user["repositories"]["nodes"]:
        if repo["name"] in EXCLUDE_REPOS:
            continue
        for edge in repo["languages"]["edges"]:
            lang = edge["node"]["name"]
            if lang in HIDE_LANGS:
                continue
            sizes[lang] = sizes.get(lang, 0) + edge["size"]
            colors[lang] = edge["node"]["color"] or "#8e8e93"
    total = sum(sizes.values()) or 1
    ranked = sorted(sizes.items(), key=lambda kv: -kv[1])
    langs = [(name, size / total, colors[name]) for name, size in ranked[:5] if size / total >= .02]
    rest = 1 - sum(share for _, share, _ in langs)
    if rest > 0.005:
        langs.append(("Other", rest, "#8e8e93"))

    return dict(
        total=cal["totalContributions"], weeks=weeks, current=current, longest=longest,
        prs=user["pullRequests"]["totalCount"], issues=user["issues"]["totalCount"],
        repos=user["repositories"]["totalCount"],
        stars=sum(r["stargazerCount"] for r in user["repositories"]["nodes"]),
        langs=langs,
    )


# --------------------------------------------------------------------------- hero

FOCUS = ["Speech recognition", "Natural language processing", "Applied ML systems", "Road-safety analytics"]


def hero(t):
    w, h = 1200, 460
    blobs = [(130, 40, 190, "#0a84ff", 17), (1090, 30, 170, "#bf5af2", 21),
             (600, 560, 230, "#ff375f", 19), (1150, 470, 140, "#ff9f0a", 23), (40, 470, 130, "#30d158", 25)]
    blob_svg = "".join(
        f'<circle class="blob b{i}" cx="{x}" cy="{y}" r="{r}" fill="{c}"/>' for i, (x, y, r, c, _) in enumerate(blobs))
    blob_css = "".join(
        f".b{i}{{animation: drift{i % 2} {s}s ease-in-out {-i * 3}s infinite alternate;}}"
        for i, (*_, s) in enumerate(blobs))

    stops = "".join(f'<stop offset="{i / (len(SPECTRUM) - 1):.2f}" stop-color="{c}"/>' for i, c in enumerate(SPECTRUM))
    period, n = 3.2, len(FOCUS)
    focus = "".join(
        f'<text class="focus f{i}" x="600" y="352" text-anchor="middle" font-size="22" font-weight="600" '
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
<text class="rise" x="600" y="150" text-anchor="middle" font-size="15" font-weight="600" letter-spacing="6" fill="{t['sub']}" {delay(.1)}>HELLO, I'M</text>
<text class="rise" x="600" y="240" text-anchor="middle" font-size="96" font-weight="700" letter-spacing="-3" fill="url(#spectrum)" {delay(.3)}>{NAME}</text>
<text class="rise" x="600" y="296" text-anchor="middle" font-size="26" font-weight="500" fill="{t['text']}" {delay(.6)}>Data scientist. Building machine learning that ships.</text>
{focus}
<text class="rise" x="600" y="410" text-anchor="middle" font-size="16" fill="{t['sub']}" {delay(1)}>It works — don’t ask how.</text>
"""
    return svg(w, h, body, css, f"{NAME} — Data Scientist")


# --------------------------------------------------------------------------- bento

def tile(x, y, w, h, t, i, inner):
    return (f'<g class="rise" {delay(.1 + i * .08)}><g transform="translate({x},{y})">'
            f'<rect width="{w}" height="{h}" rx="24" fill="{t["tile"]}" stroke="{t["stroke"]}"/>{inner}</g></g>')


def label(text, t, x=28, y=42):
    return f'<text x="{x}" y="{y}" font-size="17" font-weight="600" fill="{t["sub"]}">{escape(text)}</text>'


def big(value, t, x=28, y=114, size=62):
    return (f'<text x="{x}" y="{y}" font-size="{size}" font-weight="700" letter-spacing="-2" '
            f'fill="{t["text"]}">{value}</text>')


def caption(text, t, x=28, y=144):
    return f'<text x="{x}" y="{y}" font-size="17" fill="{t["sub"]}">{escape(text)}</text>'


def heat_levels(weeks):
    counts = sorted(d["contributionCount"] for w in weeks for d in w if d["contributionCount"])
    if not counts:
        return lambda c: 0
    q = [counts[int(len(counts) * f)] for f in (.25, .5, .75)]  # quartiles keep spikes from washing out the map
    return lambda c: 0 if c == 0 else 1 + sum(c > v for v in q)


def heatmap(s, t, w):
    weeks = s["weeks"]
    pitch = (w - 56) / len(weeks)
    cell = pitch * .78
    level = heat_levels(weeks)
    cells, months, last_month = [], [], None
    for col, week in enumerate(weeks):
        for d in week:
            x, y = 28 + col * pitch, 78 + d["weekday"] * pitch
            cells.append(f'<rect class="cell k{col}" x="{x:.1f}" y="{y:.1f}" width="{cell:.1f}" height="{cell:.1f}" '
                         f'rx="{cell * .28:.1f}" fill="{t["heat"][level(d["contributionCount"])]}"/>')
        month = dt.date.fromisoformat(week[0]["date"]).strftime("%b")
        if month != last_month and col < len(weeks) - 2:
            months.append(f'<text x="{28 + col * pitch:.1f}" y="64" font-size="14" fill="{t["sub"]}">{month}</text>')
            last_month = month
    legend_x = w - 28 - 5 * 18 - 78
    legend = (f'<text x="{legend_x}" y="42" font-size="14" fill="{t["sub"]}">Less</text>' +
              "".join(f'<rect x="{legend_x + 34 + i * 18}" y="31" width="13" height="13" rx="3.5" fill="{c}"/>'
                      for i, c in enumerate(t["heat"])) +
              f'<text x="{legend_x + 34 + 5 * 18 + 4}" y="42" font-size="14" fill="{t["sub"]}">More</text>')
    css = "".join(f".k{c}{{animation-delay:{.5 + c * .018:.3f}s}}" for c in range(len(weeks)))
    return label("Contribution activity", t) + legend + "".join(months) + "".join(cells), css


def ring(s, t):
    r, c = 46, 2 * 3.14159 * 46
    p = min(1, s["current"] / s["longest"]) if s["longest"] else 0
    css = f"""
.ring {{ stroke-dasharray: {c:.1f}; stroke-dashoffset: {c:.1f}; animation: ring 1.6s cubic-bezier(.2,.8,.2,1) .6s forwards; }}
@keyframes ring {{ to {{ stroke-dashoffset: {c * (1 - p):.1f}; }} }}
@media (prefers-reduced-motion: reduce) {{ .ring {{ animation: none !important; stroke-dashoffset: {c * (1 - p):.1f}; }} }}
"""
    g = (f'<g transform="translate(212,92) rotate(-90)">'
         f'<circle r="{r}" stroke="{t["track"]}" stroke-width="12"/>'
         f'<circle class="ring" r="{r}" stroke="url(#ringfill)" stroke-width="12" stroke-linecap="round"/></g>')
    return g, css


def languages(s, t, w):
    bar_w = w - 56
    x, segs, legend = 0.0, [], []
    lx, ly = 0.0, 62
    for name, share, color in s["langs"]:
        seg = bar_w * share
        segs.append(f'<rect x="{x:.1f}" width="{seg + .5:.1f}" height="12" fill="{color}"/>')
        x += seg
        pct = f"{share * 100:.1f}%"
        name_w, item_w = len(name) * 10.4, 20 + len(name) * 10.4 + 8 + len(pct) * 9.6
        if lx and lx + item_w > bar_w:
            lx, ly = 0.0, ly + 36
        legend.append(f'<circle cx="{lx + 6:.0f}" cy="{ly - 6}" r="6" fill="{color}"/>'
                      f'<text x="{lx + 20:.0f}" y="{ly}" font-size="18" font-weight="600" fill="{t["text"]}">{escape(name)}</text>'
                      f'<text x="{lx + 28 + name_w:.0f}" y="{ly}" font-size="18" fill="{t["sub"]}">{pct}</text>')
        lx += item_w + 26
    css = """
.bar { transform-box: fill-box; transform-origin: left; transform: scaleX(0); animation: grow 1.4s cubic-bezier(.2,.8,.2,1) .9s forwards; }
@keyframes grow { to { transform: scaleX(1); } }
"""
    return (label("Languages", t) +
            f'<g transform="translate(28,64)"><clipPath id="barclip"><rect width="{bar_w}" height="12" rx="6"/></clipPath>'
            f'<rect width="{bar_w}" height="12" rx="6" fill="{t["track"]}"/>'
            f'<g clip-path="url(#barclip)"><g class="bar">{"".join(segs)}</g></g>{"".join(legend)}</g>'), css


def waveform(t, x0, y0, n=34):
    bars = []
    for i in range(n):
        h = 10 + (i * 37 % 23) + (i % 5) * 4
        dur = .8 + (i * 13 % 7) / 10
        bars.append(f'<rect class="wave" x="{x0 + i * 9}" y="{y0 - h / 2:.1f}" width="5" height="{h}" rx="2.5" '
                    f'fill="url(#ringfill)" style="animation-duration:{dur:.1f}s;animation-delay:{-i * .07:.2f}s"/>')
    css = """
.wave { transform-box: fill-box; transform-origin: center; animation: talk 1s ease-in-out infinite alternate; }
@keyframes talk { from { transform: scaleY(.25); } to { transform: scaleY(1); } }
"""
    return "".join(bars), css


def bento(s, t):
    W, gap = 1200, 16
    col = (W - 3 * gap) / 4
    half = col * 2 + gap
    y1, h1 = 0, 168
    y2, h2 = h1 + gap, 250
    y3, h3 = y2 + h2 + gap, 176
    H = y3 + h3

    ring_svg, ring_css = ring(s, t)
    heat_svg, heat_css = heatmap(s, t, W)
    lang_svg, lang_css = languages(s, t, half)
    wave_svg, wave_css = waveform(t, 28, 142, 56)

    tiles = [
        tile(0, y1, col, h1, t, 0, label("Contributions", t) + big(f"{s['total']:,}", t) + caption("in the last year", t)),
        tile(col + gap, y1, col, h1, t, 1, label("Current streak", t) + big(s["current"], t) +
             caption(f"days · best {s['longest']}", t) + ring_svg),
        tile(2 * (col + gap), y1, col, h1, t, 2, label("Pull requests", t) + big(s["prs"], t) +
             caption(f"{s['issues']} issues opened", t)),
        tile(3 * (col + gap), y1, col, h1, t, 3, label("Repositories", t) + big(s["repos"], t) +
             caption(f"{s['stars']} stars earned", t)),
        tile(0, y2, W, h2, t, 4, heat_svg),
        tile(0, y3, half, h3, t, 5, lang_svg),
        tile(half + gap, y3, half, h3, t, 6,
             label("Now building", t) +
             f'<text x="28" y="88" font-size="26" font-weight="700" letter-spacing="-.5" fill="{t["text"]}">Speech recognition with NVIDIA NeMo</text>'
             f'<text x="28" y="114" font-size="17" fill="{t["sub"]}">FastAPI · ONNX · real-time inference</text>' + wave_svg),
    ]
    defs = (f'<defs><linearGradient id="ringfill" x1="0" y1="0" x2="1" y2="1">'
            f'<stop offset="0" stop-color="#0a84ff"/><stop offset=".55" stop-color="#bf5af2"/>'
            f'<stop offset="1" stop-color="#ff375f"/></linearGradient></defs>')
    css = ring_css + lang_css + wave_css + heat_css + """
.cell { opacity: 0; transform-box: fill-box; transform-origin: center; animation: pop .6s cubic-bezier(.2,.8,.2,1) forwards; }
@keyframes pop { from { opacity: 0; transform: scale(.4); } to { opacity: 1; transform: none; } }
"""
    return svg(W, H, defs + "".join(tiles), css, f"{s['total']:,} contributions in the last year")


# --------------------------------------------------------------------------- small pieces

def header(title, subtitle, t):
    body = (f'<text class="rise" x="600" y="58" text-anchor="middle" font-size="44" font-weight="700" '
            f'letter-spacing="-1.5" fill="{t["text"]}">{escape(title)}</text>'
            f'<text class="rise" x="600" y="94" text-anchor="middle" font-size="19" fill="{t["sub"]}" {delay(.15)}>'
            f'{escape(subtitle)}</text>')
    return svg(1200, 112, body, label=title)


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


def footer(t):
    body = (f'<text class="rise" x="600" y="40" text-anchor="middle" font-size="18" font-style="italic" '
            f'fill="{t["sub"]}">“Peace isn’t quiet — it’s a clean log file.”</text>')
    return svg(1200, 64, body, label="Peace isn't quiet, it's a clean log file.")


# --------------------------------------------------------------------------- main

def main():
    out = Path(sys.argv[1] if len(sys.argv) > 1 else "dist")
    out.mkdir(parents=True, exist_ok=True)
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        sys.exit("GITHUB_TOKEN is required")
    stats = summarize(fetch(token))
    for mode, t in THEMES.items():
        files = {
            "hero": hero(t),
            "bento": bento(stats, t),
            "toolbox": header("Toolbox.", "What I reach for, from notebook to production.", t),
            "connect": header("Say hello.", "Open to collaborations in NLP and applied machine learning.", t),
            "footer": footer(t),
            **{f"pill-{n.lower()}": pill(n, t) for n in ICONS},
        }
        for name, content in files.items():
            (out / f"{name}-{mode}.svg").write_text(content, encoding="utf-8")
    print(json.dumps({k: v for k, v in stats.items() if k != "weeks"}, indent=1))


if __name__ == "__main__":
    main()
