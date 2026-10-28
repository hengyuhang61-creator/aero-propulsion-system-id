# Evidence, reading scope, and ownership

Audit date: 2026-10-28. Links identify sources; a citation alone does not mean its full text or code was audited.

## Official physical sources

| Source | What was checked in this takeover |
|---|---|
| [NASA Sajben main page](https://www.grc.nasa.gov/WWW/wind/valid/transdif/transdif.html) | Geometry, units, boundary-condition table, study index and experimental references |
| [NASA Study #2](https://www.grc.nasa.gov/WWW/wind/valid/transdif/transdif02/transdif02.html) | Weak/strong ratios, 81x51 grid, WIND/NPARC and SST/Chien comparisons, numerical strategy and raw-file links; existing local raw files were hashed, not downloaded |
| [NASA Study #3](https://www.grc.nasa.gov/WWW/wind/valid/transdif/transdif03/transdif03.html) | WIND-version and SA/SST comparison; wall resolution and local-time convergence observables. Its conditions are not silently substituted for Study #2 |
| [NASA Study #4](https://www.grc.nasa.gov/WWW/wind/valid/transdif/transdif04/transdif04.html) | Extruded unstructured grid, strong-case boundary conditions, modified Rusanov and load-convergence strategy. This is contextual evidence, not a matched local control |
| Qian & Agarwal (2025), [High Fidelity CFD Verification Workshop 2024 Test Case: Transonic Turbulent Flow in Sajben Diffuser](https://doi.org/10.2514/6.2025-2403) | Bibliography and abstract verified via [author institution](https://profiles.wustl.edu/en/publications/high-fidelity-cfd-verification-workshop-2024-test-case-transonic-/): WA/SA/SST comparison and downstream-pressure limitations. Full numerical setup and tables not obtained or independently replicated |

Source inconsistencies in pressure, temperature, unit systems and the direction of backpressure change are retained in [data provenance](../data/README.md). R08 estimates are derived from time-averaged measurements; the experiments have sidewall/corner suction and do not establish exact equivalence to a plain 2D CFD model.

## Actual GitHub/source audit

Repository: [MDCHAMP/nonlinear_baselines](https://github.com/MDCHAMP/nonlinear_baselines), pinned commit `d9c4972f6bd59cfdde23a014bc57579e2af957aa`.

- Queried repository metadata, complete recursive tree, current main ref, all-state Issues (100-item page returned one issue), its comment thread, Releases (one release), and the release tag ref. Both `main` and `DCE_paper` resolve to the pinned commit.
- Read README; `run_baselines.py`; `trainers.py` with focused inspection of `GPNARX_trainer`; `models.py` scaling, lag scan, free-running prediction and scoring functions; `dataload.py` including Silverbox split; `src/metrics.py`; and `src/jacks/opt.py`. Fifteen locally retained source files were checked against fresh remote Git blob hashes. Hash equality is provenance verification, not a complete code audit.
- [Issue #1](https://github.com/MDCHAMP/nonlinear_baselines/issues/1) is closed and concerns version-dependent reproduction. The maintainer's [reply](https://github.com/MDCHAMP/nonlinear_baselines/issues/1#issuecomment-3472279356) describes approximate historical dependency versions and possible code/publication drift. This corrects R08's overly broad statement that the repository had no recorded issues.
- [DCE_paper release](https://github.com/MDCHAMP/nonlinear_baselines/releases/tag/DCE_paper) was checked; it has no attached binary assets. No license file was found in the complete tree and GitHub license metadata is null. This is not permission to redistribute its code.
- Not audited: every neural-network path, every dataset/model result archive, SLURM behavior, all upstream tests, cross-platform training, or other repositories' current source/issues/releases. No upstream training was rerun and no upstream source was copied into this repository. MaartenSchoukens/nonlinear_benchmarks, PyDMD and SysIdentPy are historical dependencies discussed in local R01–R07 reports; they are not runtime dependencies here and were not fully re-audited in this takeover.

The [2026 Data-Centric Engineering paper](https://doi.org/10.1017/dce.2026.10067), *Benchmarking for nonlinear system identification: Submission platform and baseline results*, by Schoukens, Champneys, Beintema and Rogers, was checked at its publisher for authorship, data/code availability and Table 6. Its Silverbox GP-NARX entries are 0.418 / 0.772 / 0.373 mV. The local historical R07 continuation reports agreement at published precision; this does not establish aerospace transfer or reproduce the entire paper.

## Closest aerospace studies and claim limits

The following entries were reconciled against retained R01–R07 evidence, especially the R04-A prior-work matrix and later R06 report. Reading scope below distinguishes that prior work from new full-text verification.

| Work | Relevance / evidence limit |
|---|---|
| Xu, Lv, Kong, Wang & Chang (2026), [Dynamic modeling and multi-mode characteristic analysis of buzz instability in ramjets](https://doi.org/10.1016/j.cja.2026.104150) | Original dynamic-model target. Retained equation audit reports unresolved Eq.11/24 and capture/spillage closure. No new full-paper reproduction here |
| Xu et al. (2026), [Multimodal Identification of Ramjet Instability via Time-Frequency Feature Fusion](https://doi.org/10.1016/j.ast.2026.113485) | Time-frequency/mode-recognition neighbor; historical abstract-level evidence, not this project's demonstrated parameter identification |
| Kong, Lv, Yang, Chang & Guo (2026), [surrogate analysis of variable-geometry inlet performance](https://doi.org/10.7638/kqdlxxb-2026.0101) | Static surrogate comparisons already exist; historical partial publisher reading, not a novel dynamic feedback claim |
| Zeng et al. (2026), [Model correction and unstart protection control for scramjet engines](https://hkxb.buaa.edu.cn/CN/10.7527/S1000-6893.2026.33314) | GP correction and dual-EKF neighbor. R06 superseded R04's missing-full-text status: full text was acquired, with dynamic identification assessed as simulation rather than a verified dynamic experiment. That report was read; its equations were not re-audited here |
| Edelman et al. (2025), [Shock-Stationary Application of Pseudoshock Models During High-Amplitude Combustion-Driven Unsteadiness](https://ntrs.nasa.gov/citations/20240006842) | Conservation-based calibration and held-out experimental comparison already overlap broad novelty claims; retained methods/results review |
| Hunt & Hunt (2021), [Locating the Isolator Shock-Train Leading Edge with Limited Pressure Information](https://ntrs.nasa.gov/citations/20210011998) | Sparse-pressure localization precedent; its historical multi-run data are not established as an obtainable, licensed Sajben backpressure dataset |
| Wang et al. (2025), [low-frequency shock-train oscillations with vortex-generator jets](https://doi.org/10.1371/journal.pone.0328630) | R05 source is a fixed-backpressure CFD sequence, not a controlled experimental identification dataset |
| Wang, Kong, Wang & Chang (2024), [variable-Mach reconstruction with POD and sensor compression](https://doi.org/10.1063/5.0233389); Wang, Kong & Chang (2025), [wall-pressure reconstruction and sensor arrangement](https://doi.org/10.1063/5.0245653) | Reconstruction/sensor-selection precedents; historical abstracts only, full Methods/Results remain unverified |
| Hutchins et al. (2014), [Experimental Identification of Transient Dynamics for Supersonic Inlet Unstart](https://doi.org/10.2514/1.B35230) | Dynamic experimental identification is established prior art; historical bibliographic/abstract scope |
| Li et al. (2025), [Intelligent model correction and trajectory planning considering inlet unstart](https://doi.org/10.1016/j.ast.2025.110401) | Close model-correction neighbor; full text remains a reading gap |

This is a bounded evidence review, not an exhaustive novelty search. No unknown method detail is treated as proof of absence.

## Rights and reproducibility

| Material | Treatment |
|---|---|
| Original Python code, synthetic tests, original documentation | MIT; see [LICENSE](../LICENSE) |
| NASA experimental files and original papers | Original provenance/rights; acquisition links and hashes only; no blanket MIT assertion |
| MDCHAMP and other upstream code | Separately owned; referenced, not bundled; missing license explicitly retained |
| Fluent executable, native case/data, licensing and sensitive logs | Proprietary/private local assets; excluded from Git |
| Numerical summaries | Original derived analysis with algorithm definitions, source hashes and scientific limits; not a raw dataset mirror |

Raw CFD reproduction is limited to holders of the original assets and a licensed simulator. This limitation is explicit; public software reproducibility and CFD physical validation are distinct.
