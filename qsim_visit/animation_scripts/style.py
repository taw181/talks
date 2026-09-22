"""Visual style for the talk's manim animations.

One place for the colour scheme, line styles, type sizes and pacing, so that
every animation in the talk reads as one set of figures:

    from manim import *
    from style import *

The ``*_STYLE`` bundles are dicts meant to be splatted into a mobject's
constructor, e.g. ``DashedLine(a, b, **GUIDE_STYLE)``.
"""

from manim import (
    BLUE_B,
    BLUE_D,
    GREY_B,
    PURPLE_B,
    RED_C,
    WHITE,
    ManimColor,
    interpolate_color,
)

# --- colour scheme --------------------------------------------------------
ATOM_COLOR = BLUE_D  # |g, p>
# |e, p + hbar k>. Purple rather than a second blue-green: TEAL sampled too
# close to ATOM_COLOR to separate on a projector, and telling the two arms
# apart is the whole point of an interferometer figure.
KICKED_COLOR = PURPLE_B
LASER_COLOR = RED_C  # beams, pulses, and every annotation about them
GUIDE_COLOR = GREY_B  # construction lines, e.g. the incoming trajectory
AREA_COLOR = BLUE_B  # the area a closed interferometer encloses

# An interferometer arm is an amplitude, not a whole atom.
SUPERPOSITION_OPACITY = 0.65


def lighten(color, amount=0.35):
    """The stroke and label shade that goes with a fill colour."""
    return interpolate_color(color, WHITE, amount)


# --- type -----------------------------------------------------------------
FONT_TITLE = 32
FONT_STATE = 36  # a state label beside an atom that has come to rest
FONT_ANNOTATION = 34  # recoil arrows, pulse captions, the readout formula
FONT_LEGEND = 30
FONT_PHASE = 40
FONT_K = 32  # the k-vector marker beside a beam

# --- atoms ----------------------------------------------------------------
ATOM_RADIUS = 0.18
LEGEND_ATOM_RADIUS = 0.13
ATOM_STROKE_WIDTH = 2

# --- laser pulses ---------------------------------------------------------
PULSE_LENGTH = 2.2
PULSE_AMPLITUDE = 0.28
PULSE_CYCLES = 4.5
PULSE_STROKE_WIDTH = 4
PULSE_TAPER = [0.15, 1.0, 0.15]  # stroke opacity along the packet

# --- line styles ----------------------------------------------------------
GUIDE_STYLE = dict(
    dash_length=0.12, stroke_width=2, stroke_opacity=0.3, color=GUIDE_COLOR
)
TRAJECTORY_STYLE = dict(stroke_width=4)
RECOIL_ARROW_STYLE = dict(
    buff=0, stroke_width=4, color=LASER_COLOR, max_tip_length_to_length_ratio=0.22
)
K_ARROW_STYLE = dict(
    buff=0, stroke_width=3, color=LASER_COLOR, max_tip_length_to_length_ratio=0.3
)
FLASH_STYLE = dict(color=LASER_COLOR, flash_radius=0.55, line_length=0.3)
LOOP_AREA_STYLE = dict(stroke_width=0, fill_color=AREA_COLOR, fill_opacity=0.09)

# --- pacing ---------------------------------------------------------------
# Pacing is part of the house style. Every leg's run_time is distance / V, so
# an atom's speed never visibly changes when a pulse splits it -- which is what
# makes a 45 degree kick honest: the recoil is purely vertical and equal in
# magnitude to the forward motion.
V = 2.0
PULSE_SPEED = V * 1.6

# --- spacetime and gravitational waves ------------------------------------
# The sheet is coloured by height, so it needs three shades that stay apart at
# a 1.5px stroke: a calm slate at rest, a bright crest and a deep trough. The
# holes themselves are warm, which is the one hue nothing else in the talk
# uses -- against the blue sheet they read instantly as the source.
SHEET_COLOR = ManimColor("#33607f")  # undisturbed spacetime
CREST_COLOR = ManimColor("#a8e4ff")  # a wave crest
TROUGH_COLOR = ManimColor("#54367f")  # a trough, and the floor of a gravitational well
HORIZON_COLOR = ManimColor("#000000")  # the event horizon: darker than the background
HORIZON_GLOW = ManimColor("#ffb26b")  # the rim light and the merger burst

SHEET_STROKE_WIDTH = 1.5
HORIZON_MESH_WIDTH = 0.6
HORIZON_MESH_OPACITY = 0.14
BURST_STROKE_WIDTH = 5

# An h(t) trace is the wave measured rather than the wave itself, so it takes
# the crest shade: bright enough to sit above a diagram without competing with
# the laser red that marks everything the pulses do.
STRAIN_COLOR = CREST_COLOR
STRAIN_STROKE_WIDTH = 3

# --- an oscillating background field --------------------------------------
# A trace above the diagram is the same kind of object whether what oscillates
# is the metric or a scalar field driving the fundamental constants, so a
# dark-matter field takes the strain trace's shade and width. What it needs on
# top is the stretch of the oscillation one arm was excited during: a wash
# rather than an outline, because what matters is which part of the cycle it
# covers, not where its edges fall.
FIELD_COLOR = STRAIN_COLOR
FIELD_STROKE_WIDTH = STRAIN_STROKE_WIDTH
FIELD_WINDOW_STYLE = dict(stroke_width=0, fill_color=AREA_COLOR, fill_opacity=0.16)

# --- phase, drawn as a clock hand -----------------------------------------
# A hand is only legible on an atom about twice the usual size, which crowds a
# figure, so only the atoms that actually carry one are grown. The hand is
# white because it has to read against both state colours.
CLOCK_ATOM_RADIUS = 0.32
CLOCK_HAND_COLOR = WHITE
CLOCK_HAND_WIDTH = 3
CLOCK_HAND_RATIO = 0.8  # of the atom's radius
CLOCK_DIAL_RADIUS = 0.95
CLOCK_SWEEP_OPACITY = 0.4

# --- the phase budget -----------------------------------------------------
# Breaking Phi into its terms sorts them into two kinds, and the colour does
# the sorting: white for the term the measurement is after, and the usual
# laser red for the one the light brings with it, circled or struck depending
# on the instrument. A ring lends its colour to its label; a struck term takes
# the grey instead, since the cross has already said the term is out of play.
SIGNAL_COLOR = WHITE
STRUCK_COLOR = GUIDE_COLOR
STRUCK_OPACITY = 0.45  # what a crossed-out term dims to
CROSS_COLOR = LASER_COLOR
CROSS_STROKE_WIDTH = 4
NOISE_COLOR = LASER_COLOR
RING_STROKE_WIDTH = 3
RING_BUFF = 0.18  # how far a ring stands off the term it circles

# --- output ports ---------------------------------------------------------
# What the last pulse actually produces: two states, each holding a fraction
# of the atoms fixed by the phase. A port that got none of them is still drawn
# -- as a dashed guide with a dimmed label -- because the null only reads as
# "all of them came out here" if the side they did not come out of is visible.
PORT_EMPTY = 0.02  # below this share, a port is drawn as an empty one
PORT_EMPTY_OPACITY = 0.4  # how far an empty port's label is dimmed


# --- energy levels --------------------------------------------------------
# A two-level system drawn beside an interferometer doubles as its key, so the
# level lines take the state colours straight: a short horizontal segment has
# to carry its colour at a glance, which needs a heavier stroke than a
# trajectory. The gap arrow is furniture and takes the construction grey; it
# only goes laser red while a pulse is actually driving the transition, which
# is the one moment the light and the atom are the same object.
LEVEL_STROKE_WIDTH = 6
LEVEL_GAP_ARROW_STYLE = dict(
    buff=0,
    stroke_width=3,
    color=lighten(GUIDE_COLOR),
    max_tip_length_to_length_ratio=0.09,
)
LEVEL_GLOW_ARROW_STYLE = dict(
    buff=0,
    stroke_width=5,
    color=LASER_COLOR,
    max_tip_length_to_length_ratio=0.12,
)
