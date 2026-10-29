# /// script
# requires-python = ">=3.10"
# dependencies = ["fonttools[woff]"]
# ///
"""Build assets/ana-light.svg and assets/ana-dark.svg from assets/hero.svg.tmpl.

Fonts are pinned to static weights, subset to the glyphs the hero uses and
inlined as WOFF2, because GitHub renders the SVG as an image and won't fetch
web fonts.

    uv run scripts/build_hero.py
"""

import base64
import io
import re
from pathlib import Path
from string import Template

from fontTools import subset
from fontTools.ttLib import TTFont
from fontTools.varLib import instancer

ROOT = Path(__file__).resolve().parent.parent
TEMPLATE = ROOT / "assets" / "hero.svg.tmpl"

THEMES = {
    "light": {"ink": "#1B2430", "muted": "#5B6573", "rule": "#C9CFD8", "violet": "#5B3FD0", "pass": "#2F7D5B", "bg": "#FFFFFF"},
    "dark": {"ink": "#E4E8EE", "muted": "#8B95A3", "rule": "#30363D", "violet": "#A08CF7", "pass": "#4FBF8B", "bg": "#0D1117"},
}


def font_b64(path: Path, weight: int, text: str) -> str:
    font = instancer.instantiateVariableFont(TTFont(path), {"wght": weight})
    options = subset.Options()
    options.flavor = "woff2"
    options.layout_features = ["kern", "liga"]
    subsetter = subset.Subsetter(options)
    subsetter.populate(text=text)
    subsetter.subset(font)
    buf = io.BytesIO()
    font.flavor = "woff2"
    font.save(buf)
    return base64.b64encode(buf.getvalue()).decode()


def main() -> None:
    template = TEMPLATE.read_text()
    # Every visible character, plus a little slack for edits to the copy.
    visible = re.sub(r"<[^>]+>", "", template.split("</style>", 1)[1])
    glyphs = "".join(sorted(set(visible))) + "0123456789"
    fonts = dict(
        sg400=font_b64(ROOT / "fonts/SchibstedGrotesk.ttf", 400, glyphs),
        sg700=font_b64(ROOT / "fonts/SchibstedGrotesk.ttf", 700, "ana"),
        jbm400=font_b64(ROOT / "fonts/JetBrainsMono.ttf", 400, glyphs),
    )
    for name, colors in THEMES.items():
        svg = Template(template).substitute(**fonts, **colors)
        out = ROOT / "assets" / f"ana-{name}.svg"
        out.write_text(svg)
        print(f"{out.relative_to(ROOT)}  {len(svg) / 1024:.1f} KB")


if __name__ == "__main__":
    main()
