"""Atom interferometry animations.

Mobject helpers and pulse primitives live at module level; each scene keeps its
own geometry block. Everything visual comes from style.py.
"""

import numpy as np
from manim import *

from style import *

# --- single-kick geometry -------------------------------------------------
# The frame is ~14.2 x 8 units. The incoming trajectory sits below centre so
# the 45 degree arm has room to climb without clipping the top edge.
BEAM_Y = -1.0
START_X = -6.0
SPLIT_X = -1.0
ARM_LENGTH = 4.0
SPLIT_POINT = np.array([SPLIT_X, BEAM_Y, 0.0])

# --- Mach-Zehnder geometry ------------------------------------------------
# pi/2 - pi - pi/2 traces a parallelogram: the arms separate, the mirror pulse
# swaps their momenta so they converge, and they overlap again at the
# recombining pulse. Because both arms carry the same horizontal velocity,
# they always share an x coordinate, so one vertical laser line catches both.
MZ_L = 2.8  # horizontal length of each interferometer leg
MZ_OUT = 2.2  # how far the output ports run past the last pulse
MZ_A = np.array([-5.8, -2.6, 0.0])  # first pi/2
MZ_B = MZ_A + RIGHT * MZ_L  # pi pulse, lower arm
MZ_B_UP = MZ_A + (RIGHT + UP) * MZ_L  # pi pulse, upper arm
MZ_C = MZ_B_UP + RIGHT * MZ_L  # second pi/2, where the arms overlap again


def make_atom(color=ATOM_COLOR, radius=ATOM_RADIUS, opacity=1.0):
    """An atom drawn as a shaded sphere: a filled disc plus a specular highlight."""
    body = Circle(
        radius=radius,
        fill_color=color,
        fill_opacity=opacity,
        stroke_color=lighten(color),
        stroke_width=ATOM_STROKE_WIDTH,
    )
    highlight = Circle(
        radius=radius * HIGHLIGHT_RADIUS_RATIO,
        fill_color=HIGHLIGHT_COLOR,
        fill_opacity=HIGHLIGHT_OPACITY * opacity,
        stroke_width=0,
    ).move_to(
        body.get_center()
        + radius * HIGHLIGHT_OFFSET_RATIO * (UP + LEFT) / np.sqrt(2)
    )
    return VGroup(body, highlight)


def make_laser_pulse(x, y, length=PULSE_LENGTH, n_cycles=PULSE_CYCLES):
    """A Gaussian-enveloped sine wavepacket propagating along +y, centred on (x, y)."""
    sigma = length / 5.0
    k = 2 * PI * n_cycles / length

    packet = FunctionGraph(
        lambda t: PULSE_AMPLITUDE * np.sin(k * t) * np.exp(-((t / sigma) ** 2)),
        x_range=[-length / 2, length / 2, 0.01],
        color=LASER_COLOR,
        stroke_width=PULSE_STROKE_WIDTH,
    )
    packet.rotate(90 * DEGREES).move_to([x, y, 0])
    packet.set_stroke(opacity=PULSE_TAPER)
    return packet


def momentum_arrow(origin, direction, tex, label_dir=LEFT, length=1.1):
    """A recoil arrow with its label, e.g. the hbar k an atom gains from a pulse."""
    arrow = Arrow(origin, origin + direction * length, **RECOIL_ARROW_STYLE)
    label = MathTex(tex, font_size=FONT_ANNOTATION, color=LASER_COLOR).next_to(
        arrow, label_dir, buff=0.15
    )
    return VGroup(arrow, label)


def grow(annotation):
    """Animations that bring a momentum_arrow on screen."""
    return [GrowArrow(annotation[0]), FadeIn(annotation[1])]


def make_k_arrow(x, y):
    """The little vertical k-vector marker that sits beside a beam."""
    arrow = Arrow(ORIGIN, UP * 0.7, **K_ARROW_STYLE)
    label = MathTex(r"\vec{k}", font_size=FONT_K, color=LASER_COLOR)
    return VGroup(arrow, label.next_to(arrow, RIGHT, buff=0.12)).move_to([x, y, 0])


def make_guide(start, end):
    """A dashed construction line, e.g. the trajectory an atom arrives along."""
    return DashedLine(start, end, **GUIDE_STYLE)


def absorb(scene, x, atom, extras=(), fade=()):
    """A wavepacket rises from below and is absorbed: |g, p> -> |e, p + hbar k>.

    The packet collapses into the atom rather than simply fading, so absorption
    is visibly a different event from the stimulated emission at the mirror.
    """
    y0 = -config.frame_y_radius - 0.6
    pulse = make_laser_pulse(x, y0)
    scene.add(pulse)

    rise = atom.get_center()[1] - y0
    scene.play(
        pulse.animate.shift(UP * rise),
        *[FadeIn(m) for m in extras],
        rate_func=linear,
        run_time=rise / PULSE_SPEED,
    )
    scene.play(
        Flash(atom, **FLASH_STYLE),
        pulse.animate.scale(0.02).move_to(atom.get_center()).set_stroke(opacity=0),
        *[FadeOut(m) for m in fade],
        run_time=0.4,
    )
    scene.remove(pulse)


def emit(scene, x, atom, extras=()):
    """Stimulated emission: one photon arrives and two leave.

    Both leave in the mode of the driving field, so the pair climbs together
    and the atom recoils the other way, by -hbar k.
    """
    y0 = -config.frame_y_radius - 0.6
    incoming = make_laser_pulse(x, y0)
    scene.add(incoming)

    rise = atom.get_center()[1] - y0
    scene.play(
        incoming.animate.shift(UP * rise),
        *[FadeIn(m) for m in extras],
        rate_func=linear,
        run_time=rise / PULSE_SPEED,
    )

    y = atom.get_center()[1] + 1.15
    pair = VGroup(*[make_laser_pulse(x + dx, y) for dx in (-0.22, 0.22)])
    scene.play(
        Flash(atom, **FLASH_STYLE),
        FadeOut(incoming, scale=0.3),
        FadeIn(pair, shift=UP * 0.25),
        run_time=0.5,
    )

    climb = config.frame_y_radius + 1.4 - y
    scene.play(
        pair.animate.shift(UP * climb),
        rate_func=linear,
        run_time=climb / PULSE_SPEED,
    )
    scene.remove(pair)


def draw_legs(scene, legs, fade=()):
    """Move atoms along straight legs, drawing each trajectory in step.

    Every leg shares the same horizontal extent, so they all take the same
    run_time at speed V -- that is what keeps the kicked arms at 45 degrees.
    A Line created in step is used rather than a TracedPath because a
    TracedPath collapses once the point it follows stops moving.
    """
    anims = []
    for atom, start, end, color in legs:
        anims.append(atom.animate.move_to(end))
        anims.append(Create(Line(start, end, color=color, **TRAJECTORY_STYLE)))
    dx = abs(legs[0][2][0] - legs[0][1][0])
    scene.play(
        *anims,
        *[FadeOut(m) for m in fade],
        rate_func=linear,
        run_time=dx / V,
    )


def state_colors(atom, color):
    """Recolour an atom's body to match a new internal state, keeping the highlight."""
    return atom[0].animate.set_fill(color).set_stroke(lighten(color))


def state_label(tex, color, font_size=FONT_STATE):
    return MathTex(tex, font_size=font_size, color=lighten(color))


class SingleLaserKick(Scene):
    """One beamsplitter pulse: an atom splits into two momentum states."""

    def construct(self):
        # --- 1. setup ----------------------------------------------------
        guide = make_guide(
            [START_X, BEAM_Y, 0], [config.frame_x_radius, BEAM_Y, 0]
        )
        caption = Tex(
            r"Atom interferometry: one beamsplitter pulse", font_size=FONT_TITLE
        ).to_corner(UL)

        self.play(FadeIn(guide), FadeIn(caption), run_time=1.0)

        # --- 2. incoming atom --------------------------------------------
        atom = make_atom().move_to([START_X, BEAM_Y, 0])
        in_label = state_label(r"|g,\,p\rangle", ATOM_COLOR, FONT_ANNOTATION)
        in_label.add_updater(lambda m: m.next_to(atom, UP, buff=0.25))

        self.play(FadeIn(atom, scale=0.5), FadeIn(in_label), run_time=0.6)
        self.play(
            atom.animate.shift(RIGHT * (SPLIT_X - START_X)),
            rate_func=linear,
            run_time=(SPLIT_X - START_X) / V,
        )
        in_label.clear_updaters()

        # --- 3. laser pulse from below -----------------------------------
        pulse_caption = MathTex(
            r"\pi/2\ \text{pulse}", font_size=FONT_ANNOTATION, color=LASER_COLOR
        ).next_to(SPLIT_POINT, DOWN, buff=0.9)
        k_arrow = make_k_arrow(SPLIT_X - 0.9, -config.frame_y_radius + 0.45)
        absorb(self, SPLIT_X, atom, extras=[pulse_caption, k_arrow], fade=[k_arrow])

        # --- 4. the split -------------------------------------------------
        straight = make_atom(opacity=SUPERPOSITION_OPACITY).move_to(SPLIT_POINT)
        kicked = make_atom(KICKED_COLOR, opacity=SUPERPOSITION_OPACITY).move_to(
            SPLIT_POINT
        )

        # The momentum kick is purely vertical -- the 45 degree path is the
        # resultant of the forward momentum p and the recoil hbar k.
        recoil = momentum_arrow(SPLIT_POINT, UP, r"\hbar k", length=1.2)

        self.remove(atom)
        self.add(straight, kicked)
        self.play(*grow(recoil), FadeOut(in_label), run_time=0.7)

        # --- 5. diverging arms -------------------------------------------
        # Equal horizontal component on both arms -> a true 45 degree kick.
        draw_legs(
            self,
            [
                (straight, SPLIT_POINT, SPLIT_POINT + RIGHT * ARM_LENGTH, ATOM_COLOR),
                (
                    kicked,
                    SPLIT_POINT,
                    SPLIT_POINT + ARM_LENGTH * (RIGHT + UP),
                    KICKED_COLOR,
                ),
            ],
        )

        # --- 6. final state labels ---------------------------------------
        straight_label = state_label(r"|g,\,p\rangle", ATOM_COLOR).next_to(
            straight, DOWN, buff=0.3
        )
        kicked_label = state_label(
            r"|e,\,p + \hbar k\rangle", KICKED_COLOR
        ).next_to(kicked, RIGHT, buff=0.3)

        self.play(Write(straight_label), Write(kicked_label), run_time=1.2)
        self.wait(1.5)


class MachZehnder(Scene):
    """The full pi/2 - pi - pi/2 sequence: split, mirror, recombine."""

    def construct(self):
        # --- 1. setup ----------------------------------------------------
        # Title right, legend left: the mirror's emitted photons fly straight up
        # the line x = MZ_B[0], and this keeps that column clear of both.
        title = Tex(
            r"Mach--Zehnder atom interferometer: $\pi/2 - \pi - \pi/2$",
            font_size=FONT_TITLE,
        ).to_corner(UR)
        legend = self.make_legend().to_corner(UL)
        guide = make_guide([-config.frame_x_radius, MZ_A[1], 0], MZ_A)
        self.play(FadeIn(title), FadeIn(legend), FadeIn(guide), run_time=1.0)

        # --- 2. incoming atom --------------------------------------------
        atom = make_atom().move_to([-config.frame_x_radius + 0.2, MZ_A[1], 0])
        self.play(FadeIn(atom, scale=0.5), run_time=0.5)
        self.play(
            atom.animate.move_to(MZ_A),
            rate_func=linear,
            run_time=(MZ_A[0] - atom.get_center()[0]) / V,
        )

        # --- 3. first pi/2: split ----------------------------------------
        k_arrow = make_k_arrow(MZ_A[0] - 0.9, -config.frame_y_radius + 0.45)
        absorb(
            self,
            MZ_A[0],
            atom,
            extras=[self.pulse_caption(r"\pi/2", MZ_A[0]), k_arrow],
            fade=[k_arrow],
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
        # The pi pulse exchanges the two arms' internal states, and with them
        # their momenta: the upper arm loses hbar k and flattens out, the lower
        # arm gains it and climbs. The arms converge instead of diverging.
        gain = momentum_arrow(MZ_B, UP, r"+\hbar k")
        lose = momentum_arrow(MZ_B_UP, DOWN, r"-\hbar k", label_dir=RIGHT)

        # Bottom to top, following the beam. Both arms share a column, so the
        # pulse rising to the upper arm passes over the lower arm's +hbar k
        # arrow -- that overlap is worth accepting, because each arrow has to
        # stand on the atom it acts on, where the kick actually happens.
        absorb(self, MZ_B[0], lower, extras=[self.pulse_caption(r"\pi", MZ_B[0])])
        self.play(state_colors(lower, KICKED_COLOR), *grow(gain), run_time=0.6)
        # The excited arm is driven the other way: one photon arrives, two
        # leave, and it recoils by -hbar k, which flattens it out.
        emit(self, MZ_B_UP[0], upper)
        self.play(state_colors(upper, ATOM_COLOR), *grow(lose), run_time=0.6)
        draw_legs(
            self,
            [(lower, MZ_B, MZ_C, KICKED_COLOR), (upper, MZ_B_UP, MZ_C, ATOM_COLOR)],
            fade=[gain, lose],
        )

        # --- 5. second pi/2: recombine -----------------------------------
        # Both arms sit at MZ_C now, so one pulse covers them.
        absorb(self, MZ_C[0], lower, extras=[self.pulse_caption(r"\pi/2", MZ_C[0])])

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

    # --- helpers ---------------------------------------------------------
    @staticmethod
    def make_legend():
        rows = VGroup()
        for color, tex in (
            (ATOM_COLOR, r"|g,\,p\rangle"),
            (KICKED_COLOR, r"|e,\,p + \hbar k\rangle"),
        ):
            rows.add(
                VGroup(
                    make_atom(color, radius=LEGEND_ATOM_RADIUS),
                    state_label(tex, color, FONT_LEGEND),
                ).arrange(RIGHT, buff=0.22)
            )
        return rows.arrange(DOWN, buff=0.28, aligned_edge=LEFT)

    @staticmethod
    def pulse_caption(tex, x):
        """A pulse label on the caption row, offset clear of the beam it names."""
        return MathTex(tex, font_size=FONT_ANNOTATION, color=LASER_COLOR).move_to(
            [x + 0.5, -config.frame_y_radius + 0.35, 0]
        )
