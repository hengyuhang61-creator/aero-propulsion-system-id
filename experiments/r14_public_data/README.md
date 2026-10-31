# R14 — Public experimental data, eligibility audit and low-order modelling

Round 14 of the aero-propulsion system-identification programme. Everything here
runs against **publicly downloadable** experimental data; no raw data are
committed to this repository.

**Status: PARTIAL_DELIVERED.** Data access and modelling are complete. Video
tracking is blocked (CDN throughput) and CFD was not executed (3-D geometry
assumptions). No dynamic identification was possible.

Read `docs/R14_FINAL_REPORT.md` first.

## What is here

| Path | Contents |
|---|---|
| `docs/02_DATA_ELIGIBILITY_AUDIT.md` | what was actually downloaded, what each dataset may and may not support |
| `docs/03_RESEARCH_PROTOCOL.md` | pre-registered validation design and stop conditions |
| `docs/05_SBLI205_ROM_REPORT.md` | shock-crossing-point regression + POD results |
| `docs/06_HMVE_CROSS_VALIDATION.md` | cross-experiment comparison contract |
| `docs/04_BUSEMANN_VIDEO_TRACKING.md` | blocked video acquisition, delivered pipeline |
| `docs/07_CFD_COMPARISON.md` | frozen CFD case set and geometry status (not executed) |
| `docs/08_LIMITATIONS.md` | the ten statements this round cannot make |
| `src/` | all analysis code |
| `tests/` | 9 assertions (5 data/model, 4 synthetic video code-path) |
| `results/` | every number in the reports, as CSV/JSON |
| `figures/` | four report figures |

## Reproducing

Raw data are **not** in the repo. Download them first:

| File | URL |
|---|---|
| `UQ_experiment.zip` | `https://www.nasa.gov/wp-content/uploads/2025/10/uq-experiment.zip` |
| `HMVE2_PIVprofiles.zip` | `https://ntrs.nasa.gov/api/citations/20250008885/downloads/HMVE2_PIVprofiles.zip` |
| `Campo_thesis.pdf` | `https://tmbwg.github.io/turbmodels/Other_exp_Data/SBLI2.05/Campo_thesis.pdf` |
| `README_UQ.pdf` | `https://tmbwg.github.io/turbmodels/Other_exp_Data/SBLI2.05/README_UQ.pdf` |
| `data.Mach46.txt` | `https://www.grc.nasa.gov/www/wind/valid/transdif/transdif01/data.Mach46.txt` |

Verify against `docs/01_DATA_CATALOG.csv` (SHA256 per file), then:

```bash
export R14_ROOT=/path/to/r14_workdir      # defaults to the author's local path
python src/sbli205_io.py
python src/sbli205_model.py
python src/sbli205_pod.py
python src/hmve_analysis.py
python src/export_artifacts.py
python src/make_figures.py
python tests/test_r14.py
python tests/test_video_code_path.py
```

Requires `numpy scipy matplotlib scikit-learn pypdf pymupdf opencv-python-headless pandas`,
plus `ffmpeg`/`ffprobe` for the video tooling.

## Headline numbers

| Quantity | Result |
|---|---|
| Leave-one-position-out, Δx_scp | RMSE 0.65 mm (12.7% of the 5.12 mm signal span) |
| Leave-one-height-out, Δx_scp | RMSE 0.44 mm |
| Boundary extrapolation penalty | 2–2.5× the interior error |
| POD + GP, streamwise velocity | 16.0 m/s RMSE (−13.5% vs nearest case) |
| POD + GP, wall-normal velocity | 7.00 m/s RMSE (**worse** than the nearest-case baseline) |

## Three data caveats that will bite anyone reusing this

1. The ASCII `dataSummary` header lists `x_bump` before `h_bump`; the values are
   the other way round (verified against `dataMatlab_caseN.mat` and README Table 1).
2. The per-case X grids are translated by up to 2.04 mm between `x_bump` groups,
   contradicting the README coordinate definition. Field comparisons must state
   the alignment choice; index alignment correlates better with the physical
   perturbation (r = 0.93 vs 0.73).
3. `data.Mach46.txt` is a **M ≈ 0.46 transonic** Sajben diffuser, not Mach 4.6.
