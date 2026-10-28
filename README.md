# Aero Propulsion System ID

A small reproducible study of **NASA Sajben steady wall-pressure response** and unresolved CFD convergence. This is exploratory internal-flow research, not a validated propulsion model or a general research platform.

| Result | Status |
|---|---|
| R08 two-condition experimental pressure contrast | Recomputed; bottom shock estimator shift **+0.8585 H**, top **+0.7665 H** |
| R09 CFL diagnostic | **SCIENTIFIC_HOLD**; both 200-iteration branches fail conservation thresholds |
| R10 single flux-scheme experiment | **Negative result**; Roe-FDS did not meet the frozen improvement criterion and triggered the 10% mass-gap stop |
| R11 reference and closed-field audit | NASA numeric reference comparison executed; local mass accounting closes, but R09/R10 conservation fails and full energy is unavailable |
| R11 data / solver decision | 31-setting VT files not obtained; recent dynamic records not downloadable as numeric series; **NO_NEW_CFD_JUSTIFIED / BLOCKED_BY_DATA** |
| Aerospace dynamic identification | **HOLD**: no qualified independently excited time series |
| Xu paper reproduction / innovation | **Not established / UNKNOWN** |

## Run the reproducible calculation

Requires Python 3.12 or 3.13. Pressure calculations and synthetic tests use only the standard library; the optional R11 closed-HDF reader additionally requires NumPy/h5py. Synthetic tests require no network, NASA data, Fluent, NumPy, or training.

```bash
git clone https://github.com/hengyuhang61-creator/aero-propulsion-system-id.git
cd aero-propulsion-system-id
python -m unittest discover -s experiments/sajben_study2/tests -v
python -m unittest discover -s cfd/tests -v
```

Obtain the two pressure files using the [data instructions](data/README.md), then supply their paths. The output directory must be new.

```bash
python experiments/sajben_study2/compare_steady.py --weak /path/to/sajwpres.data --strong /path/to/sajspres.data --out results/r08 --verify-frozen
```

On Windows, pass quoted Windows paths. The script writes `experiment_result.json` and `contrast_points.csv`. It never edits its inputs. `--verify-frozen` checks exact input SHA-256 values and both known shock shifts. [Expected aggregates](experiments/sajben_study2/expected_summary.json) include all wall/zone metrics; the local acceptance compared all metrics and all 121 CSV records with the preserved R08 outputs.

## What is computed

The two cases have nominal exit/inlet-total pressure ratios 0.82 and 0.72. Strong-case pressures are linearly interpolated at weak-case stations within common spatial coverage. Adjacent repeated stations with agreeing pressure (absolute tolerance 1e-12) are collapsed separately for each wall; conflicting duplicates and unsorted stations are rejected. No extrapolation is performed.

The shock estimator is the midpoint of the largest positive adjacent pressure-gradient interval whose midpoint lies in [0,4] H; equal gradients select the rightmost interval. Its interval reflects station spacing, **not a statistical confidence interval**. Fixed predictions are unchanged weak pressure and weak pressure minus 0.10. RMSE/MAE describe these two no-fit baselines; they do not validate a learned surrogate. Spatial zones overlap and are not independent samples. The permissive 0 < p/p0 < 1.1 parser bound is a sanity check, not a physical acceptance theorem.

Two steady operating conditions are not replicate experiments. Steady pseudo-time iteration histories are not physical-time training data.

## Evidence and scope

- [R01–R11 status and history](docs/STATUS.md)
- [Three-stage roadmap and stopping gates](docs/ROADMAP.md)
- [Sources, upstream audit, and ownership](docs/EVIDENCE.md)
- [R09 numerical audit](cfd/R09_DIAGNOSTIC.md) and [machine summary](cfd/r09_summary.json)
- [R10 bounded negative experiment](cfd/R10_FLUX_TEST.md) and [machine summary](cfd/r10_summary.json)
- [R11 independent reference physics](docs/R11_REFERENCE_PHYSICS_AUDIT.md) and [mass/energy audit](docs/R11_LOCAL_MASS_ENERGY_AUDIT.md)
- [R11 data eligibility](docs/R11_DATA_ELIGIBILITY.md), [CFD decision](docs/R11_CFD_DECISION.md), [algorithm eligibility](docs/R11_ALGORITHM_ELIGIBILITY.md), and [nearest work](docs/R11_NEAREST_WORK.md)
- [Reproduce the R11 offline analysis](docs/R11_REPRODUCE.md)

Owners of the completed native R09 logs can independently recompute them:

```bash
python cfd/audit_r09.py --root /path/to/completed-r09 --out r09-audit.json
```

The raw proprietary CFD assets and sensitive logs remain private, so this repository does **not** claim a publicly executable Fluent case. Public reproducibility covers the standard-library pressure algorithm, synthetic parser tests, and published diagnostic arithmetic. Full native CFD verification requires the preserved local assets and a licensed simulator.

## License and citation

[MIT](LICENSE) covers original code, synthetic tests, and original documentation only. NASA experimental data, MDCHAMP code, papers, and proprietary simulator files retain their separate rights and are not bundled. See [CITATION.cff](CITATION.cff) and cite the original experimental and methodological sources separately.
