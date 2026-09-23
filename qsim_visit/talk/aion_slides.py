"""AION talk: a manim-slides deck built from a selection of aionanim scenes.

Each class below is one slide-scene: a thin `Slide` wrapper around an
existing `Scene` from aionanim.scenes, picked up unmodified via multiple
inheritance. None of them call `self.next_slide()` internally, so each
plays through in full and then waits for the presenter to advance -- the
scenes are already paced and don't need splitting.

Order follows the story: the single-photon scheme, its phase
readout, the gradiometer built from two such clocks, the two signals it's
pointed at (dark matter, then a gravitational wave), and the momentum-
transfer trick that buys more sensitivity.

Render:
    uv run manim-slides render -q h talk/aion_slides.py

Present (all six, in order):
    uv run manim-slides present SinglePhotonMachZehnderSlide ClockPhaseSlide \
        GradiometerSlide DarkMatterPhaseSlide GradiometerGWStretchSlide \
        LargeMomentumTransferSlide

Or build a standalone HTML deck:
    uv run manim-slides convert SinglePhotonMachZehnderSlide ClockPhaseSlide \
        GradiometerSlide DarkMatterPhaseSlide GradiometerGWStretchSlide \
        LargeMomentumTransferSlide aion_talk.html --to html --one-file
"""

from manim_slides import Slide

from aionanim.scenes.gradiometer_gw import GradiometerGWStretch
from aionanim.scenes.clock import ClockPhase
from aionanim.scenes.gradiometer import Gradiometer
from aionanim.scenes.lmt import LargeMomentumTransfer
from aionanim.scenes.single_photon import SinglePhotonMachZehnder
from aionanim.scenes.uldm import DarkMatterPhase


class SinglePhotonMachZehnderSlide(Slide, SinglePhotonMachZehnder):
    pass


class ClockPhaseSlide(Slide, ClockPhase):
    pass


class GradiometerSlide(Slide, Gradiometer):
    pass


class DarkMatterPhaseSlide(Slide, DarkMatterPhase):
    pass


class GradiometerGWStretchSlide(Slide, GradiometerGWStretch):
    pass


class LargeMomentumTransferSlide(Slide, LargeMomentumTransfer):
    pass
