#!/usr/bin/env python3
"""Generate the banner with an object-detection overlay.

The profile already signals AI (the braille brain in noblefetch) and gaming (the
galaga contribution graph) but had nothing for computer vision. This puts
detection boxes over the existing lighthouse photo rather than replacing it.

A scan line sweeps left to right on a loop; each box and label brightens as the
line crosses it, so the overlay reads as inference running rather than as a
static diagram. Boxes are visible at t=0, so a frozen render is still the photo
plus its annotations -- never a bare photo waiting for an animation.

The confidence values are DECORATIVE. No model produced them; they are part of
the visual idiom, the same way `$ cat background.md` is not a real shell.

Source photo lives beside this script's output as a base64 JPEG so the SVG stays
self-contained -- an SVG loaded through <img> cannot fetch external resources.

    python3 tools/vision.py

Bump VERSION on any visual change -- camo caches these hard.
"""

import base64
import pathlib

VERSION = "v1"
ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "banners"
SRC = ROOT / "banners" / "banner-1200.jpg"

W, H = 1200, 343
SCAN = 5.0          # seconds for one left-to-right pass

MONO = "ui-monospace,SFMono-Regular,Menlo,Consolas,monospace"
FS = 11
CW = FS * 0.6

# (x, y, w, h, label, confidence, colour)
DETECTIONS = [
    (362, 120, 50, 150, "lighthouse", "0.97", "#22d3ee"),
    (784, 90, 52, 165, "lighthouse", "0.94", "#58a6ff"),
    (542, 42, 60, 66, "moon", "0.91", "#f472b6"),
    (540, 176, 120, 66, "structure", "0.86", "#a855f7"),
]


def box(x, y, w, h, label, conf, col):
    cx = x + w / 2
    p = max(0.02, min(0.98, cx / W))          # when the scan line crosses it
    pulse = (f'<animate attributeName="opacity" values="0.55;1;0.55" '
             f'keyTimes="0;{p:.3f};1" dur="{SCAN}s" repeatCount="indefinite"/>')
    text = f"{label} {conf}"
    lw = len(text) * CW + 10
    ly = y - 16 if y > 24 else y + h + 4
    tick = 9                                   # corner tick length
    return f"""  <g opacity="0.55">{pulse}
    <rect x="{x}" y="{y}" width="{w}" height="{h}" fill="none"
          stroke="{col}" stroke-width="1.6" rx="2"/>
    <path d="M{x},{y+tick}V{y}H{x+tick} M{x+w-tick},{y}H{x+w}V{y+tick}
             M{x+w},{y+h-tick}V{y+h}H{x+w-tick} M{x+tick},{y+h}H{x}V{y+h-tick}"
          fill="none" stroke="{col}" stroke-width="2.6" stroke-linecap="square"/>
    <rect x="{x}" y="{ly}" width="{lw:.1f}" height="14" rx="2" fill="{col}"/>
    <text x="{x + 5}" y="{ly + 10.5}" font-family="{MONO}" font-size="{FS}"
          font-weight="700" fill="#0d1117">{text}</text>
  </g>"""


def build(b64):
    boxes = "\n".join(box(*d) for d in DETECTIONS)
    c = 26      # corner bracket length on the frame
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" \
viewBox="0 0 {W} {H}" role="img" \
aria-label="Twin lighthouses at dusk under a crescent moon, with object-detection \
boxes labelling two lighthouses, the moon, and a structure">
  <title>Navesink Twin Lights &#183; detection overlay</title>
  <defs>
    <linearGradient id="scan" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0" stop-color="#22d3ee" stop-opacity="0"/>
      <stop offset="0.5" stop-color="#22d3ee" stop-opacity="0.85"/>
      <stop offset="1" stop-color="#22d3ee" stop-opacity="0"/>
    </linearGradient>
  </defs>
  <image href="data:image/jpeg;base64,{b64}" x="0" y="0" width="{W}" height="{H}"/>
{boxes}
  <rect width="38" height="{H}" fill="url(#scan)" opacity="0.32">
    <animate attributeName="x" values="{-38};{W}" dur="{SCAN}s" repeatCount="indefinite"/>
  </rect>
  <path d="M0,{c}V0H{c} M{W-c},0H{W}V{c} M{W},{H-c}V{H}H{W-c} M{c},{H}H0V{H-c}"
        fill="none" stroke="#ffffff" stroke-opacity="0.45" stroke-width="2"/>
  <text x="14" y="{H-13}" font-family="{MONO}" font-size="{FS}" fill="#ffffff"
        opacity="0.5">vision.detect &#183; {len(DETECTIONS)} objects</text>
</svg>
"""


def main():
    assert SRC.exists(), f"missing {SRC} -- put the 1200px jpeg there first"
    b64 = base64.b64encode(SRC.read_bytes()).decode()
    p = OUT / f"banner-vision-{VERSION}.svg"
    p.write_text(build(b64), encoding="utf-8")
    print(f"wrote {p.name}  ({p.stat().st_size/1024:.0f} KB, "
          f"{len(DETECTIONS)} detections, {SCAN}s scan)")


if __name__ == "__main__":
    main()
