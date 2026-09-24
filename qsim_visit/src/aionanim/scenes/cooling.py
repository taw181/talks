"""Cooling Sr: the three MOT stages that open every shot, as a cartoon.

A blue MOT on the broad 461 nm line catches the atoms, with the repumps
fetching back the ones that leak into 3P2; a red MOT on the narrow 689 nm
line, its frequency swept so it catches atoms at every Doppler shift the
blue MOT leaves them with, takes over; and with the sweep off and the beams
turned down, the narrowband red MOT squeezes the cloud small and cold,
with a seventh beam from below holding it up against gravity.

The Sr level scheme in the corner shows which light is on, and the first
three blocks of the sequence timeline say where in the shot this is. No
numbers beyond the wavelengths: this is the shape of the sequence, not
its settings.
"""

from manim import *

from aionanim.style import *
from aionanim.tools.cooling import (
    AtomCloud,
    Coils,
    MotBeams,
    SweepFan,
    make_up_beam,
)
from aionanim.tools.sequence import STAGES, SrLevels, Timeline, stage_heading

# --- cooling layout -------------------------------------------------------
COOL_MOT_CENTER = np.array([-3.0, -0.35, 0])
COOL_LEVELS_CENTER = [3.75, 1.3, 0]
COOL_LEVELS_SCALE = 0.85
COOL_TIMELINE_CENTER = [3.75, -2.85, 0]
COOL_HEADING_CORNER = [-6.6, 3.7, 0]  # upper left of the stage heading
COOL_TEMPERATURE_AT = COOL_MOT_CENTER + [2.9, -1.55, 0]
COOL_N_ATOMS = 140
COOL_NARROWBAND_INTENSITY = 0.3  # of the beams' starting brightness

# The cloud at the end of each stage: (radius, temperature). Cartoon values,
# chosen to read as "big and hot", "smaller and cooler", "small and cold".
COOL_CLOUD = {
    "blue_mot": (1.0, 1.0),
    "modulated_red_mot": (0.55, 0.12),
    "narrowband_red_mot": (0.2, 0.008),
}
COOL_TEMPERATURE_TEX = {
    "blue_mot": r"T \sim 1\,\mathrm{mK}",
    "modulated_red_mot": r"T \sim 10\,\mu\mathrm{K}",
    "narrowband_red_mot": r"T \sim 1\,\mu\mathrm{K}",
}

# --- pacing ---------------------------------------------------------------
COOL_SWITCH_TIME = 1.2  # one stage's light and field giving way to the next
COOL_LOAD_TIME = 3.0  # atoms arriving into the blue MOT
COOL_LEAK_TIME = 1.5
COOL_REPUMP_TIME = 1.5
COOL_SWEEP_TIME = 3.0  # the modulated MOT at work
COOL_RAMP_TIME = 3.0  # the narrowband MOT's intensity ramp
COOL_HOLD = 1.5  # the pause after each stage, where a slide stops instead


def temperature_tag(key):
    return MathTex(COOL_TEMPERATURE_TEX[key], font_size=FONT_TEMPERATURE,
                   color=lighten(GUIDE_COLOR)).move_to(COOL_TEMPERATURE_AT)


class CoolingSequence(Scene):
    def stage_break(self):
        """The pause after each stage. A slide wrapper stops here instead."""
        self.wait(COOL_HOLD)

    def construct(self):
        levels = SrLevels(repump=True)
        fan = SweepFan()
        levels.add(fan)  # in the diagram's own coordinates, so before scaling
        levels.scale(COOL_LEVELS_SCALE).move_to(COOL_LEVELS_CENTER)
        stages = STAGES[:3]
        timeline = Timeline(stages).move_to(COOL_TIMELINE_CENTER)

        coils = Coils(COOL_MOT_CENTER)
        blue = MotBeams(TRANSITION_461_COLOR, COOL_MOT_CENTER)
        red = MotBeams(TRANSITION_689_COLOR, COOL_MOT_CENTER)
        up = make_up_beam(TRANSITION_689_COLOR, COOL_MOT_CENTER)
        up_label = Tex("up beam", font_size=FONT_LEGEND, color=TRANSITION_689_COLOR)
        up_label.next_to(up[0].get_bottom(), RIGHT, buff=0.3).shift(UP * 0.05)

        radius, temperature = COOL_CLOUD["blue_mot"]
        cloud = AtomCloud(COOL_N_ATOMS, COOL_MOT_CENTER,
                          palette=(TRANSITION_461_COLOR, TRANSITION_689_COLOR),
                          radius=radius, temperature=temperature)
        cloud.arrived.set_value(0)

        self.play(FadeIn(levels), FadeIn(timeline), Create(coils))

        # --- blue MOT ---
        heading = stage_heading(stages[0]).move_to(COOL_HEADING_CORNER, aligned_edge=UL)
        tag = temperature_tag("blue_mot")
        self.play(*timeline.activate(0), *levels.drive("461"), FadeIn(heading),
                  FadeIn(blue), run_time=COOL_SWITCH_TIME)
        self.add(cloud)
        self.play(cloud.arrived.animate.set_value(1), rate_func=linear,
                  run_time=COOL_LOAD_TIME)
        self.play(FadeIn(tag))
        # a few atoms fall out of the cooling cycle into 3P2 and go dark...
        self.play(*levels.drive("461", "leak"), cloud.dark.animate.set_value(1),
                  run_time=COOL_LEAK_TIME)
        # ...until the repumps bring them back
        self.play(*levels.drive("461", "679", "707", "return"), run_time=0.6)
        self.play(cloud.dark.animate.set_value(0), run_time=COOL_REPUMP_TIME)
        self.stage_break()

        # --- modulated red MOT ---
        heading = self.next_stage(timeline, 1, heading, [
            *levels.drive(), fan.shown.animate.set_value(1),
            FadeOut(blue), FadeIn(red), coils.animate.set_gradient(COIL_WEAK_WIDTH),
            cloud.glow.animate.set_value(1),
        ])
        tag = self.cool(cloud, "modulated_red_mot", tag, run_time=COOL_SWEEP_TIME)
        self.stage_break()

        # --- narrowband red MOT ---
        heading = self.next_stage(timeline, 2, heading, [
            *levels.drive("689"), fan.shown.animate.set_value(0),
        ])
        self.play(FadeIn(up), FadeIn(up_label), run_time=COOL_SWITCH_TIME)
        tag = self.cool(cloud, "narrowband_red_mot", tag,
                        red.animate.set_intensity(COOL_NARROWBAND_INTENSITY),
                        run_time=COOL_RAMP_TIME)
        self.stage_break()

    def next_stage(self, timeline, i, heading, anims):
        """Move the timeline and heading on to stage ``i``, alongside
        ``anims``; returns the new heading."""
        new_heading = stage_heading(STAGES[i]).move_to(COOL_HEADING_CORNER, aligned_edge=UL)
        self.play(
            *timeline.activate(i), *anims,
            # out, then in: two headings crossing each other can't be read
            Succession(FadeOut(heading, shift=UP * 0.2), FadeIn(new_heading, shift=UP * 0.2)),
            run_time=COOL_SWITCH_TIME,
        )
        return new_heading

    def cool(self, cloud, key, tag, *anims, run_time):
        """Shrink and cool the cloud to where stage ``key`` leaves it, the
        temperature tag changing over halfway; returns the new tag."""
        radius, temperature = COOL_CLOUD[key]
        new_tag = temperature_tag(key)
        self.play(
            cloud.radius.animate.set_value(radius),
            cloud.temperature.animate.set_value(temperature),
            Succession(FadeOut(tag), FadeIn(new_tag)),
            *anims, run_time=run_time,
        )
        return new_tag
