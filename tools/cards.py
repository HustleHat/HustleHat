#!/usr/bin/env python3
"""Generate the What I Do card grid used in README.md.

A 2 x 3 grid replacing the six pill rows. Roughly 200px shorter, because the
long AI/ML bullets wrap inside their card instead of dictating the width of the
whole section.

Discipline text and bullets are verbatim, bold spans included. The data lives in
tools/pills.py so both treatments read from one source -- switching back to
pills is `python3 tools/pills.py` and a README swap, with no risk of the two
drifting apart.

    python3 tools/cards.py

Bump VERSION on any visual change -- camo caches these hard.
"""

import pathlib
import sys
from xml.sax.saxutils import escape

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from pills import DISCIPLINES, lerp_hex, sample  # noqa: E402

VERSION = "v1"
OUT = pathlib.Path(__file__).resolve().parent.parent / "banners"

W = 870
COLS, GAP, PAD = 2, 16, 15
CARD_W = (W - GAP * (COLS - 1)) / COLS
FS, LH = 11, 16
HEAD_FS, HEAD_Y, RULE_Y = 13, 26, 36
CHARS = int((CARD_W - PAD * 2 - 12) / (FS * 0.6))

MONO = "ui-monospace,SFMono-Regular,Menlo,Consolas,monospace"
EMOJI_FONT = ('"Apple Color Emoji","Segoe UI Emoji","Noto Color Emoji",'
              "ui-monospace,Menlo,monospace")

DARK_RAMP = ["#22d3ee", "#58a6ff", "#a855f7", "#f472b6"]
LIGHT_RAMP = ["#0891b2", "#2563eb", "#9333ea", "#db2777"]
# Body text is plain white on dark, matching the pill treatment it replaces.
DARK_INK = {"body": "#ffffff", "rule": "#21262d", "fill": 0.05, "stroke": 0.30}
LIGHT_INK = {"body": "#1f2328", "rule": "#d1d9e0", "fill": 0.06, "stroke": 0.32}


def to_chars(bullet):
    """[(char, is_bold)] with the ** markers consumed."""
    out, bold, i = [], False, 0
    while i < len(bullet):
        if bullet[i:i + 2] == "**":
            bold, i = not bold, i + 2
            continue
        out.append((bullet[i], bold))
        i += 1
    return out


def wrap(chars, width):
    """Greedy word wrap over [(char, bold)], breaking at spaces."""
    lines, cur = [], []
    for ch in chars:
        cur.append(ch)
        if len(cur) > width:
            cut = max((i for i, c in enumerate(cur) if c[0] == " "), default=len(cur) - 1)
            lines.append(cur[:cut])
            cur = cur[cut + 1:]
    if cur:
        lines.append(cur)
    return lines


def tspans(line):
    runs = []
    for ch, bold in line:
        if runs and runs[-1][1] == bold:
            runs[-1][0] += ch
        else:
            runs.append([ch, bold])
    return "".join(
        f'<tspan font-weight="700">{escape(t)}</tspan>' if b else escape(t)
        for t, b in runs
    )


def build(ramp, ink):
    wrapped = [[wrap(to_chars(b), CHARS) for b in d[3]] for d in DISCIPLINES]
    # One uniform card height, so rows line up rather than stepping.
    tallest = max(sum(len(w) for w in card) for card in wrapped)
    card_h = RULE_Y + 18 + tallest * LH + len(DISCIPLINES[0][3]) * 5 + PAD

    parts = []
    for i, (emoji, name, slug, _) in enumerate(DISCIPLINES):
        col = sample(ramp, i / (len(DISCIPLINES) - 1))
        cx = (i % COLS) * (CARD_W + GAP)
        cy = (i // COLS) * (card_h + GAP)
        inner = [
            f'    <rect width="{CARD_W:.1f}" height="{card_h}" rx="7" fill="{col}" '
            f'fill-opacity="{ink["fill"]}" stroke="{col}" stroke-opacity="{ink["stroke"]}"/>',
            f'    <text x="{PAD}" y="{HEAD_Y}" font-family={EMOJI_FONT!r} '
            f'font-size="14">{escape(emoji)}</text>',
            f'    <text x="{PAD + 22}" y="{HEAD_Y}" font-family="{MONO}" font-size="{HEAD_FS}" '
            f'font-weight="700" fill="{col}">{escape(name)}</text>',
            f'    <rect x="{PAD}" y="{RULE_Y}" width="{CARD_W - PAD * 2:.1f}" height="1" '
            f'fill="{ink["rule"]}"/>',
        ]
        ty = RULE_Y + 18
        for wlines in wrapped[i]:
            for j, ln in enumerate(wlines):
                if j == 0:
                    inner.append(
                        f'    <text x="{PAD}" y="{ty}" font-family="{MONO}" font-size="{FS}" '
                        f'fill="{col}">&#183;</text>'
                    )
                inner.append(
                    f'    <text x="{PAD + 12}" y="{ty}" font-family="{MONO}" font-size="{FS}" '
                    f'fill="{ink["body"]}">{tspans(ln)}</text>'
                )
                ty += LH
            ty += 5
        parts.append(f'  <g transform="translate({cx:.1f},{cy})">\n'
                     + "\n".join(inner) + "\n  </g>")

    rows = -(-len(DISCIPLINES) // COLS)
    h = int(rows * (card_h + GAP) - GAP)
    label = " | ".join(
        f"{n}: " + ", ".join(b.replace("**", "") for b in bs)
        for _, n, _, bs in DISCIPLINES
    )
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{h}" '
            f'viewBox="0 0 {W} {h}" role="img" aria-label="{escape(label)}">\n'
            f"  <title>What I Do</title>\n" + "\n".join(parts) + "\n</svg>\n")


def main():
    OUT.mkdir(exist_ok=True)
    for theme, ramp, ink in (("dark", DARK_RAMP, DARK_INK),
                             ("light", LIGHT_RAMP, LIGHT_INK)):
        p = OUT / f"whatido-cards-{theme}-{VERSION}.svg"
        svg = build(ramp, ink)
        p.write_text(svg, encoding="utf-8")
        print(f"wrote {p.name}  height {svg.split('height=')[1].split(chr(34))[1]}px  "
              f"({p.stat().st_size / 1024:.1f} KB)")
    print(f"wrap width: {CHARS} chars per line")


if __name__ == "__main__":
    main()
