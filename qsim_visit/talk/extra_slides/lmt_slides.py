"""Large momentum transfer: out of the talk, kept as extra slides.

The same DeckSlide wrappers as the deck, imported from talk/aion_slides.py, so
they look like the rest of it; they are not in talk/deck.txt, so they carry no
footer number. Render and present them by name, from the project root:

    uv run manim-slides render -q l talk/extra_slides/lmt_slides.py \
        LargeMomentumTransferSlide LMTMachZehnderSlide LMTResultsSlide
    uv run manim-slides present LargeMomentumTransferSlide LMTMachZehnderSlide LMTResultsSlide
"""

import sys
from pathlib import Path

from manim import *

# aion_slides.py is a script beside the package, not in it: put talk/ on the
# path to reach it. manim loads this file by path, so a relative import won't do.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from aion_slides import MEDIA, Clicks, DeckSlide  # noqa: E402
from aionanim.scenes.lmt import LargeMomentumTransfer, LMTMachZehnder  # noqa: E402
from aionanim.tools.layout import load_image, slide_title  # noqa: E402


class LargeMomentumTransferSlide(DeckSlide, LargeMomentumTransfer):
    """No stops: the ladder plays straight through."""


class LMTMachZehnderSlide(Clicks, DeckSlide, LMTMachZehnder):
    """A click after each stage, then the area against the N = 1 one."""


class LMTResultsSlide(DeckSlide):
    """The upper/lower Lissajous ellipses from 1 to 71 LMT pulses."""

    def construct(self):
        title = slide_title(r"Large momentum transfer: results")
        figure = load_image(MEDIA / "lmt_ellipses.png", width=13.0)
        figure.next_to(title, DOWN, buff=0.35).set_x(0)
        self.play(FadeIn(title), FadeIn(figure), run_time=0.8)
