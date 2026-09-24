"""Two clock interferometers on one baseline, driven by one laser.

Drawing the photons with a finite slope is the whole point of this scene --
the light reaches the far cloud later than the near one, so a single laser
writes its phase into the two interferometers at different retarded times.
That is what the single-photon clock scheme buys: the laser's own phase noise
is common to both and cancels in the difference.
"""

from manim import *

from aionanim.style import *
from aionanim.tools.clock import (
    clock_rate,
    dial_hand,
    draw_ports,
    leg_slope,
    ground_share,
    make_clock_hand,
    make_dial,
    show_phase_budget,
)
from aionanim.tools.gradiometer import (
    GR_DIALS,
    GR_DIAL_RADIUS,
    GR_LAG,
    GR_LOWER_Z,
    GR_OUT,
    GR_T,
    GR_T0,
    GR_TERMS,
    GR_TERMS_WIDTH,
    GR_UPPER_Z,
    fire_pulse,
    gradiometer_frame,
    vertices,
)
from aionanim.tools.primitives import (
    draw_legs,
    make_atom,
    state_colors,
)


class Gradiometer(Scene):
    """Two interferometers, one baseline, one laser -- so, two clocks.

    The quiet twin of GradiometerGW: same geometry, same dials, nothing
    passing through. Both clocks therefore read the same, which is the null
    the wave has to break, and it ends on what the difference is made of.
    """

    def construct(self):
        gradiometer_frame(self, r"Gradiometer: one laser, two interferometers")

        low = vertices(GR_LOWER_Z, 0.0)
        up = vertices(GR_UPPER_Z, GR_LAG)

        # Nothing is passing through, so the two pulse intervals are equal in
        # both interferometers -- but they are still read off the vertices,
        # the same way GradiometerGW reads them, so the two scenes cannot
        # drift apart.
        rate = clock_rate(GR_T)
        excited = {
            cloud: (v[1][0] - v[0][0], v[3][0] - v[2][0])
            for cloud, v in (("low", low), ("up", up))
        }
        phase = {
            cloud: (ValueTracker(0.0), ValueTracker(0.0))
            for cloud in ("low", "up")
        }

        dials = VGroup(*[
            make_dial(GR_DIALS[c], cap, GR_DIAL_RADIUS)
            for c, cap in (
                ("low", r"$\Phi_{\text{lower}}$"),
                ("up", r"$\Phi_{\text{upper}}$"),
            )
        ])
        hand_key = Tex(
            r"each hand turns while in $|e\rangle$",
            font_size=FONT_LEGEND, color=lighten(GUIDE_COLOR),
        ).to_corner(UL).shift(DOWN * 0.7)
        self.play(FadeIn(dials), FadeIn(hand_key), run_time=0.6)

        # --- the two clouds ----------------------------------------------
        atoms = {
            cloud: [
                make_atom(radius=CLOCK_ATOM_RADIUS).move_to(v[0]),
                make_atom(KICKED_COLOR, radius=CLOCK_ATOM_RADIUS).move_to(v[0]),
            ]
            for cloud, v in (("low", low), ("up", up))
        }
        seed_low = make_atom(radius=CLOCK_ATOM_RADIUS).move_to(low[0])
        seed_up = make_atom(radius=CLOCK_ATOM_RADIUS).move_to(up[0])
        self.play(FadeIn(seed_low, scale=0.5), FadeIn(seed_up, scale=0.5), run_time=0.6)

        # --- pulse 1: the beamsplitter -----------------------------------
        fire_pulse(self, GR_T0, flash=[seed_low, seed_up])
        for pair, v in ((atoms["low"], low), (atoms["up"], up)):
            for a in pair:
                a.set_opacity(SUPERPOSITION_OPACITY).move_to(v[0])
        self.remove(seed_low, seed_up)
        self.add(*atoms["low"], *atoms["up"])

        # index 0 is the arm kicked at the mirror, index 1 the arm kicked now
        hands = [
            make_clock_hand(atoms[cloud][k], phase[cloud][k])
            for cloud in ("low", "up")
            for k in (0, 1)
        ]
        self.add(*hands)
        big = VGroup()
        for cloud in ("low", "up"):
            big.add(
                dial_hand(
                    GR_DIALS[cloud], phase[cloud][0], lighten(ATOM_COLOR),
                    GR_DIAL_RADIUS,
                ),
                dial_hand(
                    GR_DIALS[cloud], phase[cloud][1], lighten(KICKED_COLOR),
                    GR_DIAL_RADIUS,
                ),
            )
        self.add(big)

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
        ], fade=[lag_note], extra=[
            phase[c][1].animate.set_value(rate * excited[c][0])
            for c in ("low", "up")
        ])

        # --- pulse 2: the mirror ------------------------------------------
        fire_pulse(self, GR_T0 + GR_T, flash=[a for p in atoms.values() for a in p])
        self.play(
            *[state_colors(p[0], KICKED_COLOR) for p in atoms.values()],
            *[state_colors(p[1], ATOM_COLOR) for p in atoms.values()],
            *[big[k].animate.set_color(lighten(KICKED_COLOR)) for k in (0, 2)],
            *[big[k].animate.set_color(lighten(ATOM_COLOR)) for k in (1, 3)],
            run_time=0.5,
        )
        draw_legs(self, [
            (atoms["low"][0], low[1], low[3], KICKED_COLOR),
            (atoms["low"][1], low[2], low[3], ATOM_COLOR),
            (atoms["up"][0], up[1], up[3], KICKED_COLOR),
            (atoms["up"][1], up[2], up[3], ATOM_COLOR),
        ], extra=[
            phase[c][0].animate.set_value(rate * excited[c][1])
            for c in ("low", "up")
        ])

        # --- pulse 3: recombine -------------------------------------------
        fire_pulse(self, GR_T0 + 2 * GR_T, flash=[atoms["low"][0], atoms["up"][0]])

        # --- the ports ------------------------------------------------------
        # The arms are spent: that pulse couples the two states each pair is
        # in, so what leaves the last vertex is a pair of ports sharing the
        # atoms out by the angle between the hands. Nothing is passing
        # through, both interferometers spent equal time excited, and so both
        # send everything into |g, p> -- the null the wave has to break, drawn
        # against an empty excited port so that it reads as one.
        self.remove(*atoms["low"], *atoms["up"], *hands)
        for cloud, v in (("low", low), ("up", up)):
            draw_ports(
                self, v[3], GR_OUT,
                ground_share(phase[cloud][1], phase[cloud][0]),
                slope=leg_slope(v[1], v[3]), labels=False,
            )

        # --- the readout ---------------------------------------------------
        # Both dials have come round to the same place, so say what is done
        # with them -- and then what that difference is made of. The laser term
        # is the one that changes its verdict here: common to both
        # interferometers, so it goes out of the difference entirely.
        self.play(
            *[Flash(d[0], **{**FLASH_STYLE, "color": AREA_COLOR}) for d in dials],
            run_time=0.5,
        )
        show_phase_budget(
            self, GR_TERMS, laser_struck=True, laser_label=r"cancelled",
            difference_lhs=r"\Delta\Phi = \Phi_{\text{upper}} - \Phi_{\text{lower}}",
            max_width=GR_TERMS_WIDTH,
        )
        self.wait(2.5)
