#!/usr/bin/env python3
"""Generate the Core Thesis line with a travelling specular glint.

Two copies of the same sentence sit on top of each other: a legible base, and a
full-gradient copy revealed through a moving window mask. A soft-edged band
crosses the line, then waits off-screen before the next pass, so it reads as a
periodic glint rather than constant motion.

The base copy is deliberately readable on its own. Anything that renders the
SVG without running SMIL freezes at t=0 with the band off-screen left -- so the
fallback state is the plain sentence, not a dim smear. Same rule as the typed
nameplate: if the element carries meaning, frame zero has to be the readable one.

    python3 tools/sweep.py

Bump VERSION on any visual change -- camo caches these hard.
"""

import pathlib
from xml.sax.saxutils import escape

VERSION = "v1"
OUT = pathlib.Path(__file__).resolve().parent.parent / "banners"

TEXT = "Building digital experiences where technology fades and humanity deepens."

W, H = 870, 46
FS = 19
CW = FS * 0.6
BASE_Y = 30

BAND = 280          # width of the glint
CYCLE = 7.0         # seconds per pass, including the rest
CROSS = 0.45        # fraction of the cycle the band is actually moving

MONO = "ui-monospace,SFMono-Regular,Menlo,Consolas,monospace"
DARK = {"stops": ["#22d3ee", "#58a6ff", "#a855f7", "#f472b6"],
        "base": "#ffffff", "base_op": 0.72}
LIGHT = {"stops": ["#0891b2", "#2563eb", "#9333ea", "#db2777"],
         "base": "#1f2328", "base_op": 0.78}


def build(pal):
    tl = len(TEXT) * CW
    stops = "".join(
        f'<stop offset="{i/(len(pal["stops"])-1):.4g}" stop-color="{c}"/>'
        for i, c in enumerate(pal["stops"])
    )
    shared = (f'font-family="{MONO}" font-size="{FS}" font-weight="600" '
              f'textLength="{tl:.1f}" lengthAdjust="spacingAndGlyphs"')
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" \
viewBox="0 0 {W} {H}" role="img" aria-label="{escape(TEXT)}">
  <title>{escape(TEXT)}</title>
  <defs>
    <linearGradient id="g" x1="0" y1="0" x2="1" y2="0">{stops}</linearGradient>
    <linearGradient id="win" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0" stop-color="#000000"/>
      <stop offset="0.5" stop-color="#ffffff"/>
      <stop offset="1" stop-color="#000000"/>
    </linearGradient>
    <mask id="m">
      <rect y="0" width="{BAND}" height="{H}" fill="url(#win)">
        <animate attributeName="x" values="{-BAND};{W};{W}" \
keyTimes="0;{CROSS};1" dur="{CYCLE}s" repeatCount="indefinite"/>
      </rect>
    </mask>
  </defs>
  <text x="0" y="{BASE_Y}" {shared} fill="{pal['base']}" \
opacity="{pal['base_op']}">{escape(TEXT)}</text>
  <text x="0" y="{BASE_Y}" {shared} fill="url(#g)" mask="url(#m)">{escape(TEXT)}</text>
</svg>
"""


def main():
    OUT.mkdir(exist_ok=True)
    end = len(TEXT) * CW
    assert end <= W, f"line overflows: {end:.0f}px > {W}px"
    for theme, pal in (("dark", DARK), ("light", LIGHT)):
        p = OUT / f"thesis-sweep-{theme}-{VERSION}.svg"
        p.write_text(build(pal), encoding="utf-8")
        print(f"wrote {p.name}")
    print(f"line {end:.0f}px of {W}px  ·  glint crosses in "
          f"{CYCLE*CROSS:.1f}s, rests {CYCLE*(1-CROSS):.1f}s")


if __name__ == "__main__":
    main()
