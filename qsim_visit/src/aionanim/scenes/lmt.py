"""Large momentum transfer: more photon recoils, arms further apart."""

import numpy as np
from manim import *

from aionanim.style import *
from aionanim.tools.lmt import (
    LMT_KICKS,
    LMT_T0,
    LMT_U,
    LMT_Z,
    kick_worldline,
    lmt_points,
)
from aionanim.tools.primitives import (
    draw_legs,
    make_atom,
    state_colors,
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
