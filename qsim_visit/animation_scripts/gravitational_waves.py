"""Gravitational waves from a binary black hole merger.

A flat sheet of spacetime, drawn as a wireframe grid, is dented by two black
holes and rippled by the radiation they emit. As the pair spirals in, both the
frequency and the amplitude of the ripples climb, until the holes merge and the
sheet rings down to a single well.

The field is evaluated at retarded time, so at any instant the rim of the sheet
is still showing the slow, weak waves emitted seconds earlier while the centre
shows the fast, strong ones -- that contrast across the sheet *is* the chirp.

Everything visual comes from style.py.
"""

import numpy as np
from manim import *

from style import *

# --- sheet geometry -------------------------------------------------------
# The sheet is a wireframe rather than a Surface: a Surface rebuilds thousands
# of little quads every frame, while 2 * GRID_LINES polylines are just point
# arrays. GRID_LINES sets the line spacing, and the shortest wavelength the
# sheet has to carry (see WAVE_SPEED below) needs about four lines to resolve.
GRID_HALF = 5.5  # the sheet spans [-GRID_HALF, GRID_HALF] in x and y
GRID_LINES = 41  # grid lines per direction -> 0.275 spacing
GRID_SAMPLES = 111  # sample points along each line
GRADIENT_STOPS = 21  # colour stops per line; a gradient needs far fewer than
#                      samples, and each stop costs real time per frame
EDGE_FADE = 1.3  # width of the taper that flattens the sheet at the rim
HEIGHT_COLOR_SCALE = 0.45  # the height at which the colour ramp saturates

# --- the binary -----------------------------------------------------------
# Separation collapses from R_START to R_MERGE over T_INSPIRAL, and the orbital
# frequency rises with it. The exponent is derived from CHIRP_RATIO rather than
# set to Kepler's 3/2: a true 3/2 takes the frequency up by a factor of ~14 in
# the last second, which aliases against the grid and the frame rate. A factor
# of 3.5 is the most the sheet can actually draw, and it still reads as a chirp.
R_START = 2.2
R_MERGE = 0.38
T_INSPIRAL = 14.0
T_RINGDOWN = 4.5
INSPIRAL_SHARPNESS = 1.7  # how late in the inspiral the collapse happens
CHIRP_RATIO = 3.5  # final orbital frequency / initial
OMEGA_START = 1.2  # initial orbital angular frequency, rad/s
KEPLER_EXPONENT = np.log(CHIRP_RATIO) / np.log(R_START / R_MERGE)

BH_RADIUS = 0.38
REMNANT_RADIUS = 0.52
BH_SIT = 0.55  # fraction of its radius a hole sits above the sheet

# --- the radiation --------------------------------------------------------
# A quadrupole pattern: two arms rotating at twice the orbital frequency. The
# wavelength is WAVE_SPEED * pi / omega, so WAVE_SPEED is really a choice of
# how many ripples fit across the sheet -- 1.5 puts ~1.7 wavelengths across the
# radius at the start and ~5 at merger.
WAVE_SPEED = 1.5
H_START = 0.17  # strain amplitude while the binary is still wide
H_GROWTH = 0.8  # h ~ omega**H_GROWTH; 2/3 is the real chirp, 0.8 is legible
NEAR_ZONE = 1.0  # radius inside which the field is not retarded
# A true 1/rho falloff leaves the outer half of the sheet visibly flat, which
# buries the story. The profile below only zeroes the field inside the orbit
# and then fades gently, so a ripple is still legible when it reaches the rim.
RHO_SOFT = 1.1  # radius over which the field ramps up out of the near zone
RHO_FALL = 6.0  # scale of the 1/(1 + rho/RHO_FALL) decay beyond it
WAVE_ONSET = 0.8  # seconds over which the radiation switches on at t = 0
TAU_RINGDOWN = 0.9  # e-folding time of the post-merger amplitude

# --- the wells ------------------------------------------------------------
WELL_DEPTH = 0.62
WELL_WIDTH = 0.7
REMNANT_WELL_DEPTH = 1.15
REMNANT_WELL_WIDTH = 0.95
MERGE_BLEND = 1.0  # seconds over which two wells become one

T_END = T_INSPIRAL + T_RINGDOWN


# --- the source's history -------------------------------------------------
# Orbital phase is the integral of a frequency that changes the whole time, so
# it is tabulated once here and interpolated. The table runs from well before
# t = 0 because the rim of the sheet asks about retarded times that far back.
def separation(t):
    """Orbital separation (half the distance between the holes) at time t."""
    s = np.clip(t / T_INSPIRAL, 0.0, 1.0)
    return R_MERGE + (R_START - R_MERGE) * (1.0 - s) ** INSPIRAL_SHARPNESS


def omega(t):
    """Orbital angular frequency at time t, frozen at both ends."""
    return OMEGA_START * (R_START / separation(t)) ** KEPLER_EXPONENT


_T_TABLE = np.linspace(-15.0, T_END + 5.0, 30001)
_OMEGA_TABLE = omega(_T_TABLE)
_PHASE_TABLE = np.concatenate(
    [[0.0], np.cumsum(0.5 * (_OMEGA_TABLE[1:] + _OMEGA_TABLE[:-1]) * np.diff(_T_TABLE))]
)
_PHASE_TABLE -= np.interp(0.0, _T_TABLE, _PHASE_TABLE)


def orbital_phase(t):
    """Accumulated orbital phase, zero at t = 0."""
    return np.interp(t, _T_TABLE, _PHASE_TABLE)


def hole_positions(t):
    """Centres of the two holes, diametrically opposite on the orbit."""
    r = separation(t)
    phi = orbital_phase(t)
    offset = np.array([r * np.cos(phi), r * np.sin(phi), 0.0])
    return offset, -offset


# --- the field ------------------------------------------------------------
def smooth_step(x):
    x = np.clip(x, 0.0, 1.0)
    return x * x * (3.0 - 2.0 * x)


def strain(t_emit):
    """Wave amplitude emitted at time t_emit: switches on, chirps, rings down."""
    growing = H_START * (omega(t_emit) / OMEGA_START) ** H_GROWTH
    decay = np.exp(-np.maximum(t_emit - T_INSPIRAL, 0.0) / TAU_RINGDOWN)
    return growing * decay * smooth_step(t_emit / WAVE_ONSET)


def wells(x, y, t, gain=1.0):
    """The static dent each hole makes, blended into one well at the merger."""
    p1, p2 = hole_positions(t)
    pair = sum(
        np.exp(-((x - p[0]) ** 2 + (y - p[1]) ** 2) / (2 * WELL_WIDTH**2))
        for p in (p1, p2)
    )
    single = (
        REMNANT_WELL_DEPTH
        / WELL_DEPTH
        * np.exp(-(x**2 + y**2) / (2 * REMNANT_WELL_WIDTH**2))
    )
    w = smooth_step((t - T_INSPIRAL) / MERGE_BLEND)
    return -gain * WELL_DEPTH * ((1.0 - w) * pair + w * single)


def sheet_height(x, y, t, gain=1.0):
    """Height of the spacetime sheet at (x, y) and scene time t."""
    rho = np.hypot(x, y)
    # Outside the near zone the sheet reports what the source was doing a
    # light-crossing time ago; that delay is what curls the pattern into arms.
    t_emit = t - np.maximum(rho - NEAR_ZONE, 0.0) / WAVE_SPEED
    radial = smooth_step(rho / RHO_SOFT) / (1.0 + rho / RHO_FALL)
    edge = smooth_step((GRID_HALF - rho) / EDGE_FADE)
    quadrupole = np.cos(2.0 * np.arctan2(y, x) - 2.0 * orbital_phase(t_emit))
    return wells(x, y, t, gain) + gain * strain(t_emit) * radial * edge * quadrupole


# --- colour by height -----------------------------------------------------
_LUT = [
    interpolate_color(TROUGH_COLOR, SHEET_COLOR, 1.0 + u)
    if u < 0
    else interpolate_color(SHEET_COLOR, CREST_COLOR, u)
    for u in np.linspace(-1.0, 1.0, 33)
]


def height_colors(z):
    """Map an array of heights onto the trough-sheet-crest ramp."""
    idx = (z / HEIGHT_COLOR_SCALE + 1.0) * 0.5 * (len(_LUT) - 1)
    return [_LUT[i] for i in np.clip(idx, 0, len(_LUT) - 1).astype(int)]


# --- mobjects -------------------------------------------------------------
# A stand-in reference point far below the sheet. Anything whose z_index_group
# is set to it sorts to the back: its depth is -1000 * cos(phi), which beats
# anything in the scene for any camera above the horizon. Used by the grid
# lines (see SheetLine).
BEHIND_EVERYTHING = VectorizedPoint([0.0, 0.0, -1000.0])


class SheetLine(VMobject):
    """A grid line that sits at the back of the camera's depth sort.

    shade_in_3d is what puts a mobject into ThreeDCamera's depth sort at all;
    anything without it scores np.inf, and np.inf sorts last, so an unshaded
    sheet is painted over the holes. But sorting the sheet honestly is no good
    either: each line spans the whole sheet, and the sort has only one depth
    per mobject to work with, so a line whose midpoint is near the camera gets
    drawn over the holes along its entire length. The wireframe ends up
    splattered across them.

    So the flag goes on and z_index_group sends every line to a point far
    behind the scene. All the lines then share one key, which leaves their
    order among themselves exactly as built, and the whole sheet lands behind
    both holes -- while the holes, which are compact enough for one depth each
    to be meaningful, sort properly against each other.

    Setting the flag has one side effect to undo: it reroutes the stroke
    gradient through get_3d_vmob_gradient_start_and_end_points, whose
    end-corner index ((n - 1) // 6) * 3 assumes a four-corner Surface face. On
    a polyline of a hundred-odd anchors that lands near the middle, squashing
    the height colours into the first half of every line.
    """

    def __init__(self, **kwargs):
        super().__init__(shade_in_3d=True, **kwargs)
        self.z_index_group = BEHIND_EVERYTHING

    def get_gradient_start_and_end_points(self):
        return self.points[0], self.points[-1]


def make_sheet():
    """The wireframe sheet, flat, with each line's sampling stashed on it."""
    grid = VGroup()
    coords = np.linspace(-GRID_HALF, GRID_HALF, GRID_LINES)
    samples = np.linspace(-GRID_HALF, GRID_HALF, GRID_SAMPLES)
    stops = np.linspace(0, GRID_SAMPLES - 1, GRADIENT_STOPS).astype(int)
    fixed = np.full_like(samples, 0.0)

    for c in coords:
        for xs, ys in ((samples, fixed + c), (fixed + c, samples)):
            line = SheetLine(stroke_width=SHEET_STROKE_WIDTH)
            line.set_points_as_corners(np.stack([xs, ys, np.zeros_like(xs)], axis=1))
            line.set_stroke(SHEET_COLOR, SHEET_STROKE_WIDTH)
            line.xs, line.ys, line.stops = xs, ys, stops
            grid.add(line)
    return grid


def refresh_sheet(grid, t, gain=1.0):
    """Re-evaluate every grid line at time t and recolour it by height."""
    for line in grid:
        z = sheet_height(line.xs, line.ys, t, gain)
        line.set_points_as_corners(np.stack([line.xs, line.ys, z], axis=1))
        line.set_stroke(color=height_colors(z[line.stops]))


def make_black_hole(radius=BH_RADIUS):
    """A black sphere with a warm rim mesh.

    It keeps manim's default shade_in_3d, which is what earns it a place in the
    camera's depth sort: ThreeDCamera.get_mobjects_to_display scores every
    mobject without that flag as np.inf, so unshaded mobjects are painted in
    scene order and two unshaded holes would never swap over as they orbit.
    The lighting pass itself is switched off at the camera (see construct), so
    the fill stays properly black instead of being brightened to grey.

    Nothing else is needed to make it read against the background: the hole
    sits in a well ringed by bright grid lines, so its silhouette is a gap
    punched in the wireframe, and the mesh supplies the curvature.
    """
    horizon = Sphere(radius=radius, resolution=(16, 16), checkerboard_colors=False)
    horizon.set_fill(HORIZON_COLOR, 1.0)
    horizon.set_stroke(HORIZON_GLOW, HORIZON_MESH_WIDTH, HORIZON_MESH_OPACITY)
    return horizon


def follow_orbit(hole, clock, which, gain, radius=BH_RADIUS):
    """Keep a hole on its orbit and resting in the bottom of its own well."""

    def update(m):
        t = clock.get_value()
        x, y = hole_positions(t)[which][:2]
        m.move_to([x, y, sheet_height(x, y, t, gain.get_value()) + BH_SIT * radius])

    hole.add_updater(update)
    update(hole)
    return hole


# --- the chirp trace ------------------------------------------------------
# The same field, sampled by one distant observer: the strip along the bottom
# is the waveform a detector would record, and it makes "frequency and
# amplitude both climb" a thing you can read off rather than infer.
TRACE_WIDTH = 9.0
TRACE_HEIGHT = 0.45
TRACE_CENTER = np.array([0.0, -3.45, 0.0])
TRACE_SAMPLES = 600


def observed_strain(t):
    """h(t) for an observer far out along +x, in the sheet's own height units."""
    return strain(t) * np.cos(2.0 * orbital_phase(t))


def make_trace(clock):
    """A polyline of h(t) up to the current clock, pinned to the bottom edge."""
    curve = VMobject(stroke_width=3)
    scale = TRACE_HEIGHT / (H_START * CHIRP_RATIO**H_GROWTH)

    def update(m):
        t = max(clock.get_value(), 1e-3)
        ts = np.linspace(0.0, t, TRACE_SAMPLES)
        xs = TRACE_CENTER[0] - TRACE_WIDTH / 2 + TRACE_WIDTH * ts / T_END
        ys = TRACE_CENTER[1] + scale * observed_strain(ts)
        m.set_points_as_corners(np.stack([xs, ys, np.zeros_like(xs)], axis=1))
        m.set_stroke(color=height_colors(observed_strain(ts[::40]) * 3.0))

    curve.add_updater(update)
    update(curve)
    return curve


class BlackHoleMerger(ThreeDScene):
    """Two black holes spiral in, radiating, and merge into one ringing remnant."""

    def construct(self):
        clock = ValueTracker(0.0)
        gain = ValueTracker(0.0)  # how strongly the sheet feels the holes

        # Depth sorting and lighting are both keyed off shade_in_3d, but only
        # the sorting is wanted here. The lighting pass keeps just the first two
        # stroke colours of whatever it touches, which would cut every grid
        # line's height gradient down to two stops, and it only ever brightens,
        # which turns a black horizon grey. Switching it off at the camera
        # leaves the sort untouched -- z_key never consults this flag.
        self.camera.should_apply_shading = False

        # frame_center lifts the sheet off the bottom of the frame so the chirp
        # trace has a clear strip to live in.
        self.set_camera_orientation(
            phi=67 * DEGREES,
            theta=-60 * DEGREES,
            zoom=0.84,
            frame_center=[0.0, 0.0, -0.45],
        )

        # --- 1. flat spacetime -------------------------------------------
        sheet = make_sheet()
        title = Tex(
            r"Gravitational waves from a binary black hole merger",
            font_size=FONT_TITLE,
        ).to_corner(UL)
        self.add_fixed_in_frame_mobjects(title)
        self.play(FadeIn(sheet, run_time=1.5), FadeIn(title, run_time=1.0))

        # The sheet redraws from the clock from here on; everything below just
        # moves the clock and lets the field do the work.
        sheet.add_updater(
            lambda m: refresh_sheet(m, clock.get_value(), gain.get_value())
        )
        self.begin_ambient_camera_rotation(rate=0.02)

        # --- 2. two holes dent it ----------------------------------------
        pair = VGroup(
            *[follow_orbit(make_black_hole(), clock, i, gain) for i in (0, 1)]
        )
        self.play(FadeIn(pair, scale=0.4), gain.animate.set_value(1.0), run_time=1.6)

        trace = make_trace(clock)
        self.add_fixed_in_frame_mobjects(trace)
        self.play(FadeIn(trace), run_time=0.8)

        # --- 3. the inspiral ---------------------------------------------
        # One linear sweep of the clock: the separation, the orbital frequency
        # and the retardation all follow from it, so the ripples tighten and
        # brighten on their own.
        self.play(
            clock.animate.set_value(T_INSPIRAL),
            rate_func=linear,
            run_time=T_INSPIRAL,
        )

        # --- 4. merger ----------------------------------------------------
        remnant = make_black_hole(REMNANT_RADIUS)
        remnant.add_updater(
            lambda m: m.move_to(
                [
                    0.0,
                    0.0,
                    sheet_height(0.0, 0.0, clock.get_value(), gain.get_value())
                    + BH_SIT * REMNANT_RADIUS,
                ]
            )
        )
        # Two rings leaving at different speeds read as a burst rather than as
        # one more ripple; they lie in the sheet's own plane, so they spread
        # across it instead of hanging in front of it.
        burst = VGroup(
            *[
                Circle(radius=0.5, color=HORIZON_GLOW, stroke_width=BURST_STROKE_WIDTH)
                for _ in range(2)
            ]
        )
        self.add(burst)
        self.play(
            clock.animate.set_value(T_INSPIRAL + MERGE_BLEND),
            FadeOut(pair, scale=0.5),
            FadeIn(remnant, scale=0.6),
            burst[0].animate.scale(7.0).set_stroke(opacity=0.0),
            burst[1].animate.scale(4.0).set_stroke(opacity=0.0),
            rate_func=linear,
            run_time=MERGE_BLEND,
        )
        self.remove(burst)

        # --- 5. ringdown --------------------------------------------------
        self.play(
            clock.animate.set_value(T_END),
            rate_func=linear,
            run_time=T_END - T_INSPIRAL - MERGE_BLEND,
        )

        # --- 6. one hole, one well, a sheet nearly flat again -------------
        self.wait(2.0)
        sheet.clear_updaters()
        self.stop_ambient_camera_rotation()
        self.wait(1.0)
