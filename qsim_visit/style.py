"""Visual style for the talk's manim animations.

One place for the colour scheme, line styles, type sizes and pacing, so that
every animation in the talk reads as one set of figures:

    from manim import *
    from style import *

The ``*_STYLE`` bundles are dicts meant to be splatted into a mobject's
constructor, e.g. ``DashedLine(a, b, **GUIDE_STYLE)``.
"""

from manim import BLUE_B, BLUE_D, GREY_B, PURPLE_B, RED_C, WHITE, interpolate_color

# --- colour scheme --------------------------------------------------------
ATOM_COLOR = BLUE_D  # |g, p>
# |e, p + hbar k>. Purple rather than a second blue-green: TEAL sampled too
# close to ATOM_COLOR to separate on a projector, and telling the two arms
# apart is the whole point of an interferometer figure.
KICKED_COLOR = PURPLE_B
LASER_COLOR = RED_C  # beams, pulses, and every annotation about them
GUIDE_COLOR = GREY_B  # construction lines, e.g. the incoming trajectory
AREA_COLOR = BLUE_B  # the area a closed interferometer encloses
HIGHLIGHT_COLOR = WHITE  # the specular dot that makes an atom read as a sphere

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
HIGHLIGHT_RADIUS_RATIO = 0.32  # of the atom's radius
HIGHLIGHT_OFFSET_RATIO = 0.4  # ditto, up and to the left
HIGHLIGHT_OPACITY = 0.55

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
