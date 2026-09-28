"""AION's reach for ultralight dark matter, as a small log-log inset.

The photon-coupling panel of Badurina et al. 2020 (Fig. 3): |d_e| against
the scalar's mass m_phi, with the region other experiments have already
excluded in grey and each AION stage's projected reach as a line -- anything
above a line that is not already grey, that stage would see. A dark-matter
figure puts it beside itself with the mass it is drawing marked across it
(mass_mark), which is what ties an oscillating trace to a place in the
parameter space.

It is an inset, so it is built to be read small: the axes are labelled every
few decades, and the six curves carry four labels, since a stage's initial
and goal curves share a hue (the initial one fainter) and one name.
"""

from functools import lru_cache

import numpy as np
from manim import *

from aionanim.physics.uldm_sensitivity import (
    EXCLUDED,
    ULDM_SCENARIOS,
    load_uldm_sensitivity,
)
from aionanim.style import *
from aionanim.tools.gw_plot import plot_point, sensitivity_axes

# The paper's mass range, and its coupling range cut at 1, above which
# everything is excluded. The bottom stays at the paper's 1e-16, two decades
# under AEDGE's best, which leaves room for a mass label at the foot of the
# plot even where AEDGE runs along it.
ULDM_LOG_M = (-19, -10)
ULDM_LOG_D = (-16, 0)
ULDM_LABEL_EVERY = (2, 4)  # 10^-18, -16, ... on x; 10^-16, -12, ... on y, as the paper
ULDM_TICK_BUFF = 0.08
# Where each label goes, in (log10 m, log10 d_e), and which side of that
# point it hangs: AION-10 and AION-100 centred in the V of their goal curves
# (carried below 0.3 Hz, each curve turns back up on the left, so there is
# no longer an open end to label), a little left of the middle so the mass
# the dark-matter slides mark (~1.8e-15 eV) clears them; AION-km right of
# its line, and AEDGE under the end of its own, in the empty lower right --
# anywhere left of that, a mark at the light end of the range would run
# through it.
ULDM_LABELS = {
    "AION-10": ((-15.7, -1.9), ORIGIN),
    "AION-100": ((-15.8, -5.6), ORIGIN),
    "AION-km": ((-13.3, -8.8), RIGHT),
    "AEDGE": ((-14.0, -13.1), UR),
}
ULDM_MARK_LABEL_ROOM = 1.0  # decades a mass label needs right of its line
ULDM_LABEL_STEMS = {
    "AION-10": "aion10_goal",
    "AION-100": "aion100_goal",
    "AION-km": "aion_km",
    "AEDGE": "aedge",
}


@lru_cache(maxsize=None)
def _log_curve(stem):
    m, d = load_uldm_sensitivity(stem)
    return np.log10(m), np.log10(d)


def clipped(stem, top):
    """A curve's (log m, log d), cut to the stretch under `top` around its
    lowest point: where it comes down through `top` on the left, if it does
    (the AION curves carried below 0.3 Hz do), and goes up through it on the
    right."""
    x, y = _log_curve(stem)
    low = int(np.argmin(y))
    if y[low] > top:
        return x[:0], y[:0]
    over = np.nonzero(y > top)[0]
    left = over[over < low]
    right = over[over > low]
    i = left[-1] + 1 if len(left) else 0
    j = right[0] if len(right) else len(x)
    xs, ys = x[i:j], y[i:j]

    def crossing(a, b):
        s = (top - y[a]) / (y[b] - y[a])
        return x[a] + s * (x[b] - x[a])

    if i > 0:
        xs, ys = np.insert(xs, 0, crossing(i - 1, i)), np.insert(ys, 0, top)
    if j < len(x):
        xs, ys = np.append(xs, crossing(j - 1, j)), np.append(ys, top)
    return xs, ys


def uldm_axes(origin, width, height):
    """The inset's frame: decades of m_phi / eV and |d_e|, as (axes, frame)."""
    return sensitivity_axes(
        ULDM_LOG_M, ULDM_LOG_D, origin, width, height,
        x_label=r"$m_\phi$ / eV", y_label=r"$|d_e|$",
        tick_font=FONT_INSET_TICK, label_font=FONT_INSET_LABEL,
        label_every=ULDM_LABEL_EVERY, buff=ULDM_TICK_BUFF,
    )


def _polyline(axes, x, y, **style):
    line = VMobject(**style)
    line.set_points_as_corners([plot_point(axes, a, b) for a, b in zip(x, y)])
    return line


def excluded_region(axes):
    """The grey region already ruled out, and the line along its lower edge."""
    x, y = clipped(EXCLUDED, axes.log_top)
    edge = [plot_point(axes, a, b) for a, b in zip(x, y)]
    top = plot_point(axes, axes.log_origin[0], axes.log_top)[1]
    region = Polygon(
        *edge, [edge[-1][0], top, 0], [edge[0][0], top, 0], **ULDM_EXCLUDED_STYLE
    )
    return VGroup(region, _polyline(axes, x, y, **ULDM_EXCLUDED_EDGE))


def uldm_curves(axes):
    """Each stage's reach, stem: line, clipped to the top of the axes."""
    curves = {}
    for stem in ULDM_SCENARIOS:
        curves[stem] = _polyline(
            axes, *clipped(stem, axes.log_top),
            stroke_color=ULDM_COLORS[stem], stroke_width=ULDM_CURVE_WIDTH,
            stroke_opacity=ULDM_INITIAL_OPACITY if stem.endswith("_initial") else 1.0,
        )
    return curves


def uldm_labels(axes):
    labels = VGroup()
    for name, ((x, y), side) in ULDM_LABELS.items():
        labels.add(Tex(
            name, font_size=FONT_INSET_LABEL, color=ULDM_COLORS[ULDM_LABEL_STEMS[name]],
        ).next_to(plot_point(axes, x, y), side, buff=0))
    return labels


def uldm_inset(origin, width, height):
    """The whole inset, its axes' lower-left corner at `origin`.

    A VGroup of the frame, the excluded region, the curves and their labels,
    with `.axes` on it for mass_mark. The curves go over the grey, since
    where a stage's line runs inside it is part of what the plot says.
    """
    axes, frame = uldm_axes(origin, width, height)
    curves = uldm_curves(axes)
    inset = VGroup(frame, excluded_region(axes), VGroup(*curves.values()), uldm_labels(axes))
    inset.axes = axes
    return inset


def reach(stem, mass):
    """log10 |d_e| on a stage's curve at `mass`, or None off its ends."""
    x, y = _log_curve(stem)
    lm = np.log10(mass)
    if not x[0] <= lm <= x[-1]:
        return None
    return float(np.interp(lm, x, y))


def deepest_reach(mass):
    """(stem, log10 |d_e|) of the curve reaching the smallest coupling at
    `mass`, or (None, None) where no curve covers it."""
    reaches = [(y, stem) for stem in ULDM_SCENARIOS if (y := reach(stem, mass)) is not None]
    if not reaches:
        return None, None
    y, stem = min(reaches)
    return stem, y


def mass_mark(axes, mass, on=None, label=r"m_\phi"):
    """A mass marked across the inset.

    A faint line up the plot at m_phi, and a dot where it meets the curve
    `on` -- by default whichever reaches deepest there. From the edge of the
    grey down to that dot the line is drawn at full strength: the couplings
    nothing has ruled out yet that AION would see, which is the point of
    marking a mass at all. (Not AION-10's curve by default: at every mass
    the dark-matter figures draw, it lies inside the grey, so a dot on it
    says only that the prototype's next stage reaches today's limits.)

    `label` goes at the foot of the line (see mass_label); label=None leaves
    it off, for a mark that moves and a label that is swapped instead.
    """
    lm = np.log10(mass)
    bottom = plot_point(axes, lm, axes.log_origin[1])
    top = plot_point(axes, lm, axes.log_top)
    mark = VGroup(Line(bottom, top, **ULDM_MARK_STYLE).set_stroke(
        opacity=ULDM_MARK_FAINT_OPACITY
    ))
    y = reach(on, mass) if on else deepest_reach(mass)[1]
    if y is not None and y <= axes.log_top:
        edge = min(reach(EXCLUDED, mass), axes.log_top)
        if y < edge:
            mark.add(Line(plot_point(axes, lm, edge), plot_point(axes, lm, y),
                          **ULDM_MARK_STYLE))
        mark.add(Dot(plot_point(axes, lm, y), radius=ULDM_MARK_DOT_RADIUS,
                     color=FIELD_COLOR))
    if label is not None:
        mark.add(mass_label(axes, mass, label))
    return mark


def mass_label(axes, mass, label=r"m_\phi"):
    """`label` at the foot of the mark: right of the line, where the plot is
    emptiest at every mass, unless the right-hand edge is too close."""
    lm = np.log10(mass)
    side = LEFT if lm > ULDM_LOG_M[1] - ULDM_MARK_LABEL_ROOM else RIGHT
    return MathTex(label, font_size=FONT_INSET_LABEL, color=FIELD_COLOR).next_to(
        plot_point(axes, lm, axes.log_origin[1]), UP + side, buff=0.04
    )
