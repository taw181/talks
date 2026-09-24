"""One shot of the experiment, stage by stage, beside the imaging of it.

A timeline of the sequence runs along the bottom and lights up one stage at
a time; the Sr level scheme lights the transition that stage drives; and the
imaging video plays in the upper right corner through the stages it covers,
from the broadband red MOT to loading the lower dipole trap. The stages
either side of it -- the blue MOT before, state preparation, interferometry
and readout after -- run over a veiled video: before it, nothing to see yet;
after it, its last frame, dimmed.
"""

from manim import *

from aionanim.resources import data_path
from aionanim.style import *
from aionanim.tools.sequence import (
    IMAGING_CROP,
    IMAGING_FRAMES_PER_SNAPSHOT,
    IMAGING_T0_MS,
    IMAGING_VIDEO,
    STAGES,
    References,
    SrLevels,
    Timeline,
    snapshot_index,
    snapshot_ms,
    stage_heading,
)
from aionanim.tools.video import VideoFrame, load_video_frames

# --- experiment-sequence layout --------------------------------------------
SEQ_VIDEO_SIZE = 3.9
SEQ_VIDEO_CENTER = [4.8, 1.95, 0]
SEQ_LEVELS_CENTER = [-4.35, 1.9, 0]
SEQ_LEVELS_SCALE = 0.85
SEQ_HEADING_CENTER = [0.35, 2.6, 0]
SEQ_TIMELINE_Y = -1.0

# --- pacing ---------------------------------------------------------------
SEQ_VIDEO_MS_PER_S = 25.0  # the imaging at half a second a snapshot
SEQ_STAGE_TIME = 2.5  # a stage the video doesn't cover
SEQ_SWITCH_TIME = 0.6  # how long the timeline takes to move to the next stage


class ExperimentSequence(Scene):
    def construct(self):
        levels = SrLevels().scale(SEQ_LEVELS_SCALE).move_to(SEQ_LEVELS_CENTER)
        timeline = Timeline()
        timeline.move_to([0, SEQ_TIMELINE_Y, 0], aligned_edge=UP)
        timeline.set_x(0)
        refs = References(timeline)

        frames = load_video_frames(
            data_path(*IMAGING_VIDEO), every=IMAGING_FRAMES_PER_SNAPSHOT,
            crop=IMAGING_CROP,
        )
        video = VideoFrame(frames).set(height=SEQ_VIDEO_SIZE).move_to(SEQ_VIDEO_CENTER)
        t_ms = ValueTracker(IMAGING_T0_MS)
        video.add_updater(lambda m: m.show(snapshot_index(t_ms.get_value())))
        clock = always_redraw(lambda: Tex(
            rf"$t = {snapshot_ms(t_ms.get_value()):.0f}$\,ms",
            font_size=FONT_VIDEO_CLOCK,
        ).next_to(video.get_corner(UL), DR, buff=0.15))
        # drawn over the video and its clock, since the frames can't be faded
        veil = Rectangle(width=SEQ_VIDEO_SIZE, height=SEQ_VIDEO_SIZE, stroke_width=0,
                         fill_color=PLOT_BACKGROUND, fill_opacity=1).move_to(video)
        border = SurroundingRectangle(video, buff=0, **VIDEO_BORDER_STYLE)
        # so the empty box during the blue MOT reads as "not yet", not "broken"
        not_yet = Tex(r"imaging starts\\at the red MOT", font_size=FONT_LEGEND,
                      color=lighten(GUIDE_COLOR)).move_to(video)

        self.add(video, clock, veil)
        self.play(FadeIn(levels), FadeIn(timeline), FadeIn(refs), Create(border),
                  FadeIn(not_yet))

        heading = VGroup()
        for i, stage in enumerate(STAGES):
            new_heading = stage_heading(stage).move_to(SEQ_HEADING_CENTER)
            anims = [
                *timeline.activate(i),
                *levels.drive(stage.transition),
                *refs.cite(stage.reference),
                # out, then in: two headings crossing each other can't be read
                Succession(FadeOut(heading, shift=UP * 0.2),
                           FadeIn(new_heading, shift=UP * 0.2)),
            ]
            heading = new_heading
            filmed = stage.video_ms is not None
            was_filmed = i > 0 and STAGES[i - 1].video_ms is not None
            if filmed and not was_filmed:
                anims += [veil.animate.set_fill(opacity=0), FadeOut(not_yet)]
            elif was_filmed and not filmed:
                anims.append(veil.animate.set_fill(opacity=VIDEO_DIM_OPACITY))

            if filmed:
                start, end = stage.video_ms
                t_ms.set_value(start)
                switch_end = start + SEQ_SWITCH_TIME * SEQ_VIDEO_MS_PER_S
                self.play(*anims, t_ms.animate(rate_func=linear).set_value(switch_end),
                          run_time=SEQ_SWITCH_TIME)
                self.play(t_ms.animate.set_value(end), rate_func=linear,
                          run_time=(end - switch_end) / SEQ_VIDEO_MS_PER_S)
            else:
                self.play(*anims, run_time=SEQ_SWITCH_TIME)
                self.wait(SEQ_STAGE_TIME - SEQ_SWITCH_TIME)
        self.wait()
