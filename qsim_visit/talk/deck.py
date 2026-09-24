"""The Freiburg talk, without bash (Windows): render, present or convert the deck.

    uv run talk/deck.py render [-j N] [l|m|h] [Slide ...]   # default h; all slides, or just those named;
                                                            # -j N renders N slides at once (logs in media/deck_logs/)
    uv run talk/deck.py present
    uv run talk/deck.py html                                # aion_talk.html, one standalone file

The same commands as deck.sh, and the same deck order (talk/deck.txt).
Standard library only; run from anywhere, it works from the project root so manim.cfg applies.
"""

import argparse
import os
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SLIDES = "talk/aion_slides.py"
QUALITIES = {"l", "m", "h", "p", "k"}
# manim's rich output is UTF-8; without this a Windows child writing to a log hits cp1252.
ENV = {**os.environ, "PYTHONUTF8": "1", "PYTHONIOENCODING": "utf-8"}


def deck():
    lines = (ROOT / "talk" / "deck.txt").read_text(encoding="utf-8").splitlines()
    return [slide for line in lines if (slide := line.split("#")[0].strip())]


def manim_slides(*args, sync=True, **kwargs):
    uv = ["uv", "run"] + ([] if sync else ["--no-sync"])
    return subprocess.run([*uv, "manim-slides", *args], cwd=ROOT, env=ENV, **kwargs).returncode


def render(jobs, args):
    quality = args.pop(0) if args and args[0] in QUALITIES else "h"
    slides = args or deck()
    # -q h, not -qh: manim-slides reads the h of -qh as --help.
    if jobs == 1:
        return manim_slides("render", "-q", quality, SLIDES, *slides)

    # Cairo renders on one core, so run one process per slide, each
    # logging to media/deck_logs/<Slide>.log rather than interleaving.
    logs = ROOT / "media" / "deck_logs"
    logs.mkdir(parents=True, exist_ok=True)
    subprocess.run(["uv", "sync", "-q"], cwd=ROOT, check=True)

    def render_one(slide):
        log = logs / f"{slide}.log"
        with open(log, "wb") as out:
            rc = manim_slides("render", "-q", quality, SLIDES, slide, sync=False,
                              stdin=subprocess.DEVNULL, stdout=out, stderr=subprocess.STDOUT)
        print(f"done    {slide}" if rc == 0 else
              f"FAILED  {slide}  (see {log.relative_to(ROOT).as_posix()})", flush=True)
        return rc == 0

    with ThreadPoolExecutor(jobs) as pool:
        ok = all(list(pool.map(render_one, slides)))
    return 0 if ok else 1


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("command", choices=["render", "present", "html"])
    parser.add_argument("-j", type=int, default=1, metavar="N", help="render: N slides at once")
    parser.add_argument("args", nargs="*", help="render: [l|m|h] [Slide ...]")
    opts = parser.parse_args()

    if opts.command == "render":
        return render(opts.j, opts.args)
    if opts.command == "present":
        return manim_slides("present", *deck())
    return manim_slides("convert", *deck(), "aion_talk.html", "--to", "html", "--one-file")


if __name__ == "__main__":
    sys.exit(main())
