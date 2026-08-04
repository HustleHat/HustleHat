#!/usr/bin/env python3
"""Generate the `$ cat background.md` block used in README.md.

Renders the first Background paragraph as terminal output. The second paragraph
stays real markdown prose -- that keeps the section reflowing on a phone and
readable to a screen reader without leaning on alt text, which matters more here
than anywhere else on the page since almost everything else below the game is
now an image.

Split at the sentence break so the second line stands on its own.

    python3 tools/catblock.py

Bump VERSION on any visual change -- camo caches these hard.
"""

import pathlib
import sys
from xml.sax.saxutils import escape

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from pills import sample  # noqa: E402

VERSION = "v1"
OUT = pathlib.Path(__file__).resolve().parent.parent / "banners"

W = 870
FS, LH = 14, 24
CMD = "cat background.md"
LINES = [
    "Product engineer turned AI & computer vision nerd.",
    "I build cool shit, document it, & help others do the same.",
]

MONO = "ui-monospace,SFMono-Regular,Menlo,Consolas,monospace"
DARK = {"ramp": ["#22d3ee", "#58a6ff", "#a855f7", "#f472b6"], "ink": "#ffffff"}
LIGHT = {"ramp": ["#0891b2", "#2563eb", "#9333ea", "#db2777"], "ink": "#1f2328"}


def block(pal):
    ramp, ink = pal["ramp"], pal["ink"]
    cmd_col = sample(ramp, 0.35)
    parts = [
        f'  <text x="0" y="18" font-family="{MONO}" font-size="{FS}" fill="{ink}">$</text>'
        f'<text x="18" y="18" font-family="{MONO}" font-size="{FS}" font-weight="700" '
        f'fill="{cmd_col}">{escape(CMD)}</text>'
    ]
    y = 18 + LH + 6
    for i, line in enumerate(LINES):
        col = sample(ramp, i / max(len(LINES) - 1, 1))
        parts.append(
            f'  <text x="4" y="{y}" font-family="{MONO}" font-size="{FS}" '
            f'fill="{col}">&#9656;</text>'
            f'<text x="26" y="{y}" font-family="{MONO}" font-size="{FS}" '
            f'fill="{ink}">{escape(line)}</text>'
        )
        y += LH
    h = y - LH + 12
    label = " ".join(LINES)
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{h}" '
            f'viewBox="0 0 {W} {h}" role="img" aria-label="{escape(label)}">\n'
            f"  <title>{escape(label)}</title>\n" + "\n".join(parts) + "\n</svg>\n")


def main():
    OUT.mkdir(exist_ok=True)
    # longest line must fit the canvas or the tail clips off the right edge
    longest = max(len(l) for l in LINES) * FS * 0.6 + 26
    assert longest <= W, f"line overflows: {longest:.0f}px > {W}px"
    for theme, pal in (("dark", DARK), ("light", LIGHT)):
        p = OUT / f"bg-cat-{theme}-{VERSION}.svg"
        p.write_text(block(pal), encoding="utf-8")
        print(f"wrote {p.name}  (widest line {longest:.0f}px of {W}px)")


if __name__ == "__main__":
    main()
