"""Characteristic-strain sensitivity curves of LISA, LIGO, ET, AION-km and AEDGE,
with black-hole merger tracks laid over them.

All five curves digitised from ``GW_exclusion_plot.svg`` into
``data/gw_sensitivity/`` (see each CSV's header for the shapes it came from),
drawn together on the source figure's axes, each region shaded down to its
curve and labelled beside it.

The merger tracks are computed, not digitised, for any total mass and
redshift in ``MERGERS``: the PhenomA inspiral-merger-ringdown amplitude of
Ajith et al., arXiv:0710.2335, orientation-averaged, as h_c = 2 f |h(f)|,
at the Planck 2018 luminosity distance, from ``TRACK_START`` before merger
to the ringdown cutoff. Dots mark the time left to merger (leading-order
chirp). With that recipe the nine tracks on the source figure (60, 1e4, 1e7
Msun at z = 0.1, 1, 10) are reproduced to within 0.003 dex.

    .venv/bin/python plot_scripts/gw_sensitivity.py

Writes ``figures/gw_sensitivity.png``.
"""

import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import to_hex, to_rgb
from matplotlib.lines import Line2D

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "animation_scripts"))
from style import (  # noqa: E402
    GW_DETECTOR_COLORS,
    GW_MERGER_FAR_COLOR,
    GW_MERGER_NEAR_COLOR,
    GW_MERGER_TIME_COLORS,
    GW_MERGER_Z_RANGE,
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

# name: (CSV stem, label position (f / Hz, h_c)).
DETECTORS = {
    "AEDGE": ("aedge", (1.5e-2, 1.5e-23)),
    "LISA": ("lisa", (2e-4, 1.2e-21)),
    "AION-km": ("aion_km", (2e2, 3e-19)),
    "ET": ("et", (1.2e2, 3e-24)),
    "LIGO": ("ligo", (1.8e1, 1.5e-21)),
}

# Merger tracks: (total mass / Msun, redshift, mass ratio m2/m1 <= 1). These
# are the source figure's nine.
MERGERS = [(M, z, 1) for M in (60, 1e4, 1e7) for z in (0.1, 1, 10)]

YEAR = 365.25 * 86400
TRACK_START = 10 * YEAR
TIME_MARKERS = {  # label: time left to merger / s
    "10 y": 10 * YEAR,
    "1 y": YEAR,
    "1 month": YEAR / 12,
    "1 day": 86400,
    "1 hour": 3600,
}

T_SUN = 4.925490947e-6  # G Msun / c^3, s
C_SI = 2.99792458e8
MPC = 3.0856775814913673e22
H0 = 67.66  # Planck 2018, km/s/Mpc
OMEGA_M = 0.30966


def luminosity_distance(z):
    """Luminosity distance in light-seconds, flat LambdaCDM."""
    x = np.linspace(0, z, 2001)
    comoving = np.trapezoid(1 / np.sqrt(OMEGA_M * (1 + x) ** 3 + 1 - OMEGA_M), x)
    return (1 + z) * comoving * MPC / (H0 * 1e3)


def symmetric_mass_ratio(q):
    return q / (1 + q) ** 2


def phenom_a_frequencies(M, z, eta):
    """PhenomA merger, ringdown, ringdown-width and cutoff frequencies / Hz,
    in the detector frame (redshifted mass)."""
    pi_M = np.pi * M * (1 + z) * T_SUN
    coefficients = {  # (a, b, c) of (a eta^2 + b eta + c) / (pi M)
        "merger": (2.9740e-1, 4.4810e-2, 9.5560e-2),
        "ringdown": (5.9411e-1, 8.9794e-2, 1.9111e-1),
        "width": (5.0801e-1, 7.7515e-2, 2.2369e-2),
        "cutoff": (8.4845e-1, 1.2848e-1, 2.7299e-1),
    }
    return {k: (a * eta**2 + b * eta + c) / pi_M for k, (a, b, c) in coefficients.items()}


def merger_strain(f, M, z, q=1):
    """Characteristic strain 2 f |h(f)| of a merger of total source-frame
    mass M / Msun at redshift z; NaN above the ringdown cutoff."""
    eta = symmetric_mass_ratio(q)
    fk = phenom_a_frequencies(M, z, eta)
    f1, f2, sigma = fk["merger"], fk["ringdown"], fk["width"]
    Mz = M * (1 + z) * T_SUN
    C = Mz ** (5 / 6) * f1 ** (-7 / 6) / (np.pi ** (2 / 3) * luminosity_distance(z))
    C *= np.sqrt(5 * eta / 24)
    lorentzian = sigma / (2 * np.pi) / ((f - f2) ** 2 + sigma**2 / 4)
    w = np.pi * sigma / 2 * (f2 / f1) ** (-2 / 3)
    shape = np.select(
        [f < f1, f < f2, f < fk["cutoff"]],
        [(f / f1) ** (-7 / 6), (f / f1) ** (-2 / 3), w * lorentzian],
        np.nan,
    )
    return 2 * f * C * shape


def frequency_before_merger(t, M, z, q=1):
    """Detector-frame GW frequency / Hz a time t / s before merger, from the
    leading-order chirp with the redshifted chirp mass."""
    chirp = symmetric_mass_ratio(q) ** (3 / 5) * M * (1 + z) * T_SUN
    return (5 / 256 / t) ** (3 / 8) * chirp ** (-5 / 8) / np.pi


def merger_track(M, z, q=1, t_start=TRACK_START, n=600):
    """(f, h_c) of a merger from t_start before it to the ringdown cutoff."""
    f_start = frequency_before_merger(t_start, M, z, q)
    f_end = phenom_a_frequencies(M, z, symmetric_mass_ratio(q))["cutoff"]
    f = np.geomspace(f_start, f_end * (1 - 1e-9), n)
    return f, merger_strain(f, M, z, q)


def merger_color(z):
    """White for a near source fading to grey with log redshift."""
    lo, hi = np.log10(GW_MERGER_Z_RANGE)
    s = np.clip((np.log10(z) - lo) / (hi - lo), 0, 1)
    near, far = np.array(to_rgb(GW_MERGER_NEAR_COLOR)), np.array(to_rgb(GW_MERGER_FAR_COLOR))
    return to_hex((1 - s) * near + s * far)


def mass_label(M):
    exponent = np.floor(np.log10(M))
    if M < 1e3:
        return rf"${M:g}\,M_\odot$"
    mantissa = M / 10**exponent
    lead = "" if np.isclose(mantissa, 1) else rf"{mantissa:g}\times"
    return rf"${lead}10^{{{exponent:.0f}}}\,M_\odot$"


def draw_merger(ax, M, z, q=1, label_mass=False):
    """Draw one merger track, dotted at the TIME_MARKERS it spans."""
    color = merger_color(z)
    f, h = merger_track(M, z, q)
    ax.plot(f, h, color=color, lw=1.4, zorder=3)
    for t, dot in zip(TIME_MARKERS.values(), GW_MERGER_TIME_COLORS):
        if t > TRACK_START:
            continue
        ft = frequency_before_merger(t, M, z, q)
        ax.plot(ft, merger_strain(ft, M, z, q), "o", ms=4, color=dot, mec="none", zorder=4)
    if label_mass:
        # Above the merger's peak, where the track turns over.
        merging = f >= phenom_a_frequencies(M, z, symmetric_mass_ratio(q))["merger"]
        peak = np.flatnonzero(merging)[np.nanargmax(h[merging])]
        ax.text(
            f[peak], h[peak] * 1.5, mass_label(M), color=PLOT_FOREGROUND,
            fontsize=TICK_SIZE, ha="center", va="bottom", zorder=5,
        )


def merger_legends(ax, redshifts):
    tracks = [
        Line2D([], [], color=merger_color(z), lw=1.4, label=f"$z = {z:g}$")
        for z in sorted(redshifts)
    ]
    dots = [
        Line2D([], [], ls="none", marker="o", ms=5, color=c, mec="none", label=t)
        for t, c in zip(TIME_MARKERS, GW_MERGER_TIME_COLORS)
    ]
    style = dict(frameon=False, labelcolor=PLOT_FOREGROUND, fontsize=TICK_SIZE - 2)
    first = ax.legend(handles=tracks, loc="lower left", **style)
    ax.add_artist(first)
    ax.legend(handles=dots, loc="lower left", bbox_to_anchor=(0.14, 0), handletextpad=0.1, **style)


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
        ax.text(
            *label_at, name, color=color, fontsize=LABEL_SIZE, ha="left", va="center"
        )
    # Each mass is labelled once, beside its nearest (loudest) track.
    nearest = {M: min(z for m, z, _ in MERGERS if m == M) for M, _, _ in MERGERS}
    for M, z, q in MERGERS:
        draw_merger(ax, M, z, q, label_mass=z == nearest[M])
    merger_legends(ax, {z for _, z, _ in MERGERS})
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
