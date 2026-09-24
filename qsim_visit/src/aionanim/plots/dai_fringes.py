"""Excitation-fraction fringes and the Lissajous ellipse from the AION DAI data.

Recreates Fig. 4a-c of Baynham et al., arXiv:2504.09158, in the house
palette, from the shots ``data_scripts/process_dai_fringes.py`` and the Allan
deviations ``data_scripts/process_dai_adev.py`` extracted into the package
data:

- ``fringes_figure``: each interferometer's excitation against the clock
  laser phase step, quiet laser above and noisy laser below. Noise on the
  laser washes the single-interferometer fringes out completely.
- ``lissajous_figure``: upper against lower excitation, shot by shot. The
  noise is common to both, so it only slides each shot along one ellipse,
  whose shape still holds the differential phase. Given one run instead of
  both, it draws the same axes with just that run, for building it up.
- ``adev_figure``: the Allan deviation of the differential phase read off
  each run's ellipse, against averaging time. Both runs average down along
  the standard quantum limit, so the laser noise has cancelled.

Both return matplotlib Figures; saving them is the caller's business.
"""

import csv

import matplotlib.pyplot as plt
from matplotlib.collections import PathCollection
import numpy as np

from aionanim.resources import data_path
from aionanim.style import (
    LOWER_CLOUD_COLOR,
    PLOT_BACKGROUND,
    PLOT_FOREGROUND,
    SQL_BAND_OPACITIES,
    SQL_COLOR,
    UPPER_CLOUD_COLOR,
)

DATA_DIR = data_path("dai_fringes")

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


def load_adev():
    return load("adev")


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


def legend(ax, markerscale=3, **kwargs):
    leg = ax.legend(
        frameon=False, labelcolor=PLOT_FOREGROUND, fontsize=TICK_SIZE,
        handletextpad=0.1, markerscale=markerscale, **kwargs,
    )
    # See-through shots get solid keys; shaded bands keep their shade.
    for handle in leg.legend_handles:
        if isinstance(handle, PathCollection):
            handle.set_alpha(1)


def fringes_figure(lln, hln):
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
    return fig


def lissajous_figure(runs):
    """Upper against lower excitation; runs is a list of (data, color, label)."""
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
    return fig


def adev_figure(adev, runs):
    """Allan deviation against averaging time; runs is a list of (key, color, label).

    The key picks a run's columns ("lln" or "hln"). The SQL is always drawn,
    so an empty list gives the bare limit to build up from.
    """
    fig, ax = plt.subplots(figsize=(6.4, 5.4))
    fig.set_facecolor(PLOT_BACKGROUND)
    tau = adev["mc_tau_s"]
    color = hexed(SQL_COLOR)
    for ci, opacity in zip(("68", "95"), SQL_BAND_OPACITIES):
        ax.fill_between(
            tau, adev[f"mc_{ci}ci_lower_mrad"], adev[f"mc_{ci}ci_upper_mrad"],
            color=color, alpha=opacity, lw=0, label=f"SQL, {ci}%",
        )
    ax.plot(
        tau, adev["sql_scaling_mrad"], ":", color=PLOT_FOREGROUND, lw=1.5,
        label=r"SQL $\propto 1/\sqrt{\tau}$",
    )
    for key, run_color, label in runs:
        ax.errorbar(
            adev["tau_s"], adev[f"adev_{key}_mrad"],
            yerr=[adev[f"adev_{key}_err_neg_mrad"], adev[f"adev_{key}_err_pos_mrad"]],
            ls="none", marker="o", ms=6, capsize=0, elinewidth=1.5,
            color=hexed(run_color), label=label,
        )
    ax.set_xscale("log")
    ax.set_yscale("log")
    # The paper's limits, fixed so the build-up steps share one set of axes.
    ax.set_xlim(7e2, 7e4)
    ax.set_ylim(0.1, 5)
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda y, _: f"{y:g}"))
    ax.yaxis.set_minor_formatter(plt.NullFormatter())
    dark_axes(ax)
    ax.set_xlabel("Measurement time / s")
    ax.set_ylabel(r"Allan deviation of $\delta\phi$ / mrad")
    legend(ax, loc="lower left", markerscale=1)
    fig.tight_layout()
    return fig
