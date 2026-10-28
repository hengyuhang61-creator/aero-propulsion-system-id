# Status and evidence boundaries

Snapshot: 2026-10-28. R01–R07 rows are source-backed historical reports, read during takeover; they were not rerun. R08–R10 were audited in this takeover.

| Stage | Recorded achievement | Limit |
|---|---|---|
| R01 | Assumption-explicit constant-volume mass/internal-energy model; mathematical and integration checks | Not Xu's closed dynamic model or physical validation |
| R02–R03 | NASA weak-shock setup, corrections, coarse wall comparison, 16k-grid diagnostics | Fine-grid conservation/stability failed; 64k mesh construction did not yield a solved validation case |
| R04-A | Literature/data audit and PyDMD synthetic DMDc tests | No qualified Xu feedback data; early claims about missing Zeng full text were superseded by R06 |
| R05 | Wang 2025 CFD sequence forecasting: 594 synchronized times, AR/ridge and flow-feature controls | Single fixed-backpressure CFD trajectory; flow features are endogenous observations, not independent actuation |
| R06 | Silverbox ARX and SysIdentPy FROLS free-run comparison; Zeng full text acquired and discussed | Electronics benchmark, not propulsion; static-to-dynamic evidence and blind-test limitations retained |
| R07 original | PNARX/sklearn GP adaptations and synthetic identifiability diagnostics | Initial official-GP/notification objectives were incomplete; its premature overall completion claim was corrected |
| R07 corrective continuation | Official MDCHAMP JAX GP-NARX: 0.417735330 / 0.772403128 / 0.373223057 mV | Matches published Table 6 rounding for this Silverbox branch; previously observed tests, not blind or whole-paper reproduction; not rerun here |
| R08 | All wall metrics and 121 point/zone comparison rows match the portable implementation | Two steady measured conditions only; no dynamics or independent surrogate generalization |
| R09 | Both existing 200-iteration runs audited, including native HDF face fluxes and all three monitor states | Both fail mass/reported-energy criteria; missing full windows and energy decomposition |
| R10 | One isolated AUSM→Roe-FDS test; matched 200-iteration comparison and bounded extension | Improvement hypothesis not supported; stopped at >10% mass gap; second 500-iteration window incomplete |

## Independent status axes

| Axis | Current conclusion |
|---|---|
| Software/public source | Runnable stdlib implementation and meaningful synthetic checks; see CI for the exact commit |
| Data qualification | R08 qualifies for a two-condition steady pressure contrast. It does not qualify for dynamic identification or a credible cross-condition surrogate holdout |
| Numerical verification | Sajben 16k case: **SCIENTIFIC_HOLD**; conservation/stability not accepted; grid uncertainty unresolved |
| Physical validation | Not established for the current CFD or an aerospace reduced-order model |
| Paper reproduction | R07 Silverbox branch numerical reproduction only; Xu and complete benchmark paper reproduction not established |
| Innovation | **UNKNOWN**; no demonstrated new physical result or algorithmic advantage |

No strong-shock CFD, 64k solve, Xu Stage H restart, new Silverbox training, or dynamic-model fitting was performed during this takeover. R01–R09 original files were protected by a before/after local hash inventory (4,452 files, with environment directories explicitly excluded). Native solver files, private inventories, and raw local reports remain outside GitHub.
