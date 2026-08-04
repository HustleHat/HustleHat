#!/usr/bin/env python3
"""Generate the Tech Stack section used in README.md.

Replaces 46 shields.io badges -- one wall, 46 external requests, and no way to
tell the LLM layer from the build tooling -- with one grouped SVG.

Two things this buys beyond looks:

  * 46 requests become 1, and nothing depends on shields.io being up.
  * Four tools worth listing (LlamaIndex, DSPy, vLLM, Weights & Biases) have no
    entry in simple-icons, so shields renders them as blank rectangles. Drawing
    the chips ourselves means the stack is complete rather than complete-minus-
    whatever-has-a-logo.

Groups walk the cyan-to-pink ramp in the same order the section banners do.

    python3 tools/stack.py

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
FS = 11.5
CW = FS * 0.6
PAD_X, CHIP_H = 9, 23
GAP_X, GAP_Y = 5, 6
LABEL_H, GROUP_GAP = 17, 15

MONO = "ui-monospace,SFMono-Regular,Menlo,Consolas,monospace"
DARK_RAMP = ["#22d3ee", "#58a6ff", "#a855f7", "#f472b6"]
LIGHT_RAMP = ["#0891b2", "#2563eb", "#9333ea", "#db2777"]
DARK = {"chip": "#ffffff", "fill": 0.13, "stroke": 0.40}
LIGHT = {"chip": "#1f2328", "fill": 0.10, "stroke": 0.38}

GROUPS = [
    ("LANGUAGES", ["JavaScript", "TypeScript", "Python", "C++", "Rust"]),
    ("AI / ML", ["PyTorch", "HuggingFace", "NumPy", "Pandas", "scikit-learn",
                 "Jupyter", "CUDA", "OpenCV", "Ultralytics"]),
    ("LLM / AGENTS", ["LangChain", "LangGraph", "LlamaIndex", "DSPy", "Ollama",
                      "Anthropic", "vLLM", "Ray", "MLflow", "W&B", "ONNX"]),
    ("WEB", ["React", "Next.js", "Tailwind", "Node.js", "FastAPI", "GraphQL",
             "Solidity", "IPFS"]),
    ("DATA", ["PostgreSQL", "Redis", "Qdrant", "Supabase", "Firebase"]),
    ("INFRA", ["Docker", "Kubernetes", "AWS", "Vercel", "GitHub Actions",
               "Linux", "CMake", "Conda"]),
    ("3D / DESIGN", ["Unreal Engine", "Unity", "Blender", "Figma"]),
]


def build(ramp, ink):
    parts, y = [], 0
    for gi, (name, tools) in enumerate(GROUPS):
        col = sample(ramp, gi / (len(GROUPS) - 1))
        parts.append(
            f'  <text x="0" y="{y + 11}" font-family="{MONO}" font-size="10" '
            f'font-weight="700" letter-spacing="1.6" fill="{col}">{escape(name)}</text>')
        y += LABEL_H
        x = 0.0
        for t in tools:
            tw = len(t) * CW
            w = tw + PAD_X * 2
            if x and x + w > W:                     # wrap within the group
                x, y = 0.0, y + CHIP_H + GAP_Y
            parts.append(
                f'  <g transform="translate({x:.1f},{y})">'
                f'<rect width="{w:.1f}" height="{CHIP_H}" rx="{CHIP_H/2}" fill="{col}" '
                f'fill-opacity="{ink["fill"]}" stroke="{col}" '
                f'stroke-opacity="{ink["stroke"]}"/>'
                f'<text x="{PAD_X}" y="15.5" font-family="{MONO}" font-size="{FS}" '
                f'fill="{ink["chip"]}" textLength="{tw:.1f}" '
                f'lengthAdjust="spacingAndGlyphs">{escape(t)}</text></g>')
            x += w + GAP_X
        y += CHIP_H + GROUP_GAP
    h = y - GROUP_GAP + 4
    label = " | ".join(f"{g}: " + ", ".join(t) for g, t in GROUPS)
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{h}" '
            f'viewBox="0 0 {W} {h}" role="img" aria-label="{escape(label)}">\n'
            f"  <title>Tech Stack</title>\n" + "\n".join(parts) + "\n</svg>\n")


def alt_text():
    return " | ".join(f"{g}: " + ", ".join(t) for g, t in GROUPS)


def main():
    OUT.mkdir(exist_ok=True)
    widest = max((len(t) * CW + PAD_X * 2 for _, ts in GROUPS for t in ts))
    assert widest <= W, f"chip wider than the canvas: {widest:.0f}px"
    for theme, ramp, ink in (("dark", DARK_RAMP, DARK), ("light", LIGHT_RAMP, LIGHT)):
        p = OUT / f"stack-{theme}-{VERSION}.svg"
        s = build(ramp, ink)
        p.write_text(s, encoding="utf-8")
        if theme == "dark":
            print(f"wrote {p.name}  height {s.split('height=')[1].split(chr(34))[1]}px  "
                  f"({p.stat().st_size/1024:.0f} KB)")
        else:
            print(f"wrote {p.name}")
    print(f"{sum(len(t) for _, t in GROUPS)} tools · {len(GROUPS)} groups · "
          f"1 request (was 46)")


if __name__ == "__main__":
    main()
