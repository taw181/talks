"""AION talk: a manim-slides deck built from a selection of aionanim scenes.

Each class below is one slide-scene: a thin `Slide` wrapper around an
existing `Scene` from aionanim.scenes, picked up unmodified via multiple
inheritance. Most of them don't call `self.next_slide()` internally, so
each plays through in full and then waits for the presenter to advance --
the scenes are already paced and don't need splitting. The exception is
CoolingSequenceSlide, which stops after each of its three stages through
the scene's `stage_break` hook.

Order follows the story: how the atoms are cooled, the single-photon scheme,
its phase readout, the gradiometer built from two such clocks, the two signals it's
pointed at (dark matter, then a gravitational wave), and the momentum-
transfer trick that buys more sensitivity.

Render:
    uv run manim-slides render -q h talk/aion_slides.py

Present (all seven, in order):
    uv run manim-slides present CoolingSequenceSlide SinglePhotonMachZehnderSlide ClockPhaseSlide \
        GradiometerSlide DarkMatterPhaseSlide GradiometerGWStretchSlide \
        LargeMomentumTransferSlide

Or build a standalone HTML deck:
    uv run manim-slides convert CoolingSequenceSlide SinglePhotonMachZehnderSlide ClockPhaseSlide \
        GradiometerSlide DarkMatterPhaseSlide GradiometerGWStretchSlide \
        LargeMomentumTransferSlide aion_talk.html --to html --one-file
"""

from manim_slides import Slide

from aionanim.scenes.gradiometer_gw import GradiometerGWStretch
from aionanim.scenes.clock import ClockPhase
from aionanim.scenes.cooling import CoolingSequence
from aionanim.scenes.gradiometer import Gradiometer
from aionanim.scenes.lmt import LargeMomentumTransfer
from aionanim.scenes.single_photon import SinglePhotonMachZehnder
from aionanim.scenes.uldm import DarkMatterPhase


class CoolingSequenceSlide(Slide, CoolingSequence):
    """Stops after each MOT stage, looping two seconds of it so the cloud
    keeps moving while the stage is talked through."""

    def stage_break(self):
        self.next_slide(loop=True)
        self.wait(2)
        self.next_slide()


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
