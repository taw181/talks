"""Large momentum transfer: a ladder of kicks, one photon recoil each."""

import numpy as np
from manim import *

from aionanim.style import *


# --- large momentum transfer geometry -------------------------------------
# Same space-time frame. Each pulse adds one photon recoil to the upper arm,
# so its worldline steepens by a fixed slope per kick while the lower arm
# stays put; the arms end up n*hbar*k apart instead of hbar*k.
# Ten kicks climb as n^2, so the slope per kick is small: the first few barely
# lift the arm, which is the point -- each recoil is small, and they add up.
LMT_T0 = -5.3
LMT_Z = -2.8
LMT_STEP = 1.0  # time between kicks in the ladder
LMT_TAIL = 1.3  # free flight after the last kick
LMT_U = 0.09  # baseline covered per unit time, per photon recoil
LMT_KICKS = 10


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


# --- the LMT Mach-Zehnder -------------------------------------------------
# pi/2 - pi - pi/2 with each pulse stretched into n. The first beam splitter
# is the pi/2 and then n - 1 kicks to the upper arm; the mirror is n pulses,
# each turning both arms round by one recoil; the second beam splitter is
# n - 1 kicks to the fast arm and a pi/2 where the arms meet. n is odd so that
# the arms reach the mirror in opposite internal states: one pulse then pushes
# them opposite ways -- one absorbs, the other is stimulated to emit -- which
# is how n pulses turn both arms at once. The whole is symmetric about the
# middle of the mirror, so the arms close.
LMZ_ORDER = 3
LMZ_T0 = -5.8  # the first pi/2
LMZ_Z = -2.95  # the lower arm, before the mirror
LMZ_STEP = 0.55  # between the pulses of one stage
LMZ_T = 4.65  # the first pi/2 to the first mirror pulse
LMZ_U = 0.39  # baseline covered per unit time, per photon recoil
LMZ_PORT = 0.7  # how far the output ports are drawn
LMZ_END = 2 * LMZ_T + (LMZ_ORDER - 1) * LMZ_STEP  # the last pi/2, from the first


def recoil(state, from_below):
    """(velocity change in recoils, new state) for an arm in ``state`` ("g" or
    "e") hit by a pulse travelling up (``from_below``) or down: a |g> arm
    absorbs, moving with the photon; an |e> arm is stimulated to emit into
    the pulse, recoiling against it."""
    direction = 1 if from_below else -1
    if state == "g":
        return direction, "e"
    return -direction, "g"


def lmz_pulses(n=LMZ_ORDER, step=LMZ_STEP, T=LMZ_T):
    """The sequence as (time from the first pulse, from below?, arms it kicks,
    stage 0/1/2). The first and last pulses are the pi/2s: "split" and "merge"."""
    end = 2 * T + (n - 1) * step
    pulses = [(0.0, True, "split", 0)]
    pulses += [(j * step, j % 2 == 0, ("upper",), 0) for j in range(1, n)]
    pulses += [(T + j * step, j % 2 == 0, ("lower", "upper"), 1) for j in range(n)]
    pulses += [(end - (n - 1 - j) * step, j % 2 == 0, ("lower",), 2) for j in range(n - 1)]
    pulses.append((end, True, "merge", 2))
    return pulses


def lmz_history(t0=LMZ_T0, z0=LMZ_Z, u=LMZ_U):
    """Step through lmz_pulses: for each pulse, where it lands and what it does
    to each arm, and the legs flown until the next one.

    Returns a list of dicts: ``x``, ``from_below``, ``stage``, ``kind`` ("split",
    "merge" or "kick"), ``hits`` [(arm, point, new state)], and ``legs``
    [(arm, start, end, state)] from this pulse to the next (or, after the
    merge, the two output ports).
    """
    arms = {"lower": dict(z=z0, v=0, state="g")}
    pulses = lmz_pulses()
    history = []
    for k, (t, from_below, targets, stage) in enumerate(pulses):
        x = t0 + t
        hits = []
        if targets == "split":
            dv, state = recoil("g", from_below)
            arms["upper"] = dict(z=z0, v=dv, state=state)
            hits.append(("upper", np.array([x, z0, 0.0]), state))
        elif targets == "merge":
            pass
        else:
            for name in targets:
                arm = arms[name]
                dv, arm["state"] = recoil(arm["state"], from_below)
                arm["v"] += dv
                hits.append((name, np.array([x, arm["z"], 0.0]), arm["state"]))
        legs = []
        if targets == "merge":
            top = arms["upper"]["z"]
            start = np.array([x, top, 0.0])
            legs = [("port_g", start, start + [LMZ_PORT, 0, 0], "g"),
                    ("port_e", start, start + [LMZ_PORT, LMZ_PORT * u, 0], "e")]
        else:
            dt = pulses[k + 1][0] - t
            for name, arm in arms.items():
                start = np.array([x, arm["z"], 0.0])
                arm["z"] += arm["v"] * u * dt
                legs.append((name, start, np.array([x + dt, arm["z"], 0.0]), arm["state"]))
        kind = targets if isinstance(targets, str) else "kick"
        history.append(dict(x=x, from_below=from_below, stage=stage, kind=kind,
                            hits=hits, legs=legs))
    return history
