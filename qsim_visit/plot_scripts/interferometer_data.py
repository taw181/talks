"""Excitation-fraction fringes and the Lissajous ellipse from the AION DAI data.

Recreates Fig. 4a,b of Baynham et al., arXiv:2504.09158, in the talk's
palette, from the shots ``data_scripts/process_dai_fringes.py`` extracted:

- ``excitation_fringes``: each interferometer's excitation against the clock
  laser phase step, quiet laser above and noisy laser below. Noise on the
  laser washes the single-interferometer fringes out completely.
- ``lissajous``: upper against lower excitation, shot by shot. The noise is
  common to both, so it only slides each shot along one ellipse, whose shape
  still holds the differential phase. ``lissajous_lln`` / ``lissajous_hln``
  are the same axes with one run each, for building it up on a slide.

    .venv/bin/python plot_scripts/interferometer_data.py

Writes PNGs to ``figures/``.
"""

import csv
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "animation_scripts"))
from aionanim.resources import data_path  # noqa: E402
from aionanim.style import (  # noqa: E402
    HLN_COLOR,
    LLN_COLOR,
    LOWER_CLOUD_COLOR,
    PLOT_BACKGROUND,
    PLOT_FOREGROUND,
    UPPER_CLOUD_COLOR,
)

DATA_DIR = data_path("dai_fringes")
OUT_DIR = ROOT / "figures"

# As many shots as the paper plots: more just fills the fringe panels in.
FRINGE_SHOTS = 3000
LISSAJOUS_SHOTS = 2000
# The two runs are drawn in alternating chunks so that neither ellipse sits
# wholly on top of the other.
LISSAJOUS_CHUNK = LISSAJOUS_SHOTS // 10

LABEL_SIZE = 15
TICK_SIZE = 13


def hexed(color):
    return color if isinstance(color, str) else color.to_hex()


def load(run):
    with open(DATA_DIR / f"{run}.csv") as f:
        rows = list(csv.DictReader(line for line in f if not line.startswith("#")))
    return {k: np.array([float(r[k]) for r in rows]) for k in rows[0]}


def dark_axes(ax):
    ax.set_facecolor(PLOT_BACKGROUND)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    for side in ("left", "bottom"):
        ax.spines[side].set_color(PLOT_FOREGROUND)
    ax.tick_params(colors=PLOT_FOREGROUND, labelsize=TICK_SIZE)
    ax.xaxis.label.set_color(PLOT_FOREGROUND)
    ax.yaxis.label.set_color(PLOT_FOREGROUND)
    ax.xaxis.label.set_size(LABEL_SIZE)
    ax.yaxis.label.set_size(LABEL_SIZE)


def legend(ax, **kwargs):
    leg = ax.legend(
        frameon=False, labelcolor=PLOT_FOREGROUND, fontsize=TICK_SIZE,
        handletextpad=0.1, markerscale=3, **kwargs,
    )
    for handle in leg.legend_handles:
        handle.set_alpha(1)


def save(fig, name):
    OUT_DIR.mkdir(exist_ok=True)
    fig.savefig(OUT_DIR / f"{name}.png", dpi=200, facecolor=PLOT_BACKGROUND)
    plt.close(fig)
    print(f"wrote figures/{name}.png")


def fringes(lln, hln):
    fig, axes = plt.subplots(2, 1, figsize=(6.4, 5.4), sharex=True)
    fig.set_facecolor(PLOT_BACKGROUND)
    for ax, run, title in zip(axes, (lln, hln), ("Low laser noise", "High laser noise")):
        n = slice(FRINGE_SHOTS)
        for key, color, label in (
            ("excitation_bottom", LOWER_CLOUD_COLOR, "Lower"),
            ("excitation_top", UPPER_CLOUD_COLOR, "Upper"),
        ):
            ax.scatter(
                run["phi_rad"][n], 100 * run[key][n], s=6, marker=".",
                color=hexed(color), alpha=0.35, edgecolors="none", label=label,
            )
        dark_axes(ax)
        ax.set_ylim(0, 100)
        ax.set_xlim(0, 2 * np.pi)
        ax.set_ylabel("Excitation / %")
        ax.set_title(title, color=PLOT_FOREGROUND, fontsize=LABEL_SIZE, loc="left")
    legend(axes[0], loc="upper right", bbox_to_anchor=(1.0, 1.25), ncols=2)
    axes[1].set_xticks([0, np.pi, 2 * np.pi], ["0", r"$\pi$", r"$2\pi$"])
    axes[1].set_xlabel("Clock laser phase step / rad")
    fig.tight_layout()
    save(fig, "excitation_fringes")


def lissajous(runs, name):
    fig, ax = plt.subplots(figsize=(5.4, 5.4))
    fig.set_facecolor(PLOT_BACKGROUND)
    labelled = set()
    for start in range(0, LISSAJOUS_SHOTS, LISSAJOUS_CHUNK):
        n = slice(start, start + LISSAJOUS_CHUNK)
        for run, color, label in runs:
            ax.scatter(
                100 * run["excitation_bottom"][n], 100 * run["excitation_top"][n],
                s=6, marker=".", color=hexed(color), edgecolors="none",
                label=None if label in labelled else label,
            )
            labelled.add(label)
    dark_axes(ax)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.set_aspect("equal")
    ax.set_xlabel("Lower interferometer excitation / %")
    ax.set_ylabel("Upper interferometer excitation / %")
    legend(ax, loc="upper left")
    fig.tight_layout()
    save(fig, name)


def main():
    lln, hln = load("lln"), load("hln")
    fringes(lln, hln)
    quiet = (lln, LLN_COLOR, "Low laser noise")
    noisy = (hln, HLN_COLOR, "High laser noise")
    lissajous([quiet, noisy], "lissajous")
    lissajous([quiet], "lissajous_lln")
    lissajous([noisy], "lissajous_hln")


if __name__ == "__main__":
    main()
