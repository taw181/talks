"""Large momentum transfer: more photon recoils, arms further apart.

LargeMomentumTransfer is the ladder on its own: ten kicks to one arm.
LMTMachZehnder puts it to use, stretching each pulse of the pi/2 - pi - pi/2
sequence into n, beside the plain n = 1 interferometer it replaces.
"""

import numpy as np
from manim import *

from aionanim.style import *
from aionanim.tools.lmt import (
    LMT_KICKS,
    LMT_T0,
    LMT_U,
    LMT_Z,
    LMZ_END,
    LMZ_ORDER,
    LMZ_T0,
    LMZ_U,
    LMZ_Z,
    kick_worldline,
    lmt_points,
    lmz_history,
)
from aionanim.tools.primitives import (
    draw_legs,
    make_atom,
    state_colors,
)


class LargeMomentumTransfer(Scene):
    """A ladder of single-photon kicks separates the arms by n hbar k."""

    def beat(self):
        """The pause after each step: nothing here, a click on the slide version."""

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
        self.beat()

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
            # the first two at full pace, while the idea lands; the rest quicker
            pace = 1.0 if i < 2 else 0.6
            ray = kick_worldline(upper_pts[i], from_below=(i % 2 == 0))
            self.play(Create(ray), rate_func=linear, run_time=0.45 * pace)
            self.play(
                Flash(upper, **FLASH_STYLE),
                FadeOut(ray),
                state_colors(upper, states[i % 2]),
                run_time=0.4 * pace,
            )
            draw_legs(self, [
                (upper, upper_pts[i], upper_pts[i + 1], states[i % 2]),
                (lower, lower_pts[i], lower_pts[i + 1], ATOM_COLOR),
            ])
            if i == 0:  # one kick explained; the rest of the ladder runs on
                self.beat()
        self.beat()

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
        self.beat()

        scaling = MathTex(
            r"\Phi \;\propto\; n\,k\,a\,T^{2}", font_size=FONT_STATE
        ).to_corner(DR)
        self.play(Write(scaling), run_time=1.0)
        self.wait(2.0)


class LMTMachZehnder(Scene):
    """pi/2 - pi - pi/2 with every pulse stretched into n = LMZ_ORDER.

    Stops (beat) once the atom is in, and after each of the three stages:
    beam splitter, mirror, beam splitter. Then the enclosed area, with the
    n = 1 interferometer over the same time drawn dashed inside it.
    """

    STAGES = (r"beam splitter", r"mirror", r"beam splitter")

    def beat(self):
        """The pause after each step: nothing here, a click on the slide version."""

    def construct(self):
        title = Tex(
            rf"Large momentum transfer in the Mach--Zehnder: $n = {LMZ_ORDER}$",
            font_size=FONT_TITLE,
        ).to_corner(UL)
        note = Tex(
            r"colour is the internal state; slope is momentum",
            font_size=FONT_LEGEND,
            color=lighten(GUIDE_COLOR),
        ).next_to(title, DOWN, buff=0.2).align_to(title, LEFT)
        self.play(FadeIn(title), FadeIn(note), run_time=0.9)

        history = lmz_history()
        colors = {"g": ATOM_COLOR, "e": KICKED_COLOR}
        start = np.array([LMZ_T0, LMZ_Z, 0.0])

        atom = make_atom().move_to([-config.frame_x_radius + 0.3, LMZ_Z, 0])
        self.play(FadeIn(atom, scale=0.5), run_time=0.4)
        self.play(atom.animate.move_to(start), rate_func=linear,
                  run_time=(LMZ_T0 - atom.get_center()[0]) / V)
        self.beat()

        atoms = {"lower": atom}
        paths = {"lower": [start], "upper": [start]}
        captions = {}
        for k, step in enumerate(history):
            stage = step["stage"]
            if stage not in captions:
                xs = [h["x"] for h in history if h["stage"] == stage]
                captions[stage] = Tex(
                    self.STAGES[stage], font_size=FONT_LEGEND, color=LASER_COLOR,
                ).move_to([(xs[0] + xs[-1]) / 2, -config.frame_y_radius + 0.35, 0])
                self.play(FadeIn(captions[stage]), run_time=0.3)

            # one pulse: a ray from its side, as far as the furthest arm it reaches
            if step["kind"] == "split":
                reach = start
            elif step["kind"] == "merge":
                reach = step["legs"][0][1]
            else:
                points = [point for _, point, _ in step["hits"]]
                furthest = max if step["from_below"] else min
                reach = furthest(points, key=lambda p: p[1])
            ray = kick_worldline(reach, step["from_below"], steepness=0.0)
            self.play(Create(ray), rate_func=linear, run_time=0.3)

            if step["kind"] == "split":
                lower = make_atom(opacity=SUPERPOSITION_OPACITY).move_to(start)
                upper = make_atom(KICKED_COLOR, opacity=SUPERPOSITION_OPACITY).move_to(start)
                self.remove(atom)
                self.add(lower, upper)
                atoms = {"lower": lower, "upper": upper}
                self.play(Flash(upper, **FLASH_STYLE), FadeOut(ray), run_time=0.35)
            elif step["kind"] == "merge":
                point = step["legs"][0][1]
                ports = {
                    "port_g": make_atom(opacity=SUPERPOSITION_OPACITY).move_to(point),
                    "port_e": make_atom(KICKED_COLOR, opacity=SUPERPOSITION_OPACITY)
                    .move_to(point),
                }
                self.play(Flash(atoms["lower"], **FLASH_STYLE), FadeOut(ray), run_time=0.35)
                self.remove(*atoms.values())
                self.add(*ports.values())
                atoms = ports
            else:
                self.play(
                    *[Flash(atoms[arm], **FLASH_STYLE) for arm, _, _ in step["hits"]],
                    *[state_colors(atoms[arm], colors[state])
                      for arm, _, state in step["hits"]],
                    FadeOut(ray),
                    run_time=0.35,
                )

            draw_legs(self, [(atoms[arm], a, b, colors[state])
                             for arm, a, b, state in step["legs"]])
            for arm, _, b, _ in step["legs"]:
                if arm in paths:
                    paths[arm].append(b)
            last_of_stage = k + 1 == len(history) or history[k + 1]["stage"] != stage
            if last_of_stage:
                self.beat()

        # --- what it bought ---------------------------------------------------
        # both paths run from the split to the merge (the ports are not in them)
        loop = Polygon(*paths["upper"], *reversed(paths["lower"]), **LOOP_AREA_STYLE)
        phase = MathTex(r"\Phi", font_size=FONT_PHASE, color=lighten(AREA_COLOR))
        phase.move_to(loop.get_center_of_mass())

        # the n = 1 interferometer over the same time: one recoil, a quarter
        # of the frame high where this one fills it
        half = LMZ_END / 2
        plain = DashedVMobject(Polygon(
            start,
            start + [half, half * LMZ_U, 0],
            start + [LMZ_END, half * LMZ_U, 0],
            start + [half, 0, 0],
        ).set_stroke(lighten(GUIDE_COLOR), 3, opacity=0.7), num_dashes=60)
        plain_label = MathTex(r"n = 1", font_size=FONT_LEGEND, color=lighten(GUIDE_COLOR))
        plain_label.move_to(start + [half, half * LMZ_U / 2, 0])

        self.play(FadeIn(loop), FadeIn(phase), run_time=0.8)
        self.play(Create(plain), FadeIn(plain_label), run_time=1.0)
        self.beat()
        # bottom right, under the dashed n = 1 and clear of the caption row
        scaling = MathTex(
            r"\Phi \;\propto\; n\,k\,a\,T^{2}", font_size=FONT_STATE
        ).to_edge(RIGHT).set_y(LMZ_Z + 0.9)
        self.play(Write(scaling), run_time=1.0)
        self.wait(2.0)
