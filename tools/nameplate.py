#!/usr/bin/env python3
"""Generate the typed nameplate that replaces the `# Christopher M. Noble` H1.

A gradient `$` prompt, then the name typing out with a cursor -- the same
mechanism as the Core Thesis line, so the top of the page and the thesis speak
the same language as the section banners.

The `$` is NOT masked. It is the prompt: it stays put while the name types.

As with the thesis, the loop STARTS and ENDS fully typed. Anything that renders
the SVG without running SMIL freezes at t=0, and a name that renders as a bare
cursor is worse than no animation at all.

    python3 tools/nameplate.py

Bump VERSION on any visual change -- camo caches these hard.
"""

import pathlib
from xml.sax.saxutils import escape

VERSION = "v1"
OUT = pathlib.Path(__file__).resolve().parent.parent / "banners"

NAME = "Christopher M. Noble"

W, H = 870, 60
FS = 36
CW = FS * 0.6
BASE_Y = 42
X_PROMPT = 0
X_NAME = FS + 10          # room for the "$" plus a space

TYPE_PER_CHAR = 0.075
ERASE_PER_CHAR = 0.025
HOLD = 5.0
GAP = 0.7

MONO = "ui-monospace,SFMono-Regular,Menlo,Consolas,monospace"
DARK = {"stops": ["#22d3ee", "#58a6ff", "#a855f7", "#f472b6"],
        "ink": "#ffffff", "cursor": "#58a6ff"}
LIGHT = {"stops": ["#0891b2", "#2563eb", "#9333ea", "#db2777"],
         "ink": "#1f2328", "cursor": "#2563eb"}


def timeline():
    n = len(NAME)
    t_type, t_erase = n * TYPE_PER_CHAR, n * ERASE_PER_CHAR
    total = HOLD + t_erase + GAP + t_type

    marks, widths = [0.0], [n]                  # t=0: the whole name
    marks.append(HOLD)
    widths.append(n)
    for k in range(n, -1, -1):                  # erase
        marks.append(HOLD + (n - k) * ERASE_PER_CHAR)
        widths.append(k)
    marks.append(HOLD + t_erase + GAP)          # empty beat
    widths.append(0)
    for k in range(n + 1):                      # retype back to full
        marks.append(HOLD + t_erase + GAP + k * TYPE_PER_CHAR)
        widths.append(k)

    keytimes = ";".join(f"{m/total:.5f}" for m in marks)
    w_vals = ";".join(f"{k*CW:.1f}" for k in widths)
    c_vals = ";".join(f"{X_NAME + k*CW:.1f}" for k in widths)
    return w_vals, c_vals, keytimes, total


def plate(pal):
    w_vals, c_vals, keytimes, total = timeline()
    tl = len(NAME) * CW
    stops = "".join(
        f'<stop offset="{i/(len(pal["stops"])-1):.4g}" stop-color="{c}"/>'
        for i, c in enumerate(pal["stops"])
    )
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" \
viewBox="0 0 {W} {H}" role="img" aria-label="{escape(NAME)}">
  <title>{escape(NAME)}</title>
  <defs>
    <linearGradient id="g" x1="0" y1="0" x2="1" y2="0">{stops}</linearGradient>
    <mask id="reveal">
      <rect x="{X_NAME}" y="0" width="0" height="{H}" fill="#fff">
        <animate attributeName="width" values="{w_vals}" keyTimes="{keytimes}" \
dur="{total:.2f}s" calcMode="discrete" repeatCount="indefinite"/>
      </rect>
    </mask>
  </defs>
  <text x="{X_PROMPT}" y="{BASE_Y}" font-family="{MONO}" font-size="{FS}" \
fill="url(#g)">$</text>
  <text x="{X_NAME}" y="{BASE_Y}" font-family="{MONO}" font-size="{FS}" \
font-weight="700" fill="{pal['ink']}" mask="url(#reveal)" \
textLength="{tl:.1f}" lengthAdjust="spacingAndGlyphs">{escape(NAME)}</text>
  <rect y="{BASE_Y - FS + 6}" width="3.5" height="{FS}" fill="{pal['cursor']}">
    <animate attributeName="x" values="{c_vals}" keyTimes="{keytimes}" \
dur="{total:.2f}s" calcMode="discrete" repeatCount="indefinite"/>
    <animate attributeName="opacity" values="1;1;0;0" keyTimes="0;0.5;0.5;1" \
dur="1.05s" repeatCount="indefinite"/>
  </rect>
</svg>
"""


def main():
    OUT.mkdir(exist_ok=True)
    end = X_NAME + len(NAME) * CW + 4
    assert end <= W, f"nameplate overflows: {end:.0f}px > {W}px"
    _, _, _, total = timeline()
    for theme, pal in (("dark", DARK), ("light", LIGHT)):
        p = OUT / f"nameplate-{theme}-{VERSION}.svg"
        p.write_text(plate(pal), encoding="utf-8")
        print(f"wrote {p.name}")
    print(f"loop {total:.2f}s  ·  ends at {end:.0f}px of {W}px")


if __name__ == "__main__":
    main()
