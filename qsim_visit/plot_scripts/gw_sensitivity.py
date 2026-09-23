"""Characteristic-strain sensitivity curves of LISA, LIGO, ET, AION-km and AEDGE.

All six curves digitised from ``GW_exclusion_plot.svg`` into
``data/gw_sensitivity/`` (see each CSV's header for the shapes it came from),
drawn together on the source figure's axes, each region shaded down to its
curve and labelled beside it.

    .venv/bin/python plot_scripts/gw_sensitivity.py

Writes ``figures/gw_sensitivity.png``.
"""

import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "animation_scripts"))
from style import (  # noqa: E402
    GW_DETECTOR_COLORS,
    GW_REGION_OPACITY,
    PLOT_BACKGROUND,
    PLOT_FOREGROUND,
)

DATA_DIR = ROOT / "data" / "gw_sensitivity"
OUT_DIR = ROOT / "figures"

LABEL_SIZE = 15
TICK_SIZE = 13

# The source figure's frame.
F_RANGE = (1e-6, 1e4)
H_RANGE = (1e-24, 3e-15)

# name: (CSV stem, label position (f / Hz, h_c)). AEDGE+ is drawn under AEDGE
# so AEDGE's own curve stays on top where the two coincide above 0.05 Hz.
DETECTORS = {
    "AEDGE+": ("aedge_plus", (2e-6, 1.5e-19)),
    "AEDGE": ("aedge", (1.5e-2, 1.5e-23)),
    "LISA": ("lisa", (2e-4, 1.2e-21)),
    "AION-km": ("aion_km", (2e2, 3e-19)),
    "ET": ("et", (1.2e2, 3e-24)),
    "LIGO": ("ligo", (1.8e1, 1.5e-21)),
}


def load(stem):
    with open(DATA_DIR / f"{stem}.csv") as f:
        rows = [line for line in f if not line.startswith(("#", "f_Hz"))]
    return np.loadtxt(rows, delimiter=",").T


def dark_axes(ax):
    ax.set_facecolor(PLOT_BACKGROUND)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    for side in ("left", "bottom"):
        ax.spines[side].set_color(PLOT_FOREGROUND)
    ax.tick_params(which="both", colors=PLOT_FOREGROUND, labelsize=TICK_SIZE)
    ax.xaxis.label.set_color(PLOT_FOREGROUND)
    ax.yaxis.label.set_color(PLOT_FOREGROUND)
    ax.xaxis.label.set_size(LABEL_SIZE)
    ax.yaxis.label.set_size(LABEL_SIZE)


def save(fig, name):
    OUT_DIR.mkdir(exist_ok=True)
    fig.savefig(OUT_DIR / f"{name}.png", dpi=200, facecolor=PLOT_BACKGROUND)
    plt.close(fig)
    print(f"wrote figures/{name}.png")


def main():
    fig, ax = plt.subplots(figsize=(8, 5.4))
    fig.set_facecolor(PLOT_BACKGROUND)
    for name, (stem, label_at) in DETECTORS.items():
        f, h = load(stem)
        color = GW_DETECTOR_COLORS[name]
        ax.fill_between(f, h, H_RANGE[1], color=color, alpha=GW_REGION_OPACITY, lw=0)
        ax.plot(f, h, color=color, lw=1.6)
        ax.text(*label_at, name, color=color, fontsize=LABEL_SIZE, ha="left", va="center")
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlim(*F_RANGE)
    ax.set_ylim(*H_RANGE)
    dark_axes(ax)
    ax.set_xlabel("Frequency / Hz")
    ax.set_ylabel("Characteristic strain")
    fig.tight_layout()
    save(fig, "gw_sensitivity")


if __name__ == "__main__":
    main()
