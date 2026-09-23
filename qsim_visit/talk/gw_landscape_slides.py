"""SensitivityBuildUpSlide is aionanim's SensitivityBuildUp as a manim-slides
slide: one slide per step, advancing on the presenter's click instead of a
timed hold.

    uv run manim-slides render -q h talk/gw_landscape_slides.py SensitivityBuildUpSlide

Present it (click, space or right arrow for the next step):

    uv run manim-slides present SensitivityBuildUpSlide

or build a standalone HTML deck to open in any browser:

    uv run manim-slides convert SensitivityBuildUpSlide gw_landscape.html --to html --one-file
"""

from manim_slides import Slide

from aionanim.scenes.gw_landscape import SensitivityBuildUp


class SensitivityBuildUpSlide(Slide, SensitivityBuildUp):
    def beat(self):
        self.next_slide()
