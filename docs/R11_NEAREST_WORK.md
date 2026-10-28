# R11: nearest work and one research question

This supplements, rather than erases, the historical matrix in [EVIDENCE](EVIDENCE.md). Publication metadata and the reading scope below are distinct from reproduced results.

| Work | Closest method/result and overlap | R11 evidence limit |
|---|---|---|
| [NASA Sajben Study #3](https://www.grc.nasa.gov/www/wind/valid/transdif/transdif03/transdif03.html) | WIND versions/SA/SST, wall pressure and velocity. Independent numerical reference for current geometry. | Page, inputs, native total conditions, CFPOST commands and numeric pressure curves checked. Conditional same-position comparison executed; no whole-field certification. |
| [NASA Study #5](https://www.grc.nasa.gov/www/wind/valid/transdif/transdif05/transdif05.html) | Extended outlet changes strong separated-flow prediction; pressure must change to preserve old-plane loading. | Page/input/list/postprocessing checked. ADF/CFF field reconstruction blocked after two targeted routes. Published reattachment retained as reported, not recomputed. |
| [Hosder et al. (2006)](https://doi.org/10.1016/j.compfluid.2005.04.006) | Relative grid/turbulence/geometry/outlet uncertainty in GASP. Physical exit14.44H and suction complicate 2D equivalence. | Author manuscript relevant Methods/Results read; pages8/9/20 visually checked. Not a wall-pressure ROM benchmark or independent reproduction. |
| [Schram & Narayanaswamy (2026)](https://doi.org/10.1007/s00348-026-04215-0) | Independently driven unstart, PSP shock locator, angle/input-transience effects. | Full text/data statement checked; numeric records not public at inspected links. Input calibration ambiguity remains. |
| [Bustard et al. (2024)](https://doi.org/10.1007/s00348-024-03836-7) | Global PSP, shock tracking/coherence/conditional pressure correlations in OIWPS inlet. | Methods/data availability screened. No numeric arrays acquired; different geometry and no controlled jet excitation in this study. |
| [Johnson & Narayanaswamy (2026)](https://doi.org/10.1007/s00348-025-04156-0) | Jet removal, 10kHz restart shock/pressure dynamics. | Full-text availability screen; contradictory data statement. No raw-data or method reproduction. |

One concrete question is frozen in [R11_ALGORITHM_ELIGIBILITY](R11_ALGORITHM_ELIGIBILITY.md): whether POD coefficient interpolation improves pressure and shock prediction over direct interpolation on whole held-out Sajben conditions at equal sample budget. The literature already contains shock localization, steady reconstruction and surrogate modeling. **Novelty remains UNKNOWN.** The immediate experiment is original-file qualification, not building another algorithm platform.
