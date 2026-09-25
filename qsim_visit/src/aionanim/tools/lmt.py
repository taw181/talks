"""Large momentum transfer: sequences of single-photon pulses, each driving
every arm it crosses (after Rudolph et al., PRL 124, 083604 (2020), Figs. 1c
and 3)."""

import numpy as np
from manim import *

from aionanim.style import *


# --- large momentum transfer geometry -------------------------------------
# Same space-time frame. The first kick is the pi/2 that splits the atom; every
# kick after it drives both arms, which reach it in opposite internal states,
# so one pulse pushes them opposite ways -- one absorbs, the other is
# stimulated to emit -- and the arms end up (2n - 1) hbar k apart after n.
LMT_T0 = -5.3
LMT_Z = -0.75
LMT_STEP = 1.0  # time between kicks in the ladder
LMT_TAIL = 1.3  # free flight after the last kick
LMT_U = 0.052  # baseline covered per unit time, per photon recoil
LMT_KICKS = 10


def lmt_points(slope_per_kick):
    """Worldline corners for an arm gaining `slope_per_kick(i)` on kick i."""
    pts = [np.array([LMT_T0, LMT_Z, 0.0])]
    for i in range(LMT_KICKS):
        dt = LMT_TAIL if i == LMT_KICKS - 1 else LMT_STEP
        pts.append(pts[-1] + np.array([dt, dt * slope_per_kick(i), 0.0]))
    return pts


def kick_worldline(point, from_below, steepness=0.12, span=None):
    """A photon's worldline arriving at `point` from below or from above:
    from the frame's edge, or from the (bottom, top) of `span`, to keep it
    out of a title or a caption row."""
    bottom, top = span or (-config.frame_y_radius, config.frame_y_radius)
    edge = bottom if from_below else top
    dx = steepness * abs(point[1] - edge)
    return Line(
        [point[0] - dx, edge, 0], point,
        color=LASER_COLOR, stroke_width=PULSE_STROKE_WIDTH,
    )


def recoil(state, from_below):
    """(velocity change in recoils, new state) for an arm in ``state`` ("g" or
    "e") hit by a pulse travelling up (``from_below``) or down: a |g> arm
    absorbs, moving with the photon; an |e> arm is stimulated to emit into
    the pulse, recoiling against it."""
    direction = 1 if from_below else -1
    if state == "g":
        return direction, "e"
    return -direction, "g"


# --- LMT sequences ----------------------------------------------------------
# A sequence is a list of (time, kind, stage). The kinds:
#   "split"  a pi/2 from below: every arm splits into itself, left alone
#            (name + "0"), and a kicked copy (name + "1"). The two form a pair.
#   "up"     a pi pulse that drives every arm, from whichever side pushes the
#   "down"   kicked arm of each pair up (or down); its partner, in the other
#            state, goes the other way.
#   "decay"  no pulse: every excited arm falls back to the ground state.
#   "merge"  the closing pi/2: each pair, met again, leaves by two ports.
LMT_PORT = 0.7  # how far the output ports are drawn


def lmz_pulses(n, step, T, t0=0.0, stage=0):
    """The LMT Mach-Zehnder of order n (odd): pi/2 and (n - 1)/2 pulses out,
    a mirror of n pulses, (n - 1)/2 pulses back and a pi/2. Every pulse drives
    both arms, so each opens or closes the gap by 2 hbar k. It is symmetric in
    time about the middle of the mirror, so the arms close.
    Stages ``stage`` to ``stage + 2``: beam splitter, mirror, beam splitter."""
    m = (n - 1) // 2
    end = 2 * T + (n - 1) * step
    pulses = [(0.0, "split", stage)]
    pulses += [(j * step, "up", stage) for j in range(1, m + 1)]
    pulses += [(T + j * step, "down", stage + 1) for j in range(n)]
    pulses += [(end - j * step, "up", stage + 2) for j in range(m, 0, -1)]
    pulses.append((end, "merge", stage + 2))
    return [(t0 + t, kind, s) for t, kind, s in pulses]


def lmt_history(pulses, t0, z0, u, port=LMT_PORT):
    """Step through a sequence: for each event, where it lands and what it
    does to each arm, and the legs flown until the next one.

    Starts from one arm, "", in |g> and at rest at (t0, z0). Returns a list of
    dicts: ``x``, ``from_below`` (None for a decay), ``stage``, ``kind``,
    ``splits`` [(parent, left alone, kicked)], ``hits`` [(arm, point, new
    state)], and ``legs`` [(arm, start, end, state)] from this event to the
    next -- after the merge, the output ports, named pair + "g"/"e".
    """
    arms = {"": dict(z=z0, v=0, state="g")}
    pairs = []
    history = []
    for k, (t, kind, stage) in enumerate(pulses):
        x = t0 + t
        from_below, splits, hits, legs = True, [], [], []

        def at(arm):
            return np.array([x, arm["z"], 0.0])

        if kind == "split":
            pairs = []
            for name, arm in list(arms.items()):
                dv, state = recoil(arm["state"], True)
                arms[name + "0"] = dict(arm)
                arms[name + "1"] = dict(arm, v=arm["v"] + dv, state=state)
                del arms[name]
                pairs.append((name + "0", name + "1"))
                splits.append((name, name + "0", name + "1"))
                hits.append((name + "1", at(arm), state))
        elif kind in ("up", "down"):
            # the side that gives the kicked arms the push asked for
            dv, _ = recoil(arms[pairs[0][1]]["state"], True)
            from_below = dv == (1 if kind == "up" else -1)
            for name, arm in arms.items():
                dv, arm["state"] = recoil(arm["state"], from_below)
                arm["v"] += dv
                hits.append((name, at(arm), arm["state"]))
        elif kind == "decay":
            from_below = None
            for name, arm in arms.items():
                if arm["state"] == "e":
                    arm["state"] = "g"
                    hits.append((name, at(arm), "g"))
        if kind == "merge":
            for stay, kicked in pairs:
                a, b = arms[stay], arms[kicked]
                assert abs(a["z"] - b["z"]) < 1e-9, "the arms have not closed"
                ground = a if a["state"] == "g" else b
                start = at(ground)
                for state, v in (("g", ground["v"]), ("e", ground["v"] + 1)):
                    legs.append((stay[:-1] + state, start,
                                 start + [port, port * v * u, 0], state))
        else:
            dt = pulses[k + 1][0] - t
            for name, arm in arms.items():
                start = at(arm)
                arm["z"] += arm["v"] * u * dt
                legs.append((name, start, np.array([x + dt, arm["z"], 0.0]),
                             arm["state"]))
        history.append(dict(x=x, from_below=from_below, stage=stage, kind=kind,
                            splits=splits, hits=hits, legs=legs))
    return history


# --- the LMT Mach-Zehnder (Rudolph et al., Fig. 1c) -------------------------
LMZ_ORDER = 11
LMZ_T0 = -5.9  # the first pi/2
LMZ_Z = -0.75  # where the atom comes in
LMZ_STEP = 0.3  # between the pulses of one stage
LMZ_T = 3.3  # the first pi/2 to the first mirror pulse
LMZ_U = 0.155  # baseline covered per unit time, per photon recoil
LMZ_END = 2 * LMZ_T + (LMZ_ORDER - 1) * LMZ_STEP  # the last pi/2, from the first


# --- the LMT gradiometer (Rudolph et al., Fig. 3) ---------------------------
# An LMT beam splitter of order LGR_SPLIT sends two clouds apart; they drift
# for LGR_DRIFT while the excited one decays; then one LMT Mach-Zehnder
# sequence of order LGR_ORDER runs both interferometers at once -- every pulse
# drives all four arms.
LGR_SPLIT = 9
LGR_ORDER = 7
LGR_T0 = -6.0
LGR_Z = -0.75
LGR_STEP = 0.25
LGR_DRIFT = 2.0  # the last splitting pulse to the first interferometer pulse
LGR_T = 2.6
LGR_U = 0.055


def lgr_pulses():
    split = [(0.0, "split", 0)]
    split += [(j * LGR_STEP, "up", 0) for j in range(1, (LGR_SPLIT - 1) // 2 + 1)]
    start = split[-1][0] + LGR_DRIFT
    decay = [(split[-1][0] + LGR_DRIFT / 2, "decay", 1)]
    return split + decay + lmz_pulses(LGR_ORDER, LGR_STEP, LGR_T, t0=start, stage=2)
