#!/usr/bin/env python3
"""Generate the line that opens README.md.

`$ whoami` -- the page below it is the answer. It makes no claim, so it does not
compete with the Core Thesis section further down, and it completes the terminal
conceit the rest of the page already runs on.

Same mechanism as the section banners: a gradient `$` prompt with the text
typing behind a mask, at the same size, advance width and prompt offset, so it
reads as the first header rather than a separate hero.

Loop STARTS and ENDS fully typed -- anything that renders the SVG without
running SMIL freezes at t=0, and a bare prompt with no command is worse than no
animation at all.

    python3 tools/intro.py

Bump VERSION on any visual change -- camo caches these hard.
"""

import pathlib
from xml.sax.saxutils import escape

VERSION = "v1"
OUT = pathlib.Path(__file__).resolve().parent.parent / "banners"

TEXT = "whoami"

# Matched to tools/banners.py -- same size, same advance width, same offset.
W, H = 870, 52
FS = 26
CW = FS * 0.62
X = FS                      # text starts one glyph past the "$"
Y = 34

TYPE_PER_CHAR = 0.075
ERASE_PER_CHAR = 0.025
HOLD = 5.0
GAP = 0.7

MONO = "ui-monospace,SFMono-Regular,Menlo,Consolas,monospace"
DARK = {"stops": ["#22d3ee", "#58a6ff", "#a855f7", "#f472b6"],
        "ink": "#ffffff", "cursor": "#58a6ff"}
LIGHT = {"stops": ["#0891b2", "#2563eb", "#9333ea", "#db2777"],
         "ink": "#1f2328", "cursor": "#2563eb"}

N = len(TEXT)


def timeline():
    t_type, t_erase = N * TYPE_PER_CHAR, N * ERASE_PER_CHAR
    total = HOLD + t_erase + GAP + t_type

    marks, prog = [0.0], [N]                    # t=0: the whole command
    marks.append(HOLD)
    prog.append(N)
    for k in range(N, -1, -1):                  # erase
        marks.append(HOLD + (N - k) * ERASE_PER_CHAR)
        prog.append(k)
    marks.append(HOLD + t_erase + GAP)          # empty beat
    prog.append(0)
    for k in range(N + 1):                      # retype back to full
        marks.append(HOLD + t_erase + GAP + k * TYPE_PER_CHAR)
        prog.append(k)

    return (";".join(f"{p*CW:.1f}" for p in prog),
            ";".join(f"{X + p*CW:.1f}" for p in prog),
            ";".join(f"{m/total:.5f}" for m in marks),
            total)


def build(pal):
    w_vals, c_vals, kt, total = timeline()
    stops = "".join(
        f'<stop offset="{i/(len(pal["stops"])-1):.4g}" stop-color="{c}"/>'
        for i, c in enumerate(pal["stops"]))
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" \
viewBox="0 0 {W} {H}" role="img" aria-label="{escape(TEXT)}">
  <title>$ {escape(TEXT)}</title>
  <defs>
    <linearGradient id="g" x1="0" y1="0" x2="1" y2="0">{stops}</linearGradient>
    <mask id="reveal">
      <rect x="{X}" y="0" width="0" height="{H}" fill="#fff">
        <animate attributeName="width" values="{w_vals}" keyTimes="{kt}" \
dur="{total:.2f}s" calcMode="discrete" repeatCount="indefinite"/>
      </rect>
    </mask>
  </defs>
  <text x="0" y="{Y}" font-family="{MONO}" font-size="{FS}" fill="url(#g)">$</text>
  <text x="{X}" y="{Y}" font-family="{MONO}" font-size="{FS}" font-weight="700" \
fill="{pal['ink']}" mask="url(#reveal)" textLength="{N*CW:.1f}" \
lengthAdjust="spacingAndGlyphs">{escape(TEXT)}</text>
  <rect y="{Y - FS + 5}" width="3" height="{FS}" fill="{pal['cursor']}">
    <animate attributeName="x" values="{c_vals}" keyTimes="{kt}" \
dur="{total:.2f}s" calcMode="discrete" repeatCount="indefinite"/>
    <animate attributeName="opacity" values="1;1;0;0" keyTimes="0;0.5;0.5;1" \
dur="1.05s" repeatCount="indefinite"/>
  </rect>
</svg>
"""


def main():
    OUT.mkdir(exist_ok=True)
    end = X + N * CW + 3
    assert end <= W, f"intro overflows: {end:.0f}px > {W}px"
    _, _, _, total = timeline()
    for theme, pal in (("dark", DARK), ("light", LIGHT)):
        p = OUT / f"intro-{theme}-{VERSION}.svg"
        p.write_text(build(pal), encoding="utf-8")
        print(f"wrote {p.name}")
    print(f"$ {TEXT} · FS {FS} · ends {end:.0f}px of {W}px · loop {total:.2f}s")


if __name__ == "__main__":
    main()
