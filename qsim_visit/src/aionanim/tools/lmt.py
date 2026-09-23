"""Large momentum transfer: a ladder of kicks, one photon recoil each."""

import numpy as np
from manim import *

from aionanim.style import *


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
