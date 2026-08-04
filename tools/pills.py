#!/usr/bin/env python3
"""Generate the What I Do pill rows used in README.md.

One SVG per discipline, replacing that discipline's bullet list. The `###`
headings stay as real markdown, so the section keeps its structure and only the
grey bullet text becomes colour.

Bullet text is verbatim, including the bold spans -- `**like this**` is rendered
as a bold tspan inside the pill, so the emphasis survives. Mono keeps the
advance width identical between weights, so pinning the whole <text> with
textLength stays accurate across the mixed run.

Each discipline gets its own colour, sampled evenly along the same
cyan-blue-purple-pink ramp the banners use, so the six rows walk the spectrum.

    python3 tools/pills.py

Bump VERSION on any visual change -- camo caches these hard.
"""

import pathlib
import re
from xml.sax.saxutils import escape

VERSION = "v2"
OUT = pathlib.Path(__file__).resolve().parent.parent / "banners"

W = 870
FS = 12
CW = FS * 0.6
PAD_X, PILL_H = 11, 26
GAP_X, GAP_Y = 6, 8
TEXT_DY = 17.5

# The discipline heading lives inside the SVG so it can carry the group's
# colour. Markdown cannot colour text, and a plain white heading over coloured
# pills read as two unrelated objects rather than one block.
HEAD_FS, HEAD_H, EMOJI_X, HEAD_X = 14, 34, 0, 26
EMOJI_FONT = ('"Apple Color Emoji","Segoe UI Emoji","Noto Color Emoji",'
              "ui-monospace,Menlo,monospace")

DARK_RAMP = ["#22d3ee", "#58a6ff", "#a855f7", "#f472b6"]
LIGHT_RAMP = ["#0891b2", "#2563eb", "#9333ea", "#db2777"]

# fill alpha, stroke alpha, and whether pill text uses the accent or near-black
DARK_STYLE = {"fill": 0.14, "stroke": 0.42, "text": "#ffffff"}
LIGHT_STYLE = {"fill": 0.10, "stroke": 0.40, "text": "#1f2328"}

DISCIPLINES = [
    ('\U0001f9e0', 'AI/ML', 'ai-ml', [
        'Multi-agent orchestration and **autonomous agent systems**',
        'Building **language models** with a focus on **training efficiency over raw scale**',
        'Fine-tuning and developing **Diffusion Models** for creative 3D asset pipelines',
        'Python-based research and development for **human–machine interaction** and **adaptive narrative systems**',
    ]),
    ('\U0001f3ae', 'Game Development', 'game-development', [
        'Worldbuilding in **Unreal Engine** and **Unity 6 LTS**',
        '3D assets and environments with **Blender**',
        'Gameplay systems, mission loops, and economy design',
        'Procedural world generation and **modular level design**',
    ]),
    ('\U0001f4bb', 'Web Development', 'web-development', [
        '**Next.js**, **React**, **Tailwind** frontend',
        '**Node.js**, **GraphQL**, **PostgreSQL**, **Firebase** backend',
        'Web3 integrations with **ThirdWeb**, **Solidity**, **IPFS**',
        'AI-native application architecture',
    ]),
    ('\U0001f300', 'Creative Tech', 'creative-tech', [
        'Motion graphics: **Lottie**, **GSAP**, **Spline**',
        'AI-driven animation and narrative systems',
        'Generative 3D pipelines: **text-to-mesh**, retopology, game-ready output',
        'Design systems and **brand visual identity** at product scale',
    ]),
    ('\U0001f52e', 'Product Vision & Strategy', 'product-vision-strategy', [
        'First-principles product design',
        'Creator economies, incentive loops, UX architecture',
        '0-to-1 product specs, build docs, and technical roadmaps',
        'Pricing, monetization modeling, and unit economics',
    ]),
    ('\U0001f465', 'Community, Content & Launch', 'community-content-launch', [
        'Brand building across social media',
        'Full-funnel digital product launch strategies',
        'Narrative-driven viral content design',
        'Building in public: technical storytelling and developer-facing content',
    ]),
]


def lerp_hex(a, b, t):
    a, b = a.lstrip("#"), b.lstrip("#")
    parts = [
        round(int(a[i:i+2], 16) + (int(b[i:i+2], 16) - int(a[i:i+2], 16)) * t)
        for i in (0, 2, 4)
    ]
    return "#" + "".join(f"{v:02x}" for v in parts)


def sample(ramp, t):
    """Colour at position t (0..1) along a multi-stop ramp."""
    if t >= 1:
        return ramp[-1]
    span = 1 / (len(ramp) - 1)
    i = int(t / span)
    return lerp_hex(ramp[i], ramp[i + 1], (t - i * span) / span)


def spans(bullet):
    """Split `a **b** c` into [(text, is_bold), ...]."""
    out = []
    for i, chunk in enumerate(re.split(r"\*\*", bullet)):
        if chunk:
            out.append((chunk, i % 2 == 1))
    return out


def pill(x, y, bullet, colour, style):
    segs = spans(bullet)
    plain = "".join(s for s, _ in segs)
    tw = len(plain) * CW
    w = tw + PAD_X * 2
    body = "".join(
        f'<tspan font-weight="{700 if bold else 400}">{escape(s)}</tspan>'
        for s, bold in segs
    )
    svg = (
        f'    <g transform="translate({x:.1f},{y:.1f})">\n'
        f'      <rect width="{w:.1f}" height="{PILL_H}" rx="{PILL_H/2}" '
        f'fill="{colour}" fill-opacity="{style["fill"]}" '
        f'stroke="{colour}" stroke-opacity="{style["stroke"]}"/>\n'
        f'      <text x="{PAD_X}" y="{TEXT_DY}" '
        f'font-family="ui-monospace,SFMono-Regular,Menlo,Consolas,monospace" '
        f'font-size="{FS}" fill="{style["text"]}" '
        f'textLength="{tw:.1f}" lengthAdjust="spacingAndGlyphs">{body}</text>\n'
        f"    </g>"
    )
    return svg, w


def row(bullets, colour, style, label):
    """Flow pills left to right, wrapping at W."""
    parts, x, y, rows = [], 0.0, 0.0, 1
    for b in bullets:
        w = len(b.replace("**", "")) * CW + PAD_X * 2
        if x and x + w > W:
            x, y, rows = 0.0, y + PILL_H + GAP_Y, rows + 1
        svg, w = pill(x, y, b, colour, style)
        parts.append(svg)
        x += w + GAP_X
    h = rows * PILL_H + (rows - 1) * GAP_Y
    return "\n".join(parts), h


def build(disc_index, emoji, name, bullets, ramp, style):
    t = disc_index / (len(DISCIPLINES) - 1)
    colour = sample(ramp, t)
    body, h = row(bullets, colour, style, name)
    total = HEAD_H + h
    label = ", ".join(b.replace("**", "") for b in bullets)
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{total:.0f}" \
viewBox="0 0 {W} {total:.0f}" role="img" aria-label="{escape(name)}: {escape(label)}">
  <title>{escape(name)}</title>
  <text x="{EMOJI_X}" y="{HEAD_FS + 2}" font-family={EMOJI_FONT!r} \
font-size="{HEAD_FS + 1}">{escape(emoji)}</text>
  <text x="{HEAD_X}" y="{HEAD_FS + 2}" \
font-family="ui-monospace,SFMono-Regular,Menlo,Consolas,monospace" \
font-size="{HEAD_FS}" font-weight="700" fill="{colour}">{escape(name)}</text>
  <g transform="translate(0,{HEAD_H})">
{body}
  </g>
</svg>
"""


def main():
    OUT.mkdir(exist_ok=True)
    for theme, ramp, style in (("dark", DARK_RAMP, DARK_STYLE),
                               ("light", LIGHT_RAMP, LIGHT_STYLE)):
        for i, (emoji, name, slug, bullets) in enumerate(DISCIPLINES):
            p = OUT / f"pills-{slug}-{theme}-{VERSION}.svg"
            p.write_text(build(i, emoji, name, bullets, ramp, style), encoding="utf-8")
    n = len(DISCIPLINES)
    print(f"wrote {n*2} pill rows ({n} disciplines x 2 themes) to {OUT}/")
    for i, (_, name, slug, bullets) in enumerate(DISCIPLINES):
        print(f"  {slug:<22} {len(bullets)} pills   {sample(DARK_RAMP, i/(n-1))}")


if __name__ == "__main__":
    main()
