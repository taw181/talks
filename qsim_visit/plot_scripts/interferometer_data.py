"""Write the AION DAI fringe and Lissajous plots to ``figures/``.

``excitation_fringes.png``, then ``lissajous.png`` with both runs and
``lissajous_lln.png`` / ``lissajous_hln.png`` with one each, for building it
up on a slide. The figures themselves are aionanim.plots.dai_fringes.

    .venv/bin/python plot_scripts/interferometer_data.py
"""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from aionanim.plots.dai_fringes import fringes_figure, lissajous_figure, load
from aionanim.style import HLN_COLOR, LLN_COLOR, PLOT_BACKGROUND

ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = ROOT / "figures"


def save(fig, name):
    OUT_DIR.mkdir(exist_ok=True)
    fig.savefig(OUT_DIR / f"{name}.png", dpi=200, facecolor=PLOT_BACKGROUND)
    plt.close(fig)
    print(f"wrote figures/{name}.png")


def main():
    lln, hln = load("lln"), load("hln")
    save(fringes_figure(lln, hln), "excitation_fringes")
    quiet = (lln, LLN_COLOR, "Low laser noise")
    noisy = (hln, HLN_COLOR, "High laser noise")
    save(lissajous_figure([quiet, noisy]), "lissajous")
    save(lissajous_figure([quiet]), "lissajous_lln")
    save(lissajous_figure([noisy]), "lissajous_hln")


if __name__ == "__main__":
    main()
