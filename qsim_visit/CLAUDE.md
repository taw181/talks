# qsim_visit

commit and push frequently as you go.

Manim animations for a talk on single-photon atom clock interferometry
(AION: Sr clock transition, gradiometer baseline, large momentum transfer).

The project is two layers, because the general part gets spun out as its own package after the talk:

- `src/aionanim/` — the installable package (`uv sync` installs it editable). Anything reusable: atom-interferometry, AION and GW physics, drawing tools and scenes. **Default home for new work.**
  - `style.py` holds every colour, stroke width, font size and the pacing constant `V`; add to it rather than hardcoding inline.
  - `tools/<topic>.py` — helpers and the geometry they use (defaults bind at def time); `scenes/<topic>.py` — Scene classes and layout only they use; `physics/` — numbers, no manim; `plots/` — matplotlib figure builders; `data/` — CSVs and images read via `aionanim.resources.data_path` (sources/licences in `data/README.md`).
  - Nothing in the package may import `manim_slides` or refer to talk files.
- `talk/` — only what is specific to this talk: `aion_slides.py` (every slide: `Slide` wrappers, static photo/figure slides, talk-only tweaks done by subclassing a package scene), `deck.sh` (the deck's order), `media/` (its pictures and video).
  - Slide stops: a package scene calls a no-op hook (`beat()`; the sequence scenes' `stage_break()`) at each beat, and `aion_slides.py`'s `Clicks` / `LoopingStages` mixins turn it into `next_slide()`. Where a subclass rewrites `construct`/`fly` without `super()`, the calls go in both.
- Talk-side support: `plot_scripts/` save `aionanim.plots` figures into `figures/`; `data_scripts/` regenerate package data; `notes/` holds exported transcripts.

Working rules:

- `uv run manim -ql src/aionanim/scenes/<file>.py <Scene>` — run from the project root so `manim.cfg` applies; `-qh` for the talk. Deck: `talk/deck.sh render [l|h] [Slide ...]`, `talk/deck.sh present`, `talk/deck.sh html` (it passes `-q h`, not `-qh`: manim-slides reads the `h` as `--help`).
- Output: `media/videos/<script-stem>/<quality>/<Scene>.mp4` (gitignored).
- Imports are absolute (`from aionanim.tools.clock import make_dial`), never relative: manim loads a scene file by path under a module name built from that path, so relative imports break. Star-import only `manim` and `aionanim.style`; import names from topic modules explicitly, since they share names (`strain`, `GW_PERIOD`, ...).
- `scenes/__init__.py` and `aionanim/__init__.py` must import nothing, or a scene file rendered by path gets loaded twice.
- A method looks up globals in the module that defines it: moving a scene or mixin means moving its imports too (e.g. `RunsContinuously` in `scenes/gradiometer_gw.py` serves the light-shift scenes).
- One-off scripts: `.venv/bin/python`.
- Git root is `~/talks`, so git paths are prefixed `qsim_visit/`. Stage explicit paths — the working tree usually holds in-progress scripts of the user's, and `git add -A` will sweep them into your commit.
- Annotations belong where the physics happens: don't offset a recoil arrow off its atom to dodge an overlap — the overlap is fine.
- Measured data: `aionanim/plots/dai_fringes.py` → AION DAI fringes and Lissajous ellipse (Zenodo 19592552); `aionanim/plots/gw_sensitivity.py` → detector curves with merger tracks.
- Render-and-check loop, colour sampling, manim traps: the `manim-atom-interferometry` skill.
