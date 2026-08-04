#!/usr/bin/env python3
"""Generate the gradient section banners used in README.md.

One SVG per section per theme. Transparent background, so the banner sits on
GitHub's own canvas in both themes and there is never a dark rectangle on white.

Text is pinned with textLength because SVG loaded through <img> cannot fetch a
webfont -- it falls back to whatever mono the viewer has, and widths differ.

    python3 tools/banners.py

Bump VERSION on any visual change: GitHub's camo proxy caches these hard and
editing a file in place shows stale artwork indefinitely.
"""

import pathlib

VERSION = "v6"
OUT = pathlib.Path(__file__).resolve().parent.parent / "banners"

W, H = 870, 58
FS = 26                 # title size
CW = FS * 0.62          # mono advance width
BASE_Y = 30             # title baseline
RULE_Y = 44
LEAD = 120              # bright leading segment of the rule

# Typing, matched to tools/nameplate.py. Each title types at the same per-char
# rate, so loops differ in length by title -- they drift out of sync on purpose.
# In sync they read as a page-wide blink; staggered they read as a live terminal.
TYPE_PER_CHAR = 0.075
ERASE_PER_CHAR = 0.025
HOLD = 5.0
GAP = 0.7

# Saturated on #0d1117; darkened for contrast on white. Same hues either way.
DARK = {"cy": "#22d3ee", "bl": "#58a6ff", "pu": "#a855f7", "pk": "#f472b6",
        "dim": "#6e7681", "ink": "#ffffff"}
# "white" cannot be literal here or the title vanishes on a light canvas.
LIGHT = {"cy": "#0891b2", "bl": "#2563eb", "pu": "#9333ea", "pk": "#db2777",
         "dim": "#6a737d", "ink": "#1f2328"}

# Each section gets its own run through the palette, so the page moves cyan to
# pink as you scroll instead of repeating one gradient five times.
SECTIONS = [
    # cyan -> blue is only ~25 degrees of hue and read as a single flat colour.
    # Every run below spans at least ~55 degrees so the gradient is actually visible.
    ("core-thesis",        "CORE THESIS",        ["cy", "pu"]),
    ("background",         "BACKGROUND",         ["bl", "pu"]),
    ("what-i-do",          "WHAT I DO",          ["cy", "bl", "pu", "pk"]),
    ("currently-building", "CURRENTLY BUILDING", ["pu", "pk"]),
    ("tech-stack",         "TECH STACK",         ["pk", "pu", "cy"]),
]


def gradient(gid, stops, pal):
    n = len(stops)
    body = "".join(
        '<stop offset="{:.4g}" stop-color="{}"/>'.format(
            0 if n == 1 else i / (n - 1), pal[k]
        )
        for i, k in enumerate(stops)
    )
    return f'<linearGradient id="{gid}" x1="0" y1="0" x2="1" y2="0">{body}</linearGradient>'


def timeline(title):
    """Loop STARTS and ENDS fully typed -- a frozen render must still read."""
    n = len(title)
    t_type, t_erase = n * TYPE_PER_CHAR, n * ERASE_PER_CHAR
    total = HOLD + t_erase + GAP + t_type

    marks, widths = [0.0], [n]
    marks.append(HOLD)
    widths.append(n)
    for k in range(n, -1, -1):
        marks.append(HOLD + (n - k) * ERASE_PER_CHAR)
        widths.append(k)
    marks.append(HOLD + t_erase + GAP)
    widths.append(0)
    for k in range(n + 1):
        marks.append(HOLD + t_erase + GAP + k * TYPE_PER_CHAR)
        widths.append(k)

    return (";".join(f"{k*CW:.1f}" for k in widths),
            ";".join(f"{FS + k*CW:.1f}" for k in widths),
            ";".join(f"{m/total:.5f}" for m in marks),
            total)


def banner(title, stops, pal):
    tl = len(title) * CW
    w_vals, c_vals, keytimes, total = timeline(title)
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" \
viewBox="0 0 {W} {H}" role="img" aria-label="{title.title()}">
  <title>{title.title()}</title>
  <defs>
    {gradient("g", stops, pal)}
    <mask id="reveal">
      <rect x="{FS}" y="0" width="0" height="{H}" fill="#fff">
        <animate attributeName="width" values="{w_vals}" keyTimes="{keytimes}" \
dur="{total:.2f}s" calcMode="discrete" repeatCount="indefinite"/>
      </rect>
    </mask>
  </defs>
  <text x="0" y="{BASE_Y}" font-family="ui-monospace,SFMono-Regular,Menlo,Consolas,monospace" \
font-size="{FS}" fill="url(#g)">$</text>
  <text x="{FS}" y="{BASE_Y}" font-family="ui-monospace,SFMono-Regular,Menlo,Consolas,monospace" \
font-size="{FS}" font-weight="700" fill="{pal['ink']}" mask="url(#reveal)" \
textLength="{tl:.1f}" lengthAdjust="spacingAndGlyphs">{title}</text>
  <rect y="{BASE_Y - FS + 5}" width="3" height="{FS}" fill="{pal[stops[0]]}">
    <animate attributeName="x" values="{c_vals}" keyTimes="{keytimes}" \
dur="{total:.2f}s" calcMode="discrete" repeatCount="indefinite"/>
    <animate attributeName="opacity" values="1;1;0;0" keyTimes="0;0.5;0.5;1" \
dur="1.05s" repeatCount="indefinite"/>
  </rect>
  <rect x="0" y="{RULE_Y}" width="{W}" height="2" rx="1" fill="url(#g)" opacity="0.45"/>
  <rect x="0" y="{RULE_Y}" width="{LEAD}" height="2" rx="1" fill="{pal[stops[0]]}"/>
</svg>
"""


def main():
    OUT.mkdir(exist_ok=True)
    written = []
    for slug, title, stops in SECTIONS:
        for theme, pal in (("dark", DARK), ("light", LIGHT)):
            path = OUT / f"{slug}-{theme}-{VERSION}.svg"
            path.write_text(banner(title, stops, pal), encoding="utf-8")
            written.append(path.name)
    print(f"wrote {len(written)} banners to {OUT}/")
    for n in written:
        print("  " + n)


if __name__ == "__main__":
    main()
