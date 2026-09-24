#!/usr/bin/env bash
# The Freiburg talk: render, present or convert the deck in talk/aion_slides.py.
#
#   talk/deck.sh render [-j N] [l|m|h] [Slide ...]   # default h; all slides, or just those named;
#                                                     # -j N renders N slides at once (logs in media/deck_logs/)
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
    SignalInjectionSlide
    LightShiftSignalSlide
    LaserNoiseLissajousSlide
    ExtractedSignalSlide
    # future plans
    FuturePlansSlide
    Aion10BeecroftSlide
    AICECernSlide
    LargeMomentumTransferSlide
    LMTResultsSlide
    # outro
    OutroSlide
)

case "${1:-}" in
    render)
        shift
        jobs=1
        if [[ "${1:-}" == -j* ]]; then
            jobs="${1#-j}"
            shift
            [[ -n "$jobs" ]] || { jobs="${1:?-j needs a number}"; shift; }
        fi
        quality="${1:-h}"
        shift $(( $# < 1 ? $# : 1 ))
        (( $# )) || set -- "${DECK[@]}"
        # -q h, not -qh: manim-slides reads the h of -qh as --help.
        if (( jobs == 1 )); then
            uv run manim-slides render -q "$quality" talk/aion_slides.py "$@"
            exit
        fi
        # Cairo renders on one core, so run one process per slide, each
        # logging to media/deck_logs/<Slide>.log rather than interleaving.
        mkdir -p media/deck_logs
        uv sync -q
        render_one() {
            local log="media/deck_logs/$1.log"
            if uv run --no-sync manim-slides render -q "$2" talk/aion_slides.py "$1" >"$log" 2>&1; then
                echo "done    $1"
            else
                echo "FAILED  $1  (see $log)"
                return 1
            fi
        }
        export -f render_one
        printf '%s\n' "$@" | xargs -P "$jobs" -I{} bash -c 'render_one "$1" "$2"' _ {} "$quality"
        ;;
    present)
        uv run manim-slides present "${DECK[@]}"
        ;;
    html)
        uv run manim-slides convert "${DECK[@]}" aion_talk.html --to html --one-file
        ;;
    *)
        sed -n '2,8p' "$0" | sed 's/^# \{0,1\}//'
        exit 1
        ;;
esac
