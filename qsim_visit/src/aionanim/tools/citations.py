"""A citation as a line on a slide.

citation() turns references (aionanim.bibliography entries, or LaTeX
strings already formatted) into small grey lines, one per reference;
place_citation() puts them in the footer, bottom left. A slide that wants its
citation elsewhere, under a figure say, calls citation() and places it itself.
"""

from manim import *

from aionanim.bibliography import SHORT, Reference, format_reference
from aionanim.style import *


def citation(*refs, fmt=SHORT, numbered=False, font_size=FONT_CITATION,
             color=CITATION_COLOR, max_width=CITATION_MAX_WIDTH):
    """One line per reference, left aligned, shrunk to fit ``max_width``.

    Each of ``refs`` is a Reference, formatted under ``fmt``, or a LaTeX
    string used as it is. ``numbered`` puts [1], [2], ... in front.
    """
    lines = VGroup()
    for n, ref in enumerate(refs):
        text = format_reference(ref, fmt) if isinstance(ref, Reference) else ref
        if numbered:
            text = f"[{n + 1}] {text}"
        # \mbox: Tex's default environment would wrap a line this long
        lines.add(Tex(rf"\mbox{{{text}}}", font_size=font_size, color=color))
    lines.arrange(DOWN, aligned_edge=LEFT, buff=CITATION_LINE_BUFF)
    if lines.width > max_width:
        lines.scale_to_fit_width(max_width)
    # legible over a photograph, as the slide number is
    lines.set_stroke(PLOT_BACKGROUND, width=4, background=True)
    return lines


def place_citation(mob):
    """``mob`` in the footer: bottom left, its last line just above the
    progress bar."""
    return mob.move_to(
        [-config.frame_x_radius + CITATION_EDGE_BUFF,
         -config.frame_y_radius + CITATION_BOTTOM, 0],
        aligned_edge=DL,
    )
