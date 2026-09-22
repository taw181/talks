"""AION: single-photon clock interferometry.

These are space-time diagrams, not plan views: the horizontal axis is time and
the vertical axis is height along the baseline, which is also the direction the
lasers propagate and the direction of the photon recoil. An atom at rest is a
horizontal worldline; a photon is a steep diagonal.

Drawing the photons with a finite slope is the whole point of the gradiometer
scene -- the light reaches the far cloud later than the near one, so a single
laser writes its phase into the two interferometers at different retarded
times. That is what the single-photon clock scheme buys: the laser's own phase
noise is common to both and cancels in the difference.

The slope is exaggerated by many orders of magnitude. For a 100 m baseline
L/c is ~0.3 us against an interrogation time T of order a second.
"""

import numpy as np
from manim import *

from style import *
from atom_interferometry import draw_legs, make_atom, make_guide, state_colors

# --- gradiometer geometry -------------------------------------------------
GR_T = 3.8  # time between pulses
GR_T0 = -5.0  # time of the first pulse, at the lower cloud
GR_ARM = 1.05  # arm separation, i.e. (hbar k / m) T in real units
GR_LOWER_Z = -2.9
GR_BASELINE = 3.5  # L
GR_UPPER_Z = GR_LOWER_Z + GR_BASELINE
GR_LASER_Z = -3.85  # the laser sits at the bottom of the shaft
GR_LAG = 0.42  # light travel time across L, hugely exaggerated
GR_SLOPE = GR_LAG / GR_BASELINE  # dt/dz for a photon worldline


def photon_worldline(x_at_lower, z_from, z_to):
    """The segment of a pulse's worldline between two heights.

    `x_at_lower` is when it passes the lower cloud, so the geometry of every
    pulse is fixed by one number and the two crossings stay consistent.
    """
    start = [x_at_lower + GR_SLOPE * (z_from - GR_LOWER_Z), z_from, 0]
    end = [x_at_lower + GR_SLOPE * (z_to - GR_LOWER_Z), z_to, 0]
    return Line(start, end, color=LASER_COLOR, stroke_width=PULSE_STROKE_WIDTH)


def vertices(z0, lag):
    """The four corners of one interferometer in the (time, height) plane."""
    a = np.array([GR_T0 + lag, z0, 0.0])
    b = a + RIGHT * GR_T
    b_up = b + UP * GR_ARM
    c = b_up + RIGHT * GR_T
    return a, b, b_up, c


class Gradiometer(Scene):
    """Two interferometers, one baseline, one laser."""

    def construct(self):
        title = Tex(
            r"Gradiometer: one laser, two interferometers", font_size=FONT_TITLE
        ).to_corner(UL)

        # The laser is a fixed object, so its worldline is horizontal.
        laser = make_guide(
            [-config.frame_x_radius + 0.4, GR_LASER_Z, 0],
            [config.frame_x_radius - 0.4, GR_LASER_Z, 0],
        )
        laser_tag = Tex("laser", font_size=FONT_LEGEND, color=LASER_COLOR).next_to(
            laser, UP, buff=0.12
        ).align_to(laser, LEFT)

        # axes of the space-time diagram
        # above the laser line, not below it -- below is off the bottom edge
        t_axis = Tex("time $\\rightarrow$", font_size=FONT_LEGEND,
                     color=lighten(GUIDE_COLOR))
        t_axis.next_to(laser, UP, buff=0.12).align_to(laser, RIGHT)
        z_axis = Tex("height", font_size=FONT_LEGEND, color=lighten(GUIDE_COLOR))
        z_axis.rotate(90 * DEGREES).to_edge(LEFT, buff=0.18).set_y(0.3)

        low = vertices(GR_LOWER_Z, 0.0)
        up = vertices(GR_UPPER_Z, GR_LAG)

        baseline = DoubleArrow(
            [GR_T0 - 0.75, GR_LOWER_Z, 0],
            [GR_T0 - 0.75, GR_UPPER_Z, 0],
            buff=0,
            stroke_width=3,
            color=lighten(GUIDE_COLOR),
            max_tip_length_to_length_ratio=0.06,
        )
        baseline_label = MathTex(
            r"L", font_size=FONT_STATE, color=lighten(GUIDE_COLOR)
        ).next_to(baseline, LEFT, buff=0.12)

        self.play(
            FadeIn(title), FadeIn(laser), FadeIn(laser_tag),
            FadeIn(t_axis), FadeIn(z_axis), run_time=1.0,
        )
        self.play(GrowFromCenter(baseline), FadeIn(baseline_label), run_time=0.7)

        # --- the two clouds ----------------------------------------------
        atoms = {
            "low": [make_atom().move_to(low[0]), make_atom(KICKED_COLOR).move_to(low[0])],
            "up": [make_atom().move_to(up[0]), make_atom(KICKED_COLOR).move_to(up[0])],
        }
        seed_low, seed_up = make_atom().move_to(low[0]), make_atom().move_to(up[0])
        self.play(FadeIn(seed_low, scale=0.5), FadeIn(seed_up, scale=0.5), run_time=0.6)

        # --- pulse 1: the beamsplitter -----------------------------------
        self.fire(GR_T0, flash=[seed_low, seed_up])
        for pair, v in ((atoms["low"], low), (atoms["up"], up)):
            for a in pair:
                a.set_opacity(SUPERPOSITION_OPACITY).move_to(v[0])
        self.remove(seed_low, seed_up)
        self.add(*atoms["low"], *atoms["up"])

        # The offset between the two interferometers is the reason for all of
        # this, so name it rather than leaving it as an unexplained shift.
        lag_note = MathTex(
            r"L/c\ \text{later}", font_size=FONT_LEGEND, color=LASER_COLOR
        ).next_to(up[0], UP, buff=0.3)
        self.play(FadeIn(lag_note), run_time=0.5)

        draw_legs(self, [
            (atoms["low"][0], low[0], low[1], ATOM_COLOR),
            (atoms["low"][1], low[0], low[2], KICKED_COLOR),
            (atoms["up"][0], up[0], up[1], ATOM_COLOR),
            (atoms["up"][1], up[0], up[2], KICKED_COLOR),
        ], fade=[lag_note])

        # --- pulse 2: the mirror ------------------------------------------
        self.fire(GR_T0 + GR_T, flash=[a for p in atoms.values() for a in p])
        self.play(
            *[state_colors(p[0], KICKED_COLOR) for p in atoms.values()],
            *[state_colors(p[1], ATOM_COLOR) for p in atoms.values()],
            run_time=0.5,
        )
        draw_legs(self, [
            (atoms["low"][0], low[1], low[3], KICKED_COLOR),
            (atoms["low"][1], low[2], low[3], ATOM_COLOR),
            (atoms["up"][0], up[1], up[3], KICKED_COLOR),
            (atoms["up"][1], up[2], up[3], ATOM_COLOR),
        ])

        # --- pulse 3: recombine -------------------------------------------
        self.fire(GR_T0 + 2 * GR_T, flash=[atoms["low"][0], atoms["up"][0]])

        # --- the readout ---------------------------------------------------
        phi_low = MathTex(
            r"\Phi_{\text{lower}}", font_size=FONT_ANNOTATION, color=lighten(ATOM_COLOR)
        ).next_to(low[3], RIGHT, buff=0.35)
        phi_up = MathTex(
            r"\Phi_{\text{upper}}", font_size=FONT_ANNOTATION, color=lighten(ATOM_COLOR)
        ).next_to(up[3], RIGHT, buff=0.35)
        self.play(Write(phi_low), Write(phi_up), run_time=0.9)

        signal = VGroup(
            MathTex(
                r"\Delta\Phi = \Phi_{\text{upper}} - \Phi_{\text{lower}}",
                font_size=FONT_ANNOTATION,
            ),
            Tex(
                r"laser phase noise is common to both, and cancels",
                font_size=FONT_LEGEND,
                color=lighten(GUIDE_COLOR),
            ),
        ).arrange(DOWN, buff=0.22).to_corner(UR)
        self.play(FadeIn(signal), run_time=1.0)
        self.wait(2.0)

    def fire(self, x_at_lower, flash):
        """Send one pulse up the baseline, reaching the far cloud later."""
        below = photon_worldline(x_at_lower, GR_LASER_Z, GR_LOWER_Z)
        across = photon_worldline(x_at_lower, GR_LOWER_Z, GR_UPPER_Z)
        beyond = photon_worldline(x_at_lower, GR_UPPER_Z, config.frame_y_radius + 0.3)

        low_hits = [m for m in flash if m.get_center()[1] < 0]
        up_hits = [m for m in flash if m.get_center()[1] >= 0]

        self.play(Create(below), rate_func=linear, run_time=0.45)
        self.play(*[Flash(m, **FLASH_STYLE) for m in low_hits], run_time=0.35)
        self.play(Create(across), rate_func=linear, run_time=0.7)
        self.play(*[Flash(m, **FLASH_STYLE) for m in up_hits], run_time=0.35)
        self.play(Create(beyond), rate_func=linear, run_time=0.3)
        self.play(
            *[FadeOut(m) for m in (below, across, beyond)], run_time=0.3
        )


# --- large momentum transfer geometry -------------------------------------
# Same space-time frame. Each pulse adds one photon recoil to the upper arm,
# so its worldline steepens by a fixed slope per kick while the lower arm
# stays put; the arms end up n*hbar*k apart instead of hbar*k.
LMT_T0 = -5.0
LMT_Z = -2.8
LMT_STEP = 1.4  # time between kicks in the ladder
LMT_TAIL = 1.6  # free flight after the last kick
LMT_U = 0.35  # height gained per unit time, per photon recoil
LMT_KICKS = 4


def lmt_points(slope_per_kick):
    """Worldline corners for an arm gaining `slope_per_kick(i)` on kick i."""
    pts = [np.array([LMT_T0, LMT_Z, 0.0])]
    for i in range(LMT_KICKS):
        dt = LMT_TAIL if i == LMT_KICKS - 1 else LMT_STEP
        pts.append(pts[-1] + np.array([dt, dt * slope_per_kick(i), 0.0]))
    return pts


def kick_worldline(point, from_below, steepness=0.12):
    """A photon's worldline arriving at `point` from below or from above."""
    edge = -config.frame_y_radius if from_below else config.frame_y_radius
    dx = steepness * abs(point[1] - edge)
    return Line(
        [point[0] - dx, edge, 0], point,
        color=LASER_COLOR, stroke_width=PULSE_STROKE_WIDTH,
    )


class LargeMomentumTransfer(Scene):
    """A ladder of single-photon kicks separates the arms by n hbar k."""

    def construct(self):
        title = Tex(
            r"Large momentum transfer: $n$ single-photon kicks",
            font_size=FONT_TITLE,
        ).to_corner(UL)
        note = Tex(
            r"colour is the internal state; slope is momentum",
            font_size=FONT_LEGEND,
            color=lighten(GUIDE_COLOR),
        ).next_to(title, DOWN, buff=0.2).align_to(title, LEFT)
        self.play(FadeIn(title), FadeIn(note), run_time=0.9)

        upper_pts = lmt_points(lambda i: (i + 1) * LMT_U)
        lower_pts = lmt_points(lambda i: 0.0)

        # --- the atom arrives ---------------------------------------------
        atom = make_atom().move_to([-config.frame_x_radius + 0.3, LMT_Z, 0])
        self.play(FadeIn(atom, scale=0.5), run_time=0.4)
        self.play(
            atom.animate.move_to(upper_pts[0]),
            rate_func=linear,
            run_time=(LMT_T0 - atom.get_center()[0]) / V,
        )

        lower = make_atom(opacity=SUPERPOSITION_OPACITY).move_to(upper_pts[0])
        upper = make_atom(opacity=SUPERPOSITION_OPACITY).move_to(upper_pts[0])
        self.remove(atom)
        self.add(lower, upper)

        # --- the ladder -----------------------------------------------------
        # Kicks alternate direction: absorb an upward photon, then emit a
        # downward one. Either way the atom is pushed up by hbar k, and its
        # internal state flips back and forth.
        states = [KICKED_COLOR, ATOM_COLOR]
        for i in range(LMT_KICKS):
            ray = kick_worldline(upper_pts[i], from_below=(i % 2 == 0))
            self.play(Create(ray), rate_func=linear, run_time=0.45)
            self.play(
                Flash(upper, **FLASH_STYLE),
                FadeOut(ray),
                state_colors(upper, states[i % 2]),
                run_time=0.4,
            )
            draw_legs(self, [
                (upper, upper_pts[i], upper_pts[i + 1], states[i % 2]),
                (lower, lower_pts[i], lower_pts[i + 1], ATOM_COLOR),
            ])

        # --- what the ladder bought -----------------------------------------
        # A single kick, drawn for the same total time, for comparison.
        single = DashedLine(
            upper_pts[0],
            upper_pts[0] + np.array([
                upper_pts[-1][0] - upper_pts[0][0],
                (upper_pts[-1][0] - upper_pts[0][0]) * LMT_U,
                0.0,
            ]),
            dash_length=0.12,
            stroke_width=3,
            color=lighten(GUIDE_COLOR),
            stroke_opacity=0.55,
        )
        single_label = MathTex(
            r"n = 1", font_size=FONT_LEGEND, color=lighten(GUIDE_COLOR)
        ).next_to(single.get_end(), UP, buff=0.14)  # clear of the n*hbar*k arrow

        gap = DoubleArrow(
            [upper_pts[-1][0] + 0.55, lower_pts[-1][1], 0],
            [upper_pts[-1][0] + 0.55, upper_pts[-1][1], 0],
            buff=0,
            stroke_width=3,
            color=lighten(KICKED_COLOR),
            max_tip_length_to_length_ratio=0.05,
        )
        gap_label = MathTex(
            r"n\hbar k", font_size=FONT_STATE, color=lighten(KICKED_COLOR)
        ).next_to(gap, RIGHT, buff=0.18)

        self.play(Create(single), FadeIn(single_label), run_time=0.9)
        self.play(GrowFromCenter(gap), FadeIn(gap_label), run_time=0.7)

        scaling = MathTex(
            r"\Phi \;\propto\; n\,k\,a\,T^{2}", font_size=FONT_STATE
        ).to_corner(DR)
        self.play(Write(scaling), run_time=1.0)
        self.wait(2.0)
