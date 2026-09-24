"""The Freiburg talk as one manim-slides deck, in the order of the talk.

Intro, motivation, how atom interferometry works, the prototype, future
plans, outro. The animated slides are aionanim scenes, picked up unmodified
through multiple inheritance; the static ones (title, contents, photographs,
figures) are laid out here, with the pictures in talk/media/.

A scene marks where the presenter should stop by calling a hook, and the
wrappers below turn the hook into a slide break:

- beat() is a no-op in the package; Clicks makes it a plain stop. Nothing in
  those scenes moves while they are paused, so there is nothing to loop.
- stage_break() is the sequence scenes' timed hold; LoopingStages loops two
  seconds of it instead, so the cloud keeps moving while a stage is talked
  through.
- hold() is DarkMatterField's one period of the field; the slide loops it.

The deck order lives in talk/deck.sh, which renders, presents and converts:

    talk/deck.sh render h     # -q h; `l` for a quick look
    talk/deck.sh present
    talk/deck.sh html         # aion_talk.html, standalone
"""

from pathlib import Path

from manim import *
from manim_slides import Slide

from aionanim.style import *
from aionanim.scenes.clock import ClockPhaseTerms
from aionanim.scenes.cooling import CoolingSequence
from aionanim.scenes.dai_data import FringesFirst, FringesFirstNoisy
from aionanim.scenes.dipole import DipoleTrapLoading
from aionanim.scenes.gradiometer import Gradiometer
from aionanim.scenes.gradiometer_gw import GradiometerGWStretch
from aionanim.scenes.gravitational_waves import BlackHoleMerger, MergerOnSensitivityPlot
from aionanim.scenes.gw_landscape import SensitivityBuildUp
from aionanim.scenes.light_shift import LightShiftSignal
from aionanim.scenes.lmt import LargeMomentumTransfer
from aionanim.scenes.single_photon import SinglePhotonMachZehnder
from aionanim.scenes.slicing import VelocitySlicing
from aionanim.scenes.uldm import DarkMatterField, DarkMatterPhase
from aionanim.tools.layout import load_image, numbered_list, placeholder_frame, slide_title
from aionanim.tools.video import VideoFrame, load_video_frames

MEDIA = Path(__file__).parent / "media"

TITLE = (r"A prototype differential atom interferometer", r"for fundamental physics")
AUTHOR = r"Thomas Walker"
VENUE = r"University of Freiburg, 2026"
SECTIONS = (
    r"Motivation",
    r"How atom interferometry works",
    r"Our prototype device",
    r"Future plans",
)
# The title slide's background: the video's own frame rate, and how much of
# it the veil over it takes back so the title reads.
TITLE_VIDEO_FPS = 15
TITLE_VEIL_OPACITY = 0.55
# None until the LMT results figure exists; then its path under talk/media/.
LMT_RESULTS_IMAGE = None


# --- how a scene's hooks become slide breaks -------------------------------
class Clicks:
    """beat() stops and waits for the presenter."""

    def beat(self):
        self.next_slide()


class LoopingStages:
    """stage_break() loops two seconds of the running stage, then stops."""

    def stage_break(self):
        self.next_slide(loop=True)
        self.wait(2)
        self.next_slide()


# --- intro -------------------------------------------------------------------
class TitleSlide(Slide):
    """The title over the blue MOT, with the video running for as long as the
    slide is up: driven forwards and then backwards, so the loop has no seam."""

    def construct(self):
        frames = load_video_frames(MEDIA / "blue_mot.mp4")
        video = VideoFrame(frames)
        video.width = config.frame_width
        cycle = 2 * (len(frames) - 1)  # there and back, in frames
        clock = ValueTracker(0.0)

        def ping_pong(m):
            f = clock.get_value() % cycle
            m.show(round(f if f <= cycle / 2 else cycle - f))

        video.add_updater(ping_pong)
        # The video cannot be faded (see VideoFrame), so a veil drawn over it
        # lifts instead, and stops part way to keep the text readable.
        veil = FullScreenRectangle(
            stroke_width=0, fill_color=PLOT_BACKGROUND, fill_opacity=1.0
        )

        aion = load_image(MEDIA / "aion_logo_on_dark.png", height=1.0)
        imperial = load_image(MEDIA / "imperial_logo_on_dark.png", height=0.42)
        aion.to_corner(UL, buff=0.4)
        imperial.to_corner(UR, buff=0.4).match_y(aion)
        title = VGroup(*[Tex(line, font_size=FONT_DECK_TITLE) for line in TITLE])
        title.arrange(DOWN, buff=0.25)
        byline = VGroup(
            Tex(AUTHOR, font_size=FONT_DECK_BYLINE),
            Tex(VENUE, font_size=FONT_DECK_BYLINE, color=lighten(GUIDE_COLOR)),
        ).arrange(DOWN, buff=0.18)
        VGroup(title, byline).arrange(DOWN, buff=0.7).shift(DOWN * 0.2)

        self.add(video, veil)
        self.next_slide(auto_next=True)  # straight on into the loop
        fade_in = 1.5
        self.play(
            veil.animate.set_fill(opacity=TITLE_VEIL_OPACITY),
            FadeIn(aion), FadeIn(imperial), FadeIn(title), FadeIn(byline),
            clock.animate.increment_value(fade_in * TITLE_VIDEO_FPS),
            rate_func=linear, run_time=fade_in,
        )
        self.next_slide(loop=True)
        self.play(
            clock.animate.increment_value(cycle),
            rate_func=linear, run_time=cycle / TITLE_VIDEO_FPS,
        )


class ContentsSlide(Slide):
    def construct(self):
        contents = numbered_list(SECTIONS).move_to(DOWN * 0.2)
        self.play(FadeIn(slide_title(r"Outline")), FadeIn(contents), run_time=0.8)


# --- motivation --------------------------------------------------------------
class BlackHoleMergerSlide(Clicks, Slide, BlackHoleMerger):
    pass


class MergerOnSensitivityPlotSlide(Clicks, Slide, MergerOnSensitivityPlot):
    pass


class SensitivityLandscapeSlide(Clicks, Slide, SensitivityBuildUp):
    """The landscape without AEDGE: AION-km is the one gap filler here."""

    GAP_FILLERS = ("AION-km",)


class DarkMatterFieldSlide(Slide, DarkMatterField):
    def hold(self):
        self.next_slide(loop=True)
        super().hold()
        self.next_slide()


# --- how atom interferometry works -----------------------------------------
class SinglePhotonMachZehnderSlide(Clicks, Slide, SinglePhotonMachZehnder):
    pass


class ClockPhaseTermsSlide(Clicks, Slide, ClockPhaseTerms):
    pass


class DarkMatterPhaseSlide(Clicks, Slide, DarkMatterPhase):
    pass


class GradiometerSlide(Clicks, Slide, Gradiometer):
    pass


class GradiometerGWStretchSlide(Clicks, Slide, GradiometerGWStretch):
    pass


class AIONCollabSlide(Slide):
    """Who AION are and where, then the baseline they are building."""

    def construct(self):
        title = slide_title(r"The AION collaboration")
        logo = load_image(MEDIA / "aion_logo_on_dark.png", height=1.0)
        logo.to_corner(UR, buff=0.4)
        uk_map = load_image(MEDIA / "aion_map.jpeg", height=6.0)
        baseline = load_image(MEDIA / "baseline.png", height=6.0)
        # Laid out as the pair they end up as, so the map does not move when
        # the baseline arrives beside it.
        Group(uk_map, baseline).arrange(RIGHT, buff=1.2).move_to(DOWN * 0.45)
        self.play(FadeIn(title), FadeIn(logo), FadeIn(uk_map), run_time=0.8)
        self.next_slide()
        self.play(FadeIn(baseline, shift=LEFT * 0.3), run_time=0.8)


# --- our prototype device -------------------------------------------------
class CoolingSequenceSlide(LoopingStages, Slide, CoolingSequence):
    pass


class DipoleTrapLoadingSlide(LoopingStages, Slide, DipoleTrapLoading):
    pass


class VelocitySlicingSlide(LoopingStages, Slide, VelocitySlicing):
    pass


class LightShiftSignalSlide(Clicks, Slide, LightShiftSignal):
    pass


class FringesFirstSlide(Clicks, Slide, FringesFirst):
    pass


class FringesFirstNoisySlide(Clicks, Slide, FringesFirstNoisy):
    pass


class ExtractedSignalSlide(Slide):
    def construct(self):
        title = slide_title(r"Extracted signals")
        figure = load_image(MEDIA / "extracted_signal.png", width=12.0)
        figure.next_to(title, DOWN, buff=0.35).set_x(0)
        self.play(FadeIn(title), FadeIn(figure), run_time=0.8)


# --- future plans ---------------------------------------------------------
class Aion10BeecroftSlide(Slide):
    """The building, then the layout of the shaft inside it."""

    def construct(self):
        title = slide_title(r"AION-10 in the Beecroft building")
        building = load_image(MEDIA / "beecroft.png", height=6.2)
        shaft = load_image(MEDIA / "shaft_diagram.png", height=6.2)
        Group(building, shaft).arrange(RIGHT, buff=0.7).move_to(DOWN * 0.45)
        self.play(FadeIn(title), FadeIn(building), run_time=0.8)
        self.next_slide()
        self.play(FadeIn(shaft, shift=LEFT * 0.3), run_time=0.8)


class AICECernSlide(Slide):
    def construct(self):
        title = slide_title(r"AICE at CERN")
        site = load_image(MEDIA / "cern.png", height=6.5)
        site.next_to(title, DOWN, buff=0.45).set_x(0)
        self.play(FadeIn(title), FadeIn(site), run_time=0.8)


class LargeMomentumTransferSlide(Clicks, Slide, LargeMomentumTransfer):
    pass


class LMTResultsSlide(Slide):
    def construct(self):
        title = slide_title(r"Large momentum transfer: results")
        if LMT_RESULTS_IMAGE is None:
            figure = placeholder_frame(10.5, 5.6, r"LMT results")
        else:
            figure = load_image(MEDIA / LMT_RESULTS_IMAGE, height=5.6)
        figure.move_to(DOWN * 0.4)
        self.play(FadeIn(title), FadeIn(figure), run_time=0.8)


# --- outro -------------------------------------------------------------------
class OutroSlide(Slide):
    """The Sr group and the AION collaboration, Oliver, and the logo."""

    def construct(self):
        sr_group = load_image(MEDIA / "sr_lab_group.jpg", height=3.5)
        aion_group = load_image(MEDIA / "aion_group.png", height=3.5)
        oliver = load_image(MEDIA / "oliver.png", height=3.1)
        logo = load_image(MEDIA / "aion_logo_on_dark.png", height=1.7)
        top = Group(sr_group, aion_group).arrange(RIGHT, buff=0.35)
        bottom = Group(oliver, logo).arrange(RIGHT, buff=1.2)
        Group(top, bottom).arrange(DOWN, buff=0.35)
        self.play(FadeIn(top), FadeIn(bottom), run_time=0.8)
