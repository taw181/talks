"""The clock interferometer's phase, read out as the angle between two hands.

ClockPhase introduces the readout the other scenes lean on. The clock is the
interferometer, not either arm: each arm carries a hand that turns only while
that arm is excited, but what the last pulse reads out is the angle between
the two hands, and a symmetric interferometer comes back to zero. The
gradiometer then compares two such clocks at opposite ends of the baseline
through one laser, and the wave changes the light travel time between them.
ClockPhaseTerms is the same scene with the phase budget on the end, naming the
laser term the gradiometer exists to cancel.
"""

import numpy as np
from manim import *

from aionanim.style import *
from aionanim.tools.clock import (
    CP_ARM,
    CP_DIAL,
    CP_OUT,
    CP_T,
    CP_T0,
    CP_Z,
    clock_rate,
    dial_hand,
    draw_ports,
    fire_vertical_pulse,
    make_clock_hand,
    make_dial,
    readout_equation,
    show_phase_budget,
)
from aionanim.tools.primitives import (
    draw_legs,
    make_atom,
    state_colors,
)


# where ClockPhaseTerms puts the budget: the open band between the note and
# the interferometer, left of the dial
CP_TERMS = np.array([-2.3, 2.0, 0.0])


class ClockPhase(Scene):
    """One interferometer -- one clock -- with the phase on show.

    The hands are drawn per arm, but the clock is not: what the last pulse
    reads out is the angle between them. See the comment above CLOCK_TURNS for
    why a single arm is not a clock and why the hands are still right.

    The null this establishes is the point: both arms spend the same time in
    |e>, so the hands come back together and the interferometer reads zero.
    Everything the gradiometer measures is a departure from that.
    """

    def construct(self):
        title = Tex(
            r"Phase: the interferometer is a clock",
            font_size=FONT_TITLE,
        ).to_corner(UL)
        note = VGroup(*[
            Tex(line, font_size=FONT_LEGEND, color=lighten(GUIDE_COLOR))
            for line in (
                r"a hand turns only while that arm is in $|e\rangle$",
                r"the readout is the angle between them",
            )
        ]).arrange(DOWN, buff=0.12, aligned_edge=LEFT)
        note.next_to(title, DOWN, buff=0.2).align_to(title, LEFT)
        self.play(FadeIn(title), FadeIn(note), run_time=0.9)

        a = np.array([CP_T0, CP_Z, 0.0])
        b = a + RIGHT * CP_T
        b_up = b + UP * CP_ARM
        c = b_up + RIGHT * CP_T
        rate = clock_rate(CP_T)

        # One tracker per arm, advanced only over the leg on which that arm is
        # the excited one.
        kicked_first = ValueTracker(0.0)  # up at the first pulse, down at the mirror
        kicked_last = ValueTracker(0.0)  # the other way round

        dial = make_dial(CP_DIAL, r"accumulated phase")
        self.play(FadeIn(dial), run_time=0.6)

        seed = make_atom(radius=CLOCK_ATOM_RADIUS).move_to(a)
        self.play(FadeIn(seed, scale=0.5), run_time=0.5)

        # --- the beamsplitter ----------------------------------------------
        fire_vertical_pulse(self, a[0], [seed])
        arm_lo = make_atom(
            radius=CLOCK_ATOM_RADIUS, opacity=SUPERPOSITION_OPACITY
        ).move_to(a)
        arm_hi = make_atom(
            KICKED_COLOR, radius=CLOCK_ATOM_RADIUS, opacity=SUPERPOSITION_OPACITY
        ).move_to(a)
        self.remove(seed)
        self.add(arm_lo, arm_hi)

        # The dial hands take the state colour too, so the one that is turning
        # is always the purple one -- which is the whole rule, shown rather
        # than asserted.
        big_lo = dial_hand(CP_DIAL, kicked_last, lighten(ATOM_COLOR))
        big_hi = dial_hand(CP_DIAL, kicked_first, lighten(KICKED_COLOR))
        hand_lo = make_clock_hand(arm_lo, kicked_last)
        hand_hi = make_clock_hand(arm_hi, kicked_first)
        self.add(hand_lo, hand_hi, big_lo, big_hi)

        # --- leg 1: the kicked arm is the excited one ------------------------
        draw_legs(self, [
            (arm_lo, a, b, ATOM_COLOR),
            (arm_hi, a, b_up, KICKED_COLOR),
        ], extra=[kicked_first.animate.set_value(rate * CP_T)])

        # --- the mirror: the arms swap state ----------------------------------
        # Bottom to top, following the beam. The two arms are driven in
        # opposite directions by the same pulse: the ground-state arm absorbs
        # a photon, and the excited one emits, so they swap states.
        # One pulse crosses both arms, so they swap together -- and each
        # arm's hand on the dial takes its new colour with it.
        fire_vertical_pulse(self, b[0], [arm_lo, arm_hi])
        self.play(
            state_colors(arm_lo, KICKED_COLOR),
            state_colors(arm_hi, ATOM_COLOR),
            big_lo.animate.set_color(lighten(KICKED_COLOR)),
            big_hi.animate.set_color(lighten(ATOM_COLOR)),
            run_time=0.5,
        )

        # --- leg 2: and so the other hand turns --------------------------------
        draw_legs(self, [
            (arm_lo, b, c, KICKED_COLOR),
            (arm_hi, b_up, c, ATOM_COLOR),
        ], extra=[kicked_last.animate.set_value(rate * CP_T)])

        # --- recombine ----------------------------------------------------------
        fire_vertical_pulse(self, c[0], [arm_lo])

        # --- and the readout ----------------------------------------------------
        # The arms are spent: the pulse has mixed them into the two output
        # states, so what leaves c is the ports, not the arms. Their hands go
        # with them -- the phase is a population from here on, and the dial is
        # where it is still shown as an angle.
        self.remove(arm_lo, arm_hi, hand_lo, hand_hi)
        gap = (kicked_first.get_value() - kicked_last.get_value()) % TAU
        draw_ports(self, c, CP_OUT, 0.5 * (1 + np.cos(gap)))
        self.play(Write(readout_equation()), run_time=1.0)

        result = VGroup(
            MathTex(r"\Phi = 0", font_size=FONT_STATE),
            Tex(
                # Kept short so it stays under the dial and clear of the
                # ports' own labels off to the left.
                r"equal time in $|e\rangle$",
                font_size=FONT_LEGEND, color=lighten(GUIDE_COLOR),
            ),
        ).arrange(DOWN, buff=0.2).next_to(dial, DOWN, buff=0.5)
        self.play(Flash(dial[0], **{**FLASH_STYLE, "color": AREA_COLOR}), run_time=0.5)
        self.play(FadeIn(result), run_time=1.0)
        self.wait(2.0)
        self.phase_budget(note, result)

    def phase_budget(self, note, result):
        """Hook: ClockPhaseTerms breaks the measured phase into its terms here.

        A no-op in this scene, so the plain version stays the short one.
        """


class ClockPhaseTerms(ClockPhase):
    """ClockPhase, and then what the phase it just read out is made of.

    Phi = Phi_interferometer + Phi_laser, with the separation term of the
    usual decomposition neglected as it is everywhere else in this talk. The
    first is the signal: omega_A times the difference in time the two arms
    spend excited, which is what a passing wave moves. The laser term is
    circled instead of struck, because it carries the laser's own phase noise
    and can be large enough to bury the first -- and it is exactly the term
    the gradiometer makes common to its two interferometers so that it cancels
    in the difference. That is the argument the gradiometer scenes go on to
    make, and this is where the term it cancels gets named.
    """

    def phase_budget(self, note, result):
        # The note has said its piece, and the band it sits in is the only one
        # wide enough for the equation.
        self.play(FadeOut(note), run_time=0.5)
        show_phase_budget(self, CP_TERMS, laser_struck=False, laser_label=r"noisy")
        self.wait(2.5)
