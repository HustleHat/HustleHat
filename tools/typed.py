#!/usr/bin/env python3
"""Generate the typed Core Thesis line used in README.md.

Types the thesis out character by character, holds, erases, loops. Generated
locally rather than pulled from readme-typing-svg, so it uses the same palette
and the same mono stack as everything else here.

How the typing works: the text is drawn once, in full, behind a mask. The mask
is a rect whose width steps one character at a time with calcMode="discrete".
Because the text is pinned with textLength, one character is exactly CW wide,
so the mask edge always lands on a character boundary -- no half-glyphs.

    python3 tools/typed.py

Bump VERSION on any visual change -- camo caches these hard.
"""

import pathlib
from xml.sax.saxutils import escape

VERSION = "v1"
OUT = pathlib.Path(__file__).resolve().parent.parent / "banners"

TEXT = "Building digital experiences where technology fades and humanity deepens."

W, H = 870, 46
# FS must satisfy len(TEXT)*FS*0.6 + cursor <= W or the tail clips off the
# canvas. At 73 chars that caps FS at ~19.7; lengthen TEXT and this must drop.
FS = 19
CW = FS * 0.6
BASE_Y = 30
X = 0

TYPE_PER_CHAR = 0.058
ERASE_PER_CHAR = 0.018
HOLD = 5.0
GAP = 0.7

DARK = {"stops": ["#22d3ee", "#58a6ff", "#a855f7", "#f472b6"], "cursor": "#58a6ff"}
LIGHT = {"stops": ["#0891b2", "#2563eb", "#9333ea", "#db2777"], "cursor": "#2563eb"}


def timeline():
    """(width_values, cursor_x_values, keyTimes, total_seconds) for one loop."""
    n = len(TEXT)
    t_type, t_erase = n * TYPE_PER_CHAR, n * ERASE_PER_CHAR
    total = t_type + HOLD + t_erase + GAP

    marks, widths = [], []

    for k in range(n + 1):                      # typing
        marks.append(k * TYPE_PER_CHAR)
        widths.append(k)
    marks.append(t_type + HOLD)                 # hold at full
    widths.append(n)
    for k in range(n, -1, -1):                  # erasing
        marks.append(t_type + HOLD + (n - k) * ERASE_PER_CHAR)
        widths.append(k)
    marks.append(total)                         # empty gap before the loop
    widths.append(0)

    keytimes = [f"{m/total:.5f}" for m in marks]
    w_vals = ";".join(f"{k*CW:.1f}" for k in widths)
    c_vals = ";".join(f"{X + k*CW:.1f}" for k in widths)
    return w_vals, c_vals, ";".join(keytimes), total


def typed(pal):
    w_vals, c_vals, keytimes, total = timeline()
    tl = len(TEXT) * CW
    stops = "".join(
        f'<stop offset="{i/(len(pal["stops"])-1):.4g}" stop-color="{c}"/>'
        for i, c in enumerate(pal["stops"])
    )
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" \
viewBox="0 0 {W} {H}" role="img" aria-label="{escape(TEXT)}">
  <title>{escape(TEXT)}</title>
  <defs>
    <linearGradient id="g" x1="0" y1="0" x2="1" y2="0">{stops}</linearGradient>
    <mask id="reveal">
      <rect x="{X}" y="0" width="0" height="{H}" fill="#fff">
        <animate attributeName="width" values="{w_vals}" keyTimes="{keytimes}" \
dur="{total:.2f}s" calcMode="discrete" repeatCount="indefinite"/>
      </rect>
    </mask>
  </defs>
  <text x="{X}" y="{BASE_Y}" font-family="ui-monospace,SFMono-Regular,Menlo,Consolas,monospace" \
font-size="{FS}" font-weight="600" fill="url(#g)" mask="url(#reveal)" \
textLength="{tl:.1f}" lengthAdjust="spacingAndGlyphs">{escape(TEXT)}</text>
  <rect y="{BASE_Y - FS + 3}" width="2.5" height="{FS}" fill="{pal['cursor']}">
    <animate attributeName="x" values="{c_vals}" keyTimes="{keytimes}" \
dur="{total:.2f}s" calcMode="discrete" repeatCount="indefinite"/>
    <animate attributeName="opacity" values="1;1;0;0" keyTimes="0;0.5;0.5;1" \
dur="1.05s" repeatCount="indefinite"/>
  </rect>
</svg>
"""


def main():
    OUT.mkdir(exist_ok=True)
    _, _, _, total = timeline()
    for theme, pal in (("dark", DARK), ("light", LIGHT)):
        p = OUT / f"thesis-{theme}-{VERSION}.svg"
        p.write_text(typed(pal), encoding="utf-8")
        print(f"wrote {p.name}  ({p.stat().st_size/1024:.1f} KB)")
    print(f"loop: {total:.2f}s  ({len(TEXT)} chars)")


if __name__ == "__main__":
    main()
