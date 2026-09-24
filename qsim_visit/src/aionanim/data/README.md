# Data shipped with aionanim

Read through `aionanim.resources.data_path(...)`.

| Path | What | Source | Licence |
|---|---|---|---|
| `dai_fringes/{lln,hln}.csv` | Shot-by-shot excitation fractions of the AION prototype differential atom interferometer, low and high laser noise | C. Baynham et al., arXiv:2504.09158; data at doi:10.5281/zenodo.19592552, extracted by `data_scripts/process_dai_fringes.py` | CC BY 4.0 |
| `dai_fringes/adev.csv` | Allan deviation of the DAI differential phase for both runs, with the Monte Carlo SQL band (Fig. 4c) | Same paper and record: the `allan_deviation` sheet of `figures/Figure_4_data.xlsx`, extracted by `data_scripts/process_dai_adev.py` | CC BY 4.0 |
| `dai_fringes/signals.csv` | Likelihood of a fitted sinusoid against trial frequency for seven phases imprinted by a light shift (0.1–100 mHz), over each drive's periodogram (Fig. 5a) | Same paper and record: `signal_fitting_results_by_frequency.csv` and `precomputed_true_signals/`, reduced as `figures/Figure 5a.ipynb` does by `data_scripts/process_dai_signals.py` | CC BY 4.0 |
| `gw_sensitivity/*.csv` | Characteristic-strain sensitivity curves of LIGO, LISA, ET, AION-km, AEDGE, AEDGE+ | Digitised from `GW_exclusion_plot.svg` (see each CSV's header for the exact path and calibration) | Belongs to the owner of the source figure: check before redistributing |
| `images/ligo20160211a.jpg` | GW150914 as observed by LIGO Hanford and Livingston | LIGO press release, 11 Feb 2016 | Credit Caltech/MIT/LIGO Laboratory |
| `videos/midway_imaging_b059528_slow.mp4` | Side-on imaging of the Sr cloud from the broadband red MOT through loading the upper then the lower dipole trap; 48 snapshots, t = 10–599 ms, each held for 4 frames at 10 fps | AION prototype imaging, supplied by T. Walker (the `b059528` in the name is the commit that made it) | Unpublished: check with the owner before redistributing |
