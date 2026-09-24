#!/usr/bin/env bash
# The Freiburg talk: render, present or convert the deck in talk/aion_slides.py.
#
#   talk/deck.sh render [l|m|h] [Slide ...]   # default h; all slides, or just those named
#   talk/deck.sh present
#   talk/deck.sh html                         # aion_talk.html, one standalone file
#
# Run from anywhere; it works from the project root so manim.cfg applies.
set -euo pipefail
cd "$(dirname "$0")/.."

DECK=(
    # intro
    TitleSlide
    ContentsSlide
    # motivation
    BlackHoleMergerSlide
    MergerOnSensitivityPlotSlide
    SensitivityLandscapeSlide
    DarkMatterFieldSlide
    # how atom interferometry works
    SinglePhotonMachZehnderSlide
    ClockPhaseTermsSlide
    DarkMatterPhaseSlide
    GradiometerSlide
    GradiometerGWStretchSlide
    AIONCollabSlide
    # our prototype device
    CoolingSequenceSlide
    DipoleTrapLoadingSlide
    VelocitySlicingSlide
    LightShiftSignalSlide
    FringesFirstSlide
    FringesFirstNoisySlide
    ExtractedSignalSlide
    # future plans
    Aion10BeecroftSlide
    AICECernSlide
    LargeMomentumTransferSlide
    LMTResultsSlide
    # outro
    OutroSlide
)

case "${1:-}" in
    render)
        quality="${2:-h}"
        shift $(( $# < 2 ? $# : 2 ))
        (( $# )) || set -- "${DECK[@]}"
        # -q h, not -qh: manim-slides reads the h of -qh as --help.
        uv run manim-slides render -q "$quality" talk/aion_slides.py "$@"
        ;;
    present)
        uv run manim-slides present "${DECK[@]}"
        ;;
    html)
        uv run manim-slides convert "${DECK[@]}" aion_talk.html --to html --one-file
        ;;
    *)
        sed -n '2,7p' "$0" | sed 's/^# \{0,1\}//'
        exit 1
        ;;
esac
