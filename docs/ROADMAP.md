# Scientific route and stop rules

## Stage 1: a real steady physical benchmark — current stage

Freeze geometry, units, inlet conditions, outlet pressure, turbulence/transport laws and pressure definitions. Establish a numerically qualified weak-shock solution before interpreting NASA discrepancies. Research thresholds inherited from R03 are mass gap <=0.5%; complete energy gap <=0.5%; two separate 500-iteration window means of each throughflow drifting <=0.5%; normalized wall-pressure drift <=0.005; finite physically admissible fields and checked outlet Mach/backflow. Residual histories must support the conclusion. NASA comparisons require separate top/bottom MAE <=0.05 in p/p0 and shock-position difference <=0.5 H. These are project thresholds, not NASA certification standards. Grid and boundary-condition uncertainty remain additional requirements.

R09 and R10 fail this gate. The R10 first 200 steps did not support changing AUSM to Roe-FDS as the proposed remedy. Do not infer a unique root cause from a negative test or continue arbitrary CFL/flux scans.

R11 completed the stored mass budget and independent NASA pressure comparison. Missing interior energy flux/stress/gradient data block complete energy closure. The local snapshots do not show Study #5-like outlet separation; no causal single intervention is justified. See [R11 decision](R11_CFD_DECISION.md).

**One next highest-value experiment:** qualify the actual two VT/Sajben files claimed to contain 31 experimental backpressure settings, if obtained through an authorized custodian channel. Verify file-level case independence, normalization, geometry and reuse rights before any whole-condition static model comparison. Stop repeating public searches or solver scans if the files remain unavailable; details and the bounded stop are in [data eligibility](R11_DATA_ELIGIBILITY.md). Do not launch the strong case or Xu Stage H.

## Stage 2: cross-condition static reduced-order/surrogate models — blocked

Require substantially more independent backpressure settings with consistent geometry, normalization, credible measurements, uncertainties and provenance. Before fitting, freeze entire held-out operating conditions and comparable data/compute budgets. Compare simple interpolation, POD-based methods and GP only when each is applicable. Two curves are insufficient for an informative training/validation/test split. Adjacent spatial samples or pseudo-time states do not create independent conditions.

## Stage 3: dynamic system identification — blocked

Require independent controlled excitation, synchronized physical-time inputs/outputs, noise and repeatability information, identifiable parameters, and untouched whole excitation trajectories/conditions. Use ARX and state-space baselines first. Nonlinear models must demonstrate an additional need and value on the same protocol. Inspect simulation error, stability, units and conservation as well as RMSE.

Steady pseudo-time iteration count is not physical time. Neither R08's two curves nor R09/R10 iterative histories are valid dynamic training sets. Any future unsteady calculation needs its own physical-time, time-step and inner-convergence contract.

## Novelty boundary

Sajben shock relocation, turbulence-model comparison, GP-NARX, conservation-constrained calibration, sparse-pressure shock localization and EKF-based model correction all have prior art. The [nearest-work matrix](EVIDENCE.md) identifies overlap and remaining reading limits. Innovation stays UNKNOWN until a concrete difference, independent data and a fair test establish it. Do not reopen known Silverbox tests to tune toward their published scores.
