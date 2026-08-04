#!/usr/bin/env python3
"""Generate the typed quote that opens README.md.

Same mechanism as tools/nameplate.py: a gradient `$` prompt with the text
typing behind a mask.

The quote runs on ONE line, which sets the type size rather than the other way
round. 61 characters plus the prompt must clear 870px, so FS is capped at about
22 -- see the assert in main(). Lengthen the quote and that cap drops; the
assert fails loudly instead of letting the tail clip off the canvas.

Attribution sits below, right-aligned to the end of the quote, and only appears
once the line is fully typed.

Loop STARTS and ENDS fully typed, so a frozen render -- backgrounded tab,
reduced motion, static rasteriser -- shows the whole quote rather than a bare
prompt.

    python3 tools/quote.py

Bump VERSION on any visual change -- camo caches these hard.
"""

import pathlib
from xml.sax.saxutils import escape

VERSION = "v2"
OUT = pathlib.Path(__file__).resolve().parent.parent / "banners"

QUOTE = "A little nonsense, now and then, is relished by the wisest men"
ATTRIB = "— Willy Wonka"

W, H = 870, 76
FS = 21.5                   # capped by the one-line rule, see main()
CW = FS * 0.62
X = FS                      # text starts one glyph past the "$"
Y = 32

AT_FS = 13
AT_CW = AT_FS * 0.62
AT_Y = 60

TYPE_PER_CHAR = 0.06
ERASE_PER_CHAR = 0.02
HOLD = 5.0
GAP = 0.7

MONO = "ui-monospace,SFMono-Regular,Menlo,Consolas,monospace"
DARK = {"stops": ["#22d3ee", "#58a6ff", "#a855f7", "#f472b6"],
        "ink": "#ffffff", "dim": "#8b949e", "cursor": "#58a6ff"}
LIGHT = {"stops": ["#0891b2", "#2563eb", "#9333ea", "#db2777"],
         "ink": "#1f2328", "dim": "#6a737d", "cursor": "#2563eb"}

N = len(QUOTE)


def timeline():
    t_type, t_erase = N * TYPE_PER_CHAR, N * ERASE_PER_CHAR
    total = HOLD + t_erase + GAP + t_type

    marks, prog = [0.0], [N]                    # t=0: the whole quote
    marks.append(HOLD)
    prog.append(N)
    for k in range(N, -1, -1):
        marks.append(HOLD + (N - k) * ERASE_PER_CHAR)
        prog.append(k)
    marks.append(HOLD + t_erase + GAP)
    prog.append(0)
    for k in range(N + 1):
        marks.append(HOLD + t_erase + GAP + k * TYPE_PER_CHAR)
        prog.append(k)

    return (";".join(f"{p*CW:.1f}" for p in prog),
            ";".join(f"{X + p*CW:.1f}" for p in prog),
            ";".join("1" if p >= N else "0" for p in prog),
            ";".join(f"{m/total:.5f}" for m in marks),
            total)


def build(pal):
    w_vals, c_vals, at_vals, kt, total = timeline()
    stops = "".join(
        f'<stop offset="{i/(len(pal["stops"])-1):.4g}" stop-color="{c}"/>'
        for i, c in enumerate(pal["stops"]))
    at_x = X + N * CW - len(ATTRIB) * AT_CW       # right-align under the quote
    full = f"{QUOTE} {ATTRIB}"
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" \
viewBox="0 0 {W} {H}" role="img" aria-label="{escape(full)}">
  <title>{escape(full)}</title>
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
lengthAdjust="spacingAndGlyphs">{escape(QUOTE)}</text>
  <text x="{at_x:.1f}" y="{AT_Y}" font-family="{MONO}" font-size="{AT_FS}" \
fill="{pal['dim']}" textLength="{len(ATTRIB)*AT_CW:.1f}" \
lengthAdjust="spacingAndGlyphs">{escape(ATTRIB)}
    <animate attributeName="opacity" values="{at_vals}" keyTimes="{kt}" \
dur="{total:.2f}s" calcMode="discrete" repeatCount="indefinite"/>
  </text>
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
    end = X + N * CW + 3                          # + cursor
    assert end <= W, (f"quote overflows on one line: {end:.0f}px > {W}px. "
                      f"Drop FS to {(W - 4) / (1 + N * 0.62):.1f} or shorter.")
    _, _, _, _, total = timeline()
    for theme, pal in (("dark", DARK), ("light", LIGHT)):
        p = OUT / f"quote-{theme}-{VERSION}.svg"
        p.write_text(build(pal), encoding="utf-8")
        print(f"wrote {p.name}")
    print(f"{N} chars on one line at FS {FS} · ends {end:.0f}px of {W}px · "
          f"loop {total:.2f}s")


if __name__ == "__main__":
    main()
