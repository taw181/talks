"""Write the GW sensitivity plot to ``figures/gw_sensitivity.png``.

The figure itself is aionanim.plots.gw_sensitivity.

    .venv/bin/python plot_scripts/gw_sensitivity.py
"""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from aionanim.plots.gw_sensitivity import sensitivity_figure
from aionanim.style import PLOT_BACKGROUND

ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = ROOT / "figures"


def save(fig, name):
    OUT_DIR.mkdir(exist_ok=True)
    fig.savefig(OUT_DIR / f"{name}.png", dpi=200, facecolor=PLOT_BACKGROUND)
    plt.close(fig)
    print(f"wrote figures/{name}.png")


def main():
    save(sensitivity_figure(), "gw_sensitivity")


if __name__ == "__main__":
    main()
