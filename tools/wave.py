#!/usr/bin/env python3
"""Generate the animated wave section dividers used in README.md.

The filled gradient wave from the design pitch, but generated locally and
actually moving. capsule-render was the original source and is not used:
its `animation=` parameter only affects the caption text, the wave itself is
static, and its shape types ignore a custom colour list and return a default
salmon gradient.

Two filled wave layers drift left at different speeds for parallax. Each path
spans 2x the visible width and carries a whole number of cycles across W, so
translating by exactly -W loops seamlessly with no visible seam. A vertical
mask fades the fill out downward, so it reads as a divider and not a slab.

    python3 tools/wave.py

Bump VERSION on any visual change -- camo caches these hard.
"""

import math
import pathlib

VERSION = "v1"
OUT = pathlib.Path(__file__).resolve().parent.parent / "banners"

W, H = 870, 78
CYCLES = 3          # whole cycles across W -- must stay an integer to loop cleanly
STEP = 5            # sampling interval in px

DARK = ["#22d3ee", "#58a6ff", "#a855f7", "#f472b6"]
LIGHT = ["#0891b2", "#2563eb", "#9333ea", "#db2777"]

# (phase, amplitude, midline, opacity, seconds per loop)
LAYERS = [
    (math.pi * 0.7, 11.0, H * 0.46, 0.34, 19.0),   # back, slower
    (0.0,           14.0, H * 0.34, 1.00, 11.0),   # front
]


def area_path(phase, amp, mid):
    """Filled area under a sine, spanning 2W so it can scroll seamlessly."""
    pts = []
    x = 0
    while x <= 2 * W:
        y = mid + amp * math.sin(2 * math.pi * CYCLES * x / W + phase)
        pts.append(f"{x},{y:.2f}")
        x += STEP
    return "M" + "L".join(pts) + f"L{2*W},{H}L0,{H}Z"


def wave(colors):
    stops = "".join(
        f'<stop offset="{i/(len(colors)-1):.4g}" stop-color="{c}"/>'
        for i, c in enumerate(colors)
    )
    layers = []
    for i, (phase, amp, mid, op, dur) in enumerate(LAYERS):
        layers.append(
            f'  <g opacity="{op}">\n'
            f'    <path d="{area_path(phase, amp, mid)}" fill="url(#c)" mask="url(#m)"/>\n'
            f'    <animateTransform attributeName="transform" type="translate" '
            f'values="0,0;{-W},0" dur="{dur}s" repeatCount="indefinite"/>\n'
            f"  </g>"
        )
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" \
viewBox="0 0 {W} {H}" role="presentation" aria-hidden="true">
  <defs>
    <linearGradient id="c" x1="0" y1="0" x2="1" y2="0" gradientUnits="objectBoundingBox">{stops}</linearGradient>
    <linearGradient id="f" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#fff" stop-opacity="0.95"/>
      <stop offset="0.55" stop-color="#fff" stop-opacity="0.35"/>
      <stop offset="1" stop-color="#fff" stop-opacity="0"/>
    </linearGradient>
    <mask id="m"><rect x="{-W}" y="0" width="{3*W}" height="{H}" fill="url(#f)"/></mask>
  </defs>
{chr(10).join(layers)}
</svg>
"""


def main():
    OUT.mkdir(exist_ok=True)
    for theme, cols in (("dark", DARK), ("light", LIGHT)):
        p = OUT / f"wave-{theme}-{VERSION}.svg"
        p.write_text(wave(cols), encoding="utf-8")
        print(f"wrote {p.name}  ({p.stat().st_size/1024:.1f} KB)")


if __name__ == "__main__":
    main()
