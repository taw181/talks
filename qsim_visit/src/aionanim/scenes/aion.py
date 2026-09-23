"""AION: single-photon clock interferometry.

These are space-time diagrams, not plan views: the horizontal axis is time and
the vertical axis is distance along the baseline, which is also the direction the
lasers propagate and the direction of the photon recoil. An atom at rest is a
horizontal worldline; a photon is a steep diagonal.

Drawing the photons with a finite slope is the whole point of the gradiometer
scene -- the light reaches the far cloud later than the near one, so a single
laser writes its phase into the two interferometers at different retarded
times. That is what the single-photon clock scheme buys: the laser's own phase
noise is common to both and cancels in the difference.

The slope is exaggerated by many orders of magnitude. For a 100 m baseline
L/c is ~0.3 us against an interrogation time T of order a second.

SinglePhotonMachZehnder is the sequence on its own, with the photons
resolved: every pulse is a wavepacket that climbs the baseline into the atom,
and at the mirror the excited arm is driven the other way by stimulated
emission -- one photon arrives and two leave, so that arm recoils by -hbar k.
Beside it is the two-level system the whole scheme rests on, the Sr clock
transition, which doubles as the figure's key because its levels carry the
colours the two arms are drawn in.

ClockPhase introduces the readout the other scenes lean on. The clock is the
interferometer, not either arm: each arm carries a hand that turns only while
that arm is excited, but what the last pulse reads out is the angle between
the two hands, and a symmetric interferometer comes back to zero. The
gradiometer then compares two such clocks at opposite ends of the baseline
through one laser, and the wave changes the light travel time between them.
ClockPhaseTerms is the same scene with the phase budget on the end, naming the
laser term the gradiometer exists to cancel.

DarkMatterPhase is ClockPhase with that null broken. An oscillating ultralight
scalar field modulates the fundamental constants, and with them the Sr clock
frequency: omega_A -> omega_A [1 + eps cos(omega_phi t + theta)]. The mirror
hands the excitation from one arm to the other halfway through, so the two
arms integrate omega_A over different stretches of the oscillation, the hands
come back to different angles and the two output ports split. Same instrument
as the gravitational-wave scenes, pointed at a different source.

GradiometerGW and GradiometerGWStretch are the same figure with a wave passing
through, drawn the two ways people draw one. GradiometerGW modulates the light
travel time and leaves the freely falling atoms on the worldlines they already
had, which is where the signal actually comes from; GradiometerGWStretch bows
the worldlines so the baseline visibly breathes, which is the picture most
people carry. The same h(t) runs along the top of both, they take their pulse
timing from the same place, and so their dials read the same phase.
"""

import numpy as np
from manim import *

from aionanim.style import *
from aionanim.tools.primitives import (
    draw_legs,
    make_atom,
    make_guide,
    state_colors,
)
from aionanim.tools.spacetime import (
    no_displacement,
    run_to,
    worldline,
    wound,
    growing_band,
    wound_with_shift,
    carry,
    growing_trail,
    draw_wavy_legs,
)
from aionanim.tools.gradiometer import (
    GR_T,
    GR_T0,
    GR_ARM,
    GR_LOWER_Z,
    GR_UPPER_Z,
    GR_LAG,
    GR_SLOPE,
    GR_MID_Z,
    GR_OUT,
    vertices,
    gradiometer_frame,
    fire_pulse,
    GR_TERMS,
    GR_TERMS_WIDTH,
    GR_SIGNAL,
    GR_DIAL_RADIUS,
    GR_DIALS,
    sweep_pulse,
    GR_LASER_GAP,
)
from aionanim.tools.clock import (
    clock_rate,
    make_clock_hand,
    make_dial,
    dial_hand,
    phase_sweep,
    ground_share,
    draw_ports,
    fly_ports,
    show_phase_budget,
)
from aionanim.tools.gradiometer_gw import (
    GW_PULSES,
    GW_TRACE_X,
    gw_lag,
    gw_arrival_lags,
    quiet_arrival,
    gw_displacement,
    make_strain_trace,
    strain_marker,
    gw_vertices,
    arrival_note,
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
                labels=False,
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


class GradiometerGW(Scene):
    """A wave modulates the light travel time, so the pulses arrive early or late.

    The honest picture of what AION measures. The atoms are freely falling test
    masses, so their worldlines keep the shape they had in Gradiometer; what
    the wave changes is L/c, and with it the retarded time at which the laser
    writes its phase into the upper interferometer.
    """

    def construct(self):
        gradiometer_frame(
            self, r"A gravitational wave modulates the light travel time"
        )

        trace, dots = make_strain_trace()
        self.play(FadeIn(trace[0]), Create(trace[1]), FadeIn(trace[2]), run_time=1.2)

        lags = [gw_lag(t) for t in GW_PULSES]  # cloud to cloud, i.e. L/c
        low_lags = gw_arrival_lags(GR_LOWER_Z)
        up_lags = gw_arrival_lags(GR_UPPER_Z)
        low = gw_vertices(GR_LOWER_Z, low_lags)
        up = gw_vertices(GR_UPPER_Z, up_lags)

        # What the wave has done, in one number per interferometer: the upper
        # one's two pulse intervals are no longer equal, so its arms no longer
        # spend equal time excited.
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
        ).to_corner(UR)
        self.play(FadeIn(dials), FadeIn(hand_key), run_time=0.6)

        # --- the two clouds ----------------------------------------------
        atoms = {
            "low": [
                make_atom(radius=CLOCK_ATOM_RADIUS).move_to(low[0]),
                make_atom(KICKED_COLOR, radius=CLOCK_ATOM_RADIUS).move_to(low[0]),
            ],
            "up": [
                make_atom(radius=CLOCK_ATOM_RADIUS).move_to(up[0]),
                make_atom(KICKED_COLOR, radius=CLOCK_ATOM_RADIUS).move_to(up[0]),
            ],
        }
        seeds = {
            "low": make_atom(radius=CLOCK_ATOM_RADIUS).move_to(low[0]),
            "up": make_atom(radius=CLOCK_ATOM_RADIUS).move_to(up[0]),
        }
        self.play(
            FadeIn(seeds["low"], scale=0.5), FadeIn(seeds["up"], scale=0.5),
            run_time=0.6,
        )

        # A tracker only runs its updaters if it is in the scene, and it has to
        # be in it ahead of the hands that read it or they lag a frame behind
        # the phase they are drawing. Invisible either way, and the stop-start
        # sequence neither needs nor minds it.
        self.add(*[t for pair in phase.values() for t in pair])

        self.low, self.up = low, up
        self.lags, self.low_lags, self.up_lags = lags, low_lags, up_lags
        self.rate, self.excited, self.phase = rate, excited, phase
        self.atoms, self.seeds, self.dots = atoms, seeds, dots
        self.hands, self.big = [], VGroup()
        self.fly()

        # --- the readout ---------------------------------------------------
        # Each face carries its own interferometer's phase, so what is read
        # out is the difference between the two -- which stays the measurement
        # if the lower one's hands ever come apart as well.
        sweeps = []
        for cloud in ("low", "up"):
            sweep, gap = phase_sweep(
                GR_DIALS[cloud], phase[cloud][1], phase[cloud][0], GR_DIAL_RADIUS
            )
            if gap > 0.01:
                sweeps.append(sweep)
        # And the same angle as a population. The wave pulled the far cloud's
        # two pulse intervals further apart than the near cloud's, so the two
        # interferometers split their ports by different amounts. That
        # difference is the signal: one laser, two clocks, and only what is
        # not common to both survives.
        self.remove(*atoms["low"], *atoms["up"], *self.hands)
        self.close(sweeps)

        signal = VGroup(
            Tex(
                r"the wave changes the light travel time, more for the far cloud",
                font_size=FONT_LEGEND, color=lighten(GUIDE_COLOR),
            ),
            # A proportionality rather than the equation: what a talk needs
            # off this slide is which knobs it turns, and the prefactor
            # 2 omega_A / c is fixed the moment the atom is chosen. What is
            # left is the baseline, the photon kicks, and the interrogation
            # time -- the last through a sin^2 rather than a power, because it
            # is a resonance: the pulses land on crest, trough and crest when
            # omega_GW T = pi, which is the case drawn, and the response falls
            # away as T^2 well below it.
            MathTex(
                r"\Delta\Phi = \Phi_{\text{upper}} - \Phi_{\text{lower}}"
                r" \propto n\,L\,h\,\sin^2(\omega_{\text{GW}} T/2)",
                font_size=FONT_ANNOTATION,
            ),
        ).arrange(DOWN, buff=0.22).move_to(GR_SIGNAL)
        if signal.width > GR_TERMS_WIDTH:
            signal.scale(GR_TERMS_WIDTH / signal.width)
        self.play(FadeIn(signal), run_time=1.0)
        self.wait(2.0)

    # --- what the variants, and the stretched picture, agree on ----------
    # The wave in this scene changes the light travel time and nothing else,
    # so the clouds sit still on the baseline and every pulse crosses them
    # where the baseline says. GradiometerGWStretch draws the other half of
    # the same wave -- it moves the clouds -- and overrides exactly these
    # three, which is the whole difference between the two pictures once the
    # pulse timing is shared.
    REFERENCE = True  # the dashed quiet-baseline ghost beside each pulse

    def vertices(self, cloud):
        return self.low if cloud == "low" else self.up

    def nominal(self, cloud):
        """Where on the baseline a cloud belongs."""
        return GR_LOWER_Z if cloud == "low" else GR_UPPER_Z

    def displacement(self, cloud):
        """How the wave bows this cloud's worldline. Not at all, here."""
        return no_displacement

    def rest(self, cloud):
        """Where the cloud is when lab time starts."""
        return self.nominal(cloud) + self.displacement(cloud)(GW_PULSES[0])

    def crossing(self, cloud, k):
        """Where the cloud is when pulse k reaches it."""
        return self.nominal(cloud)

    def pulse_note(self, k):
        """What pulse k is captioned with, if anything.

        The arrivals are what this picture is about, so the first two are each
        named against the dashed ghost beside them -- and the ghost has to be
        named once too, or "late" is late against nothing in particular. The
        third has nothing left to say that the two before it have not.
        """
        if k == 0:
            return VGroup(
                arrival_note(self.up[0], self.lags[0]),
                Tex(
                    r"no wave", font_size=FONT_LEGEND, color=lighten(GUIDE_COLOR)
                ).move_to([GW_PULSES[0] + 1.25, GR_MID_Z, 0]),
            )
        if k == 1:
            return arrival_note(self.up[1], self.lags[1])
        return None

    def open_arms(self, cloud):
        """One cloud's seed becomes two arms, each carrying a hand.

        Per cloud rather than for both at once, because the pulse does not
        reach them at the same time: the far cloud is split L/c after the near
        one, which is the whole quantity this figure is about.
        """
        v = self.vertices(cloud)
        for atom in self.atoms[cloud]:
            atom.set_opacity(SUPERPOSITION_OPACITY).move_to(v[0])
        self.remove(self.seeds[cloud])
        self.add(*self.atoms[cloud])
        # index 0 is the arm kicked at the mirror, index 1 the arm kicked now
        hands = [
            make_clock_hand(self.atoms[cloud][k], self.phase[cloud][k])
            for k in (0, 1)
        ]
        self.hands.extend(hands)
        self.add(*hands)
        big = VGroup(
            dial_hand(
                GR_DIALS[cloud], self.phase[cloud][0], lighten(ATOM_COLOR),
                GR_DIAL_RADIUS,
            ),
            dial_hand(
                GR_DIALS[cloud], self.phase[cloud][1], lighten(KICKED_COLOR),
                GR_DIAL_RADIUS,
            ),
        )
        self.big.add(*big)
        self.add(big)

    def port_extra(self):
        """What rides along with the output ports. Nothing, unless lab time does."""
        return ()

    def close(self, sweeps):
        """Read both dials, then let each pair of ports fly."""
        self.play(*[FadeIn(m) for m in sweeps], run_time=0.7)
        for cloud, v in (("low", self.low), ("up", self.up)):
            draw_ports(
                self, v[3], GR_OUT,
                ground_share(self.phase[cloud][1], self.phase[cloud][0]),
                labels=False, extra=self.port_extra(),
            )

    def fly(self):
        """Three pulses and two legs, one at a time.

        The atoms wait for each pulse to be drawn, which buys the pulse the
        wall time to be read and costs the wave the right to keep moving while
        it is. GradiometerGWContinuous makes the other trade.
        """
        low, up, lags = self.low, self.up, self.lags
        atoms, phase, rate, excited = self.atoms, self.phase, self.rate, self.excited

        # --- pulse 1: the beamsplitter, arriving late on a crest ----------
        self.play(FadeIn(self.dots[0], scale=0.4), run_time=0.3)
        fire_pulse(
            self, GW_PULSES[0] + self.low_lags[0],
            flash=[self.seeds["low"], self.seeds["up"]],
            lag=lags[0], reference=True, quiet_x=quiet_arrival(0),
            note=self.pulse_note(0),
        )
        self.open_arms("low")
        self.open_arms("up")

        draw_legs(self, [
            (atoms["low"][0], low[0], low[1], ATOM_COLOR),
            (atoms["low"][1], low[0], low[2], KICKED_COLOR),
            (atoms["up"][0], up[0], up[1], ATOM_COLOR),
            (atoms["up"][1], up[0], up[2], KICKED_COLOR),
        ], extra=[
            phase[c][1].animate.set_value(rate * excited[c][0])
            for c in ("low", "up")
        ])

        # --- pulse 2: the mirror, arriving early on a trough --------------
        self.play(FadeIn(self.dots[1], scale=0.4), run_time=0.3)
        fire_pulse(
            self, GW_PULSES[1] + self.low_lags[1],
            flash=[a for p in atoms.values() for a in p],
            lag=lags[1], reference=True, quiet_x=quiet_arrival(1),
            note=self.pulse_note(1),
        )
        big = self.big
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
        self.play(FadeIn(self.dots[2], scale=0.4), run_time=0.3)
        fire_pulse(
            self, GW_PULSES[2] + self.low_lags[2],
            flash=[atoms["low"][0], atoms["up"][0]],
            lag=lags[2], reference=True, quiet_x=quiet_arrival(2),
        )


class RunsContinuously:
    """Mixin: a gradiometer scene whose lab time never stops.

    Only the pulse-and-leg sequence differs between a stop-start scene and a
    continuous one, and it differs the same way for both pictures of the wave.
    So it is written once here and mixed in ahead of whichever scene it is
    running, which is what lets the stretched baseline have a continuous
    variant for free. Everything it needs -- the vertices, where each cloud is
    when a pulse crosses it, how its worldlines bow -- it asks the scene for.

    What the mixin buys these scenes in particular: the one quantity a
    gradiometer figure exists to show -- that the far cloud is split, mirrored
    and recombined L/c after the near one -- is a statement about *when*
    things happen to each of them. Stopping the atoms to draw a pulse makes it
    unshowable, so the stop-start scenes say it in words: a caption reading
    "arrives late" beside a dashed ghost. Here the pulse climbs while the
    atoms fly, the near cloud splits, and the far cloud is still a single seed
    for L/c afterwards. The caption becomes a label on something the frame is
    doing.

    The price is that the pulses are quick. Run at V a crest pulse crosses the
    frame in under a second and the trough pulse, whose light travel time the
    wave has very nearly closed up, in a tenth of one -- which is not a defect
    but the measurement: the two are drawn at the ratio the wave put between
    them rather than dilated to the same length and annotated.
    """

    def port_extra(self):
        # By the same amount the ports run, not to the same place: the last
        # pulse has carried lab time a little past the final corner, and what
        # has to match is the rate, so the wave keeps step with the atoms.
        return [self.clock.animate.set_value(self.clock.get_value() + GR_OUT)]

    def close(self, sweeps):
        """The sectors arrive while the ports fly, not before them.

        Same reason the pulses do not stop the atoms: what leaves the last
        vertex is still the interferometer running on in its own time. And the
        angle between a pair of hands and the split between a pair of ports
        are one fact, so they belong in one beat rather than two.
        """
        fly_ports(
            self,
            [
                (v[3], ground_share(self.phase[cloud][1], self.phase[cloud][0]))
                for cloud, v in (("low", self.low), ("up", self.up))
            ],
            GR_OUT, labels=False,
            extra=[*self.port_extra(), *[FadeIn(m) for m in sweeps]],
        )

    def open_arms(self, cloud):
        v, clock = self.vertices(cloud), self.clock
        # Trails before atoms, so an atom is never drawn under the line it is
        # drawing. One per leg rather than per arm: the two arms swap states
        # at the mirror, so the colour belongs to the leg.
        self.add(
            growing_trail([v[0], v[1]], ATOM_COLOR, clock, self.displacement(cloud)),
            growing_trail([v[1], v[3]], KICKED_COLOR, clock, self.displacement(cloud)),
            growing_trail([v[0], v[2]], KICKED_COLOR, clock, self.displacement(cloud)),
            growing_trail([v[2], v[3]], ATOM_COLOR, clock, self.displacement(cloud)),
        )
        super().open_arms(cloud)
        pair = self.atoms[cloud]
        carry(pair[0], worldline([v[0], v[1], v[3]], self.displacement(cloud)), clock)
        carry(pair[1], worldline([v[0], v[2], v[3]], self.displacement(cloud)), clock)

    def mirror(self, cloud):
        """The pulse hands the excitation over, on the instant it arrives."""
        pair = self.atoms[cloud]
        pair[0][0].set_fill(KICKED_COLOR).set_stroke(lighten(KICKED_COLOR))
        pair[1][0].set_fill(ATOM_COLOR).set_stroke(lighten(ATOM_COLOR))
        k = 0 if cloud == "low" else 2
        self.big[k].set_color(lighten(KICKED_COLOR))
        self.big[k + 1].set_color(lighten(ATOM_COLOR))

    def fly(self):
        low, up, lags = self.low, self.up, self.lags

        # Lab time starts when the first pulse leaves the laser, so the first
        # thing the scene does is send it.
        clock = self.clock = ValueTracker(GW_PULSES[0])
        self.add(clock, strain_marker(clock))
        for k, dot in enumerate(self.dots):
            dot.add_updater(lambda m, k=k: m.set_opacity(
                1.0 if clock.get_value() >= GW_PULSES[k] else 0.0
            ))
        self.add(self.dots)

        for cloud in ("low", "up"):
            v = self.vertices(cloud)
            disp = self.displacement(cloud)
            # The seeds are already falling when the pulse is fired, so they
            # fly the stretch between the laser's column and their own corner
            # rather than waiting on it.
            start = np.array([GW_PULSES[0], self.rest(cloud), 0.0])
            self.add(growing_trail([start, v[0]], ATOM_COLOR, clock, disp))
            carry(self.seeds[cloud], worldline([start, v[0]], disp), clock)
            self.phase[cloud][1].add_updater(
                wound(clock, self.rate, v[0][0], v[1][0])
            )
            self.phase[cloud][0].add_updater(
                wound(clock, self.rate, v[2][0], v[3][0])
            )

        # --- pulse 1: the beamsplitter -------------------------------------
        drawn = self.shoot(
            0, near=[low[0]], far=[up[0]],
            on_near=lambda: self.open_arms("low"),
            on_far=lambda: self.open_arms("up"),
        )

        # --- pulse 2: the mirror, arriving early on a trough --------------
        # gw_vertices puts a cloud's two arms at the same time, so one flash
        # does for both even though the upper arm is an arm's height further
        # up the column. The slope that separates them is a fortieth of the
        # one the figure is about.
        drawn = self.shoot(
            1, near=[low[1], low[2]], far=[up[1], up[2]], fade=drawn,
            on_near=lambda: self.mirror("low"),
            on_far=lambda: self.mirror("up"),
        )

        # --- pulse 3: recombine -------------------------------------------
        drawn = self.shoot(2, near=[low[3]], far=[up[3]], fade=drawn)
        run_to(
            self, clock, clock.get_value() + PULSE_LINGER,
            *[FadeOut(m) for m in drawn],
        )

    def shoot(self, k, near, far, fade=(), on_near=None, on_far=None):
        """One pulse, fired the way this scene's geometry has it arriving."""
        return sweep_pulse(
            self, self.clock, GW_PULSES[k] + self.low_lags[k],
            near=near, far=far, lag=self.lags[k],
            reference=self.REFERENCE, quiet_x=quiet_arrival(k),
            note=self.pulse_note(k),
            z_near=self.crossing("low", k), z_far=self.crossing("up", k),
            fade=fade, on_near=on_near, on_far=on_far,
        )


class GradiometerGWContinuous(RunsContinuously, GradiometerGW):
    """GradiometerGW with the pulses climbing while the atoms fly."""


class GradiometerGWStretch(GradiometerGW):
    """The same wave drawn as a stretching baseline, for comparison.

    The picture most people carry: the wave pushes the ends of the baseline
    apart and together, so the two clouds bow in antiphase about its midpoint
    and L breathes. It is the proper-distance picture rather than the one the
    experiment reads out -- GradiometerGW is what the phase actually comes
    from -- but the two are the same wave, and the same h(t) runs above both.

    A subclass of it for the three things that differ: the clouds move, so a
    pulse crosses them where the wave has put them rather than where the
    baseline says; and with the bow itself on the page there is nothing for a
    dashed ghost to be a reference against.
    """

    REFERENCE = False

    def displacement(self, cloud):
        z0 = self.nominal(cloud)
        return lambda t: gw_displacement(t, z0)

    def crossing(self, cloud, k):
        lags = self.low_lags if cloud == "low" else self.up_lags
        return self.nominal(cloud) + self.displacement(cloud)(GW_PULSES[k] + lags[k])

    def pulse_note(self, k):
        """The bow is the claim here, so it is named once and not again.

        Nothing in this picture arrives early or late -- it is drawn in proper
        distance, where what the wave does is move the clouds -- so the
        arrival captions would be naming something the frame is not showing.
        """
        if k:
            return None
        return Tex(
            r"$L$ stretches and squeezes", font_size=FONT_LEGEND, color=STRAIN_COLOR
        ).next_to(self.up[0], DOWN, buff=0.35).shift(RIGHT * 0.9)

    def construct(self):
        gradiometer_frame(
            self, r"A gravitational wave stretches and squeezes the baseline"
        )

        trace, dots = make_strain_trace(r"\Delta L(t)")
        self.play(FadeIn(trace[0]), Create(trace[1]), FadeIn(trace[2]), run_time=1.2)

        # Where each cloud would sit with nothing passing through, so the bow
        # is visibly a departure from something rather than just a wobble.
        rest = VGroup(*[
            make_guide([GW_TRACE_X[0], z, 0], [GW_TRACE_X[1], z, 0])
            for z in (GR_LOWER_Z, GR_UPPER_Z)
        ])
        self.play(FadeIn(rest), run_time=0.6)

        def low_disp(t):
            return gw_displacement(t, GR_LOWER_Z)

        def up_disp(t):
            return gw_displacement(t, GR_UPPER_Z)

        lags = [gw_lag(t) for t in GW_PULSES]  # cloud to cloud, i.e. L/c
        low_lags = gw_arrival_lags(GR_LOWER_Z)
        up_lags = gw_arrival_lags(GR_UPPER_Z)
        low = gw_vertices(GR_LOWER_Z, low_lags)
        up = gw_vertices(GR_UPPER_Z, up_lags)
        # Corners ride the wave; the legs between them bow to match.
        low = tuple(v + UP * low_disp(v[0]) for v in low)
        up = tuple(v + UP * up_disp(v[0]) for v in up)

        # The pulses land where they landed in GradiometerGW, so the arms come
        # apart by the same amount and the dial reads the same phase.
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
        ).to_corner(UR)
        self.play(FadeIn(dials), FadeIn(hand_key), run_time=0.6)

        atoms = {
            "low": [
                make_atom(radius=CLOCK_ATOM_RADIUS).move_to(low[0]),
                make_atom(KICKED_COLOR, radius=CLOCK_ATOM_RADIUS).move_to(low[0]),
            ],
            "up": [
                make_atom(radius=CLOCK_ATOM_RADIUS).move_to(up[0]),
                make_atom(KICKED_COLOR, radius=CLOCK_ATOM_RADIUS).move_to(up[0]),
            ],
        }
        seeds = {
            "low": make_atom(radius=CLOCK_ATOM_RADIUS).move_to(low[0]),
            "up": make_atom(radius=CLOCK_ATOM_RADIUS).move_to(up[0]),
        }
        self.play(
            FadeIn(seeds["low"], scale=0.5), FadeIn(seeds["up"], scale=0.5),
            run_time=0.6,
        )
        self.add(*[t for pair in phase.values() for t in pair])

        self.low, self.up = low, up
        self.lags, self.low_lags, self.up_lags = lags, low_lags, up_lags
        self.rate, self.excited, self.phase = rate, excited, phase
        self.atoms, self.seeds, self.dots = atoms, seeds, dots
        self.hands, self.big = [], VGroup()
        self.fly()

        # --- the readout -----------------------------------------------------
        # Each face carries its own interferometer's phase, so what is read
        # out is the difference between the two -- which stays the measurement
        # if the lower one's hands ever come apart as well.
        sweeps = []
        for cloud in ("low", "up"):
            sweep, gap = phase_sweep(
                GR_DIALS[cloud], phase[cloud][1], phase[cloud][0], GR_DIAL_RADIUS
            )
            if gap > 0.01:
                sweeps.append(sweep)
        # And the same angle as a population. The wave pulled the far cloud's
        # two pulse intervals further apart than the near cloud's, so the two
        # interferometers split their ports by different amounts. That
        # difference is the signal: one laser, two clocks, and only what is
        # not common to both survives.
        self.remove(*atoms["low"], *atoms["up"], *self.hands)
        self.close(sweeps)

        signal = VGroup(
            Tex(
                r"the wave changes the light travel time, more for the far cloud",
                font_size=FONT_LEGEND, color=lighten(GUIDE_COLOR),
            ),
            # A proportionality rather than the equation: what a talk needs
            # off this slide is which knobs it turns, and the prefactor
            # 2 omega_A / c is fixed the moment the atom is chosen. What is
            # left is the baseline, the photon kicks, and the interrogation
            # time -- the last through a sin^2 rather than a power, because it
            # is a resonance: the pulses land on crest, trough and crest when
            # omega_GW T = pi, which is the case drawn, and the response falls
            # away as T^2 well below it.
            MathTex(
                r"\Delta\Phi = \Phi_{\text{upper}} - \Phi_{\text{lower}}"
                r" \propto n\,L\,h\,\sin^2(\omega_{\text{GW}} T/2)",
                font_size=FONT_ANNOTATION,
            ),
        ).arrange(DOWN, buff=0.22).move_to(GR_SIGNAL)
        if signal.width > GR_TERMS_WIDTH:
            signal.scale(GR_TERMS_WIDTH / signal.width)
        self.play(FadeIn(signal), run_time=1.0)
        self.wait(2.0)

    def fly(self):
        """Three pulses and two legs, one at a time, on bowed worldlines."""
        low, up, lags = self.low, self.up, self.lags
        atoms, phase, rate, excited = self.atoms, self.phase, self.rate, self.excited
        low_disp, up_disp = self.displacement("low"), self.displacement("up")

        def shoot(k, flash, note=None):
            self.play(FadeIn(self.dots[k], scale=0.4), run_time=0.3)
            fire_pulse(
                self, GW_PULSES[k] + self.low_lags[k], flash=flash, lag=lags[k],
                note=note,
                z_near=self.crossing("low", k), z_far=self.crossing("up", k),
            )

        # --- pulse 1: the beamsplitter -------------------------------------
        shoot(0, [self.seeds["low"], self.seeds["up"]], note=self.pulse_note(0))
        self.open_arms("low")
        self.open_arms("up")

        draw_wavy_legs(self, [
            (atoms["low"][0], low[0], low[1], ATOM_COLOR, low_disp),
            (atoms["low"][1], low[0], low[2], KICKED_COLOR, low_disp),
            (atoms["up"][0], up[0], up[1], ATOM_COLOR, up_disp),
            (atoms["up"][1], up[0], up[2], KICKED_COLOR, up_disp),
        ], extra=[
            phase[c][1].animate.set_value(rate * excited[c][0])
            for c in ("low", "up")
        ])

        # --- pulse 2: the mirror --------------------------------------------
        shoot(1, [a for p in atoms.values() for a in p])
        big = self.big
        self.play(
            *[state_colors(p[0], KICKED_COLOR) for p in atoms.values()],
            *[state_colors(p[1], ATOM_COLOR) for p in atoms.values()],
            *[big[k].animate.set_color(lighten(KICKED_COLOR)) for k in (0, 2)],
            *[big[k].animate.set_color(lighten(ATOM_COLOR)) for k in (1, 3)],
            run_time=0.5,
        )
        draw_wavy_legs(self, [
            (atoms["low"][0], low[1], low[3], KICKED_COLOR, low_disp),
            (atoms["low"][1], low[2], low[3], ATOM_COLOR, low_disp),
            (atoms["up"][0], up[1], up[3], KICKED_COLOR, up_disp),
            (atoms["up"][1], up[2], up[3], ATOM_COLOR, up_disp),
        ], extra=[
            phase[c][0].animate.set_value(rate * excited[c][1])
            for c in ("low", "up")
        ])

        # --- pulse 3: recombine ---------------------------------------------
        shoot(2, [atoms["low"][0], atoms["up"][0]])


class GradiometerGWStretchContinuous(RunsContinuously, GradiometerGWStretch):
    """GradiometerGWStretch with the pulses climbing while the atoms fly.

    Free, once the continuous sequence is a mixin and this picture's two
    differences are methods: the bow goes into the worldlines the atoms are
    carried along and into the trails behind them, exactly as it goes into
    draw_wavy_legs in the stop-start version.
    """


# --- a light shift injected into one interferometer -----------------------
# How a gradiometer is tested without waiting for a wave. Between the first
# pi/2 and the pi pulse an off-resonant beam is turned on across the upper
# cloud alone. It is far enough from resonance to drive nothing -- no atom
# changes state, no momentum is handed over, the geometry is untouched -- but
# while it is on it shifts the clock levels, and with them omega_A.
#
# Only one arm picks the shift up, and not because only one arm is lit: the
# beam covers the whole cloud. A hand turns at omega_A only while its arm is
# in |e>, so the arm that has been excited since the beamsplitter accumulates
# the shift and its partner, sitting in |g>, does not. The two hands stop
# agreeing, and that disagreement is the phase.
#
# The lower interferometer never sees the beam and stays on its null, so the
# shift does not cancel in Phi_upper - Phi_lower. That is the whole point: it
# arrives in the difference exactly the way a dark-matter or gravitational-wave
# signal would, which is what makes it a test of whether one would be caught.
# The same figure as GradiometerGW's, with the source on a shutter.
LS_ON, LS_OFF = 0.3, 0.72  # the stretch of the first leg the beam is on for
LS_PAD = 0.38  # how far its band stands off the interferometer it covers
# What the shift is tuned to inject. A third of a turn is chosen to be read
# rather than to be realistic: big enough to see on a dial and to split the
# upper ports plainly (P_g = 1/4), against a lower interferometer that still
# sends everything into |g>.
#
# Negative because delta_LS is signed and a beam below resonance pushes the
# levels together -- and because the sector on the dial is then the angle
# itself rather than the rest of the turn. phase_sweep wraps into one turn and
# sweeps from one hand to the other, so a hand that has run ahead by a third
# of a turn is drawn as two thirds of one. Nothing about the measurement
# changes with the sign: the ports split by cos(Phi) either way.
LS_PHASE = -TAU / 3


def along(start, end, f):
    """A fraction f of the way from one corner to the next."""
    return start + (end - start) * f


class LightShiftSignal(GradiometerGW):
    """A signal put in on purpose, to see whether the gradiometer catches it.

    Gradiometer ends on a null: nothing is passing through, both clocks read
    the same, and the difference between them is zero. This is that scene with
    one thing added -- an off-resonant beam across the upper cloud, on between
    the first two pulses -- and the null breaks.

    Drawn on the quiet geometry deliberately, as DarkMatterPhase is drawn on
    ClockPhase's: nothing about the instrument has changed and nothing about
    the worldlines has moved. The only new thing on the page is a band of
    light over one of the two interferometers.

    A subclass of GradiometerGW for its machinery and not for its wave: the
    two clouds, the hands they carry, the dials and the ports are the same
    apparatus whatever is being measured with it, and inheriting them is also
    what lets RunsContinuously drive this scene without knowing about it.
    """

    def construct(self):
        gradiometer_frame(
            self, r"A light shift on one interferometer mimics a signal"
        )

        low = vertices(GR_LOWER_Z, 0.0)
        up = vertices(GR_UPPER_Z, GR_LAG)

        rate = clock_rate(GR_T)
        phase = {
            cloud: (ValueTracker(0.0), ValueTracker(0.0))
            for cloud in ("low", "up")
        }
        self.add(*[t for pair in phase.values() for t in pair])

        dials = VGroup(*[
            make_dial(GR_DIALS[c], cap, GR_DIAL_RADIUS)
            for c, cap in (
                ("low", r"$\Phi_{\text{lower}}$"),
                ("up", r"$\Phi_{\text{upper}}$"),
            )
        ])
        # Upper right here rather than under the title, which the beam's own
        # label needs: it is the one caption that has to sit over the
        # interferometer it is about.
        hand_key = Tex(
            r"each hand turns while in $|e\rangle$",
            font_size=FONT_LEGEND, color=lighten(GUIDE_COLOR),
        ).to_corner(UR)
        self.play(FadeIn(dials), FadeIn(hand_key), run_time=0.6)

        # --- the two clouds ----------------------------------------------
        atoms = {
            cloud: [
                make_atom(radius=CLOCK_ATOM_RADIUS).move_to(v[0]),
                make_atom(KICKED_COLOR, radius=CLOCK_ATOM_RADIUS).move_to(v[0]),
            ]
            for cloud, v in (("low", low), ("up", up))
        }
        seeds = {
            cloud: make_atom(radius=CLOCK_ATOM_RADIUS).move_to(v[0])
            for cloud, v in (("low", low), ("up", up))
        }
        self.play(*[FadeIn(m, scale=0.5) for m in seeds.values()], run_time=0.6)

        # --- the beam, and the stretch of the first leg it is on for -------
        # Its band covers the whole upper interferometer, both arms, because
        # that is what a beam across a cloud does. Only one arm picks the
        # shift up all the same: a hand turns at omega_A while its arm is in
        # |e>, and the other arm is sitting in |g>.
        self.on_x = along(up[0], up[1], LS_ON)[0]
        self.off_x = along(up[0], up[1], LS_OFF)[0]
        self.beam = Rectangle(
            width=self.off_x - self.on_x,
            height=GR_ARM + 2 * LS_PAD,
            **LIGHT_SHIFT_STYLE,
        ).move_to([
            0.5 * (self.on_x + self.off_x), GR_UPPER_Z + GR_ARM / 2, 0,
        ])
        self.beam_label = VGroup(
            Tex(
                r"off-resonant beam, upper cloud only",
                font_size=FONT_LEGEND, color=LIGHT_SHIFT_COLOR,
            ),
            MathTex(
                r"\omega_A \to \omega_A + \delta_{\text{LS}}",
                font_size=FONT_LEGEND, color=LIGHT_SHIFT_COLOR,
            ),
        ).arrange(DOWN, buff=0.14).next_to(self.beam, UP, buff=0.25)

        self.low, self.up = low, up
        self.rate, self.phase = rate, phase
        self.atoms, self.seeds = atoms, seeds
        self.hands, self.big = [], VGroup()
        self.fly()

        # --- the readout ---------------------------------------------------
        # One dial has a sector on it and the other has not, which is the
        # figure: the lower interferometer is exactly where Gradiometer left
        # it, and the upper one is not.
        sweeps = []
        for cloud in ("low", "up"):
            sweep, gap = phase_sweep(
                GR_DIALS[cloud], phase[cloud][1], phase[cloud][0], GR_DIAL_RADIUS
            )
            if gap > 0.01:
                sweeps.append(sweep)
        self.remove(*atoms["low"], *atoms["up"], *self.hands)
        self.close(sweeps)

        signal = VGroup(
            Tex(
                r"applied to one interferometer, so it survives the difference",
                font_size=FONT_LEGEND, color=lighten(GUIDE_COLOR),
            ),
            MathTex(
                r"\Delta\Phi = \Phi_{\text{upper}} - \Phi_{\text{lower}}"
                r" = \delta_{\text{LS}}\,\tau",
                font_size=FONT_ANNOTATION,
            ),
        ).arrange(DOWN, buff=0.22).move_to(GR_SIGNAL)
        if signal.width > GR_TERMS_WIDTH:
            signal.scale(GR_TERMS_WIDTH / signal.width)
        self.play(FadeIn(signal), run_time=1.0)
        self.wait(2.0)

    def fly(self):
        """Three pulses and two legs, with the beam on across the middle of
        the first.
        """
        low, up, atoms, phase = self.low, self.up, self.atoms, self.phase
        rate = self.rate

        # --- pulse 1: the beamsplitter -----------------------------------
        fire_pulse(self, GR_T0, flash=list(self.seeds.values()))
        self.open_arms("low")
        self.open_arms("up")

        # --- leg 1, flown in three stretches ------------------------------
        # The beam is on for the middle one. Splitting the leg rather than
        # easing a tracker is what puts the shift somewhere on the page: the
        # stretch of flight it covers is a stretch of the drawing, and the
        # upper hand visibly changes pace over exactly that stretch and no
        # other, while the lower one keeps the rate both started at.
        legs = [
            (atoms["low"][0], low[0], low[1], ATOM_COLOR),
            (atoms["low"][1], low[0], low[2], KICKED_COLOR),
            (atoms["up"][0], up[0], up[1], ATOM_COLOR),
            (atoms["up"][1], up[0], up[2], KICKED_COLOR),
        ]

        def stretch(f_from, f_to, extra=()):
            draw_legs(self, [
                (atom, along(a, b, f_from), along(a, b, f_to), color)
                for atom, a, b, color in legs
            ], extra=extra)

        def wound_to(f, shifted):
            """Where each hand has got to a fraction f into the first leg."""
            return [
                phase["low"][1].animate.set_value(rate * GR_T * f),
                phase["up"][1].animate.set_value(
                    rate * GR_T * f + (LS_PHASE if shifted else 0.0)
                ),
            ]

        stretch(0.0, LS_ON, extra=wound_to(LS_ON, shifted=False))
        self.play(FadeIn(self.beam), FadeIn(self.beam_label), run_time=0.6)
        self.bring_to_back(self.beam)
        stretch(LS_ON, LS_OFF, extra=wound_to(LS_OFF, shifted=True))
        stretch(LS_OFF, 1.0, extra=wound_to(1.0, shifted=True))

        # --- pulse 2: the mirror ------------------------------------------
        fire_pulse(self, GR_T0 + GR_T, flash=[a for p in atoms.values() for a in p])
        big = self.big
        self.play(
            *[state_colors(p[0], KICKED_COLOR) for p in atoms.values()],
            *[state_colors(p[1], ATOM_COLOR) for p in atoms.values()],
            *[big[k].animate.set_color(lighten(KICKED_COLOR)) for k in (0, 2)],
            *[big[k].animate.set_color(lighten(ATOM_COLOR)) for k in (1, 3)],
            run_time=0.5,
        )
        # The beam is off, so the second leg is the quiet one in both clouds:
        # whatever the shift put in stays in, because nothing takes it out.
        draw_legs(self, [
            (atoms["low"][0], low[1], low[3], KICKED_COLOR),
            (atoms["low"][1], low[2], low[3], ATOM_COLOR),
            (atoms["up"][0], up[1], up[3], KICKED_COLOR),
            (atoms["up"][1], up[2], up[3], ATOM_COLOR),
        ], extra=[
            phase[c][0].animate.set_value(rate * GR_T) for c in ("low", "up")
        ])

        # --- pulse 3: recombine -------------------------------------------
        fire_pulse(self, GR_T0 + 2 * GR_T, flash=[atoms["low"][0], atoms["up"][0]])


class LightShiftSignalContinuous(RunsContinuously, LightShiftSignal):
    """The injected signal with lab time never stopped.

    The beam is a duration -- it is on between two pulses, for a stretch of
    one leg -- so it is the scene in this set that gains most from the atoms
    not stopping. The band fills in from its left edge while the beam is on
    and stops growing when the shutter shuts, so what is drawn is the window
    rather than a caption about it, and the upper hand changes pace across
    exactly the span the band covers.
    """

    def fly(self):
        low, up, phase = self.low, self.up, self.phase

        # Lab time starts as the first pulse leaves the laser.
        clock = self.clock = ValueTracker(GR_T0 - GR_SLOPE * GR_LASER_GAP)
        self.add(clock)

        for cloud in ("low", "up"):
            v = self.vertices(cloud)
            start = np.array([clock.get_value(), self.nominal(cloud), 0.0])
            self.add(growing_trail([start, v[0]], ATOM_COLOR, clock))
            carry(self.seeds[cloud], worldline([start, v[0]]), clock)
            # The arm kicked at the mirror is excited over the second leg in
            # both clouds and sees nothing; the arm kicked at the beamsplitter
            # is excited over the first, which is when the beam is on -- so
            # only the upper one of those four hands knows about it.
            phase[cloud][0].add_updater(
                wound(clock, self.rate, v[1][0], v[3][0])
            )
        phase["low"][1].add_updater(
            wound(clock, self.rate, low[0][0], low[1][0])
        )
        phase["up"][1].add_updater(wound_with_shift(
            clock, self.rate, up[0][0], up[1][0],
            self.on_x, self.off_x, LS_PHASE,
        ))

        # The band grows from the moment the shutter opens and stops at the
        # moment it shuts, and is then left where it is: the window it covers
        # is what the readout at the end is about.
        self.add(growing_band(
            self.beam, self.on_x, self.off_x, clock, LIGHT_SHIFT_STYLE
        ))

        # Each pulse goes out in the stretch of flight after it rather than
        # lingering into the next, which is what the wave scenes need and this
        # one does not: nothing here is captioned or set against a dashed
        # ghost, so a worldline that has left the frame has nothing left to
        # say -- and the band is what should have the page while it is on.
        def clear(drawn, to):
            run_to(self, clock, to, *[FadeOut(m) for m in drawn])

        drawn = self.shoot(0, near=[low[0]], far=[up[0]],
                           on_near=lambda: self.open_arms("low"),
                           on_far=lambda: self.open_arms("up"))
        # The label arrives with the beam, not before it, so the run up to the
        # shutter is its own stretch.
        clear(drawn, self.on_x)
        run_to(self, clock, self.off_x, FadeIn(self.beam_label))
        drawn = self.shoot(1, near=[low[1], low[2]], far=[up[1], up[2]],
                           on_near=lambda: self.mirror("low"),
                           on_far=lambda: self.mirror("up"))
        clear(drawn, GR_T0 + 1.5 * GR_T)
        drawn = self.shoot(2, near=[low[3]], far=[up[3]])
        clear(drawn, clock.get_value() + PULSE_LINGER)

    def shoot(self, k, near, far, fade=(), on_near=None, on_far=None):
        """One pulse. No wave here, so every one of them is the quiet one."""
        return sweep_pulse(
            self, self.clock, GR_T0 + k * GR_T, near=near, far=far,
            lag=GR_LAG, reference=False, fade=fade,
            on_near=on_near, on_far=on_far,
        )
