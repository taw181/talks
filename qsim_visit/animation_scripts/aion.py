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
GR_SIGNAL = np.array([-1.5, -0.35, 0.0])

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


def draw_ports(scene, origin, length, p_ground, labels=True):
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
    """
    empty, legs, tags = VGroup(), [], VGroup()
    for direction, color, p, tex, label_dir in (
        (RIGHT, ATOM_COLOR, p_ground, r"P_1", DOWN),
        (RIGHT + UP, KICKED_COLOR, 1.0 - p_ground, r"P_2", UP),
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

    if len(empty):
        scene.play(FadeIn(empty), run_time=0.5)
    if legs:
        draw_legs(scene, legs)
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
        r"P_{1,2} = \tfrac{1}{2}\left(1 \pm \cos\Phi\right)",
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
DM_LAW = np.array([-3.0, 0.8, 0.0])


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

    `windows` are the (start, end, caption) of the stretches to wash in, one
    per leg. Returns the curve, those washes, and the three pulse markers
    separately, so a scene can bring each one on at the moment it is earned.
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
    for t_from, t_to, caption in windows:
        band = Rectangle(
            width=t_to - t_from, height=top - bottom, **FIELD_WINDOW_STYLE
        ).move_to([0.5 * (t_from + t_to), 0.5 * (top + bottom), 0])
        bands.add(VGroup(band, Tex(
            caption, font_size=FONT_LEGEND, color=lighten(GUIDE_COLOR)
        ).next_to(band, DOWN, buff=0.12)))

    dots = VGroup(*[
        Dot(at(CP_T0 + k * CP_T), radius=0.07, color=LASER_COLOR) for k in range(3)
    ])
    return VGroup(zero, curve, tag), bands, dots


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
        trace, bands, dots = make_field_trace([
            (a[0], b[0], r"arm 1 excited"),
            (b[0], c[0], r"arm 2 excited"),
        ])
        law = MathTex(
            r"\omega_A \to \omega_A\left[1 + \varepsilon\cos"
            r"(\omega_\phi t + \theta)\right]",
            font_size=FONT_ANNOTATION, color=FIELD_COLOR,
        ).move_to(DM_LAW)
        self.play(FadeIn(trace[0]), Create(trace[1]), FadeIn(trace[2]), run_time=1.2)
        self.play(Write(law), run_time=1.2)

        # One tracker per arm, as in ClockPhase, but each advanced by the
        # integral over its own window instead of by rate * T.
        kicked_first = ValueTracker(0.0)  # arm 1: excited on leg 1
        kicked_last = ValueTracker(0.0)  # arm 2: excited on leg 2
        leg_one = dm_phase(rate, a[0], b[0])
        leg_two = dm_phase(rate, b[0], c[0])

        dial = make_dial(CP_DIAL, r"accumulated phase")
        self.play(FadeIn(dial), run_time=0.6)

        seed = make_atom(radius=CLOCK_ATOM_RADIUS).move_to(a)
        self.play(FadeIn(seed, scale=0.5), run_time=0.5)

        # --- the beamsplitter ----------------------------------------------
        self.play(FadeIn(dots[0], scale=0.4), run_time=0.3)
        fire_vertical_pulse(self, a[0], [seed])
        arm_lo = make_atom(
            radius=CLOCK_ATOM_RADIUS, opacity=SUPERPOSITION_OPACITY
        ).move_to(a)
        arm_hi = make_atom(
            KICKED_COLOR, radius=CLOCK_ATOM_RADIUS, opacity=SUPERPOSITION_OPACITY
        ).move_to(a)
        self.remove(seed)
        self.add(arm_lo, arm_hi)

        big_lo = dial_hand(CP_DIAL, kicked_last, lighten(ATOM_COLOR))
        big_hi = dial_hand(CP_DIAL, kicked_first, lighten(KICKED_COLOR))
        hand_lo = make_clock_hand(arm_lo, kicked_last)
        hand_hi = make_clock_hand(arm_hi, kicked_first)
        self.add(hand_lo, hand_hi, big_lo, big_hi)

        # --- leg 1: arm 1 is excited, over the positive half-cycle ----------
        self.play(FadeIn(bands[0]), run_time=0.5)
        draw_legs(self, [
            (arm_lo, a, b, ATOM_COLOR),
            (arm_hi, a, b_up, KICKED_COLOR),
        ], extra=[kicked_first.animate.set_value(leg_one)])

        # --- the mirror: the arms swap, and so does the window ---------------
        # The same pulse that reverses the momenta hands the excitation over,
        # which is what makes the two arms sample the field at different times
        # rather than together.
        self.play(FadeIn(dots[1], scale=0.4), run_time=0.3)
        fire_vertical_pulse(self, b[0], [arm_lo, arm_hi])
        self.play(
            state_colors(arm_lo, KICKED_COLOR),
            state_colors(arm_hi, ATOM_COLOR),
            big_lo.animate.set_color(lighten(KICKED_COLOR)),
            big_hi.animate.set_color(lighten(ATOM_COLOR)),
            run_time=0.5,
        )

        # --- leg 2: arm 2 is excited, over the negative half-cycle ----------
        self.play(FadeIn(bands[1]), run_time=0.5)
        draw_legs(self, [
            (arm_lo, b, c, KICKED_COLOR),
            (arm_hi, b_up, c, ATOM_COLOR),
        ], extra=[kicked_last.animate.set_value(leg_two)])

        # --- recombine -------------------------------------------------------
        self.play(FadeIn(dots[2], scale=0.4), run_time=0.3)
        fire_vertical_pulse(self, c[0], [arm_lo])

        # --- the readout ------------------------------------------------------
        # The hands have missed each other, so the sector between them is the
        # measurement rather than a rounding error, and both ports come out
        # populated: neither the bright fringe ClockPhase ends on nor a null.
        self.remove(arm_lo, arm_hi, hand_lo, hand_hi)
        sweep, gap = phase_sweep(CP_DIAL, kicked_last, kicked_first)
        self.play(Flash(dial[0], **{**FLASH_STYLE, "color": AREA_COLOR}), run_time=0.5)
        self.play(FadeIn(sweep), run_time=0.7)
        draw_ports(self, c, CP_OUT, 0.5 * (1 + np.cos(gap)))
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
        self.wait(2.0)


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


def leg_point(start, end, disp, s):
    """Where an atom on a bowed leg is, a fraction s of the way along it.

    The displacement is subtracted at the two ends and added back along the
    way, so the leg still passes exactly through both corners -- the pulses
    have to land on the atoms.
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
        seed_low = make_atom(radius=CLOCK_ATOM_RADIUS).move_to(low[0])
        seed_up = make_atom(radius=CLOCK_ATOM_RADIUS).move_to(up[0])
        self.play(FadeIn(seed_low, scale=0.5), FadeIn(seed_up, scale=0.5), run_time=0.6)

        # --- pulse 1: the beamsplitter, arriving late on a crest ----------
        self.play(FadeIn(dots[0], scale=0.4), run_time=0.3)
        # The dashed ghost has to be named once, or "late" is late against
        # nothing in particular.
        fire_pulse(
            self, GW_PULSES[0] + low_lags[0], flash=[seed_low, seed_up],
            lag=lags[0], reference=True, quiet_x=quiet_arrival(0),
            note=VGroup(
                arrival_note(up[0], lags[0]),
                Tex(
                    r"no wave", font_size=FONT_LEGEND, color=lighten(GUIDE_COLOR)
                ).move_to([GW_PULSES[0] + 1.25, GR_MID_Z, 0]),
            ),
        )
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
        self.play(FadeIn(dots[1], scale=0.4), run_time=0.3)
        fire_pulse(
            self, GW_PULSES[1] + low_lags[1],
            flash=[a for p in atoms.values() for a in p],
            lag=lags[1], reference=True, quiet_x=quiet_arrival(1),
            note=arrival_note(up[1], lags[1]),
        )
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
        self.play(FadeIn(dots[2], scale=0.4), run_time=0.3)
        fire_pulse(
            self, GW_PULSES[2] + low_lags[2], flash=[atoms["low"][0], atoms["up"][0]],
            lag=lags[2], reference=True, quiet_x=quiet_arrival(2),
        )

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
        self.play(*[FadeIn(m) for m in sweeps], run_time=0.7)

        # And the same angle as a population. The wave pulled the far cloud's
        # two pulse intervals further apart than the near cloud's, so the two
        # interferometers split their ports by different amounts. That
        # difference is the signal: one laser, two clocks, and only what is
        # not common to both survives.
        self.remove(*atoms["low"], *atoms["up"], *hands)
        for cloud, v in (("low", low), ("up", up)):
            draw_ports(
                self, v[3], GR_OUT,
                ground_share(phase[cloud][1], phase[cloud][0]),
                labels=False,
            )

        signal = VGroup(
            Tex(
                r"the wave changes the light travel time, more for the far cloud",
                font_size=FONT_LEGEND, color=lighten(GUIDE_COLOR),
            ),
            MathTex(
                r"\Delta\Phi = \Phi_{\text{upper}} - \Phi_{\text{lower}}",
                font_size=FONT_ANNOTATION,
            ),
        ).arrange(DOWN, buff=0.22).move_to(GR_SIGNAL)
        if signal.width > GR_TERMS_WIDTH:
            signal.scale(GR_TERMS_WIDTH / signal.width)
        self.play(FadeIn(signal), run_time=1.0)
        self.wait(2.0)


def arrival_note(point, lag):
    """Names an arrival early or late against the quiet baseline's own L/c.

    It sits below the cloud, which is the one direction that stays clear: the
    arms climb away above it and the pulse is only passing through underneath.
    """
    word = "arrives late" if lag > GR_LAG else "arrives early"
    return Tex(word, font_size=FONT_LEGEND, color=LASER_COLOR).next_to(
        point, DOWN, buff=0.3
    ).shift(RIGHT * 1.1)


class GradiometerGWStretch(Scene):
    """The same wave drawn as a stretching baseline, for comparison.

    The picture most people carry: the wave pushes the ends of the baseline
    apart and together, so the two clouds bow in antiphase about its midpoint
    and L breathes. It is the proper-distance picture rather than the one the
    experiment reads out -- GradiometerGW is what the phase actually comes
    from -- but the two are the same wave, and the same h(t) runs above both.
    """

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
        seed_low = make_atom(radius=CLOCK_ATOM_RADIUS).move_to(low[0])
        seed_up = make_atom(radius=CLOCK_ATOM_RADIUS).move_to(up[0])
        self.play(FadeIn(seed_low, scale=0.5), FadeIn(seed_up, scale=0.5), run_time=0.6)

        def shoot(k, flash, note=None):
            self.play(FadeIn(dots[k], scale=0.4), run_time=0.3)
            at_low = GW_PULSES[k] + low_lags[k]
            at_up = GW_PULSES[k] + up_lags[k]
            fire_pulse(
                self, at_low, flash=flash, lag=lags[k], note=note,
                z_near=GR_LOWER_Z + low_disp(at_low),
                z_far=GR_UPPER_Z + up_disp(at_up),
            )

        # --- pulse 1: the beamsplitter -------------------------------------
        stretch_note = Tex(
            r"$L$ stretches and squeezes", font_size=FONT_LEGEND, color=STRAIN_COLOR
        ).next_to(up[0], DOWN, buff=0.35).shift(RIGHT * 0.9)
        shoot(0, [seed_low, seed_up], note=stretch_note)
        for pair, v in ((atoms["low"], low), (atoms["up"], up)):
            for a in pair:
                a.set_opacity(SUPERPOSITION_OPACITY).move_to(v[0])
        self.remove(seed_low, seed_up)
        self.add(*atoms["low"], *atoms["up"])

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
        self.play(*[FadeIn(m) for m in sweeps], run_time=0.7)

        # And the same angle as a population. The wave pulled the far cloud's
        # two pulse intervals further apart than the near cloud's, so the two
        # interferometers split their ports by different amounts. That
        # difference is the signal: one laser, two clocks, and only what is
        # not common to both survives.
        self.remove(*atoms["low"], *atoms["up"], *hands)
        for cloud, v in (("low", low), ("up", up)):
            draw_ports(
                self, v[3], GR_OUT,
                ground_share(phase[cloud][1], phase[cloud][0]),
                labels=False,
            )

        signal = VGroup(
            Tex(
                r"the wave changes the light travel time, more for the far cloud",
                font_size=FONT_LEGEND, color=lighten(GUIDE_COLOR),
            ),
            MathTex(
                r"\Delta\Phi = \Phi_{\text{upper}} - \Phi_{\text{lower}}",
                font_size=FONT_ANNOTATION,
            ),
        ).arrange(DOWN, buff=0.22).move_to(GR_SIGNAL)
        if signal.width > GR_TERMS_WIDTH:
            signal.scale(GR_TERMS_WIDTH / signal.width)
        self.play(FadeIn(signal), run_time=1.0)
        self.wait(2.0)


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
        p1 = state_label(r"P_1", ATOM_COLOR).next_to(port_g, RIGHT, buff=0.3)
        p2 = state_label(r"P_2", KICKED_COLOR).next_to(port_e, RIGHT, buff=0.3)
        readout = MathTex(
            r"P_{1,2} = \tfrac{1}{2}\left(1 \pm \cos\Phi\right)",
            font_size=FONT_ANNOTATION,
        ).to_corner(DR)

        self.play(FadeIn(loop), FadeIn(phase), run_time=0.8)
        self.play(Write(p1), Write(p2), Write(readout), run_time=1.3)
        self.wait(2.0)
