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

from style import *
from atom_interferometry import (
    MZ_A,
    MZ_B,
    MZ_B_UP,
    MZ_C,
    MZ_OUT,
    MachZehnder,
    absorb,
    draw_legs,
    emit,
    grow,
    make_atom,
    make_guide,
    make_k_arrow,
    momentum_arrow,
    state_colors,
    state_label,
)

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
GR_MID_Z = 0.5 * (GR_LOWER_Z + GR_UPPER_Z)  # tells the two clouds apart
# How far the output ports run past the last pulse. Shorter than CP_OUT,
# because two interferometers have to leave their ports in the one frame: the
# upper pair climbs towards the top edge and the lower pair has the dials to
# its right, and this is the run that clears both.
GR_OUT = 0.8


def photon_worldline(x_at_lower, z_from, z_to, slope=GR_SLOPE, z_at=GR_LOWER_Z):
    """The segment of a pulse's worldline between two points on the baseline.

    `x_at_lower` is when it passes `z_at` on the baseline, i.e. the lower cloud,
    so the geometry of every pulse is fixed by one number and the two crossings
    stay consistent. The slope is the light travel time per unit baseline: a
    constant in a quiet gradiometer, and the signal itself once a wave is passing.
    """
    start = [x_at_lower + slope * (z_from - z_at), z_from, 0]
    end = [x_at_lower + slope * (z_to - z_at), z_to, 0]
    return Line(start, end, color=LASER_COLOR, stroke_width=PULSE_STROKE_WIDTH)


def vertices(z0, lag):
    """The four corners of one interferometer in the (time, baseline) plane."""
    a = np.array([GR_T0 + lag, z0, 0.0])
    b = a + RIGHT * GR_T
    b_up = b + UP * GR_ARM
    c = b_up + RIGHT * GR_T
    return a, b, b_up, c


def gradiometer_frame(scene, title_tex):
    """The furniture every gradiometer scene shares, played onto the screen.

    Returns the baseline arrow and its label, which are the only pieces a
    scene goes on to touch.
    """
    title = Tex(title_tex, font_size=FONT_TITLE).to_corner(UL)

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
    z_axis = Tex("baseline", font_size=FONT_LEGEND, color=lighten(GUIDE_COLOR))
    z_axis.rotate(90 * DEGREES).to_edge(LEFT, buff=0.18).set_y(0.3)

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

    scene.play(
        FadeIn(title), FadeIn(laser), FadeIn(laser_tag),
        FadeIn(t_axis), FadeIn(z_axis), run_time=1.0,
    )
    scene.play(GrowFromCenter(baseline), FadeIn(baseline_label), run_time=0.7)
    return baseline, baseline_label


def fire_pulse(scene, x_at_lower, flash, lag=GR_LAG, reference=False, note=None,
               z_near=GR_LOWER_Z, z_far=GR_UPPER_Z, quiet_x=None):
    """Send one pulse up the baseline, reaching the far cloud `lag` later.

    `z_near` and `z_far` are where the two clouds actually are when the pulse
    crosses them, which only differ from the nominal positions on the baseline
    once a wave is
    moving the clouds around. With `reference` the worldline the pulse would
    have followed in a quiet baseline is drawn alongside as a dashed ghost, so
    an arrival is visibly early or late rather than merely shifted; `note` is
    faded in at the far crossing to name it, and fades out with the pulse.
    """
    slope = lag / (z_far - z_near)
    below = photon_worldline(x_at_lower, GR_LASER_Z, z_near, slope, z_near)
    across = photon_worldline(x_at_lower, z_near, z_far, slope, z_near)
    beyond = photon_worldline(
        x_at_lower, z_far, config.frame_y_radius + 0.3, slope, z_near
    )

    low_hits = [m for m in flash if m.get_center()[1] < GR_MID_Z]
    up_hits = [m for m in flash if m.get_center()[1] >= GR_MID_Z]

    drawn = [below, across, beyond]
    ghost = None
    if reference:
        # Anchored on where the pulse would have crossed with no wave passing,
        # which is not where it actually crossed: the wave has already held it
        # up on the way from the laser to the near cloud.
        base = x_at_lower if quiet_x is None else quiet_x
        quiet = photon_worldline(base, z_near, z_near + GR_BASELINE)
        ghost = DashedLine(
            quiet.get_start(), quiet.get_end(),
            **{**GUIDE_STYLE, "stroke_opacity": 0.55},
        )
        drawn.append(ghost)
    if note is not None:
        drawn.append(note)

    scene.play(Create(below), rate_func=linear, run_time=0.45)
    scene.play(*[Flash(m, **FLASH_STYLE) for m in low_hits], run_time=0.35)
    scene.play(
        Create(across),
        *([Create(ghost)] if ghost is not None else []),
        rate_func=linear,
        run_time=0.7,
    )
    scene.play(
        *[Flash(m, **FLASH_STYLE) for m in up_hits],
        *([FadeIn(note)] if note is not None else []),
        run_time=0.35,
    )
    scene.play(Create(beyond), rate_func=linear, run_time=0.3)
    scene.play(*[FadeOut(m) for m in drawn], run_time=0.3)


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

# --- phase, drawn as a clock hand -----------------------------------------
# The clock is the whole interferometer, not either arm on its own. The
# oscillator is the Sr clock transition at omega_A, and the pulses start and
# stop a Ramsey comparison against it -- that is what makes this an atom
# *clock* interferometer.
#
# A single arm is not a clock. Between pulses each arm is in a definite
# internal state, one in |e> and the other in |g>, swapped at the mirror, and
# an energy eigenstate does not tick: its phase e^{-iEt/hbar} only means
# something relative to another state. A hand that turns "only in |e>" is
# bookkeeping with E_g set to zero, showing the phase of |e> relative to |g>.
# What is measured is omega_A times the *difference* in the two arms' time
# spent excited, and that quantity belongs to both arms together.
#
# The hands are still exactly the lab-frame phase, which is why the drawing
# works. Each pulse writes omega_L * t_emission, fixed by when the laser
# fired rather than when the pulse arrived, so with equally spaced pulses the
# laser terms cancel between the arms; on resonance what is left is
# omega_A * [(t2'-t1') - (t3'-t2')] in arrival times. Two arms that have
# spent equal time up there land their hands on top of each other -- the null
# a gradiometer sits on, and what a gravitational wave breaks by moving those
# arrival times.
CLOCK_TURNS = 1.5  # turns of a hand per interrogation time T

# the explainer's own geometry: one interferometer, low and left, leaving the
# upper right for a dial big enough to read
CP_T0 = -6.2  # far enough left that the output ports clear the dial
CP_T = 3.8  # the same T as the gradiometer, so the hands turn at the same rate
CP_Z = -2.4
CP_ARM = 1.7
CP_OUT = 1.1  # how far the output ports run past the last pulse
CP_DIAL = np.array([4.6, 0.9, 0.0])
# where ClockPhaseTerms puts the budget: the open band between the note and
# the interferometer, left of the dial
CP_TERMS = np.array([-2.3, 2.0, 0.0])
# and where the readout goes: the strip under the interferometer's lower leg,
# which is the one part of the frame no pulse column ends in and nothing on
# the crowded right-hand side -- dial, result, port labels -- reaches into.
CP_READOUT = np.array([-4.6, -3.3, 0.0])
# And where the scalings go: the rest of that same strip, right of the readout
# equation. The only clear span left, once the dial and its verdict have taken
# the right-hand side and the trace has taken the top. Wide enough for a
# proportionality and a line naming it, which is all that goes here: a full
# expression had to be shrunk to fit, and a shrunk equation at the bottom of a
# frame is one nobody reads.
CP_SCALING = np.array([1.5, -3.25, 0.0])
CP_SCALING_WIDTH = 8.4

# One dial per interferometer, each level with the cloud it belongs to, so the
# two faces sit in the same order on the page as the clouds do on the baseline.
# the open band between the two interferometers, which is where the budget
# goes once the diagram is drawn -- and left of centre, because the right-hand
# end of that band is where the lower interferometer's ports climb into
GR_TERMS = np.array([-1.5, -0.3, 0.0])
GR_TERMS_WIDTH = 7.6  # the clear span between the L arrow and the ports
# Where the wave scenes say what is done with the two dials. Same band and
# same clear span as the budget, so all three gradiometer scenes end in the
# same place with the ports beside them.
# Centred in the band rather than a little above it, which was room enough
# when what went here was one line: the scaling runs to two, and the stretched
# picture bows the upper cloud down into whatever clearance is left.
GR_SIGNAL = np.array([-1.5, -0.62, 0.0])

GR_DIAL_RADIUS = 0.75
GR_DIALS = {
    "low": np.array([5.8, -1.95, 0.0]),  # clear of the time-axis label
    "up": np.array([5.8, 1.2, 0.0]),
}


def clock_rate(interrogation_time):
    """How fast a hand turns, fixed by how far it should get in one leg."""
    return CLOCK_TURNS * TAU / interrogation_time


def make_clock_hand(atom, phase):
    """A hand riding an atom, pointing at the phase that arm has accumulated.

    Deliberately not part of the atom's own VGroup: every scene here moves an
    atom by its group centre, and folding a turning hand into that group would
    drag the centre around and pull the atom off the trajectory it is drawing.
    """
    length = CLOCK_HAND_RATIO * CLOCK_ATOM_RADIUS

    def follow(hand):
        pivot = atom[0].get_center()
        hand.put_start_and_end_on(
            pivot, pivot + rotate_vector(UP * length, -phase.get_value())
        )

    hand = Line(
        ORIGIN, UP * length, color=CLOCK_HAND_COLOR, stroke_width=CLOCK_HAND_WIDTH
    )
    hand.add_updater(follow)
    return hand


def make_dial(center, caption=None, radius=CLOCK_DIAL_RADIUS):
    """A clock face, for a phase that is too small to read off a moving atom.

    The caption is optional because in a crowded figure the only room left
    under the face is where a phase label from the diagram already sits.
    """
    face = Circle(
        radius=radius, stroke_width=2,
        stroke_color=lighten(GUIDE_COLOR), fill_opacity=0,
    )
    ticks = VGroup(*[
        Line(
            (radius - 0.14 * radius) * rotate_vector(UP, -k * TAU / 12),
            radius * rotate_vector(UP, -k * TAU / 12),
            stroke_width=2, color=lighten(GUIDE_COLOR),
        )
        for k in range(12)
    ])
    dial = VGroup(face, ticks).move_to(center)
    if caption is None:
        return VGroup(dial)
    label = Tex(
        caption, font_size=FONT_LEGEND, color=lighten(GUIDE_COLOR)
    ).next_to(dial, DOWN, buff=0.2)
    return VGroup(dial, label)


def dial_hand(center, phase, color, radius=CLOCK_DIAL_RADIUS):
    """The same phase a clock hand shows, at a size you can actually read."""
    length = radius - 0.16 * radius

    def follow(hand):
        hand.put_start_and_end_on(
            center, center + rotate_vector(UP * length, -phase.get_value())
        )

    hand = Line(
        ORIGIN, UP * length, color=color, stroke_width=CLOCK_HAND_WIDTH + 1
    )
    hand.add_updater(follow)
    return hand


def phase_sweep(center, phase_a, phase_b, radius=CLOCK_DIAL_RADIUS):
    """The angle between two arms' hands: what the interferometer reads out.

    Wrapped into one turn, because a hand that has been round three times and
    a hand that has been round twice and a bit are only distinguishable by
    where they end up.
    """
    gap = (phase_b.get_value() - phase_a.get_value()) % TAU
    sector = AnnularSector(
        inner_radius=0.0,
        outer_radius=radius - 0.3 * radius,
        start_angle=PI / 2 - phase_b.get_value(),
        angle=gap,
        color=AREA_COLOR,
        fill_opacity=CLOCK_SWEEP_OPACITY,
        stroke_width=0,
    )
    return sector.move_arc_center_to(center), gap


def ground_share(phase_a, phase_b):
    """The share of the atoms the last pulse leaves in |g, p>.

    The same angle phase_sweep draws, read as a population instead of as a
    sector: P = (1 + cos Phi) / 2. Wrapped into one turn for the same reason
    the sector is -- a hand that has been round an extra time is in the same
    place, and the ports cannot tell the two apart either.
    """
    gap = (phase_b.get_value() - phase_a.get_value()) % TAU
    return 0.5 * (1 + np.cos(gap))


def fire_vertical_pulse(scene, x, hits):
    """One pulse climbing the diagram at time `x`, flashing what it crosses.

    A bare worldline, as in the gradiometer, but vertical: nothing in this
    scene turns on the light travel time, and both arms share a column, so one
    pulse reaches them at the same instant -- which is what makes the two legs
    equal and the null exact. It stops at the topmost atom it acts on rather
    than running off the top, because there is nothing above to draw it for.
    """
    hits = sorted(hits, key=lambda m: m.get_center()[1])
    y = -config.frame_y_radius - 0.3
    drawn = []
    for atom in hits:
        y_next = atom.get_center()[1]
        segment = Line(
            [x, y, 0], [x, y_next, 0],
            color=LASER_COLOR, stroke_width=PULSE_STROKE_WIDTH,
        )
        scene.play(
            Create(segment), rate_func=linear, run_time=(y_next - y) / PULSE_SPEED
        )
        scene.play(Flash(atom, **FLASH_STYLE), run_time=0.3)
        drawn.append(segment)
        y = y_next
    scene.play(*[FadeOut(m) for m in drawn], run_time=0.3)


# --- running the diagram continuously -------------------------------------
# Every scene below draws a space-time diagram: x is lab time and y is where
# on the baseline something is. Stop-start rendering therefore stops lab time
# itself -- the atoms wait for a pulse to be drawn, and so does the wave or
# the field that is passing through, which is the one thing those scenes are
# about. The continuous variants run a single ValueTracker whose value *is*
# the diagram's x coordinate, and make everything a function of it: atom
# positions, the trails behind them, the photon worldlines, the marker on the
# trace, the phase each arm has wound up. Nothing can then disagree with
# anything else, because there is only one number.
#
# The corollary is a discipline rather than a helper: between the first pulse
# and the last, every scene.play has to advance the clock. One that does not
# is exactly the freeze these variants exist to remove, so a beat that cannot
# be folded into a clock-advancing play has to become an always_redraw that
# switches itself on as lab time passes it.


def leg_point(start, end, disp, s):
    """Where an atom on a bowed leg is, a fraction s of the way along it.

    The displacement is subtracted at the two ends and added back along the
    way, so the leg still passes exactly through both corners -- the pulses
    have to land on the atoms.

    With a disp that returns zero this is straight interpolation, which is
    what lets one set of helpers carry both the bowed legs of the stretched
    gradiometer and the straight ones everywhere else.
    """
    x = interpolate(start[0], end[0], s)
    y = interpolate(start[1] - disp(start[0]), end[1] - disp(end[0]), s) + disp(x)
    return np.array([x, y, 0.0])


def wavy_path(start, end, color, disp, s_max=1.0):
    """The leg bowed by the wave, drawn a fraction s_max of the way along."""
    return ParametricFunction(
        lambda s: leg_point(start, end, disp, s),
        t_range=[0.0, max(s_max, 1e-4), 0.01],
        color=color,
        **TRAJECTORY_STYLE,
    )


def no_displacement(_):
    """A quiet baseline: the legs are straight and the corners are where they say."""
    return 0.0


def leg_share(start, end, t):
    """How far along the leg from `start` to `end` lab time `t` has got.

    Clamped at both ends, which is what lets one arm's whole worldline be
    written as a sequence of legs and evaluated at any time: before its first
    corner it sits at the start, after its last it sits at the end.
    """
    return float(np.clip((t - start[0]) / (end[0] - start[0]), 0.0, 1.0))


def run_to(scene, clock, to, *anims, **kwargs):
    """Advance lab time to `to` at V, playing `anims` while it runs.

    The one primitive the continuous scenes are built out of. Everything that
    has to happen between the first pulse and the last goes through here, so
    that it happens *while* the diagram is being drawn rather than instead of
    it.

    Asking for a time lab time is already at plays the animations on the spot.
    The only call that should ever land there is the run-up to the first
    pulse, which is where the clock starts; anywhere else it is the freeze
    this helper exists to avoid, and it will show.

    The pacing goes on the sweep itself and never as a play() kwarg, because
    Scene.play sets every kwarg it is given on every animation in the call --
    which would stretch a quarter-second flash to the length of a whole leg.
    Anything handed in that is longer than the sweep is cut back to it for the
    same reason in reverse: Scene.play runs for the longest animation it has,
    so lab time would arrive at `to` and then sit there for the remainder.
    """
    run_time = (to - clock.get_value()) / V
    if run_time <= 1e-6:
        return scene.play(*anims, **kwargs) if anims else None
    for anim in anims:
        anim.run_time = min(anim.run_time, run_time)
    return scene.play(
        clock.animate(run_time=run_time, rate_func=linear).set_value(to),
        *anims,
        **kwargs,
    )


def worldline(corners, disp=no_displacement):
    """A function from lab time to where an arm is, given the corners it turns at.

    `corners` are in lab-time order. Outside the arm's own span the value is
    held at the nearer end, so an arm can be built and put on the screen
    before the beamsplitter has made it and left parked after it recombines,
    without the caller having to guard either edge.
    """
    def at(t):
        for start, end in zip(corners, corners[1:]):
            if t <= end[0]:
                return leg_point(start, end, disp, leg_share(start, end, t))
        start, end = corners[-2], corners[-1]
        return leg_point(start, end, disp, 1.0)

    return at


def wound(clock, rate, t_from, t_to):
    """An updater for the angle an arm excited from t_from to t_to has reached.

    The continuous counterpart of draw_legs' extra=[tracker.animate...]: the
    phase is read off the clock rather than advanced leg by leg, so a hand
    keeps turning through a pulse as well as along a leg, and holds of its own
    accord once the mirror has handed the excitation over.
    """
    def turn(tracker):
        tracker.set_value(
            rate * (float(np.clip(clock.get_value(), t_from, t_to)) - t_from)
        )

    return turn


def growing_band(band, t_from, t_to, now, style=FIELD_WINDOW_STYLE):
    """A band over a stretch of the diagram, filling in as that stretch is flown.

    Takes the finished band's height and redraws its width off the clock, so
    it keeps pace with the atoms underneath it instead of arriving all at once
    in a beat of its own -- which in a continuous scene would be a beat with
    lab time stopped. Used for the washes over an oscillation's windows, and
    for a beam that is switched on and off, which is why the style is the
    caller's: a bounded band cannot be drawn at zero width without its own
    left edge standing there before it is due, so nothing is returned at all
    until lab time is inside the window.
    """
    top, bottom = band.get_top()[1], band.get_bottom()[1]

    def draw():
        t = float(np.clip(now.get_value(), t_from, t_to))
        if t - t_from < 1e-3:
            return VGroup()
        return Rectangle(
            width=t - t_from, height=top - bottom, **style
        ).move_to([0.5 * (t_from + t), 0.5 * (top + bottom), 0])

    return always_redraw(draw)


def wound_with_shift(clock, rate, t_from, t_to, on, off, shift):
    """wound(), with `shift` accrued on top of it across the window [on, off].

    What a light shift does to a hand. The arm is in |e> for the whole leg, so
    it turns at omega_A throughout; for the stretch the beam is on it turns at
    omega_A + delta_LS instead, and the difference is what is left in the
    hand afterwards. Linear across the window because a shutter is open or
    shut, not ramped.
    """
    def turn(tracker):
        t = float(np.clip(clock.get_value(), t_from, t_to))
        held = float(np.clip((t - on) / (off - on), 0.0, 1.0))
        tracker.set_value(rate * (t - t_from) + shift * held)

    return turn


def carry(atom, path, clock):
    """Pin an atom to its worldline for as long as lab time is running.

    Deliberately an updater on the atom rather than an animation: an animation
    would have to be restarted at every corner, which is the stop-start
    structure again. Note that draw_wavy_legs clears an atom's updaters when
    it finishes, so the two movers cannot be mixed on one atom.
    """
    atom.add_updater(lambda m: m.move_to(path(clock.get_value())))
    return atom


def growing_trail(corners, color, clock, disp=no_displacement):
    """The trajectory behind an arm, drawn as far as lab time has got.

    One always_redraw per leg clipped by a clamped share, rather than one
    polyline for the whole arm: that is what wavy_path's s_max already does,
    and it keeps the bowed and the straight cases the same code. A leg lab
    time has not reached yet draws as a stub of length 1e-4, which is
    invisible and, unlike a zero-length path, does not upset ParametricFunction.
    """
    return VGroup(*[
        always_redraw(
            lambda start=start, end=end: wavy_path(
                start, end, color, disp, leg_share(start, end, clock.get_value())
            )
        )
        for start, end in zip(corners, corners[1:])
    ])


def climbing_pulse(clock, x_at_lower, slope, z_from, z_to, z_at):
    """A photon's worldline, drawn as far up the baseline as it has got.

    The counterpart of Create(photon_worldline(...)): same geometry, but the
    length is read off the clock instead of off an animation's alpha, so the
    pulse and the atoms it is about to hit are both being drawn by the same
    number.
    """
    def reached():
        z = z_at + (clock.get_value() - x_at_lower) / slope
        floor = min(z_from, z_to) + 1e-3  # never a zero-length Line
        return float(np.clip(z, floor, max(z_from, z_to)))

    return always_redraw(
        lambda: photon_worldline(x_at_lower, z_from, reached(), slope, z_at)
    )


def sweep_pulse(scene, clock, x_at_lower, near, far, lag=GR_LAG, reference=False,
                note=None, z_near=GR_LOWER_Z, z_far=GR_UPPER_Z, quiet_x=None,
                fade=(), on_near=None, on_far=None):
    """fire_pulse with lab time running: the pulse climbs, the atoms carry on.

    `near` and `far` are the points to flash at the two crossings -- the
    vertices themselves rather than the atoms sitting on them. Flash snapshots
    a mobject's centre when it is built, so on an atom that is still moving
    the ring would be left behind; the vertex is where the atom is at that
    instant by construction, and flashing it marks the event rather than
    chasing the mobject.

    `on_near` and `on_far` are called as the pulse reaches each cloud, which
    is where whatever it does to those atoms belongs. They are separate
    because in these scenes the two crossings are separate events: the clouds
    are a baseline apart, so the far one is split, mirrored and recombined
    L/c after the near one, and a continuous scene shows that rather than
    asserting it in a caption.

    Returns everything it drew instead of fading it, and `fade` takes the
    previous pulse's return. At V a pulse crosses the frame in well under a
    second, and the arrival notes are the explanatory payload of these scenes
    -- faded out with the pulse that earned them they could not be read. So
    each one stays up until the next pulse is on its way, and goes out over
    the last PULSE_LINGER of lab time before it arrives.
    """
    slope = lag / (z_far - z_near)
    drawn = VGroup(climbing_pulse(
        clock, x_at_lower, slope, GR_LASER_Z, config.frame_y_radius + 0.3, z_near
    ))
    if reference:
        # The ghost goes on whole rather than growing: a DashedLine rebuilt at
        # a new length every frame reshuffles its dashes, which reads as a
        # shimmer instead of as a reference.
        base = x_at_lower if quiet_x is None else quiet_x
        quiet = photon_worldline(base, z_near, z_near + GR_BASELINE)
        drawn.add(DashedLine(
            quiet.get_start(), quiet.get_end(),
            **{**GUIDE_STYLE, "stroke_opacity": 0.55},
        ))

    # The leg, then the last of it with the previous pulse clearing the frame,
    # then one segment per crossing so that each flash is launched at the lab
    # time the pulse actually arrives there.
    lead = min(PULSE_LINGER, max(x_at_lower - clock.get_value(), 0.0))
    run_to(scene, clock, x_at_lower - lead)
    scene.add(drawn)
    run_to(scene, clock, x_at_lower, *[FadeOut(m) for m in fade])
    if on_near is not None:
        on_near()
    run_to(
        scene, clock, x_at_lower + lag,
        *[Flash(p, run_time=STROBE_FLASH, **FLASH_STYLE) for p in near],
    )
    if on_far is not None:
        on_far()
    if note is not None:
        scene.add(note)
        drawn.add(note)
    run_to(
        scene, clock, x_at_lower + lag + PULSE_HOLD,
        *[Flash(p, run_time=STROBE_FLASH, **FLASH_STYLE) for p in far],
    )
    return drawn


def strobe_pulse(scene, clock, x, top, flash_at, on_arrival=None, hold=PULSE_HOLD):
    """fire_vertical_pulse with lab time running.

    The clock geometry has no light travel time -- one pulse reaches both arms
    at the same instant, which is what makes the two legs equal -- so the
    column is not something that climbs. It is an instant: it appears whole at
    the crossing and fades over `hold` of lab time while the atoms carry on
    through it. `top` is where the column stops, the topmost vertex it acts
    on, for the same reason fire_vertical_pulse stops at the topmost atom.

    `on_arrival` is called once lab time is on the pulse and before anything
    is played, which is where whatever the pulse does to the atoms belongs --
    swapping which arm is excited, say. It happens on the instant because the
    pulse does: there is no window here to animate it over.
    """
    column = Line(
        [x, -config.frame_y_radius - 0.3, 0], [x, top, 0],
        color=LASER_COLOR, stroke_width=PULSE_STROKE_WIDTH,
    )
    run_to(scene, clock, x)
    if on_arrival is not None:
        on_arrival()
    scene.add(column)
    run_to(
        scene, clock, x + hold,
        *[Flash(p, run_time=STROBE_FLASH, **FLASH_STYLE) for p in flash_at],
        FadeOut(column),
    )


def ring_around(term, color):
    """An ellipse drawn round one term of an equation."""
    return Ellipse(
        width=term.width + 2 * RING_BUFF,
        height=term.height + 2 * RING_BUFF,
        color=color,
        stroke_width=RING_STROKE_WIDTH,
    ).move_to(term)


def budget_equation(lhs, term_prefix="", font_size=FONT_STATE):
    """The budget with `lhs` on the left, as one expression.

    `term_prefix` goes in front of every term on the right. It is there for
    the difference form: a gradiometer subtracts one interferometer's phase
    from another's, and subtraction distributes over the sum, so every term on
    the right becomes a Delta too. Writing the difference on the left over
    undifferenced terms on the right would just be false.

    One MathTex with the terms as separate substrings: LaTeX still sets it as
    one expression, so the relation lines up, but each term is a submobject
    that can be circled or struck through on its own. The thin spaces keep a
    mark clear of the + in front of its term. Whatever the left-hand side is,
    it stays a single substring, so the terms keep the same indices.
    """
    def term(name, trailing=r"\,"):
        return r"\," + term_prefix + r"\Phi_{\text{" + name + r"}}" + trailing

    return MathTex(
        lhs, "=", term("interferometer"), "+", term("laser", trailing=""),
        font_size=font_size,
    )


def draw_ports(scene, origin, length, p_ground, labels=True, extra=()):
    """The two output states the last pulse leaves the atoms in.

    Until that pulse fires the two arms are distinguishable -- one in
    |e, p + hbar k>, the other in |g, p> -- so the phase between them cannot
    show up anywhere. The pulse couples exactly those two states, so each port
    takes an amplitude from both arms and the angle between the hands becomes
    a population: P = (1 +- cos Phi) / 2. `p_ground` is the share that leaves
    in |g, p>; the excited port takes the rest.

    A port that got nothing is drawn as a dashed guide rather than left out,
    because a null only reads as "they all came out here" if the side they did
    not come out of is on the page.

    `labels` names the two ports. A gradiometer turns that off: it closes four
    ports rather than two, the colours already say which state each one is,
    and what its figure is about is the two splits being unequal -- eight
    labels would bury the one thing the frame has to show.

    `extra` is draw_legs' hook, passed straight through. The continuous scenes
    go through fly_ports instead, which is this with the clock kept running.
    """
    empty, legs, tags = port_parts(scene, origin, length, p_ground)
    if len(empty):
        scene.play(FadeIn(empty), run_time=0.5)
    if legs:
        draw_legs(scene, legs, extra=extra)
    if labels:
        scene.play(FadeIn(tags), run_time=0.6)


def port_parts(scene, origin, length, p_ground):
    """The pieces draw_ports is made of: empty guides, legs to fly, labels.

    The atoms that will fly are put on the scene at `origin`; nothing else is.
    """
    empty, legs, tags = VGroup(), [], VGroup()
    for direction, color, p, tex, label_dir in (
        (RIGHT, ATOM_COLOR, p_ground, r"P_g", DOWN),
        (RIGHT + UP, KICKED_COLOR, 1.0 - p_ground, r"P_e", UP),
    ):
        end = origin + direction * length
        # `end` is a bare point, so the buff has to clear the atom that will
        # be sitting on it, not just the point itself.
        label = MathTex(
            tex, font_size=FONT_ANNOTATION, color=lighten(color)
        ).next_to(end, label_dir, buff=CLOCK_ATOM_RADIUS + 0.22)
        if p < PORT_EMPTY:
            empty.add(make_guide(origin, end))
            label.set_opacity(PORT_EMPTY_OPACITY)
        else:
            atom = make_atom(color, radius=CLOCK_ATOM_RADIUS, opacity=p)
            scene.add(atom.move_to(origin))
            legs.append((atom, origin, end, color))
        tags.add(label)
    return empty, legs, tags


def fly_ports(scene, ports, length, labels=True, extra=()):
    """draw_ports for a continuous scene: every port in one beat, clock running.

    `ports` is a list of (origin, p_ground), one per interferometer. The
    stop-start version gives an empty port's guide a beat of its own before
    the flight and a gradiometer one beat per cloud; either would be a play
    with lab time stood still, which is the freeze these scenes exist to
    remove. So the guides fade in while the atoms fly, and all of a
    gradiometer's ports leave together -- the two clouds are one instrument
    read out in one frame, and `extra` (the clock, the sectors) runs once.
    """
    empty, legs, tags = VGroup(), [], VGroup()
    for origin, p_ground in ports:
        e, l, t = port_parts(scene, origin, length, p_ground)
        empty.add(*e)
        legs.extend(l)
        tags.add(*t)
    draw_legs(scene, legs, extra=[*extra, *([FadeIn(empty)] if len(empty) else [])])
    if labels:
        scene.play(FadeIn(tags), run_time=0.6)


def readout_equation(center=CP_READOUT):
    """What the angle on the dial becomes once the last pulse has fired.

    The ports are the measurement, and this is the only thing that ties them
    to the phase: a hand that has come round to a different place than its
    partner is not itself an observable, and what a shot of atoms yields is
    the two populations. Deliberately the same relation, wording and size as
    the Mach-Zehnder scene ends on, because it is the same measurement drawn
    twice -- there in momentum states, here in the clock states.
    """
    return MathTex(
        r"P_{g,e} = \tfrac{1}{2}\left(1 \pm \cos\Phi\right)",
        font_size=FONT_ANNOTATION,
    ).move_to(center)


def show_phase_budget(scene, center, laser_struck, laser_label,
                      difference_lhs=None, max_width=None):
    """Phi split into its two terms, each marked with what it is worth.

    The separation phase is the third term of the usual decomposition and is
    neglected throughout this talk, so it is not drawn: what is left is the
    phase the atoms accumulate between the pulses, which is the signal --
    omega_A times the difference in time the two arms spend excited -- and the
    phase the light writes in. The laser term is the one that depends on the
    instrument, which is the whole reason for drawing the budget twice:
    circled and noisy in a single interferometer, struck out and cancelled
    once two of them share a laser.

    `difference_lhs` rewrites the whole relation before anything is marked: a
    gradiometer does not read Phi but the difference between two of them, and
    striking a term out as cancelled only means anything once that difference
    is what is being written down. The Delta lands on every term on the right
    as well, because that is where subtracting the two budgets puts it.
    `max_width` is the clear span the result has to fit into.
    """
    eq = budget_equation(r"\Phi").move_to(center)
    scene.play(Write(eq), run_time=1.4)

    if difference_lhs is not None:
        wide = budget_equation(difference_lhs, r"\Delta").move_to(center)
        if max_width is not None and wide.width > max_width:
            wide.scale(max_width / wide.width)
        scene.play(ReplacementTransform(eq, wide), run_time=1.1)
        eq = wide

    # Each label hangs off the equation's own bounding box rather than off its
    # mark, so the two share a baseline however tall each mark is.
    def label(text, color, term):
        return Tex(
            text, font_size=FONT_LEGEND, color=color
        ).next_to(eq, DOWN, buff=0.5).set_x(term.get_x())

    def strike(term):
        # Corner to corner of the term itself: any larger and the tips reach
        # the + signs on either side and read as part of the equation.
        scene.play(
            Create(Cross(
                term, stroke_color=CROSS_COLOR, stroke_width=CROSS_STROKE_WIDTH
            )),
            term.animate.set_opacity(STRUCK_OPACITY),
            run_time=0.9,
        )

    # --- the term the measurement is after -------------------------------
    scene.play(Create(ring_around(eq[2], SIGNAL_COLOR)), run_time=0.6)
    scene.play(FadeIn(label(r"signal", SIGNAL_COLOR, eq[2])), run_time=0.5)

    # --- the one the instrument decides the fate of -----------------------
    if laser_struck:
        strike(eq[4])
        color = STRUCK_COLOR
    else:
        scene.play(Create(ring_around(eq[4], NOISE_COLOR)), run_time=0.6)
        color = NOISE_COLOR
    scene.play(FadeIn(label(laser_label, color, eq[4])), run_time=0.5)


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


# --- an oscillating ultralight dark-matter field --------------------------
# A scalar field light enough to be a coherent wave in the lab oscillates at
# omega_phi = m_phi c^2 / hbar. Coupled to the fundamental constants it drags
# them along with it, and the Sr clock frequency goes with them:
#
#     omega_A -> omega_A [1 + eps cos(omega_phi t + theta)].
#
# That is not a shift the interferometer can throw away. An arm only winds its
# hand while it is excited, and the two arms are excited over different
# windows -- arm 1 over leg 1, and the mirror hands the excitation to arm 2
# for leg 2 -- so each integrates its own stretch of the oscillation. Equal
# window lengths no longer mean equal phase, the hands miss each other and the
# ports split. It is ClockPhase's null broken by the source rather than by the
# geometry.
#
# omega_phi = pi / T is the resonant case and the one drawn: the pulses land
# on zero crossings, so one arm sits on the positive half-cycle and the other
# on the negative and the two departures add rather than averaging away. Off
# resonance the same figure is a smaller gap, which is why the search is a
# scan in omega_phi and not a single measurement.
DM_OMEGA = PI / CP_T
# The fractional swing in omega_A, exaggerated in the same spirit as
# GW_LAG_GAIN: bounds on a scalar coupling in this mass range sit below about
# 1e-16, so this is some fifteen orders of magnitude too big. What the figure
# carries is which part of the cycle each arm sampled, not how large the
# effect is.
DM_EPS = 0.17

# the field's trace, above the diagram and on the diagram's own time axis, and
# the band between it and the interferometer, which is where the modulation
# law goes -- it belongs to both, so it sits between them
DM_TRACE_Z = 2.3
DM_TRACE_AMPLITUDE = 0.32
DM_TRACE_X = (CP_T0 - 0.4, CP_T0 + 2 * CP_T + 0.7)
DM_LAW = np.array([-1.8, 0.75, 0.0])

# --- the transition the field is moving -----------------------------------
# The trace says the field is oscillating and the hands say the phase does not
# cancel; neither says what the atom sees. This is the same two-level system
# the single-photon scenes draw, with |e> riding that trace: the field walks
# omega_A up and down, and the laser, which knows nothing about the field,
# stays exactly where it was tuned. So the arrow is fixed and the level is
# not, and the gap that opens between the arrow's head and |e> is the
# detuning -- which is how a shift in a clock frequency becomes something an
# interferometer can be sensitive to at all.
#
# The swing is DM_EPS's exaggeration carried into the level diagram rather
# than a second one on top of it: both the level and the trace are drawn from
# dm_field, so they are the same curve read at the same instant.
DM_LEVELS = np.array([-5.4, 0.55, 0.0])  # centre of the unmodulated gap
DM_LEVEL_LENGTH = 1.6  # wide enough to hold two arrows and both their labels
DM_LEVEL_GAP = 1.5
DM_LEVEL_SWING = 0.38  # how far |e> rides, in the same spirit as the trace
DM_LEVEL_INSET = 0.1  # how far an arrow stands off a level line
DM_KET_BUFF = 0.2
DM_GAP_X = -0.5  # where the omega_A arrow stands, from the diagram centre
DM_GAP_LABEL_BUFF = 0.14  # and how far its label sits off it
DM_LASER_X = 0.45  # the laser's arrow, far enough right to read as its own
DM_MARK_X = 0.60  # the column the laser's labels and the detuning bar sit in


def dm_field(t):
    """The field's modulation of omega_A at time t, normalised to +-1.

    Phased to cross zero at the first pulse, which is what puts leg 1 on the
    positive half-cycle and leg 2, after the mirror, on the negative one. The
    opposite phasing -- a pulse on a crest -- is the worst case rather than a
    cosmetic choice: each window would then cover a whole crest, integrate to
    the same thing as its neighbour, and the field would drop out entirely.
    """
    return np.sin(DM_OMEGA * (t - CP_T0))


def dm_phase(rate, t_from, t_to):
    """What an arm's hand winds up while excited from t_from to t_to.

    The hand turns at the modulated frequency, so what it has accumulated is
    omega_A integrated across the window rather than omega_A times its length.
    Both windows here are one leg long; the integrals differ all the same, and
    that difference is the whole signal.
    """
    def wound(t):
        return t - DM_EPS * np.cos(DM_OMEGA * (t - CP_T0)) / DM_OMEGA

    return rate * (wound(t_to) - wound(t_from))


def make_field_trace(windows):
    """The driving field along the top of the diagram, on its own time axis.

    Built the way make_strain_trace builds h(t), and for the same reason:
    sharing the x axis with the diagram is the point, so a leg and the stretch
    of the oscillation it was excited during stand in the same column and can
    be read off against each other. The curve is the bare sine at a drawing
    amplitude, carrying the shape and not the size.

    `windows` are the (start, end) of the stretches to wash in, one per leg.
    They go uncaptioned: which arm is excited is already on the page in the
    arm colours and in the marker riding the curve, and a caption under each
    wash only repeats it in words. Returns the curve, those washes, and the
    three pulse markers separately, so a scene can bring each one on at the
    moment it is earned.
    """
    def at(t):
        return [t, DM_TRACE_Z + DM_TRACE_AMPLITUDE * dm_field(t), 0]

    zero = DashedLine(
        [DM_TRACE_X[0], DM_TRACE_Z, 0], [DM_TRACE_X[1], DM_TRACE_Z, 0],
        **GUIDE_STYLE,
    )
    curve = ParametricFunction(
        at, t_range=[*DM_TRACE_X, 0.02],
        color=FIELD_COLOR, stroke_width=FIELD_STROKE_WIDTH,
    )
    tag = MathTex(
        r"\delta\omega_A/\omega_A", font_size=FONT_LEGEND, color=FIELD_COLOR
    ).next_to(curve, RIGHT, buff=0.2)

    top = DM_TRACE_Z + DM_TRACE_AMPLITUDE + 0.2
    bottom = DM_TRACE_Z - DM_TRACE_AMPLITUDE - 0.2
    bands = VGroup()
    for t_from, t_to in windows:
        bands.add(Rectangle(
            width=t_to - t_from, height=top - bottom, **FIELD_WINDOW_STYLE
        ).move_to([0.5 * (t_from + t_to), 0.5 * (top + bottom), 0]))

    dots = VGroup(*[
        Dot(at(CP_T0 + k * CP_T), radius=0.07, color=LASER_COLOR) for k in range(3)
    ])
    return VGroup(zero, curve, tag), bands, dots


def field_marker(now):
    """A dot riding the trace at the instant the level diagram is showing.

    The one thing that ties the two halves of the figure together: without it
    the trace is a curve and the level diagram is a level, and nothing on the
    page says they are the same number.
    """
    def at():
        t = now.get_value()
        return [t, DM_TRACE_Z + DM_TRACE_AMPLITUDE * dm_field(t), 0]

    return always_redraw(
        lambda: Dot(at(), radius=0.08, color=lighten(KICKED_COLOR))
    )


def dm_upper(now, center=DM_LEVELS):
    """Where |e> sits at time `now`, with the field dragging omega_A around."""
    return center + UP * (
        DM_LEVEL_GAP / 2 + DM_LEVEL_SWING * dm_field(now.get_value())
    )


def make_modulated_levels(now, center=DM_LEVELS):
    """The clock transition with omega_A modulated, against a fixed laser.

    Everything that moves is an always_redraw off `now`, so the diagram is a
    readout of the same time coordinate the interferometer below it runs on:
    advance `now` over a leg and the level walks over exactly the stretch of
    the oscillation that leg integrated.

    The kets go left of the levels rather than right, which is where the
    single-photon diagram puts them, because the right-hand side is the
    laser's: its arrow, its label, and the detuning bar all live over there
    and the two sides then read as atom and light. Between them stands the
    gap arrow with omega_A beside it, which is the quantity the two sides
    disagree about.
    """
    half = RIGHT * DM_LEVEL_LENGTH / 2
    lower = center + DOWN * DM_LEVEL_GAP / 2
    resonant = center + UP * DM_LEVEL_GAP / 2  # where the laser was tuned

    level_g = Line(
        lower - half, lower + half, color=ATOM_COLOR, stroke_width=LEVEL_STROKE_WIDTH
    )
    ket_g = state_label(r"|g\rangle", ATOM_COLOR).next_to(
        level_g, LEFT, buff=DM_KET_BUFF
    )
    def moving():
        """|e>, its ket and the gap arrow, wherever the field has put them."""
        top = dm_upper(now, center)
        return VGroup(
            Line(
                top - half, top + half,
                color=KICKED_COLOR, stroke_width=LEVEL_STROKE_WIDTH,
            ),
            state_label(r"|e\rangle", KICKED_COLOR).next_to(
                top - half, LEFT, buff=DM_KET_BUFF
            ),
            DoubleArrow(
                lower + RIGHT * DM_GAP_X + UP * DM_LEVEL_INSET,
                top + RIGHT * DM_GAP_X + DOWN * DM_LEVEL_INSET,
                **LEVEL_GAP_ARROW_STYLE,
            ),
            # Beside the arrow rather than under the diagram: the arrow is
            # what is changing length, so the name belongs on it, and it then
            # rides up and down with the level as well.
            MathTex(
                r"\omega_A", font_size=FONT_LEGEND, color=lighten(GUIDE_COLOR)
            ).next_to(
                0.5 * (lower + top) + RIGHT * DM_GAP_X, RIGHT,
                buff=DM_GAP_LABEL_BUFF,
            ),
        )

    # The laser: one arrow, tuned to the unmodulated transition, and never
    # redrawn. It is resonant at the first pulse and at no other moment, which
    # is the whole point of drawing it fixed. Double-ended because it is a
    # frequency being compared against another, not a photon going one way --
    # the single-photon diagram's one-way glow is the arrow for that.
    laser = DoubleArrow(
        lower + RIGHT * DM_LASER_X + UP * DM_LEVEL_INSET,
        resonant + RIGHT * DM_LASER_X + DOWN * DM_LEVEL_INSET,
        **LEVEL_GLOW_ARROW_STYLE,
    )
    resonance = DashedLine(resonant - half, resonant + half, **LEVEL_RESONANCE_STYLE)
    laser_label = MathTex(
        r"\omega_L", font_size=FONT_LEGEND, color=LASER_COLOR
    ).next_to(lower + RIGHT * DM_MARK_X + UP * 0.45, RIGHT, buff=0.06)

    def detuning():
        """delta = omega_L - omega_A(t), drawn where it actually opens up."""
        offset = (dm_upper(now, center) - resonant)[1]
        if abs(offset) < 0.04:
            return VGroup()
        foot = resonant + RIGHT * DM_MARK_X
        bar = Line(foot, foot + UP * offset, color=LASER_COLOR, stroke_width=2)
        label = MathTex(
            r"\delta", font_size=FONT_LEGEND, color=LASER_COLOR
        ).next_to(foot + UP * 0.5 * offset, RIGHT, buff=0.08)
        group = VGroup(bar, label)
        group.set_opacity(min(1.0, abs(offset) / (0.5 * DM_LEVEL_SWING)))
        return group

    # The two halves are handed back as builders rather than as live
    # always_redraws so that a scene can fade a still of the whole diagram in
    # as one thing. An always_redraw rebuilds itself every frame and rewrites
    # its own opacity with it, so it cannot be faded: added straight, the
    # level and its arrow would snap on after the rest had arrived.
    static = VGroup(level_g, ket_g, laser, resonance, laser_label)
    return static, moving, detuning


class DarkMatterPhase(Scene):
    """The same clock, with a dark-matter field oscillating through it.

    ClockPhase's interferometer is symmetric and its hands come back together.
    These do not. The field modulates omega_A; the two arms are excited over
    different windows of the oscillation, so each hand winds up by its own
    integral; the angle left between them is Phi, and the last pulse turns it
    into two populations that are no longer all-or-nothing.

    Drawn on ClockPhase's geometry deliberately: nothing about the instrument
    has changed, only what is passing through it.
    """

    def construct(self):
        title = Tex(
            r"Ultralight dark matter: the phase does not cancel",
            font_size=FONT_TITLE,
        ).to_corner(UL)
        # The trace wants the whole top strip, so the rule for reading the
        # hands goes opposite the title rather than under it.
        hand_key = Tex(
            r"each hand turns while in $|e\rangle$",
            font_size=FONT_LEGEND, color=lighten(GUIDE_COLOR),
        ).to_corner(UR)
        self.play(FadeIn(title), FadeIn(hand_key), run_time=0.9)

        a = np.array([CP_T0, CP_Z, 0.0])
        b = a + RIGHT * CP_T
        b_up = b + UP * CP_ARM
        c = b_up + RIGHT * CP_T
        rate = clock_rate(CP_T)

        # --- what is passing through ---------------------------------------
        trace, bands, dots = make_field_trace([(a[0], b[0]), (b[0], c[0])])
        law = MathTex(
            r"\omega_A \to \omega_A\left[1 + \varepsilon\cos"
            r"(\omega_\phi t + \theta)\right]",
            font_size=FONT_ANNOTATION, color=FIELD_COLOR,
        ).move_to(DM_LAW)
        self.play(FadeIn(trace[0]), Create(trace[1]), FadeIn(trace[2]), run_time=1.2)
        self.play(Write(law), run_time=1.2)

        # --- and what it is doing to the atom -------------------------------
        # One tracker for lab time, shared by the marker on the trace and by
        # the level diagram, and advanced over each leg by draw_legs at
        # exactly the rate the atoms cross the diagram -- which is what makes
        # the level and the leg beneath it the same instant.
        now = ValueTracker(a[0])
        levels, moving, detuning = make_modulated_levels(now)
        marker = field_marker(now)
        # Faded in as a still and then swapped for the live version, so the
        # diagram arrives as one thing. Lab time is not running yet, so the
        # swap is between two identical pictures and cannot be seen.
        still = VGroup(moving(), detuning())
        self.play(FadeIn(levels), FadeIn(still), run_time=0.8)
        self.remove(still)
        self.add(always_redraw(moving), always_redraw(detuning), marker)
        self.wait(0.4)

        # One tracker per arm, as in ClockPhase, but each advanced by the
        # integral over its own window instead of by rate * T.
        kicked_first = ValueTracker(0.0)  # arm 1: excited on leg 1
        kicked_last = ValueTracker(0.0)  # arm 2: excited on leg 2
        # A tracker only runs its updaters if it is in the scene, and it has
        # to be in it ahead of the hands that read it or they lag a frame
        # behind the phase they are drawing. Invisible either way.
        self.add(kicked_first, kicked_last)

        dial = make_dial(CP_DIAL, r"accumulated phase")
        self.play(FadeIn(dial), run_time=0.6)

        self.seed = make_atom(radius=CLOCK_ATOM_RADIUS).move_to(a)
        self.play(FadeIn(self.seed, scale=0.5), run_time=0.5)

        self.big_lo = dial_hand(CP_DIAL, kicked_last, lighten(ATOM_COLOR))
        self.big_hi = dial_hand(CP_DIAL, kicked_first, lighten(KICKED_COLOR))
        self.add(self.big_lo, self.big_hi)

        # What the instrument does, which is the one part a continuous
        # variant rewrites. Everything either side of it -- the trace, the
        # levels, the dial, the readout -- is the same figure either way.
        self.corners = (a, b, b_up, c)
        self.rate = rate
        self.now, self.bands, self.dots = now, bands, dots
        self.kicked_first, self.kicked_last = kicked_first, kicked_last
        self.fly()

        # --- the readout ------------------------------------------------------
        # The hands have missed each other, so the sector between them is the
        # measurement rather than a rounding error, and both ports come out
        # populated: neither the bright fringe ClockPhase ends on nor a null.
        self.remove(self.arm_lo, self.arm_hi, self.hand_lo, self.hand_hi)
        sweep, gap = phase_sweep(CP_DIAL, kicked_last, kicked_first)
        self.play(Flash(dial[0], **{**FLASH_STYLE, "color": AREA_COLOR}), run_time=0.5)
        self.play(FadeIn(sweep), run_time=0.7)
        draw_ports(self, c, CP_OUT, 0.5 * (1 + np.cos(gap)), extra=self.port_extra())
        self.play(Write(readout_equation()), run_time=1.0)

        result = VGroup(
            MathTex(r"\Phi \neq 0", font_size=FONT_STATE),
            Tex(
                # As short as ClockPhase's, and for the same reason: it has to
                # stay under the dial and clear of the port labels to its left.
                r"different $\omega_A$ per leg",
                font_size=FONT_LEGEND, color=lighten(GUIDE_COLOR),
            ),
        ).arrange(DOWN, buff=0.2).next_to(dial, DOWN, buff=0.5)
        self.play(FadeIn(result), run_time=1.0)

        # What the instrument gets out of what the figure has drawn. One
        # interferometer has no L in it -- this one is a single clock, and its
        # phase is the oscillation integrated over two windows that no longer
        # agree. Two of them a baseline apart sample that oscillation L/c out
        # of step, and the length scale appears exactly as it does in the
        # wave's own signal: same form, epsilon where h was. That is the point
        # of putting it here rather than only on the gradiometer scenes.
        scaling = VGroup(
            MathTex(
                r"\Delta\Phi \propto n\,L\,\varepsilon\,"
                r"\sin^2(\omega_\phi T/2)",
                font_size=FONT_ANNOTATION,
            ),
            Tex(
                r"in a gradiometer: the wave's form, with $\varepsilon$ for $h$",
                font_size=FONT_LEGEND, color=lighten(GUIDE_COLOR),
            ),
        ).arrange(DOWN, buff=0.18).move_to(CP_SCALING)
        if scaling.width > CP_SCALING_WIDTH:
            scaling.scale(CP_SCALING_WIDTH / scaling.width)
        self.play(FadeIn(scaling), run_time=1.0)
        self.wait(2.0)

    def split(self, at):
        """The beamsplitter's output: two arms, each carrying its own hand.

        Shared by both variants, because what the pulse produces does not
        depend on how the pulse was drawn.
        """
        self.arm_lo = make_atom(
            radius=CLOCK_ATOM_RADIUS, opacity=SUPERPOSITION_OPACITY
        ).move_to(at)
        self.arm_hi = make_atom(
            KICKED_COLOR, radius=CLOCK_ATOM_RADIUS, opacity=SUPERPOSITION_OPACITY
        ).move_to(at)
        self.hand_lo = make_clock_hand(self.arm_lo, self.kicked_last)
        self.hand_hi = make_clock_hand(self.arm_hi, self.kicked_first)
        self.remove(self.seed)
        self.add(self.arm_lo, self.arm_hi, self.hand_lo, self.hand_hi)
        return self.arm_lo, self.arm_hi

    def port_extra(self):
        """What rides along with the output ports. Nothing, unless lab time does."""
        return ()

    def fly(self):
        """Three pulses and two legs, one at a time.

        The atoms wait for each pulse to be drawn. That is the explainer's
        pacing and it is deliberate here too -- but it stops the field along
        with them, which is what DarkMatterPhaseContinuous is for.
        """
        a, b, b_up, c = self.corners
        now, bands, dots = self.now, self.bands, self.dots
        leg_one = dm_phase(self.rate, a[0], b[0])
        leg_two = dm_phase(self.rate, b[0], c[0])

        # --- the beamsplitter ----------------------------------------------
        self.play(FadeIn(dots[0], scale=0.4), run_time=0.3)
        fire_vertical_pulse(self, a[0], [self.seed])
        arm_lo, arm_hi = self.split(a)

        # --- leg 1: arm 1 is excited, over the positive half-cycle ----------
        self.play(FadeIn(bands[0]), run_time=0.5)
        draw_legs(self, [
            (arm_lo, a, b, ATOM_COLOR),
            (arm_hi, a, b_up, KICKED_COLOR),
        ], extra=[
            self.kicked_first.animate.set_value(leg_one),
            now.animate.set_value(b[0]),
        ])

        # --- the mirror: the arms swap, and so does the window ---------------
        # The same pulse that reverses the momenta hands the excitation over,
        # which is what makes the two arms sample the field at different times
        # rather than together.
        self.play(FadeIn(dots[1], scale=0.4), run_time=0.3)
        fire_vertical_pulse(self, b[0], [arm_lo, arm_hi])
        self.play(
            state_colors(arm_lo, KICKED_COLOR),
            state_colors(arm_hi, ATOM_COLOR),
            self.big_lo.animate.set_color(lighten(KICKED_COLOR)),
            self.big_hi.animate.set_color(lighten(ATOM_COLOR)),
            run_time=0.5,
        )

        # --- leg 2: arm 2 is excited, over the negative half-cycle ----------
        self.play(FadeIn(bands[1]), run_time=0.5)
        draw_legs(self, [
            (arm_lo, b, c, KICKED_COLOR),
            (arm_hi, b_up, c, ATOM_COLOR),
        ], extra=[
            self.kicked_last.animate.set_value(leg_two),
            now.animate.set_value(c[0]),
        ])

        # --- recombine -------------------------------------------------------
        self.play(FadeIn(dots[2], scale=0.4), run_time=0.3)
        fire_vertical_pulse(self, c[0], [arm_lo])


class DarkMatterPhaseContinuous(DarkMatterPhase):
    """The same figure with lab time never stopped.

    DarkMatterPhase stops the atoms while each pulse is drawn, and since the
    x axis is lab time it stops the field with them: the trace marker, the
    level diagram and the detuning all sit still for seconds at a time while
    the thing the scene is about is supposed to be oscillating. Here one clock
    runs from the first pulse to the last and everything is a function of it,
    so the level and the leg beneath it are the same instant throughout.

    The price is the pulses. A column that is instantaneous in lab time cannot
    be given a drawn-out climb without lying about it, so it strobes: it
    appears whole on the instant and is gone in PULSE_HOLD. ClockPhase has
    already said what a pi/2 pulse does; this figure is about what is passing
    through, and it gets to spend its time on that instead.
    """

    def port_extra(self):
        # By the same amount the ports run, not to the same place: the last
        # strobe has already carried lab time a little past the final corner,
        # and what has to match is the rate, so the trace keeps step with the
        # atoms underneath it.
        return [self.now.animate.set_value(self.now.get_value() + CP_OUT)]

    def close(self, dial, sweep, gap, c):
        """All at once here, because the ports are still the atoms flying.

        The last pulse leaves two populations heading out along the diagram's
        own time axis. Holding them at the vertex while a sector fades onto a
        dial would be the stop-start pacing creeping back in at the one moment
        the scene has left, so instead they fly out of the pulse and the dial
        is read while they go -- which is also the truer picture, the angle
        between the hands and the split between the ports being one fact.
        draw_legs' extra hook already takes anything that has to happen over
        exactly that stretch of flight, so this costs a list rather than a
        mechanism.
        """
        draw_ports(
            self, c, CP_OUT, 0.5 * (1 + np.cos(gap)),
            extra=[
                *self.port_extra(),
                Flash(dial[0], **{**FLASH_STYLE, "color": AREA_COLOR}),
                FadeIn(sweep),
            ],
        )

    def fly(self):
        a, b, b_up, c = self.corners
        now, bands, dots = self.now, self.bands, self.dots

        # The washes fill in behind the legs and the trace markers light as
        # lab time reaches each pulse, so neither one costs a beat of its own.
        self.add(
            growing_band(bands[0], a[0], b[0], now),
            growing_band(bands[1], b[0], c[0], now),
        )
        for k, dot in enumerate(dots):
            dot.add_updater(lambda m, k=k: m.set_opacity(
                1.0 if now.get_value() >= a[0] + k * CP_T else 0.0
            ))
        self.add(dots)

        # Each hand turns at the modulated frequency while its own arm is
        # excited and holds once the mirror hands the excitation over. An
        # updater rather than draw_legs' extra, which is what lets them keep
        # turning through the pulses as well as along the legs.
        rate = self.rate
        self.kicked_first.add_updater(lambda m: m.set_value(
            dm_phase(rate, a[0], float(np.clip(now.get_value(), a[0], b[0])))
        ))
        self.kicked_last.add_updater(lambda m: m.set_value(
            dm_phase(rate, b[0], float(np.clip(now.get_value(), b[0], c[0])))
        ))

        # --- the beamsplitter ----------------------------------------------
        # On the instant, not after it: the arms are put on their worldlines
        # as the pulse arrives, so they are already moving while the column is
        # still on the screen.
        def split():
            arm_lo, arm_hi = self.split(a)
            carry(arm_lo, worldline([a, b, c]), now)
            carry(arm_hi, worldline([a, b_up, c]), now)
            # One trail per leg rather than per arm: the two arms swap states
            # at the mirror, so the colour belongs to the leg.
            self.add(
                growing_trail([a, b], ATOM_COLOR, now),
                growing_trail([b, c], KICKED_COLOR, now),
                growing_trail([a, b_up], KICKED_COLOR, now),
                growing_trail([b_up, c], ATOM_COLOR, now),
            )

        strobe_pulse(self, now, a[0], top=a[1], flash_at=[a], on_arrival=split)

        # --- the mirror -----------------------------------------------------
        def swap():
            self.arm_lo[0].set_fill(KICKED_COLOR).set_stroke(lighten(KICKED_COLOR))
            self.arm_hi[0].set_fill(ATOM_COLOR).set_stroke(lighten(ATOM_COLOR))
            self.big_lo.set_color(lighten(KICKED_COLOR))
            self.big_hi.set_color(lighten(ATOM_COLOR))

        strobe_pulse(
            self, now, b[0], top=b_up[1], flash_at=[b, b_up], on_arrival=swap
        )

        # --- recombine -------------------------------------------------------
        strobe_pulse(self, now, c[0], top=c[1], flash_at=[c])

# --- a gravitational wave passing through ---------------------------------
# A wave of period 2T is the resonant case, and the reason these scenes work:
# the three pulses land on crest, trough and crest, so the modulation builds up
# across the sequence instead of dropping out of the difference the way a
# static gradient -- or the laser's own phase noise -- does.
#
# Two exaggerations, because the diagram draws L and L/c at wildly different
# scales, and a single factor cannot make both readable. GW_LAG_GAIN is the
# swing in light travel time, GW_STRETCH_GAIN the swing in the baseline drawn
# as a displacement. Both stand for the same dimensionless h, ~1e-21 in reality.
# Every scene takes its pulse timing from GW_LAG_GAIN, including the stretch
# one, so that the two pictures of the wave read out the same phase.
#
# GW_LAG_GAIN is also what sets how the output ports split, and that is what
# fixes its value. A pulse is held up in proportion to how far it has come, so
# the near cloud -- sitting close to the laser -- always responds about five
# times less than the far one, and no single gain can drive both to a half
# and half split. At 0.8 every port has something in it (the near pair splits
# about 81/19, the far pair about 28/72) and the two ends still read visibly
# differently, which is the whole claim of the figure. Smaller gains leave the
# near cloud's excited port too faint to see; 0.6 drove the far cloud through
# very nearly a half turn, so its ground port came out empty and the far
# interferometer read as a complete transfer rather than as a split.
GW_PERIOD = 2 * GR_T
GW_OMEGA = TAU / GW_PERIOD
GW_LAG_GAIN = 0.8
GW_STRETCH_GAIN = 0.16
GW_PULSES = [GR_T0, GR_T0 + GR_T, GR_T0 + 2 * GR_T]

# the h(t) trace, drawn on the diagram's own time axis
GW_TRACE_Z = 2.75
GW_TRACE_AMPLITUDE = 0.28
GW_TRACE_X = (GR_T0 - 0.6, GR_T0 + 2 * GR_T + 0.8)


def strain(t):
    """h(t) at the detector, normalised to +-1 and phased so pulse 1 is on a crest."""
    return np.cos(GW_OMEGA * (t - GR_T0))


def gw_lag(t, gain=GW_LAG_GAIN):
    """Light travel time across the baseline while the wave is passing."""
    return GR_LAG * (1.0 + gain * strain(t))


GR_LASER_GAP = GR_LOWER_Z - GR_LASER_Z  # laser to the near cloud


def gw_arrival_lags(z):
    """How late each pulse reaches the point z on the baseline once the wave is
    passing.

    The wave stretches every stretch of the shaft by the same fraction, so a
    pulse is held up in proportion to how far it has come. The near cloud is
    not immune, only nearer: it picks up a smaller shift than the far one.
    What is left in the difference is the part that scales with the separation
    between the two clouds, which is the whole point of the instrument.
    """
    span = z - GR_LASER_Z
    return [gw_lag(t) / GR_BASELINE * span for t in GW_PULSES]


def quiet_arrival(k):
    """When pulse k would have reached the lower cloud with no wave passing."""
    return GW_PULSES[k] + GR_SLOPE * GR_LASER_GAP


def gw_displacement(t, z0):
    """How far the wave has moved a cloud nominally at z0 on the baseline.

    Symmetric about the middle of the baseline: in the local frame of an
    observer there, a passing wave pushes the two ends apart and together and
    leaves the midpoint alone, so the two clouds bow in antiphase.
    """
    return (z0 - GR_MID_Z) * GW_STRETCH_GAIN * strain(t)


def make_strain_trace(label=r"h(t)"):
    """The wave above the diagram, on the diagram's own time axis.

    The curve is the bare cosine at a drawing amplitude, so it carries which
    part of the wave each pulse samples and nothing about how big the wave is.
    That is why the label is a caller's choice: h(t) and Delta L(t) = L h(t)
    are the same shape, and a scene should name whichever one it is drawing.

    Sharing the x axis is the point: a pulse and the phase of the wave it
    samples sit in the same column, so crest-trough-crest can be read off
    against the pulses that produced it. Returns the curve and its three pulse
    markers separately, so a scene can light each marker as that pulse fires.
    """
    def at(t):
        return [t, GW_TRACE_Z + GW_TRACE_AMPLITUDE * strain(t), 0]

    zero = DashedLine(
        [GW_TRACE_X[0], GW_TRACE_Z, 0], [GW_TRACE_X[1], GW_TRACE_Z, 0],
        **GUIDE_STYLE,
    )
    curve = ParametricFunction(
        at, t_range=[*GW_TRACE_X, 0.02],
        color=STRAIN_COLOR, stroke_width=STRAIN_STROKE_WIDTH,
    )
    tag = MathTex(
        label, font_size=FONT_LEGEND, color=STRAIN_COLOR
    ).next_to(curve, LEFT, buff=0.18)
    dots = VGroup(*[Dot(at(t), radius=0.07, color=LASER_COLOR) for t in GW_PULSES])
    return VGroup(zero, curve, tag), dots


def strain_marker(clock):
    """field_marker's twin: where on the wave the diagram has got to.

    The three pulse dots say which part of the wave each pulse sampled, which
    is all a stop-start scene can show. Once lab time is running the trace can
    say it continuously, and without this it would be the one thing in the
    frame standing still. Held at the ends of the drawn curve, as the field
    marker is, because the output ports run on past the last pulse.
    """
    def at():
        t = float(np.clip(clock.get_value(), *GW_TRACE_X))
        return [t, GW_TRACE_Z + GW_TRACE_AMPLITUDE * strain(t), 0]

    return always_redraw(
        lambda: Dot(at(), radius=0.08, color=lighten(KICKED_COLOR))
    )


def gw_vertices(z0, lags):
    """The four corners when the three pulses arrive `lags` after they are fired.

    Every corner is anchored on its own pulse's arrival, which keeps the loop
    closed and keeps each flash centred on its atom. The price is that the two
    kicked legs pick up slightly different slopes, i.e. a recoil velocity that
    ought to be identical differs by a few per cent. That is the right trade:
    the real effect is a phase, not a change in the shape of the loop, and an
    interferometer drawn failing to close would read as a bug rather than as
    physics. The skew that is left is an artefact of the exaggeration.
    """
    t = [GW_PULSES[k] + lags[k] for k in range(3)]
    a = np.array([t[0], z0, 0.0])
    b = np.array([t[1], z0, 0.0])
    b_up = b + UP * GR_ARM
    c = np.array([t[2], z0 + GR_ARM, 0.0])
    return a, b, b_up, c


def draw_wavy_legs(scene, legs, fade=(), extra=()):
    """draw_legs for clouds whose worldlines carry the wave's displacement.

    draw_legs creates a straight Line and walks the atom to the far end. That
    will not do on a bowed leg: Create paints a curve by point index while an
    atom animated along it moves by arc length, and the two come apart by
    something like a fifth of the leg -- the atom visibly trails the end of
    the line it is supposed to be drawing. So the atom and the trail behind it
    are both redrawn from the one parameter, and stay together by construction.
    """
    s = ValueTracker(0.0)
    trails = [
        always_redraw(
            lambda leg=leg: wavy_path(leg[1], leg[2], leg[3], leg[4], s.get_value())
        )
        for leg in legs
    ]
    for atom, start, end, _, disp in legs:
        atom.add_updater(
            lambda m, start=start, end=end, disp=disp: m.move_to(
                leg_point(start, end, disp, s.get_value())
            )
        )
    scene.add(*trails)

    dx = abs(legs[0][2][0] - legs[0][1][0])
    scene.play(
        s.animate.set_value(1.0),
        *extra,
        *[FadeOut(m) for m in fade],
        rate_func=linear,
        run_time=dx / V,
    )

    # Freeze the finished legs: a live trail would be rebuilt against the next
    # leg's tracker, and an atom left with its updater would be pinned to the
    # end of the leg it has just finished.
    for atom, *_ in legs:
        atom.clear_updaters()
    scene.remove(*trails)
    scene.add(*[wavy_path(l[1], l[2], l[3], l[4]) for l in legs])
    scene.bring_to_front(*[l[0] for l in legs])


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


def arrival_note(point, lag):
    """Names an arrival early or late against the quiet baseline's own L/c.

    It sits below the cloud, which is the one direction that stays clear: the
    arms climb away above it and the pulse is only passing through underneath.
    """
    word = "arrives late" if lag > GR_LAG else "arrives early"
    return Tex(word, font_size=FONT_LEGEND, color=LASER_COLOR).next_to(
        point, DOWN, buff=0.3
    ).shift(RIGHT * 1.1)


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


# --- large momentum transfer geometry -------------------------------------
# Same space-time frame. Each pulse adds one photon recoil to the upper arm,
# so its worldline steepens by a fixed slope per kick while the lower arm
# stays put; the arms end up n*hbar*k apart instead of hbar*k.
LMT_T0 = -5.0
LMT_Z = -2.8
LMT_STEP = 1.4  # time between kicks in the ladder
LMT_TAIL = 1.6  # free flight after the last kick
LMT_U = 0.35  # baseline covered per unit time, per photon recoil
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


# --- the clock transition, drawn as a two-level system --------------------
# What makes AION a *single-photon* interferometer is that the transition it
# drives is narrow: in strontium the 1S0 -> 3P0 clock line at 698 nm has a
# natural linewidth of order millihertz, so an atom parked in |e> stays there
# for the whole interrogation time. Elsewhere a pair of Raman photons is
# needed to leave the atom in a long-lived ground-state sublevel; here one
# photon does the work, and the laser's phase is written into the atom once
# per pulse instead of twice.
#
# The diagram sits upper left and doubles as the figure's key: |g> carries
# ATOM_COLOR and |e> carries KICKED_COLOR, which are the colours the two arms
# are drawn in, so it says everything a separate legend would and also says
# what the pulses are resonant with. Upper left is the one corner it can sit
# in -- the mirror's emitted photons climb the column x = MZ_B[0] and out of
# the top of the frame, and the title already occupies the right.
SP_LEVELS = np.array([-5.5, 2.05, 0.0])  # centre of the gap
SP_LEVEL_LENGTH = 1.6
SP_LEVEL_GAP = 1.6  # vertical separation of the two levels
SP_LEVEL_INSET = 0.1  # how far the gap arrow stands off each level line
SP_KET_BUFF = 0.2
SP_CAPTION_BUFF = 0.3


def make_level_diagram(center=SP_LEVELS):
    """The Sr clock transition as a two-level system, with the gap labelled.

    |g> and |e> are the atom's internal states only -- the momentum a photon
    hands over lives in the interferometer beside it, not in here.
    """
    half = RIGHT * SP_LEVEL_LENGTH / 2
    lower = center + DOWN * SP_LEVEL_GAP / 2
    upper = center + UP * SP_LEVEL_GAP / 2

    level_g = Line(
        lower - half, lower + half, color=ATOM_COLOR, stroke_width=LEVEL_STROKE_WIDTH
    )
    level_e = Line(
        upper - half, upper + half, color=KICKED_COLOR, stroke_width=LEVEL_STROKE_WIDTH
    )
    ket_g = state_label(r"|g\rangle", ATOM_COLOR).next_to(
        level_g, RIGHT, buff=SP_KET_BUFF
    )
    ket_e = state_label(r"|e\rangle", KICKED_COLOR).next_to(
        level_e, RIGHT, buff=SP_KET_BUFF
    )

    gap = DoubleArrow(
        lower + UP * SP_LEVEL_INSET,
        upper + DOWN * SP_LEVEL_INSET,
        **LEVEL_GAP_ARROW_STYLE,
    )
    gap_label = MathTex(
        r"\hbar\omega_A", font_size=FONT_ANNOTATION, color=lighten(GUIDE_COLOR)
    ).next_to(gap, RIGHT, buff=0.15)

    caption = VGroup(
        Tex("Sr clock transition", font_size=FONT_LEGEND, color=lighten(GUIDE_COLOR)),
        MathTex(
            r"{}^1S_0 \to {}^3P_0,\ 698\,\text{nm}",
            font_size=FONT_LEGEND,
            color=lighten(GUIDE_COLOR),
        ),
    ).arrange(DOWN, buff=0.12)
    caption.next_to(level_g, DOWN, buff=SP_CAPTION_BUFF)

    return VGroup(level_g, level_e, ket_g, ket_e, gap, gap_label, caption)


def transition_glow(upward=True, center=SP_LEVELS):
    """The transition lit up in the laser's colour while a pulse drives it.

    Up while a photon is being absorbed, down at the mirror, where the excited
    arm is stimulated back to |g>. It is the same energy gap either way, so
    the glow is drawn over the gap arrow rather than beside it.
    """
    lower = center + DOWN * (SP_LEVEL_GAP / 2 - SP_LEVEL_INSET)
    upper = center + UP * (SP_LEVEL_GAP / 2 - SP_LEVEL_INSET)
    start, end = (lower, upper) if upward else (upper, lower)
    return Arrow(start, end, **LEVEL_GLOW_ARROW_STYLE)


class SinglePhotonMachZehnder(MachZehnder):
    """pi/2 - pi - pi/2 driven by single photons, beside the transition it drives.

    Same geometry and the same pulse captions as the Mach-Zehnder in
    atom_interferometry.py, but the two-level system takes the corner the
    legend used to hold, and lights up each time a wavepacket reaches an atom.
    """

    def construct(self):
        # --- 1. setup ----------------------------------------------------
        # Title right, levels left: the two photons stimulated out of the
        # upper arm at the mirror fly straight up x = MZ_B[0] and off the top
        # of the frame, so that column has to stay clear of both.
        title = Tex(
            r"Single-photon Mach--Zehnder: $\pi/2 - \pi - \pi/2$",
            font_size=FONT_TITLE,
        ).to_corner(UR)
        levels = make_level_diagram()
        guide = make_guide([-config.frame_x_radius, MZ_A[1], 0], MZ_A)
        self.play(FadeIn(title), FadeIn(levels), FadeIn(guide), run_time=1.0)

        # --- 2. incoming atom --------------------------------------------
        atom = make_atom().move_to([-config.frame_x_radius + 0.2, MZ_A[1], 0])
        self.play(FadeIn(atom, scale=0.5), run_time=0.5)
        self.play(
            atom.animate.move_to(MZ_A),
            rate_func=linear,
            run_time=(MZ_A[0] - atom.get_center()[0]) / V,
        )

        # --- 3. first pi/2: split ----------------------------------------
        # One photon, one transition: the glow rises with the wavepacket and
        # goes out as the atom takes it up.
        k_arrow = make_k_arrow(MZ_A[0] - 0.9, -config.frame_y_radius + 0.45)
        glow = transition_glow()
        absorb(
            self,
            MZ_A[0],
            atom,
            extras=[self.pulse_caption(r"\pi/2", MZ_A[0]), k_arrow, glow],
            fade=[k_arrow, glow],
        )

        lower = make_atom(opacity=SUPERPOSITION_OPACITY).move_to(MZ_A)
        upper = make_atom(KICKED_COLOR, opacity=SUPERPOSITION_OPACITY).move_to(MZ_A)
        recoil = momentum_arrow(MZ_A, UP, r"\hbar k")

        self.remove(atom)
        self.add(lower, upper)
        self.play(*grow(recoil), run_time=0.6)

        # Each leg is coloured by the state that arm is in while traversing it.
        draw_legs(
            self,
            [(lower, MZ_A, MZ_B, ATOM_COLOR), (upper, MZ_A, MZ_B_UP, KICKED_COLOR)],
            fade=[recoil],
        )

        # --- 4. pi pulse: the mirror -------------------------------------
        # The two arms do opposite things to the same beam. The ground-state
        # arm absorbs, gains hbar k and climbs; the excited arm is stimulated
        # back down to |g>, emits into the mode of the driving field and
        # recoils by -hbar k, which flattens it out. The level diagram shows
        # which way each one is being driven.
        gain = momentum_arrow(MZ_B, UP, r"+\hbar k")
        lose = momentum_arrow(MZ_B_UP, DOWN, r"-\hbar k", label_dir=RIGHT)

        glow_up = transition_glow()
        absorb(
            self,
            MZ_B[0],
            lower,
            extras=[self.pulse_caption(r"\pi", MZ_B[0]), glow_up],
            fade=[glow_up],
        )
        self.play(state_colors(lower, KICKED_COLOR), *grow(gain), run_time=0.6)

        glow_down = transition_glow(upward=False)
        emit(self, MZ_B_UP[0], upper, extras=[glow_down])
        self.play(
            state_colors(upper, ATOM_COLOR),
            *grow(lose),
            FadeOut(glow_down),
            run_time=0.6,
        )
        draw_legs(
            self,
            [(lower, MZ_B, MZ_C, KICKED_COLOR), (upper, MZ_B_UP, MZ_C, ATOM_COLOR)],
            fade=[gain, lose],
        )

        # --- 5. second pi/2: recombine -----------------------------------
        # Both arms sit at MZ_C now, so one pulse covers them.
        glow = transition_glow()
        absorb(
            self,
            MZ_C[0],
            lower,
            extras=[self.pulse_caption(r"\pi/2", MZ_C[0]), glow],
            fade=[glow],
        )

        port_g = make_atom(opacity=SUPERPOSITION_OPACITY).move_to(MZ_C)
        port_e = make_atom(KICKED_COLOR, opacity=SUPERPOSITION_OPACITY).move_to(MZ_C)
        self.remove(lower, upper)
        self.add(port_g, port_e)
        draw_legs(
            self,
            [
                (port_g, MZ_C, MZ_C + RIGHT * MZ_OUT, ATOM_COLOR),
                (port_e, MZ_C, MZ_C + (RIGHT + UP) * MZ_OUT, KICKED_COLOR),
            ],
        )

        # --- 6. the enclosed area and the output ports -------------------
        loop = Polygon(MZ_A, MZ_B, MZ_C, MZ_B_UP, **LOOP_AREA_STYLE)
        phase = MathTex(
            r"\Phi", font_size=FONT_PHASE, color=lighten(AREA_COLOR)
        ).move_to((MZ_A + MZ_B + MZ_C + MZ_B_UP) / 4)
        p1 = state_label(r"P_g", ATOM_COLOR).next_to(port_g, RIGHT, buff=0.3)
        p2 = state_label(r"P_e", KICKED_COLOR).next_to(port_e, RIGHT, buff=0.3)
        readout = MathTex(
            r"P_{g,e} = \tfrac{1}{2}\left(1 \pm \cos\Phi\right)",
            font_size=FONT_ANNOTATION,
        ).to_corner(DR)

        self.play(FadeIn(loop), FadeIn(phase), run_time=0.8)
        self.play(Write(p1), Write(p2), Write(readout), run_time=1.3)
        self.wait(2.0)
