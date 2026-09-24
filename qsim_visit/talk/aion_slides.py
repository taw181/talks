"""The Freiburg talk as one manim-slides deck, in the order of the talk.

Intro, atom interferometry, gravitational waves, dark matter, the prototype,
future plans, outro. The animated slides are aionanim scenes, picked up unmodified
through multiple inheritance; the static ones (title, contents, photographs,
figures) are laid out here, with the pictures in talk/media/.

A scene marks where the presenter should stop by calling a hook, and the
wrappers below turn the hook into a slide break:

- beat() is a no-op in the package; Clicks makes it a plain stop. Nothing in
  those scenes moves while they are paused, so there is nothing to loop.
- stage_break() is the sequence scenes' timed hold; LoopingStages loops two
  seconds of it instead, so the cloud keeps moving while a stage is talked
  through.
- hold() is DarkMatterScale's and DarkMatterField's one period of the field;
  the slide loops it.

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
from aionanim.scenes.dai_data import LaserNoiseLissajous
from aionanim.scenes.dipole import DipoleTrapLoading, SignalInjection
from aionanim.scenes.gradiometer import Gradiometer
from aionanim.scenes.gradiometer_gw import GradiometerGWStretch
from aionanim.scenes.gravitational_waves import BlackHoleMerger, MergerOnSensitivityPlot
from aionanim.scenes.gw_landscape import SensitivityBuildUp
from aionanim.scenes.light_shift import LightShiftSignal
from aionanim.scenes.lmt import LargeMomentumTransfer
from aionanim.scenes.single_photon import SinglePhotonMachZehnder
from aionanim.scenes.slicing import VelocitySlicing
from aionanim.scenes.uldm import DarkMatterField, DarkMatterPhase
from aionanim.scenes.uldm_scale import DarkMatterScale
from aionanim.tools.layout import image_point, load_image, numbered_list, slide_title
from aionanim.tools.primitives import make_cloud
from aionanim.tools.video import VideoFrame, load_video_frames

MEDIA = Path(__file__).parent / "media"
# The measured-data plots plot_scripts/ draw from the package data.
FIGURES = Path(__file__).parent.parent / "figures"

TITLE = (r"A prototype differential atom interferometer", r"for fundamental physics")
AUTHOR = r"Thomas Walker"
VENUE = r"University of Freiburg, 2026"
SECTIONS = (
    r"Atom interferometry",
    r"Gravitational waves",
    r"Dark matter",
    r"Our prototype device",
    r"Future plans",
)
# The title slide's background: the video's own frame rate, and how much of
# it the veil over it takes back so the title reads.
TITLE_VIDEO_FPS = 15
TITLE_VEIL_OPACITY = 0.55
# How long each slide holds its last frame before it stops. Manim only draws
# an animation's final frame when the next one starts, so without this a slide
# freezes a frame short -- atoms a hair before their vertex -- and jumps the
# rest of the way on the click. Anything over one frame at 15 fps will do.
SLIDE_SETTLE = 0.1


# --- how a scene's hooks become slide breaks -------------------------------
class DeckSlide(Slide):
    """Every slide in the deck: a Slide that stops on its finished frame.

    Looping slides are left without the settling hold: their last frame is
    their first, so the one manim leaves out is the one a loop would repeat.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.wait_time_between_slides = SLIDE_SETTLE
        self.wait_between_looping_slides = False


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
class TitleSlide(DeckSlide):
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
        # In the bottom half, clear of the MOT near the middle of the frame.
        VGroup(title, byline).arrange(DOWN, buff=0.5).to_edge(DOWN, buff=0.6)

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


class ContentsSlide(DeckSlide):
    def construct(self):
        contents = numbered_list(SECTIONS).move_to(DOWN * 0.2)
        self.play(FadeIn(slide_title(r"Outline")), FadeIn(contents), run_time=0.8)


# --- atom interferometry ----------------------------------------------------
class SinglePhotonMachZehnderSlide(Clicks, DeckSlide, SinglePhotonMachZehnder):
    pass


class ClockPhaseTermsSlide(Clicks, DeckSlide, ClockPhaseTerms):
    pass


class GradiometerSlide(Clicks, DeckSlide, Gradiometer):
    pass


# --- gravitational waves ----------------------------------------------------
class BlackHoleMergerSlide(DeckSlide, BlackHoleMerger):
    """No stops: the merger plays straight through from the moment the slide
    comes up, and holds on the settled sheet as the slide's own end."""


class MergerOnSensitivityPlotSlide(Clicks, DeckSlide, MergerOnSensitivityPlot):
    pass


class SensitivityLandscapeSlide(Clicks, DeckSlide, SensitivityBuildUp):
    """The landscape without AEDGE: AION-km is the one gap filler here."""

    GAP_FILLERS = ("AION-km",)


class GradiometerGWStretchSlide(Clicks, DeckSlide, GradiometerGWStretch):
    pass


# --- dark matter ------------------------------------------------------------
class DarkMatterScaleSlide(DeckSlide, DarkMatterScale):
    def hold(self):
        self.next_slide(loop=True)
        super().hold()
        self.next_slide()


class DarkMatterFieldSlide(DeckSlide, DarkMatterField):
    def hold(self):
        self.next_slide(loop=True)
        super().hold()
        self.next_slide()


class DarkMatterPhaseSlide(Clicks, DeckSlide, DarkMatterPhase):
    pass


# --- our prototype device -------------------------------------------------
class AIONCollabSlide(DeckSlide):
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


# The dark window between the coils in chamber_cropped.png (2475 x 1548 px),
# upper left and lower right: where the two clouds sit.
CHAMBER_WINDOW_PX = ((1090, 705), (1375, 900))
CHAMBER_GAP = 2.2  # between the cartoon clouds' centres, on screen


class ChamberSlide(DeckSlide):
    """Our chamber, with its centre called out: two atom clouds about 2 mm
    apart, then how that compares with AION's kilometre."""

    def construct(self):
        title = slide_title(r"Our prototype")
        photo = load_image(MEDIA / "chamber_cropped.png", height=5.2)
        photo.to_edge(LEFT, buff=0.4).set_y(-0.45)
        ul, dr = [image_point(photo, *p) for p in CHAMBER_WINDOW_PX]
        box = Rectangle(
            width=dr[0] - ul[0], height=ul[1] - dr[1],
            stroke_color=CALLOUT_COLOR, stroke_width=CALLOUT_STROKE_WIDTH,
        ).move_to((ul + dr) / 2)

        panel = RoundedRectangle(
            corner_radius=CALLOUT_CORNER_RADIUS,
            width=config.frame_x_radius - 0.4 - photo.get_right()[0] - 0.6,
            height=photo.height,
            stroke_color=CALLOUT_COLOR, stroke_width=CALLOUT_STROKE_WIDTH,
            fill_color=PLOT_BACKGROUND, fill_opacity=1,
        )
        panel.next_to(photo, RIGHT, buff=0.6).match_y(photo)
        joins = VGroup(
            Line(box.get_corner(UR), panel.get_corner(UL)),
            Line(box.get_corner(DR), panel.get_corner(DL)),
        ).set_stroke(CALLOUT_COLOR, CALLOUT_STROKE_WIDTH)

        lower = make_cloud(DOWN * CHAMBER_GAP / 2, LOWER_CLOUD_COLOR, seed=1)
        upper = make_cloud(UP * CHAMBER_GAP / 2, UPPER_CLOUD_COLOR, seed=2)
        gap = DoubleArrow(
            DOWN * CHAMBER_GAP / 2, UP * CHAMBER_GAP / 2,
            buff=0, stroke_width=4, color=lighten(GUIDE_COLOR),
            max_tip_length_to_length_ratio=0.12,
        ).shift(RIGHT * (CARTOON_CLOUD_RADIUS + 0.25))
        label = MathTex(r"\sim\!2\,\mathrm{mm}", r"\ll 1\,\mathrm{km}",
                        font_size=FONT_ANNOTATION)
        label.next_to(gap, RIGHT, buff=0.15)
        # centred as it ends up, with the km in, so nothing moves when it arrives
        VGroup(lower, upper, gap, label).move_to(panel)

        self.play(FadeIn(title), FadeIn(photo), FadeIn(box), FadeIn(joins),
                  FadeIn(panel), FadeIn(lower), FadeIn(upper), FadeIn(gap),
                  FadeIn(label[0]), run_time=0.8)
        self.next_slide()
        self.play(FadeIn(label[1], shift=LEFT * 0.2), run_time=0.6)


class AIONChambersSlide(DeckSlide):
    """The same chamber built at each AION site in 2022: the photos carry
    their own captions."""

    def construct(self):
        title = slide_title(r"AION chambers across the UK")
        figure = load_image(MEDIA / "aion_chambers.png", height=6.9)
        figure.next_to(title, DOWN, buff=0.25).set_x(0)
        self.play(FadeIn(title), FadeIn(figure), run_time=0.8)





class CoolingSequenceSlide(LoopingStages, DeckSlide, CoolingSequence):
    pass


class DipoleTrapLoadingSlide(LoopingStages, DeckSlide, DipoleTrapLoading):
    pass


class VelocitySlicingSlide(LoopingStages, DeckSlide, VelocitySlicing):
    pass


class LightShiftSignalSlide(Clicks, DeckSlide, LightShiftSignal):
    pass


class SignalInjectionSlide(LoopingStages, DeckSlide, SignalInjection):
    pass


class LaserNoiseLissajousSlide(Clicks, DeckSlide, LaserNoiseLissajous):
    """The quiet run full size, then shrunk to the top panel with the noisy
    run below it, both onto the one Lissajous plot."""


class ExtractedSignalSlide(DeckSlide):
    """Fig. 5a redrawn: each imprinted frequency found where it was put."""

    def construct(self):
        title = slide_title(r"Extracted signals")
        figure = load_image(FIGURES / "signals.png", width=13.4)
        figure.next_to(title, DOWN, buff=0.35).set_x(0)
        self.play(FadeIn(title), FadeIn(figure), run_time=0.8)


# --- future plans ---------------------------------------------------------
class SectionSlide(DeckSlide):
    """A section's title, numbered as it is in the outline."""

    SECTION = None  # one of SECTIONS

    def construct(self):
        number = SECTIONS.index(self.SECTION) + 1
        title = VGroup(
            Tex(f"{number}.", font_size=FONT_DECK_TITLE, color=lighten(GUIDE_COLOR)),
            Tex(self.SECTION, font_size=FONT_DECK_TITLE),
        ).arrange(RIGHT, buff=0.35)
        self.play(FadeIn(title), run_time=0.8)


class FuturePlansSlide(SectionSlide):
    SECTION = r"Future plans"


class Aion10BeecroftSlide(DeckSlide):
    """The stairwell, then the building cut away round it -- laid out as the
    row they end up in, so nothing moves."""

    def construct(self):
        title = slide_title(r"AION-10 at Oxford")
        stairwell = load_image(MEDIA / "stairwell.jpg", height=4.9)
        building = load_image(MEDIA / "beecroft.jpeg", height=4.9)
        Group(stairwell, building).arrange(RIGHT, buff=0.3).move_to(DOWN * 0.45)
        self.play(FadeIn(title), FadeIn(stairwell), run_time=0.8)
        self.next_slide()
        self.play(FadeIn(building, shift=LEFT * 0.3), run_time=0.8)


# The PX46 shaft in aice.png (1199 x 672 px): from under the surface building
# down to its rounded foot, with the arrow just clear of its right-hand side.
AICE_SHAFT_PX = ((940, 207), (940, 525))


class AICECernSlide(DeckSlide):
    """The AICE figure, which carries its own title, with the shaft's depth
    marked on it."""

    def construct(self):
        figure = load_image(MEDIA / "aice.png", width=config.frame_width)

        def at(px, py):
            """A pixel of aice.png, on screen."""
            return figure.get_corner(UL) + [px / 1199 * figure.width,
                                           -py / 672 * figure.height, 0]

        depth = DoubleArrow(*[at(*p) for p in AICE_SHAFT_PX], buff=0,
                            stroke_width=PHOTO_LABEL_STROKE_WIDTH, color=PHOTO_LABEL_COLOR,
                            tip_length=0.3, max_tip_length_to_length_ratio=0.1,
                            max_stroke_width_to_length_ratio=10)
        label = Tex(r"\textbf{150\,m}", font_size=FONT_PHOTO_LABEL, color=PHOTO_LABEL_COLOR)
        label.next_to(depth, RIGHT, buff=0.15)
        depth.set_stroke(**PHOTO_LABEL_OUTLINE, background=True, family=False)
        label.set_stroke(**PHOTO_LABEL_OUTLINE, background=True)
        self.play(FadeIn(figure), FadeIn(depth), FadeIn(label), run_time=0.8)


class LargeMomentumTransferSlide(DeckSlide, LargeMomentumTransfer):
    """No stops: the ladder plays straight through."""


class LMTResultsSlide(DeckSlide):
    """The upper/lower Lissajous ellipses from 1 to 71 LMT pulses."""

    def construct(self):
        title = slide_title(r"Large momentum transfer: results")
        figure = load_image(MEDIA / "lmt_ellipses.png", width=13.0)
        figure.next_to(title, DOWN, buff=0.35).set_x(0)
        self.play(FadeIn(title), FadeIn(figure), run_time=0.8)


# --- outro -------------------------------------------------------------------
class OutroSlide(DeckSlide):
    """Thank you: the Sr lab team down the left; Oliver and the AION logo
    over the AION collaboration down the right."""

    def construct(self):
        def labelled(image, text):
            label = Tex(text, font_size=FONT_LEGEND, color=lighten(GUIDE_COLOR))
            return Group(image, label.next_to(image, DOWN, buff=0.15))

        title = slide_title(r"Thank you")
        sr_group = labelled(load_image(MEDIA / "sr_lab_group.jpg", height=5.2),
                            r"Sr lab team")
        oliver = labelled(load_image(MEDIA / "oliver.png", height=2.3),
                          r"Oliver Buchm\"uller, PI")
        logo = load_image(MEDIA / "aion_logo_on_white.png", height=1.3)
        aion_group = labelled(load_image(MEDIA / "aion_group.png", width=6.0),
                              r"AION collaboration")
        top_right = Group(oliver, logo).arrange(RIGHT, buff=0.6)
        logo.match_y(oliver[0])
        right = Group(top_right, aion_group).arrange(DOWN, buff=0.3)
        Group(sr_group, right).arrange(RIGHT, buff=0.5).next_to(title, DOWN, buff=0.3).set_x(0)
        self.play(FadeIn(title), FadeIn(sr_group), FadeIn(right), run_time=0.8)
