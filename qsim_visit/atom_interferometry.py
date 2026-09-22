"""Atom interferometry animations.

Shared style constants and mobject helpers live at module level; each scene
keeps its own geometry block.
"""

import numpy as np
from manim import *

# --- style ----------------------------------------------------------------
ATOM_COLOR = BLUE_D  # |g, p>
KICKED_COLOR = PURPLE_B  # |e, p + hbar k>
LASER_COLOR = RED_C
SUPERPOSITION_OPACITY = 0.65

# One speed for every scene: each leg's run_time is distance / V, so the atom's
# velocity never visibly changes when it splits. That is the point of drawing
# the kick at 45 degrees -- the recoil is purely vertical and equal in
# magnitude to the forward motion.
V = 2.0
PULSE_SPEED = V * 1.6

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


def lighten(color, amount=0.35):
    return interpolate_color(color, WHITE, amount)


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


def momentum_arrow(origin, direction, tex, label_dir=LEFT, length=1.1):
    """A recoil arrow with its label, e.g. the hbar k an atom gains from a pulse."""
    arrow = Arrow(
        origin,
        origin + direction * length,
        buff=0,
        stroke_width=4,
        color=LASER_COLOR,
        max_tip_length_to_length_ratio=0.22,
    )
    label = MathTex(tex, font_size=32, color=LASER_COLOR).next_to(
        arrow, label_dir, buff=0.15
    )
    return VGroup(arrow, label)


def grow(annotation):
    """Animations that bring a momentum_arrow on screen."""
    return [GrowArrow(annotation[0]), FadeIn(annotation[1])]


def make_k_arrow(x, y):
    """The little vertical k-vector marker that sits beside a beam."""
    arrow = Arrow(
        ORIGIN,
        UP * 0.7,
        buff=0,
        stroke_width=3,
        color=LASER_COLOR,
        max_tip_length_to_length_ratio=0.3,
    )
    label = MathTex(r"\vec{k}", font_size=32, color=LASER_COLOR)
    return VGroup(arrow, label.next_to(arrow, RIGHT, buff=0.12)).move_to([x, y, 0])


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
        Flash(atom, color=LASER_COLOR, flash_radius=0.55, line_length=0.3),
        pulse.animate.scale(0.02).move_to(atom.get_center()).set_stroke(opacity=0),
        *[FadeOut(m) for m in fade],
        run_time=0.4,
    )
    scene.remove(pulse)


def emit(scene, atom, extras=()):
    """Stimulated emission: |e, p + hbar k> -> |g, p>, recoiling by -hbar k.

    The photon goes into the mode of the driving field, so it leaves upward
    alongside the beam and the atom is pushed the other way.
    """
    x, y, _ = atom.get_center()
    pulse = make_laser_pulse(x, y + 1.15)

    scene.play(
        Flash(atom, color=LASER_COLOR, flash_radius=0.55, line_length=0.3),
        FadeIn(pulse, scale=0.4),
        *[FadeIn(m) for m in extras],
        run_time=0.4,
    )
    rise = config.frame_y_radius + 1.4 - pulse.get_center()[1]
    scene.play(
        pulse.animate.shift(UP * rise),
        rate_func=linear,
        run_time=rise / PULSE_SPEED,
    )
    scene.remove(pulse)


def process_note(text, point, direction=LEFT, buff=0.3):
    """A small label naming the process a pulse drives on one arm."""
    return Tex(text, font_size=26, color=LASER_COLOR).next_to(point, direction, buff=buff)


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
        anims.append(Create(Line(start, end, stroke_width=4, color=color)))
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
        pulse_caption = MathTex(
            r"\pi/2\ \text{pulse}", font_size=32, color=LASER_COLOR
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

        self.remove(atom)
        self.add(straight, kicked)
        self.play(
            GrowArrow(recoil), FadeIn(recoil_label), FadeOut(in_label), run_time=0.7
        )

        # --- 5. diverging arms -------------------------------------------
        # Equal horizontal component on both arms -> a true 45 degree kick.
        draw_legs(
            self,
            [
                (
                    straight,
                    SPLIT_POINT,
                    SPLIT_POINT + RIGHT * ARM_LENGTH,
                    ATOM_COLOR,
                ),
                (
                    kicked,
                    SPLIT_POINT,
                    SPLIT_POINT + ARM_LENGTH * (RIGHT + UP),
                    KICKED_COLOR,
                ),
            ],
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


class MachZehnder(Scene):
    """The full pi/2 - pi - pi/2 sequence: split, mirror, recombine."""

    def construct(self):
        # --- 1. setup ----------------------------------------------------
        # Title right, legend left: the mirror's emitted photon flies straight up
        # the line x = MZ_B[0], and this keeps that column clear of both.
        title = Tex(
            r"Mach--Zehnder atom interferometer: $\pi/2 - \pi - \pi/2$", font_size=32
        ).to_corner(UR)
        legend = self.make_legend().to_corner(UL)
        guide = DashedLine(
            [-config.frame_x_radius, MZ_A[1], 0],
            MZ_A,
            dash_length=0.12,
            stroke_width=2,
            stroke_opacity=0.3,
            color=GREY_B,
        )
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
        absorbed = process_note("absorption", MZ_B, direction=DOWN, buff=0.35)
        emitted = process_note("stim.\\ emission", MZ_B_UP)

        # The ground-state arm takes a photon out of the beam and climbs.
        absorb(self, MZ_B[0], lower, extras=[self.pulse_caption(r"\pi", MZ_B[0])])
        self.play(
            state_colors(lower, KICKED_COLOR),
            *grow(gain),
            FadeIn(absorbed),
            run_time=0.6,
        )
        # The excited arm is driven the other way: it adds a photon to the beam
        # and recoils by -hbar k, which flattens it out.
        emit(self, upper, extras=[emitted])
        self.play(state_colors(upper, ATOM_COLOR), *grow(lose), run_time=0.6)
        draw_legs(
            self,
            [(lower, MZ_B, MZ_C, KICKED_COLOR), (upper, MZ_B_UP, MZ_C, ATOM_COLOR)],
            fade=[gain, lose, absorbed, emitted],
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
            ]
        )

        # --- 6. the enclosed area and the output ports -------------------
        loop = Polygon(
            MZ_A, MZ_B, MZ_C, MZ_B_UP, stroke_width=0, fill_color=BLUE_B, fill_opacity=0.09
        )
        phase = MathTex(r"\Phi", font_size=40, color=lighten(BLUE_B)).move_to(
            (MZ_A + MZ_B + MZ_C + MZ_B_UP) / 4
        )
        p1 = MathTex(r"P_1", font_size=36, color=lighten(ATOM_COLOR)).next_to(
            port_g, RIGHT, buff=0.3
        )
        p2 = MathTex(r"P_2", font_size=36, color=lighten(KICKED_COLOR)).next_to(
            port_e, RIGHT, buff=0.3
        )
        readout = MathTex(
            r"P_{1,2} = \tfrac{1}{2}\left(1 \pm \cos\Phi\right)", font_size=34
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
                    make_atom(color, radius=0.13),
                    MathTex(tex, font_size=30, color=lighten(color)),
                ).arrange(RIGHT, buff=0.22)
            )
        return rows.arrange(DOWN, buff=0.28, aligned_edge=LEFT)

    @staticmethod
    def pulse_caption(tex, x):
        """A pulse label on the caption row, offset clear of the beam it names."""
        return MathTex(tex, font_size=34, color=LASER_COLOR).move_to(
            [x + 0.5, -config.frame_y_radius + 0.35, 0]
        )

