"""Build the phone-friendly web player for the rendered deck.

Reads talk/deck.txt and each slide's manim-slides config in slides/, copies
every segment's video (remuxed with faststart so it streams) into OUT/v/, and
writes OUT/index.html with the deck inlined as a manifest.

    talk/deck.sh render m
    .venv/bin/python talk/build_player.py [OUT]     # default: player/
"""

import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "player"
TEMPLATE = Path(__file__).parent / "player_template.html"

# The sections as the outline numbers them; a slide belongs to the last
# section slide before it.
SECTION_SLIDES = {
    "AtomInterferometrySlide": "1 · Atom interferometry",
    "GravitationalWavesSlide": "2 · Gravitational waves",
    "DarkMatterSlide": "3 · Dark matter",
    "PrototypeDeviceSlide": "4 · Our prototype device",
    "FuturePlansSlide": "5 · Future plans",
    "OutroSlide": "Outro",
}
# Names for the menu where the class name reads badly once split.
NAMES = {
    "TitleSlide": "Title",
    "ContentsSlide": "Outline",
    "AIONCollabSlide": "The AION collaboration",
    "AIONChambersSlide": "AION chambers across the UK",
    "Aion10BeecroftSlide": "AION-10 at Oxford",
    "AICECernSlide": "AICE at CERN",
    "LMTMachZehnderSlide": "LMT Mach-Zehnder",
    "LMTResultsSlide": "LMT results",
    "GradiometerGWStretchSlide": "Gradiometer: a stretching baseline",
    "OutroSlide": "Thank you",
}


def deck():
    lines = (Path(__file__).parent / "deck.txt").read_text(encoding="utf-8").splitlines()
    return [s for line in lines if (s := line.split("#")[0].strip())]


def pretty(name):
    if name in NAMES:
        return NAMES[name]
    words = re.sub(r"(?<=[a-z])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])", " ", name[:-len("Slide")])
    return words[0] + words[1:].lower()


def main():
    (OUT / "v").mkdir(parents=True, exist_ok=True)
    slides, segments = [], []
    section = "Intro"
    resolution = None
    for number, name in enumerate(deck(), start=1):
        config = json.loads((ROOT / "slides" / f"{name}.json").read_text())
        resolution = resolution or config["resolution"]
        section = SECTION_SLIDES.get(name, section)
        first = len(segments)
        for k, seg in enumerate(config["slides"]):
            dest = f"v/{number:02d}-{k:02d}.mp4"
            subprocess.run(
                ["ffmpeg", "-loglevel", "error", "-y", "-i", str(ROOT / seg["file"]),
                 "-c", "copy", "-movflags", "+faststart", str(OUT / dest)],
                check=True,
            )
            segments.append({"src": dest, "slide": number - 1,
                             "loop": seg["loop"], "auto": seg["auto_next"]})
        slides.append({"name": pretty(name), "section": section, "first": first,
                       "count": len(segments) - first})
    manifest = {"slides": slides, "segments": segments, "resolution": resolution}
    html = TEMPLATE.read_text(encoding="utf-8").replace(
        "/*MANIFEST*/null", json.dumps(manifest, separators=(",", ":"))
    )
    (OUT / "index.html").write_text(html, encoding="utf-8")
    size = sum(p.stat().st_size for p in (OUT / "v").glob("*.mp4"))
    print(f"{len(slides)} slides, {len(segments)} segments, {size / 1e6:.1f} MB of video -> {OUT}")


if __name__ == "__main__":
    main()
