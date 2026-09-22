"""Atom interferometry animations.

Shared geometry/style constants and mobject helpers live at module level so that
later scenes (mirror pulse, recombination, fringes) can reuse them.
"""

import numpy as np
from manim import *

# --- geometry -------------------------------------------------------------
# The frame is ~14.2 x 8 units. The incoming trajectory sits below centre so
# the 45 degree arm has room to climb without clipping the top edge.
BEAM_Y = -1.0
START_X = -6.0
SPLIT_X = -1.0
ARM_LENGTH = 4.0  # horizontal travel of each arm after the split

SPLIT_POINT = np.array([SPLIT_X, BEAM_Y, 0.0])

# One speed for the whole animation: every leg's run_time is distance / V, so
# the atom's velocity never visibly changes when it splits. That is the point
# of drawing the kick at 45 degrees -- the recoil is purely vertical and equal
# in magnitude to the forward motion.
V = 2.0

# --- style ----------------------------------------------------------------
ATOM_COLOR = BLUE_D
KICKED_COLOR = TEAL
LASER_COLOR = RED_C
SUPERPOSITION_OPACITY = 0.65


def make_atom(color=ATOM_COLOR, radius=0.18, opacity=1.0):
    """An atom drawn as a shaded sphere: a filled disc plus a specular highlight."""
    body = Circle(
        radius=radius,
        fill_color=color,
        fill_opacity=opacity,
        stroke_color=lighten(color),
        stroke_width=2,
    )
    highlight = Circle(
        radius=radius * 0.32,
        fill_color=WHITE,
        fill_opacity=0.55 * opacity,
        stroke_width=0,
    ).move_to(body.get_center() + radius * 0.4 * (UP + LEFT) / np.sqrt(2))
    return VGroup(body, highlight)


def lighten(color, amount=0.35):
    return interpolate_color(color, WHITE, amount)


def make_laser_pulse(x, y, length=2.2, n_cycles=4.5):
    """A Gaussian-enveloped sine wavepacket propagating along +y, centred on (x, y)."""
    sigma = length / 5.0
    k = 2 * PI * n_cycles / length

    packet = FunctionGraph(
        lambda t: 0.28 * np.sin(k * t) * np.exp(-((t / sigma) ** 2)),
        x_range=[-length / 2, length / 2, 0.01],
        color=LASER_COLOR,
        stroke_width=4,
    )
    packet.rotate(90 * DEGREES).move_to([x, y, 0])
    packet.set_stroke(opacity=[0.15, 1.0, 0.15])
    return packet


class SingleLaserKick(Scene):
    """One beamsplitter pulse: an atom splits into two momentum states."""

    def construct(self):
        # --- 1. setup ----------------------------------------------------
        guide = DashedLine(
            [START_X, BEAM_Y, 0],
            [config.frame_x_radius, BEAM_Y, 0],
            dash_length=0.12,
            stroke_width=2,
            stroke_opacity=0.3,
            color=GREY_B,
        )
        caption = Tex(
            r"Atom interferometry: one beamsplitter pulse", font_size=32
        ).to_corner(UL)

        self.play(FadeIn(guide), FadeIn(caption), run_time=1.0)

        # --- 2. incoming atom --------------------------------------------
        atom = make_atom().move_to([START_X, BEAM_Y, 0])
        in_label = MathTex(r"|g,\,p\rangle", font_size=34, color=lighten(ATOM_COLOR))
        in_label.add_updater(lambda m: m.next_to(atom, UP, buff=0.25))

        self.play(FadeIn(atom, scale=0.5), FadeIn(in_label), run_time=0.6)
        self.play(
            atom.animate.shift(RIGHT * (SPLIT_X - START_X)),
            rate_func=linear,
            run_time=(SPLIT_X - START_X) / V,
        )
        in_label.clear_updaters()

        # --- 3. laser pulse from below -----------------------------------
        pulse_travel = BEAM_Y - (-config.frame_y_radius - 0.6)
        pulse = make_laser_pulse(SPLIT_X, -config.frame_y_radius - 0.6)
        k_arrow = Arrow(
            ORIGIN, UP * 0.7, buff=0, stroke_width=3, color=LASER_COLOR,
            max_tip_length_to_length_ratio=0.3,
        )
        k_label = MathTex(r"\vec{k}", font_size=32, color=LASER_COLOR)
        k_group = VGroup(k_arrow, k_label.next_to(k_arrow, RIGHT, buff=0.12))
        k_group.next_to([SPLIT_X, -config.frame_y_radius, 0], UP, buff=0.1).shift(
            LEFT * 0.9
        )

        self.add(pulse)
        self.play(
            pulse.animate.shift(UP * pulse_travel),
            FadeIn(k_group),
            rate_func=linear,
            run_time=pulse_travel / (V * 1.6),
        )

        # --- 4. the split -------------------------------------------------
        straight = make_atom(opacity=SUPERPOSITION_OPACITY).move_to(SPLIT_POINT)
        kicked = make_atom(KICKED_COLOR, opacity=SUPERPOSITION_OPACITY).move_to(
            SPLIT_POINT
        )

        recoil = Arrow(
            SPLIT_POINT,
            SPLIT_POINT + UP * 1.2,
            buff=0,
            stroke_width=4,
            color=LASER_COLOR,
            max_tip_length_to_length_ratio=0.22,
        )
        recoil_label = MathTex(r"\hbar k", font_size=34, color=LASER_COLOR).next_to(
            recoil, LEFT, buff=0.15
        )
        pulse_caption = MathTex(
            r"\pi/2\ \text{pulse}", font_size=32, color=LASER_COLOR
        ).next_to(SPLIT_POINT, DOWN, buff=0.9)

        self.play(
            Flash(atom, color=LASER_COLOR, flash_radius=0.55, line_length=0.3),
            FadeOut(pulse, scale=0.6),
            FadeOut(k_group),
            FadeOut(in_label),
            run_time=0.5,
        )
        self.remove(atom)
        self.add(straight, kicked)
        self.play(
            GrowArrow(recoil),
            FadeIn(recoil_label),
            Write(pulse_caption),
            run_time=0.7,
        )

        # --- 5. diverging arms -------------------------------------------
        straight_trace = TracedPath(
            straight.get_center, stroke_color=ATOM_COLOR, stroke_width=3
        )
        kicked_trace = TracedPath(
            kicked.get_center, stroke_color=KICKED_COLOR, stroke_width=3
        )
        self.add(straight_trace, kicked_trace)

        # Equal horizontal component on both arms -> a true 45 degree kick.
        self.play(
            straight.animate.shift(RIGHT * ARM_LENGTH),
            kicked.animate.shift(ARM_LENGTH * (RIGHT + UP)),
            rate_func=linear,
            run_time=ARM_LENGTH / V,
        )

        # --- 6. final state labels ---------------------------------------
        straight_label = MathTex(
            r"|g,\,p\rangle", font_size=36, color=lighten(ATOM_COLOR)
        ).next_to(straight, DOWN, buff=0.3)
        kicked_label = MathTex(
            r"|e,\,p + \hbar k\rangle", font_size=36, color=lighten(KICKED_COLOR)
        ).next_to(kicked, RIGHT, buff=0.3)

        self.play(Write(straight_label), Write(kicked_label), run_time=1.2)
        self.wait(1.5)
