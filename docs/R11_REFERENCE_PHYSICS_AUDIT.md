# R11: independent reference physics audit

Date: 2026-10-28 (Europe/Moscow). Baseline: `242d05249705b5995ee61a8599f654fa9e53b765`.

**Result: the local numerical obstruction is real, but its unique cause remains UNKNOWN.** An independent NASA numerical wall-pressure comparison is now reproducible. The available local weak-shock snapshots do not show the downstream separation that motivated NASA Study #5's extension. No new Fluent run is justified by that analogy alone. Scientific HOLD remains.

## Reference conditions and actual source checks

| Source | Conditions, geometry and method | Comparability |
|---|---|---|
| [Study #2](https://www.grc.nasa.gov/www/wind/valid/transdif/transdif02/transdif02.html), actual `sajben.dat` | 81 x 51 points; p0=19.58 psia in input, T0=500 R; weak outlet=16.05 psia, strong=14.10. Laminar low-pressure startup, SST then Chien k-epsilon. CFL=1. | Local R03 follows its weak input and refines its mesh. The page's 19.50 psia table and statement about increasing pressure to obtain the strong case conflict with the input/table values. |
| [Study #3](https://www.grc.nasa.gov/www/wind/valid/transdif/transdif03/transdif03.html), `run.5sst.dat`, `run.5sst.lis`, GENPLOT and CFPOST files | Same nominal 81 x 51 geometry; SA/SST and WIND-version comparison. Input M=0.46, static p=16.937 psia, static T=504.26 R. The native list explicitly reports p0=19.581 psia and T0=525.600 R; outlet=16.055 psia. CFL=1.5; monitors include mass, recovery and velocity profile. | **525.6 R is a fourth temperature, not 500 or 540 R.** Do not misread static temperature as total temperature. This is the independent numerical reference used below. |
| [Study #4](https://www.grc.nasa.gov/www/wind/valid/transdif/transdif04/transdif04.html), both input/list files | Strong case; p0=19.5 psia, T0=500 R, exit=14.1 psia. 81 x 51 x 2 extruded grid, 2-inch depth, SA, modified Rusanov; manual smoothing versus automatic load convergence. | Solver/topology/depth and strong-shock regime differ. Native completion is not a newly audited complete conservation balance. |
| [Study #5](https://www.grc.nasa.gov/www/wind/valid/transdif/transdif05/transdif05.html), structured/unstructured SST inputs, postprocessing and list files | Strong case; p0=19.58 psia, T0=540 R. Structured 81 x 51, extruded and mixed unstructured variants. A 10H constant-area extension moves the exit from 8.65H to 18.65H. Actual extended input sets 14.7745 psia, rounded to 14.775 on the page. | Original-plane target remains 14.1 psia. This is not the local weak case. Extension, discretization/limiter and solver versions are not all held constant across the published cases. |

500 R=277.7778 K; 540 R=300 K; 525.6003 R=292.0002 K. The experimental weak-pressure file explicitly says T0=300 K, p0/p_atm=1.195 and nominal p_exit/p0=0.82. Local p0=134999.348 Pa, p_exit=110660.855 Pa, so its exact ratio is 16.05/19.58=0.819714. Operating pressure is zero: local gauge and absolute static pressures coincide. Study #3's exact ratio is approximately 0.819917. The 19.50/19.58 psia difference is about 0.41%; nominal labels do not remove it.

Changing total temperature changes density, velocity and Reynolds number when pressure, geometry and transport laws are held. Normalizing p by each case's own p0 does not establish Reynolds similarity. Mach 0.9 in a uniform initial/freestream specification is not a measurement of the eventual local inlet Mach profile. Local 2D reference depth is 1 m; NASA extruded depths and physical span are different, so their total kg/s must not be directly compared.

## Why extension can matter, and what it does not prove here

Study #5 reports experimental reattachment near 6.4H, structured results near 7.5H, and separation reaching the original outlet in the mixed-unstructured cases. Its extension permits reattachment near 7.4H and attached flow at the new boundary. The extension changes displacement thickness and the pressure relation between the old measurement plane and the new boundary; copying the old pressure to the new exit changes the physical loading. These are reported results, not an independently recomputed Study #5 field.

[Hosder et al., Computers & Fluids (2006)](https://doi.org/10.1016/j.compfluid.2005.04.006), checked in the [author-hosted manuscript](https://archive.aoe.vt.edu/shosder/main/caf_revised/caf_revised.pdf), further distinguishes nominal 8.65H and experimental physical exit 14.44H. Its corresponding measured physical-exit ratios are 0.8368 (weak) and 0.7468 (strong). It discusses as-built wall geometry and suction slots at 9.8H. Thus neither a plain 10H extension nor a plain 14.44H duct automatically reproduces the experiment. The paper compares uncertainty sources, explicitly not a validation study; its extension sensitivity is prior art, not a new R11 discovery.

Local R03/R09/R10 end at 8.6500003H with the same nominal wall shape, a pressure outlet and adiabatic stationary walls. R03 best is 4,000 cells; R09/R10 use 16,000 cells derived by refinement. They do not match Study #5's unstructured geometry/algorithm or represent the experimental downstream suction and spanwise structure.

## New minimum physical comparison

Read the public **numerical** `p.bot.5sst.gen` and `p.top.5sst.gen`, the existing **experimental** `sajwpres.data`, and closed local **unqualified Fluent** wall fields. No image digitization and no R08/R09 simulation or contrast experiment was repeated.

The GENPLOT header count (80 stations per wall) is checked. CFPOST commands establish bottom `j=1`, top `j=last` and x scale 22.7273 m^-1; this resolves the Study #3 webpage's swapped table-link ordering. Convert exported x to common x/H using H=0.04399788 m. Compare piecewise-linear pressure at the same experimental stations, only within the intersection of all curve coverage; 34 bottom and 35 top points. No extrapolation, spatial train/test split or fitted model is involved. Pressure is each case's wall static p/inlet p0. Shock estimates use the existing frozen maximum-positive-gradient midpoint definition in [0,4]H.

| Case | Bottom MAE / RMSE | Top MAE / RMSE | Bottom / top shock difference from experiment, H |
|---|---|---|---|
| NASA WIND5 SST numerical | 0.006859 / 0.009817 | 0.009331 / 0.015571 | -0.03620 / +0.10180 |
| R03 `order2_14000`, unqualified | 0.007481 / 0.010538 | 0.009588 / 0.016885 | +0.00305 / +0.14105 |
| R09 CFL0.5 endpoint, unqualified | 0.016447 / 0.021291 | 0.021569 / 0.030506 | +0.00306 / -0.01604 |
| R09 CFL0.1 endpoint, unqualified | 0.015856 / 0.019718 | 0.020504 / 0.030420 | +0.00306 / -0.01604 |

R03 and NASA are substantially smoother downstream than R09. This is a new comparison at different sample locations from R03's old node-export comparison, so its MAE is not a correction or reproduction of the old MAE. Eight independent NumPy interpolation/metric checks give maximum discrepancy <1e-14. Sampling intervals are retained in the JSON and are not statistical confidence intervals. The R03 thresholds are not enough by themselves: pressure agreement cannot override failed numerical qualification, thermal mismatch or unresolved grid uncertainty.

Reproduce with `experiments/sajben_study2/compare_reference.py`; source hashes, aggregate metrics and conditions are in [r11_reference_summary.json](../cfd/r11_reference_summary.json). Local delivery additionally includes the complete point table and figure. Raw third-party values are not mirrored in the repository.

## Source format and access limits

Study #5 `sajben.tar` returned HTTP404. Individual inputs, lists, grid and extended solution downloaded successfully. Binary headers identify **ADF Database Version A02011**, NASA Common File Format, not HDF5. Two bounded routes were checked: (1) installed CFPOST/CFF conversion or Tecplot loader availability; no usable command was found, so no binary converter was developed; (2) exact text-export names from the supplied postprocessing script. `presst.lis`, `pressb.lis`, `yufive`, `yueight` returned 404. Its extended postprocessing file only exports CFL history. No Study #5 full-field pressure/reattachment reconstruction is claimed. Study #3's directly readable numeric exports satisfy the minimum comparison without this dependency.

The whole pages were read; input files were read; list setup and termination sections were inspected, and Study #3 total temperature was confirmed in its log. NASA's convergence claims were not independently certified from every residual and flux. Source retrieval evidence, bytes, hashes and failures are retained in the local manifest.
