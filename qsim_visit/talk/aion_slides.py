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

A looping stop is still one click: RunsOnIntoLoops plays each stretch straight
on into its loop, and the click moves on from the loop.

The deck order lives in talk/deck.sh, which renders, presents and converts:

    talk/deck.sh render h     # -q h; `l` for a quick look
    talk/deck.sh present
    talk/deck.sh html         # aion_talk.html, standalone
"""

from dataclasses import replace
from pathlib import Path

from manim import *
from manim_slides import Slide

from aionanim.bibliography import AUTHOR_YEAR, FULL, SHORT, format_reference, load_bibliography
from aionanim.style import *
from aionanim.scenes.aedge import AEDGESensitivity
from aionanim.scenes.clock import ClockPhaseTerms
from aionanim.scenes.cooling import CoolingSequence
from aionanim.scenes.dai_data import LaserNoiseLissajous
from aionanim.scenes.dipole import DipoleTrapLoading, SignalInjection
from aionanim.scenes.gradiometer import Gradiometer
from aionanim.scenes.gradiometer_gw import GradiometerGWStretchContinuous
from aionanim.scenes.gravitational_waves import BlackHoleMerger, MergerOnSensitivityPlot
from aionanim.scenes.gw_landscape import SensitivityBuildUp
from aionanim.scenes.light_shift import LightShiftSignalContinuous
from aionanim.scenes.sequence import SEQ_SIMPLE_REFERENCES, ExperimentSequenceSimple
from aionanim.scenes.single_photon import SinglePhotonMachZehnder
from aionanim.scenes.slicing import VelocitySlicing
from aionanim.scenes.uldm import DarkMatterField, DarkMatterPhaseContinuous
from aionanim.scenes.uldm_scale import DarkMatterScale
from aionanim.tools.citations import citation, labelled_citation, place_citation
from aionanim.tools.layout import image_point, load_image, numbered_list, slide_title
from aionanim.tools.primitives import make_cloud
from aionanim.tools.video import VideoFrame, load_video_frames

MEDIA = Path(__file__).parent / "media"
# The measured-data plots plot_scripts/ draw from the package data.
FIGURES = Path(__file__).parent.parent / "figures"
# The talk's references, exported from the Zotero collection; a slide cites
# them by key through DeckSlide.CITE.
BIB = load_bibliography(Path(__file__).parent.parent / "AION.bib")
# How a slide's footer citation reads. replace() it for another look: keep=
# names an author through the et al., collaboration= replaces the list.
CITE_FORMAT = replace(SHORT, highlight=("Walker, T",))
# ...and a slide citing many papers, as (label, key) pairs, run on together
CITE_LABELLED_FORMAT = replace(AUTHOR_YEAR, highlight=("Walker, T",))

TITLE = (r"A prototype differential atom interferometer", r"for fundamental physics")
AUTHOR = r"Thomas Walker"
VENUE = r"University of Freiburg, 2026"
SECTIONS = (
    r"Atom interferometry",
    r"Motivation",
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
def deck_order():
    """The slide classes in talk/deck.txt, in order, as deck.sh reads them."""
    lines = (Path(__file__).parent / "deck.txt").read_text(encoding="utf-8").splitlines()
    return [slide for line in lines if (slide := line.split("#")[0].strip())]


DECK = deck_order()


def cite(*keys):
    """The deck's references under these keys, failing on one not in AION.bib."""
    missing = [k for k in keys if k not in BIB]
    if missing:
        raise KeyError(f"not in AION.bib: {', '.join(missing)}")
    return [BIB[k] for k in keys]


def make_footer(number, total):
    """The progress bar along the bottom edge, filled to this slide's place in
    the deck, and the slide's number in the corner above the end of it."""
    width = config.frame_width
    bottom = -config.frame_y_radius + PROGRESS_BAR_HEIGHT / 2
    track = Rectangle(
        width=width, height=PROGRESS_BAR_HEIGHT, stroke_width=0,
        fill_color=PROGRESS_TRACK_COLOR, fill_opacity=1,
    ).move_to([0, bottom, 0])
    fill = Rectangle(
        width=width * number / total, height=PROGRESS_BAR_HEIGHT, stroke_width=0,
        fill_color=PROGRESS_FILL_COLOR, fill_opacity=1,
    ).align_to(track, LEFT).set_y(bottom)
    label = Tex(str(number), font_size=FONT_SLIDE_NUMBER, color=SLIDE_NUMBER_COLOR)
    label.next_to(track, UP, buff=0.1).to_edge(RIGHT, buff=0.15)
    label.set_stroke(PLOT_BACKGROUND, width=4, background=True)  # legible over photos
    return VGroup(track, fill, label)


class DeckSlide(Slide):
    """Every slide in the deck: a Slide that stops on its finished frame, with
    the footer (progress bar and slide number) over everything it draws, and
    the references it names in CITE (AION.bib keys) bottom left above it:
    one line each, or, if CITE holds (label, key, ...) tuples, run on together
    as "label: Author et al. (year)". CITE_CORNER moves it off something the
    footer would cover.

    Looping slides are left without the settling hold: their last frame is
    their first, so the one manim leaves out is the one a loop would repeat.

    The footer and citation are foreground mobjects, so they stay on top of
    whatever the scene adds; they are pinned to the frame in a 3D scene, ride
    along with a moving camera, and are kept out of any remove(), since a
    scene may clear the page with remove(*self.mobjects).
    """

    CITE = ()
    CITE_FORMAT = CITE_FORMAT
    CITE_CORNER = DL

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.wait_time_between_slides = SLIDE_SETTLE
        self.wait_between_looping_slides = False
        self.furniture = []

    def setup(self):
        super().setup()
        if self.CITE:
            self._pin(place_citation(self.citation(), self.CITE_CORNER))
        name = type(self).__name__
        if name in DECK:
            self._pin(make_footer(DECK.index(name) + 1, len(DECK)))

    def citation(self):
        if all(isinstance(c, tuple) for c in self.CITE):
            return labelled_citation([(label, cite(*keys)) for label, *keys in self.CITE],
                                     fmt=CITE_LABELLED_FORMAT)
        return citation(*cite(*self.CITE), fmt=self.CITE_FORMAT)

    def _pin(self, mob):
        """``mob`` on top, fixed on the screen, and out of reach of remove()."""
        if isinstance(self, ThreeDScene):
            self.add_fixed_in_frame_mobjects(mob)
        elif isinstance(self, MovingCameraScene):
            frame = self.camera.frame  # moves, but never zooms
            offset = mob.get_center() - frame.get_center()
            mob.add_updater(lambda m: m.move_to(frame.get_center() + offset))
        self.add_foreground_mobject(mob)
        self.furniture.append(mob)

    def remove(self, *mobjects):
        return super().remove(*[m for m in mobjects if m not in self.furniture])


class Clicks:
    """beat() stops and waits for the presenter."""

    def beat(self):
        self.next_slide()


class RunsOnIntoLoops:
    """Each stretch plays straight on into the loop after it, so a stage is one
    click however it is cut: the click starts the stage, and its loop holds
    the screen until the next. (Without auto_next the stretch would stop on its
    last frame and need a click of its own to start its loop.)

    auto_next belongs to the segment a next_slide() opens; one with nothing
    before it sets the options of the slide's first segment instead.
    """

    def setup(self):
        super().setup()
        self.next_slide(auto_next=True)

    def loop(self, hold):
        """Loop what hold() plays until the click, then run on into the next."""
        self.next_slide(loop=True)
        hold()
        self.next_slide(auto_next=True)


class LoopingStages(RunsOnIntoLoops):
    """stage_break() loops two seconds of the running stage until the click."""

    def stage_break(self):
        self.loop(lambda: self.wait(2))


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
            FadeIn(aion),
            FadeIn(imperial),
            FadeIn(title),
            FadeIn(byline),
            clock.animate.increment_value(fade_in * TITLE_VIDEO_FPS),
            rate_func=linear,
            run_time=fade_in,
        )
        self.next_slide(loop=True)
        self.play(
            clock.animate.increment_value(cycle),
            rate_func=linear,
            run_time=cycle / TITLE_VIDEO_FPS,
        )


class ContentsSlide(DeckSlide):
    def construct(self):
        contents = numbered_list(SECTIONS).move_to(DOWN * 0.2)
        self.play(FadeIn(slide_title(r"Outline")), FadeIn(contents), run_time=0.8)


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


# --- atom interferometry ----------------------------------------------------
class AtomInterferometrySlide(SectionSlide):
    SECTION = r"Atom interferometry"


class SinglePhotonMachZehnderSlide(Clicks, DeckSlide, SinglePhotonMachZehnder):
    pass


class ClockPhaseTermsSlide(Clicks, DeckSlide, ClockPhaseTerms):
    pass


class GradiometerSlide(Clicks, DeckSlide, Gradiometer):
    pass


# --- motivation: gravitational waves, then dark matter ---------------------
class MotivationSlide(SectionSlide):
    SECTION = r"Motivation"


class BlackHoleMergerSlide(DeckSlide, BlackHoleMerger):
    """No stops: the merger plays straight through from the moment the slide
    comes up, and holds on the settled sheet as the slide's own end."""


# The sensitivity curves are digitised from an internal AION figure, whose
# own sources aren't known, so each detector cites the paper that set it out;
# the merger tracks cite their waveform model and the cosmology that sets
# their distances.
LIGO_PAPER = ("LIGO", "LIGOScientific:2014pky")
MERGER_PAPERS = (("mergers", "Ajith:2007kx"), ("Planck", "Planck:2018vyg"))

# The recorded data on the left panel is GW150914 itself: its ~1000-author
# byline stands in for the collaboration, the way papers like it are usually
# cited, rather than truncating to one name and "et al.".
GW150914_KEY = "ligoscientificcollaborationandvirgocollaborationObservationGravitationalWaves2016"
GW150914_FORMAT = replace(CITE_LABELLED_FORMAT, collaboration="LIGO Collaboration")


class MergerOnSensitivityPlotSlide(Clicks, DeckSlide, MergerOnSensitivityPlot):
    """The left panel becomes real LIGO data partway through, so its citation
    joins the detector paper under the same "LIGO" label."""

    CITE = (LIGO_PAPER, *MERGER_PAPERS)
    CITE_CORNER = DR  # under the plot, clear of the LIGO figure's time axis

    def citation(self):
        ligo = [*cite("LIGOScientific:2014pky"), format_reference(BIB[GW150914_KEY], GW150914_FORMAT)]
        items = [("LIGO", ligo), *[(label, cite(*keys)) for label, *keys in MERGER_PAPERS]]
        return labelled_citation(items, fmt=CITE_LABELLED_FORMAT)


class SensitivityLandscapeSlide(Clicks, DeckSlide, SensitivityBuildUp):
    """The landscape without AEDGE: AION-km is the one gap filler here."""

    GAP_FILLERS = ("AION-km",)
    CITE = (
        LIGO_PAPER,
        ("LISA", "LISA:2017pwj"),
        ("ET", "Punturo:2010zz"),
        ("AION-km", "Badurina:2019hst"),
        *MERGER_PAPERS,
    )
    CITE_CORNER = UR  # the plot fills the slide down to its axis label


class GradiometerGWStretchSlide(Clicks, DeckSlide, GradiometerGWStretchContinuous):
    """Continuous: lab time never stops between the first pulse and the ports,
    so the far cloud visibly splits L/c after the near one. One click runs the
    whole sequence; the stops are the set-up before it and the readout after."""


class DarkMatterScaleSlide(RunsOnIntoLoops, DeckSlide, DarkMatterScale):
    def hold(self):
        self.loop(super().hold)


class DarkMatterFieldSlide(RunsOnIntoLoops, DeckSlide, DarkMatterField):
    def hold(self):
        self.loop(super().hold)


class DarkMatterPhaseSlide(Clicks, DeckSlide, DarkMatterPhaseContinuous):
    """Continuous: the field keeps oscillating while the pulses fire, so one
    click runs the interferometer from the first pulse to the ports."""


# --- our prototype device -------------------------------------------------
class PrototypeDeviceSlide(SectionSlide):
    SECTION = r"Our prototype device"


class AIONCollabSlide(DeckSlide):
    """Who AION are and where."""

    def construct(self):
        title = slide_title(r"The AION collaboration")
        logo = load_image(MEDIA / "aion_logo_on_dark.png", height=1.0)
        logo.to_corner(UR, buff=0.4)
        uk_map = load_image(MEDIA / "aion_map.jpeg", height=6.0).move_to(DOWN * 0.45)
        self.play(FadeIn(title), FadeIn(logo), FadeIn(uk_map), run_time=0.8)


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

    CITE = ("strayCentralizedDesignProduction2024",)

    def construct(self):
        title = slide_title(r"AION chambers across the UK")
        figure = load_image(MEDIA / "aion_chambers.png", height=6.9)
        figure.next_to(title, DOWN, buff=0.25).set_x(0)
        self.play(FadeIn(title), FadeIn(figure), run_time=0.8)


class ExperimentSequenceSlide(DeckSlide, ExperimentSequenceSimple):
    """No stops: the shot plays through to the loaded lower trap and holds
    there. Its reference list is from AION.bib, in full, and as in the
    package cut to the papers its stages cite."""

    REFERENCES = [format_reference(ref, FULL) for ref in cite(
        "strayCentralizedDesignProduction2024",
        "pasatembouProgressUltracoldSr2024",
        "baynhamPrototypeDifferentialAtom2026",
    )][:SEQ_SIMPLE_REFERENCES]


class CoolingSequenceSlide(LoopingStages, DeckSlide, CoolingSequence):
    CITE = ("walkerHighfluxSourceCold2026", "pasatembouProgressUltracoldSr2024")


class DipoleTrapLoadingSlide(LoopingStages, DeckSlide, DipoleTrapLoading):
    pass


class VelocitySlicingSlide(LoopingStages, DeckSlide, VelocitySlicing):
    pass


# The paper the prototype's results are from.
DAI_PAPER = "baynhamPrototypeDifferentialAtom2026"


class LightShiftSignalSlide(Clicks, DeckSlide, LightShiftSignalContinuous):
    """Continuous: lab time never stops from the first pulse to the imaging,
    so the beam is a window the atoms fly through. The readout ends on the
    camera image of the two clouds, S left and P right, in place of the
    dials."""

    CITE = (DAI_PAPER,)

    # the image's two columns, as fractions of its width from the left
    IMAGE_COLUMNS = {"S": (0.27, ATOM_COLOR), "P": (0.78, KICKED_COLOR)}

    def readout_image(self):
        image = load_image(MEDIA / "atom_phase_image.png", height=5.4)
        image.to_edge(RIGHT, buff=0.25).set_y(-0.25)
        left, width = image.get_left()[0], image.width
        labels = VGroup(*[
            Tex(name, font_size=FONT_STATE, color=lighten(color))
            .move_to([left + f * width, image.get_top()[1] + 0.3, 0])
            for name, (f, color) in self.IMAGE_COLUMNS.items()
        ])
        return Group(image, labels)


class SignalInjectionSlide(LoopingStages, DeckSlide, SignalInjection):
    CITE = (DAI_PAPER,)


class LaserNoiseLissajousSlide(Clicks, DeckSlide, LaserNoiseLissajous):
    """The quiet run full size, then shrunk to the top panel with the noisy
    run below it, both onto the one Lissajous plot."""

    CITE = (DAI_PAPER,)


class AllanDeviationSlide(DeckSlide):
    """The differential phase's Allan deviation, built up as in
    plot_scripts/interferometer_data.py: the standard quantum limit alone,
    then the quiet run on it, then the noisy run beside it."""

    CITE = (DAI_PAPER,)

    def construct(self):
        title = slide_title(r"Allan deviation")
        steps = [load_image(FIGURES / f"{name}.png", height=6.6)
                 for name in ("adev_sql", "adev_lln", "adev")]
        for step in steps:
            step.next_to(title, DOWN, buff=0.2).set_x(0)
        self.play(FadeIn(title), FadeIn(steps[0]), run_time=0.8)
        for previous, step in zip(steps, steps[1:]):
            self.next_slide()
            self.play(FadeIn(step), run_time=0.6)
            self.remove(previous)


class ExtractedSignalSlide(DeckSlide):
    """Fig. 5a redrawn: each imprinted frequency found where it was put."""

    CITE = (DAI_PAPER,)

    def construct(self):
        title = slide_title(r"Extracted signals")
        figure = load_image(FIGURES / "signals.png", width=13.4)
        figure.next_to(title, DOWN, buff=0.35).set_x(0)
        self.play(FadeIn(title), FadeIn(figure), run_time=0.8)


# --- future plans ---------------------------------------------------------
class FuturePlansSlide(SectionSlide):
    SECTION = r"Future plans"


# The baseline figure (baseline.png, 295 x 707 px): its own "L", covered and
# relabelled with AION-10's length, and the arrow the label goes beside.
BASELINE_L_PX = ((258, 326), (294, 379))  # upper left, lower right of the "L"
BASELINE_ARROW_PX = (244, 383)  # the arrow's midpoint


class Aion10BeecroftSlide(DeckSlide):
    """The 10 m baseline and the stairwell it runs down, then the building cut
    away round it -- laid out as the row they end up in, so nothing moves.
    The building is a tall, narrow cutaway, so it takes nearly the full height
    of the slide to be legible; it sits right of the title, so it can rise
    level with it."""

    CITE = ("bongsAION10TechnicalDesign2025",)

    def construct(self):
        title = slide_title(r"AION-10 at Oxford")
        baseline = load_image(MEDIA / "baseline.png", height=5.2)
        stairwell = load_image(MEDIA / "stairwell.jpg", height=4.9)
        building = load_image(MEDIA / "beecroft.jpeg", height=config.frame_height - 0.4)
        Group(baseline, stairwell, building).arrange(RIGHT, buff=0.7).set_x(0.2)
        baseline.set_y(-0.45)
        stairwell.set_y(-0.45)
        building.set_y(0)

        # white over the figure's own "L", and the length in its place
        ul, dr = [image_point(baseline, *p) for p in BASELINE_L_PX]
        cover = Rectangle(width=dr[0] - ul[0], height=ul[1] - dr[1], stroke_width=0,
                          fill_color=WHITE, fill_opacity=1).move_to((ul + dr) / 2)
        # in the figure's own hand: black sans, along the arrow, where the L was
        length = Tex(r"\textsf{10\,m}", font_size=FONT_ANNOTATION, color=BLACK)
        length.rotate(PI / 2).move_to(cover)
        labelled = Group(baseline, cover, length)

        self.play(FadeIn(title), FadeIn(labelled), FadeIn(stairwell), run_time=0.8)
        self.next_slide()
        self.play(FadeIn(building, shift=LEFT * 0.3), run_time=0.8)


# The PX46 shaft in aice.png (1199 x 672 px): from under the surface building
# down to its rounded foot, with the arrow just clear of its right-hand side.
AICE_SHAFT_PX = ((940, 207), (940, 525))


class AICECernSlide(DeckSlide):
    """The AICE figure, which carries its own title, with the shaft's depth
    marked on it."""

    CITE = ("arduiniTechnicalProposalAtom2026",)

    def construct(self):
        figure = load_image(MEDIA / "aice.png", width=config.frame_width)

        def at(px, py):
            """A pixel of aice.png, on screen."""
            return figure.get_corner(UL) + [
                px / 1199 * figure.width,
                -py / 672 * figure.height,
                0,
            ]

        depth = DoubleArrow(
            *[at(*p) for p in AICE_SHAFT_PX],
            buff=0,
            stroke_width=PHOTO_LABEL_STROKE_WIDTH,
            color=PHOTO_LABEL_COLOR,
            tip_length=0.3,
            max_tip_length_to_length_ratio=0.1,
            max_stroke_width_to_length_ratio=10,
        )
        label = Tex(
            r"\textbf{150\,m}", font_size=FONT_PHOTO_LABEL, color=PHOTO_LABEL_COLOR
        )
        label.next_to(depth, RIGHT, buff=0.15)
        depth.set_stroke(**PHOTO_LABEL_OUTLINE, background=True, family=False)
        label.set_stroke(**PHOTO_LABEL_OUTLINE, background=True)
        self.play(FadeIn(figure), FadeIn(depth), FadeIn(label), run_time=0.8)



class AEDGESlide(Clicks, DeckSlide, AEDGESensitivity):
    """The two sensitivity plots as the talk has shown them, then a click
    puts AEDGE on both."""

    CITE = (
        LIGO_PAPER,
        ("LISA", "LISA:2017pwj"),
        ("ET", "Punturo:2010zz"),
        ("AION", "badurinaAIONAtomInterferometer2020"),
        ("AEDGE", "AEDGE:2019nxb"),
    )


# --- outro -------------------------------------------------------------------
class OutroSlide(DeckSlide):
    """Thank you: the Sr lab team down the left; Oliver and the AION logo
    over the AION collaboration down the right."""

    def construct(self):
        def labelled(image, text):
            label = Tex(text, font_size=FONT_LEGEND, color=lighten(GUIDE_COLOR))
            return Group(image, label.next_to(image, DOWN, buff=0.15))

        title = slide_title(r"Thank you for listening!")
        sr_group = labelled(
            load_image(MEDIA / "sr_lab_group.jpg", height=5.2), r"Sr lab team"
        )
        oliver = labelled(
            load_image(MEDIA / "oliver.png", height=2.3), r"Oliver Buchm\"uller, PI"
        )
        logo = load_image(MEDIA / "aion_logo_on_white.png", height=1.3)
        aion_group = labelled(
            load_image(MEDIA / "aion_group.png", width=6.0), r"AION collaboration"
        )
        top_right = Group(oliver, logo).arrange(RIGHT, buff=0.6)
        logo.match_y(oliver[0])
        right = Group(top_right, aion_group).arrange(DOWN, buff=0.3)
        Group(sr_group, right).arrange(RIGHT, buff=0.5).next_to(
            title, DOWN, buff=0.3
        ).set_x(0)
        self.play(FadeIn(title), FadeIn(sr_group), FadeIn(right), run_time=0.8)
