"""The AION DAI data built up shot by shot.

The same shots as plot_scripts/interferometer_data.py (Baynham et al.,
arXiv:2504.09158, Fig. 4a,b), drawn in manim so they can arrive one at a time.
The fringe plot on the left sweeps left to right through the clock laser phase
step; each shot lands on it twice -- once per interferometer -- and once on the
Lissajous plot on the right, as upper against lower excitation. The newest shot
is ringed in all three places so the eye can follow one shot across.

FringesToEllipse is the quiet laser: clean fringes, and the ellipse traced
round in order as the phase sweeps. FringesToEllipseNoisy is the run with
common laser phase noise put on: the fringes wash out to a band, but each shot
still lands on the ellipse, just at a random place round it.

FringesFirst (and FringesFirstNoisy) start from the finished fringe plot,
dimmed, and light its shots up left to right as each arrives on the Lissajous
plot -- for when the fringes have already been shown and the point is where
each one goes on the ellipse.

    uv run manim -qh animation_scripts/dai_data.py FringesToEllipse

Drawing: a few thousand Dots would be a few thousand mobjects for cairo to
walk every frame. Instead each series is one VMobject whose points are every
dot's circle laid end to end -- cairo draws them as subpaths of a single path
-- and an updater slices off as many dots as have arrived. That makes the
point count nearly free, so nothing is down-sampled beyond taking the same
first shots the static figure plots.
"""

import csv
from pathlib import Path

import numpy as np
from manim import *

from style import *

DATA_DIR = Path(__file__).resolve().parent.parent / "data" / "dai_fringes"

# The first shots of the run, as many as the static Lissajous figure plots
# (~20 per phase step), sorted by phase step so the fringe plot fills left to
# right. Within a step they keep shot order.
N_SHOTS = 2000

# --- layout ---------------------------------------------------------------
FRINGE_ORIGIN = np.array([-6.0, -2.6, 0.0])  # lower-left corner of the axes
FRINGE_WIDTH = 6.2
FRINGE_HEIGHT = 4.2
LISSAJOUS_ORIGIN = np.array([1.9, -2.6, 0.0])
LISSAJOUS_SIZE = 4.2

# --- pacing ---------------------------------------------------------------
# Ease in, so the first shots arrive slowly enough to be followed one at a
# time and the rest fill in quickly.
BUILD_TIME = 14.0


def load(run):
    with open(DATA_DIR / f"{run}.csv") as f:
        rows = list(csv.DictReader(line for line in f if not line.startswith("#")))
    data = {k: np.array([float(r[k]) for r in rows[:N_SHOTS]]) for k in rows[0]}
    order = np.argsort(data["phi_rad"], kind="stable")
    return {k: v[order] for k, v in data.items()}


def plot_axes(x_range, x_length, y_length, x_ticks, x_label, y_label):
    axes = Axes(
        x_range=x_range,
        y_range=[0, 100, 50],
        x_length=x_length,
        y_length=y_length,
        tips=False,
        axis_config=dict(
            color=PLOT_FOREGROUND, stroke_width=2, tick_size=0.06,
            include_ticks=True,
        ),
        # the x ticks are MathTex set below, so the origin's 0 is the y axis's
        y_axis_config=dict(numbers_to_include=[0, 50, 100],
                           font_size=FONT_TICK, numbers_to_exclude=[]),
        x_axis_config=dict(include_numbers=False),
    )
    ticks = VGroup(*(
        MathTex(tex, font_size=FONT_TICK, color=PLOT_FOREGROUND)
        .next_to(axes.c2p(x, 0), DOWN, buff=0.18)
        for x, tex in x_ticks
    ))
    axes.y_axis.numbers.set_color(PLOT_FOREGROUND)
    xl = Tex(x_label, font_size=FONT_AXIS, color=PLOT_FOREGROUND)
    xl.next_to(ticks, DOWN, buff=0.18).set_x(axes.x_axis.get_center()[0])
    yl = Tex(y_label, font_size=FONT_AXIS, color=PLOT_FOREGROUND).rotate(PI / 2)
    yl.next_to(axes.y_axis.numbers, LEFT, buff=0.2)
    return axes, VGroup(axes, ticks, xl, yl)


def dot_points(axes, xs, ys):
    """Every dot's circle, end to end, in the order the dots arrive."""
    template = Circle(radius=DATA_DOT_RADIUS, num_components=5).points
    centres = np.array([axes.c2p(x, y) for x, y in zip(xs, ys)])
    return (centres[:, None, :] + template[None, :, :]).reshape(-1, 3), len(template)


def dot_cloud(points, per_dot, color, count, opacity):
    cloud = VMobject(fill_color=color, fill_opacity=opacity, stroke_width=0)

    def grow(mob):
        n = int(count.get_value())
        # set_points on an empty array leaves cairo nothing to draw, which is
        # what zero dots should look like.
        mob.set_points(points[: n * per_dot])

    cloud.add_updater(grow)
    return cloud


def newest_ring(centres, color, count):
    ring = Circle(radius=NEWEST_RING_RADIUS, stroke_color=color,
                  stroke_width=NEWEST_RING_WIDTH)
    ring.add_updater(
        lambda m: m.move_to(centres[max(int(count.get_value()) - 1, 0)])
    )
    return ring


def legend_row(entries):
    rows = VGroup(*(
        VGroup(
            Dot(radius=0.07, color=color),
            Tex(label, font_size=FONT_AXIS, color=PLOT_FOREGROUND),
        ).arrange(RIGHT, buff=0.12)
        for label, color in entries
    ))
    return rows.arrange(RIGHT, buff=0.4)


class FringesToEllipse(Scene):
    RUN = "lln"
    TITLE = "Low laser noise"
    ELLIPSE_COLOR = LLN_COLOR
    # Whether the whole fringe plot is up, dimmed, before any shot arrives.
    FRINGES_FIRST = False

    def construct(self):
        data = load(self.RUN)
        phi = data["phi_rad"]
        lower = 100 * data["excitation_bottom"]
        upper = 100 * data["excitation_top"]

        fringe_axes, fringe_frame = plot_axes(
            [0, TAU, PI], FRINGE_WIDTH, FRINGE_HEIGHT,
            [(0, "0"), (PI, r"\pi"), (TAU, r"2\pi")],
            "Clock laser phase step / rad", r"Excitation / \%",
        )
        fringe_frame.shift(FRINGE_ORIGIN - fringe_axes.c2p(0, 0))
        liss_axes, liss_frame = plot_axes(
            [0, 100, 50], LISSAJOUS_SIZE, LISSAJOUS_SIZE,
            [(0, "0"), (50, "50"), (100, "100")],
            r"Lower interferometer excitation / \%",
            r"Upper interferometer excitation / \%",
        )
        liss_frame.shift(LISSAJOUS_ORIGIN - liss_axes.c2p(0, 0))

        title = Tex(self.TITLE, font_size=FONT_TITLE, color=self.ELLIPSE_COLOR)
        title.to_corner(UL)
        key = legend_row([("Lower", LOWER_CLOUD_COLOR),
                          ("Upper", UPPER_CLOUD_COLOR)])
        key.next_to(fringe_axes, UP, buff=0.25).align_to(fringe_axes, RIGHT)

        count = ValueTracker(0)
        series = [
            (fringe_axes, phi, lower, LOWER_CLOUD_COLOR, FRINGE_DOT_OPACITY),
            (fringe_axes, phi, upper, UPPER_CLOUD_COLOR, FRINGE_DOT_OPACITY),
            (liss_axes, lower, upper, self.ELLIPSE_COLOR, 1.0),
        ]
        clouds, rings, dimmed = VGroup(), VGroup(), VGroup()
        for axes, xs, ys, color, opacity in series:
            points, per_dot = dot_points(axes, xs, ys)
            clouds.add(dot_cloud(points, per_dot, color, count, opacity))
            centres = points[::per_dot] - [DATA_DOT_RADIUS, 0, 0]
            rings.add(newest_ring(centres, lighten(color), count))
            if self.FRINGES_FIRST and axes is fringe_axes:
                dimmed.add(VMobject(fill_color=color, stroke_width=0,
                                    fill_opacity=FRINGE_DIM_OPACITY)
                           .set_points(points))

        self.play(FadeIn(title), FadeIn(fringe_frame), FadeIn(liss_frame),
                  FadeIn(key), FadeIn(dimmed), run_time=1.0)
        self.add(clouds)
        self.wait(0.3)
        count.set_value(1)
        self.add(rings)
        self.play(count.animate.set_value(len(phi)),
                  run_time=BUILD_TIME, rate_func=rate_functions.ease_in_quad)
        self.play(FadeOut(rings), run_time=0.6)
        self.wait(2.0)


class Noisy:
    RUN = "hln"
    TITLE = "High laser noise"
    ELLIPSE_COLOR = HLN_COLOR


class FringesToEllipseNoisy(Noisy, FringesToEllipse):
    pass


class FringesFirst(FringesToEllipse):
    FRINGES_FIRST = True


class FringesFirstNoisy(Noisy, FringesFirst):
    pass
