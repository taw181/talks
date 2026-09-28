"""AION's reach for ultralight scalar dark matter coupled to photons, as numbers.

The curves of Badurina et al., JCAP 05 (2020) 011 (arXiv:1911.11755), Fig. 3
middle panel -- the photon coupling |d_e| each scenario reaches at SNR 1 in
1e8 s, against the scalar's mass m_phi -- and the lower edge of the region
already excluded, read off the PDF's vector paths into
aionanim/data/uldm_sensitivity/ by data_scripts/digitise_uldm_sensitivity.py.

Masses are in eV; a field of mass m oscillates at f = m c^2 / h.
"""

import numpy as np

from aionanim.resources import data_path

DATA_DIR = data_path("uldm_sensitivity")

H_EV = 4.135668e-15  # Planck's constant, eV s

# stem: label, strongest reach last so it is drawn on top. The solid curves
# only: the paper's dotted continuations (0.1-0.3 Hz) are left out.
ULDM_SCENARIOS = {
    "aion10_initial": "AION-10 (initial)",
    "aion10_goal": "AION-10 (goal)",
    "aion100_initial": "AION-100 (initial)",
    "aion100_goal": "AION-100 (goal)",
    "aedge": "AEDGE",
    "aion_km": "AION-km",
}
EXCLUDED = "excluded"  # the grey region's lower edge

# The half interrogation time the paper assumes for AION-10 and AION-100
# (Table 1 and the text under it): a 10 m launch-mode interferometer.
AION10_T = 1.4  # s


def load_uldm_sensitivity(stem):
    """(m_phi / eV, |d_e|) arrays from aionanim/data/uldm_sensitivity/<stem>.csv."""
    with open(DATA_DIR / f"{stem}.csv") as f:
        rows = [line for line in f if not line.startswith(("#", "m_eV"))]
    m, d = np.loadtxt(rows, delimiter=",").T
    return m, d


def mass_from_frequency(f):
    """m_phi / eV of a field oscillating at f / Hz."""
    return H_EV * f


def frequency_from_mass(m):
    """f / Hz of a field of mass m / eV."""
    return m / H_EV


def coupling_at(stem, mass):
    """|d_e| on a curve at `mass` / eV, linear in log-log; nan off its ends."""
    m, d = load_uldm_sensitivity(stem)
    x = np.log10(mass)
    if not m[0] <= mass <= m[-1]:
        return np.nan
    return 10 ** np.interp(x, np.log10(m), np.log10(d))
