# qsim_visit

commit and push frequently as you go.

Manim animations for a talk on single-photon atom clock interferometry
(AION: Sr clock transition, gradiometer baseline, large momentum transfer).

- `uv run manim -ql animation_scripts/<file>.py <Scene>` — run from the project root so `manim.cfg` applies; `-qh` for the talk.
- Output: `media/videos/<script-stem>/<quality>/<Scene>.mp4` (gitignored).
- Scenes live in `animation_scripts/` beside `style.py` — manim puts the script's own directory on `sys.path`, which is the only reason `from style import *` resolves.
- `style.py` holds every colour, stroke width, font size and the pacing constant `V`; add to it rather than hardcoding inline.
- One-off scripts: `.venv/bin/python`.
- Git root is `~/talks`, so git paths are prefixed `qsim_visit/`. Stage explicit paths — the working tree usually holds in-progress scripts of the user's, and `git add -A` will sweep them into your commit.
- Annotations belong where the physics happens: don't offset a recoil arrow off its atom to dodge an overlap — the overlap is fine.
- Measured data: `data_scripts/` pulls it into `data/` (committed), `plot_scripts/` plots it with matplotlib into `figures/` using the plot colours in `style.py`. `plot_scripts/interferometer_data.py` → AION DAI fringes and Lissajous ellipse (Zenodo 19592552).
- Render-and-check loop, colour sampling, manim traps: the `manim-atom-interferometry` skill.
