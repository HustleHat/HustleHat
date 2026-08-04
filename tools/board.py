#!/usr/bin/env python3
"""Generate the Currently Building board used in README.md.

Replaces the markdown table. Same emoji, same project names, same focus lines --
plus a stage bar, so a reader can see how far along each one is.

Bar length is derived from STAGE, not a hand-typed percentage. That keeps the
board honest: there is no number to quietly go stale, only a stage to move.

    python3 tools/board.py

Bump VERSION on any visual change -- camo caches these hard.
"""

import pathlib
from xml.sax.saxutils import escape

VERSION = "v2"
OUT = pathlib.Path(__file__).resolve().parent.parent / "banners"

W = 870
ROW = 32
PAD_TOP = 8

# X_STAGE leaves room for the longest label ("PROTOTYPE", ~61px at FS_STAGE)
# without running past W. Widen a stage name and this is the number to move.
X_EMOJI, X_NAME, X_FOCUS, X_BAR, X_STAGE = 0, 30, 200, 598, 790
BAR_W, BAR_H = 175, 7

FS_NAME, FS_FOCUS, FS_STAGE, FS_EMOJI = 14, 13, 10.5, 15
MONO = "ui-monospace,SFMono-Regular,Menlo,Consolas,monospace"
EMOJI_FONT = ('"Apple Color Emoji","Segoe UI Emoji","Noto Color Emoji",'
              "ui-monospace,Menlo,monospace")

# Five stages, evenly spaced. The bar is the stage -- nothing else to maintain.
STAGES = {
    "RESEARCH":  (0.20, "pk"),
    "PROTOTYPE": (0.40, "pu"),
    "ALPHA":     (0.60, "bl"),
    "BETA":      (0.80, "cy"),
    "LIVE":      (1.00, "cy"),
}

DARK = {"cy": "#22d3ee", "bl": "#58a6ff", "pu": "#a855f7", "pk": "#f472b6",
        "name": "#e6edf3", "focus": "#8b949e", "track": "#21262d"}
LIGHT = {"cy": "#0891b2", "bl": "#2563eb", "pu": "#9333ea", "pk": "#db2777",
         "name": "#1f2328", "focus": "#59636e", "track": "#d1d9e0"}

# Text is verbatim from the README table. Stages are Chris's call -- see notes.
PROJECTS = [
    ("\U0001F9E0", "Noble",      "Open-source language model, built from scratch", "PROTOTYPE"),
    ("⚙️", "I.R.O.N.",  "Autonomous multi-agent operations OS",           "ALPHA"),
    ("\U0001F4E1", "SignalHunt", "Market opportunity intelligence engine",         "PROTOTYPE"),
    ("\U0001F3AF", "ProspectIQ", "Automated prospect discovery and targeting",     "PROTOTYPE"),
    ("\U0001F40D", "Skulpty",    "AI asset generation + agent framework",          "BETA"),
    ("\U0001F335", "DreamBay",   "Multi-dementional digital asset platform",       "LIVE"),
    ("\U0001F3CF", "Want3d",     "Open-world survival shooter (UE5)",              "ALPHA"),
]


def row(i, emoji, name, focus, stage, pal):
    y = PAD_TOP + i * ROW
    frac, key = STAGES[stage]
    col = pal[key]
    fill = BAR_W * frac
    # Absolute x positions, so platform emoji width never shifts the name.
    return f"""  <g transform="translate(0,{y})">
    <text x="{X_EMOJI}" y="14" font-family={EMOJI_FONT!r} font-size="{FS_EMOJI}">{escape(emoji)}</text>
    <text x="{X_NAME}" y="14" font-family="{MONO}" font-size="{FS_NAME}" font-weight="700" \
fill="{pal['name']}">{escape(name)}</text>
    <text x="{X_FOCUS}" y="14" font-family="{MONO}" font-size="{FS_FOCUS}" fill="{pal['focus']}" \
textLength="{len(focus) * FS_FOCUS * 0.6:.1f}" lengthAdjust="spacing">{escape(focus)}</text>
    <rect x="{X_BAR}" y="4" width="{BAR_W}" height="{BAR_H}" rx="{BAR_H/2}" fill="{pal['track']}"/>
    <rect x="{X_BAR}" y="4" width="{fill:.1f}" height="{BAR_H}" rx="{BAR_H/2}" fill="{col}"/>
    <text x="{X_STAGE}" y="13" font-family="{MONO}" font-size="{FS_STAGE}" fill="{col}" \
letter-spacing="0.5">{stage}</text>
  </g>"""


def board(pal):
    h = PAD_TOP * 2 + len(PROJECTS) * ROW
    rows = "\n".join(row(i, *p, pal) for i, p in enumerate(PROJECTS))
    label = ", ".join(f"{n} ({s.lower()}) - {f}" for _, n, f, s in PROJECTS)
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{h}" \
viewBox="0 0 {W} {h}" role="img" aria-label="Currently building: {escape(label)}">
  <title>Currently Building</title>
{rows}
</svg>
"""


def main():
    OUT.mkdir(exist_ok=True)
    for theme, pal in (("dark", DARK), ("light", LIGHT)):
        p = OUT / f"building-board-{theme}-{VERSION}.svg"
        p.write_text(board(pal), encoding="utf-8")
        print("wrote", p.name)


if __name__ == "__main__":
    main()
