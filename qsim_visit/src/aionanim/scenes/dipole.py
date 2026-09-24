"""Loading the two dipole traps from the red MOT, then spin-polarising them.

Picks up where CoolingSequence leaves off: a small cold red MOT. Two
crossed dipole traps are switched on, one above the other, with a
transparency beam over the upper one. The MOT is held on the upper trap to
load it; the transparency beam then keeps those atoms dark, out of reach of
the 689 nm light. The MOT is let go, the hotter atoms drop, the field zero
is stepped down, and the MOT comes back on round the lower trap to load
that. With both traps full, the MOT goes off, the atoms are optically pumped
into m_F = +9/2 with swept, circularly polarised 689 nm light, and the bias
field is turned to point along the clock beam, ready for interferometry.

As in CoolingSequence, the level scheme lights the light that is on, the
timeline's next three blocks track the stage, and nothing is quantified
beyond the wavelengths.
"""

from manim import *

from aionanim.style import *
from aionanim.tools.cooling import SweepFan
from aionanim.tools.dipole import (
    LoadingAtoms,
    SpinHistogram,
    gaussian_band,
    gaussian_spot,
    make_bias_arrow,
    make_field_zero,
    make_mot_glow,
)
from aionanim.tools.sequence import STAGES, SrLevels, Timeline, stage_heading

# --- dipole-trap layout ---------------------------------------------------
DT_X = -3.0  # the vertical beam
DT_UPPER_Y = 0.7
DT_LOWER_Y = -1.6
DT_UPPER = np.array([DT_X, DT_UPPER_Y, 0])
DT_LOWER = np.array([DT_X, DT_LOWER_Y, 0])
DT_HORIZONTAL_HALF = 2.4  # half the drawn length of a horizontal beam
DT_HORIZONTAL_WIDTH = 0.16
DT_VERTICAL_WIDTH = 0.42
DT_VERTICAL_SPAN = (-4.1, 1.9)  # it runs off the bottom and stops short of the heading
DT_TRANSPARENCY_RADIUS = 0.42
DT_ZERO_X = DT_X - DT_HORIZONTAL_HALF - 0.15  # the B = 0 pointer's tip
DT_MOT_RADIUS = 2.6
DT_BIAS_CENTER = [0.25, -0.45, 0]
DT_HISTOGRAM_CENTER = [0.8, -2.5, 0]
DT_LEVELS_CENTER = [3.95, 1.3, 0]
DT_LEVELS_SCALE = 0.72
DT_TIMELINE_CENTER = [4.6, -2.95, 0]
DT_HEADING_CORNER = [-6.6, 3.7, 0]
DT_N_ATOMS = 150

# --- pacing ---------------------------------------------------------------
DT_SWITCH_TIME = 1.2
DT_LOAD_TIME = 3.0  # each trap's loading
DT_FALL_TIME = 0.9
DT_RECAPTURE_TIME = 1.5
DT_PUMP_TIME = 3.0
DT_RAMP_TIME = 2.0  # the bias field turning to the clock beam's axis
DT_HOLD = 1.5  # the pause after each stage, where a slide stops instead


def caption(text, heading):
    return Tex(text, font_size=FONT_CAPTION, color=lighten(GUIDE_COLOR)).next_to(
        heading, DOWN, buff=0.3, aligned_edge=LEFT)


class DipoleTrapLoading(Scene):
    def stage_break(self):
        """The pause after each stage. A slide wrapper stops here instead."""
        self.wait(DT_HOLD)

    def construct(self):
        levels = SrLevels(repump=True, transparency=True)
        fan = SweepFan()
        levels.add(fan)  # in the diagram's own coordinates, so before scaling
        levels.scale(DT_LEVELS_SCALE).move_to(DT_LEVELS_CENTER)
        stages = STAGES[3:6]
        timeline = Timeline(stages).move_to(DT_TIMELINE_CENTER)

        horizontal = VGroup(*[
            gaussian_band([DT_X - DT_HORIZONTAL_HALF, y, 0], [DT_X + DT_HORIZONTAL_HALF, y, 0],
                          DT_HORIZONTAL_WIDTH, TRAP_BEAM_COLOR)
            for y in (DT_UPPER_Y, DT_LOWER_Y)
        ])
        vertical = gaussian_band([DT_X, DT_VERTICAL_SPAN[0], 0], [DT_X, DT_VERTICAL_SPAN[1], 0],
                                 DT_VERTICAL_WIDTH, TRAP_BEAM_COLOR)
        trap_labels = VGroup(
            *[Tex("1064 nm", font_size=FONT_LEGEND, color=TRAP_BEAM_COLOR)
              .next_to(band, RIGHT, buff=0.15) for band in horizontal],
            Tex("813 nm", font_size=FONT_LEGEND, color=TRAP_BEAM_COLOR)
            .next_to(vertical, RIGHT, buff=0.15).set_y(-3.5),
        )
        transparency = gaussian_spot(DT_UPPER, DT_TRANSPARENCY_RADIUS, TRANSITION_488_COLOR,
                                     opacity=TRANSPARENCY_OPACITY)
        transparency_label = Tex("488 nm", font_size=FONT_LEGEND, color=TRANSITION_488_COLOR)
        transparency_label.next_to(transparency, UL, buff=0.0).shift(LEFT * 0.1)
        traps = VGroup(vertical, horizontal, trap_labels)

        mot_center = (DT_UPPER + DT_LOWER) / 2
        mot = make_mot_glow(mot_center, DT_MOT_RADIUS)
        zero = make_field_zero(DT_UPPER_Y, DT_ZERO_X)
        atoms = LoadingAtoms(DT_N_ATOMS, DT_UPPER, DT_LOWER)
        bias = make_bias_arrow(DT_BIAS_CENTER)
        histogram = SpinHistogram().move_to(DT_HISTOGRAM_CENTER)

        # where CoolingSequence left off: a small red MOT, all the light but the 689 off
        self.add(mot, levels, atoms)
        self.play(FadeIn(timeline), FadeIn(zero), *levels.drive("689"))

        # --- the upper trap ---
        heading = stage_heading(stages[0]).move_to(DT_HEADING_CORNER, aligned_edge=UL)
        step = caption(r"traps, transparency beam and repumps on", heading)
        self.play(*timeline.activate(0), FadeIn(heading), FadeIn(step),
                  FadeIn(traps), FadeIn(transparency), FadeIn(transparency_label),
                  *levels.drive("689", "488", "679", "707", "return"),
                  run_time=DT_SWITCH_TIME)
        step = self.recaption(step, r"MOT held on the upper trap", heading)
        # the transparency beam puts the trapped atoms out of the MOT light's reach
        self.play(atoms.load_upper.animate.set_value(1),
                  atoms.glow_upper.animate(rate_func=rush_into).set_value(0),
                  run_time=DT_LOAD_TIME)
        self.stage_break()

        # --- the lower trap ---
        heading, step = self.next_stage(timeline, 1, heading, step,
                                        r"MOT released: the hotter atoms fall")
        self.play(FadeOut(mot), atoms.glow_lower.animate.set_value(0),
                  *levels.drive("488", "679", "707", "return"), run_time=0.5)
        self.play(atoms.fall.animate.set_value(1), zero.animate.set_y(DT_LOWER_Y),
                  rate_func=linear, run_time=DT_FALL_TIME)
        step = self.recaption(step, r"MOT back on round the lower trap", heading)
        self.play(FadeIn(mot), atoms.glow_lower.animate.set_value(1),
                  atoms.recapture.animate.set_value(1),
                  *levels.drive("689", "488", "679", "707", "return"),
                  run_time=DT_RECAPTURE_TIME)
        self.play(atoms.load_lower.animate.set_value(1), run_time=DT_LOAD_TIME)
        self.stage_break()

        # --- spin polarisation ---
        heading, step = self.next_stage(timeline, 2, heading, step,
                                        r"MOT off; pumped into $m_F = +\tfrac{9}{2}$")
        self.play(FadeOut(mot), FadeOut(zero), FadeOut(transparency),
                  FadeOut(transparency_label), atoms.glow_lower.animate.set_value(0),
                  FadeIn(bias), FadeIn(histogram),
                  *levels.drive("679", "707", "return"), run_time=DT_SWITCH_TIME)
        # the atoms light up faintly while they scatter the pumping light
        self.play(fan.shown.animate.set_value(1),
                  atoms.glow_upper.animate.set_value(0.5),
                  atoms.glow_lower.animate.set_value(0.5), run_time=0.6)
        self.play(histogram.pump.animate.set_value(1), run_time=DT_PUMP_TIME)
        step = self.recaption(step, r"bias field turned to the clock beam's axis", heading)
        self.play(fan.shown.animate.set_value(0), *levels.drive(),
                  atoms.glow_upper.animate.set_value(0),
                  atoms.glow_lower.animate.set_value(0), run_time=0.6)
        self.play(Rotate(bias[0], PI / 2), run_time=DT_RAMP_TIME)
        self.stage_break()

    def recaption(self, step, text, heading):
        new_step = caption(text, heading)
        self.play(FadeOut(step), FadeIn(new_step), run_time=0.6)
        return new_step

    def next_stage(self, timeline, i, heading, step, text):
        """Move the timeline, heading and caption on to stage ``i`` of this
        scene's three; returns the new heading and caption."""
        new_heading = stage_heading(STAGES[3 + i]).move_to(DT_HEADING_CORNER, aligned_edge=UL)
        new_step = caption(text, new_heading)
        self.play(
            *timeline.activate(i),
            # out, then in: two headings crossing each other can't be read
            Succession(FadeOut(VGroup(heading, step), shift=UP * 0.2),
                       FadeIn(VGroup(new_heading, new_step), shift=UP * 0.2)),
            run_time=DT_SWITCH_TIME,
        )
        return new_heading, new_step
