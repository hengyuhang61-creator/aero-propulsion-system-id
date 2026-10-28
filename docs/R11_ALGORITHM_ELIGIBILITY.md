# R11: algorithm eligibility

**BLOCKED_BY_DATA** (gate BLOCKED_WITH_EVIDENCE). Zero newly qualified experimental conditions; existing NASA weak/strong measurements provide two steady settings. No fitting, GP, POD training, ARX, NARX or GP-NARX was run. R11 interpolation aligns physical reference curves spatially; it is not a learned cross-condition surrogate.

The [data audit](R11_DATA_ELIGIBILITY.md) supplies the availability and identifiability blockers. Failed CFD and pseudo-time histories are excluded, and no Silverbox or artificial sequence substitutes for aviation evidence.

Conditional research question: **At fixed documented Sajben geometry and normalization, does POD coefficient interpolation reduce whole-condition wall-pressure RMSE and shock-location error over direct backpressure interpolation when training-set size is fixed?** This is a testable comparison, not a novelty claim or an approved training experiment.

After file qualification, and before seeing held-out responses, freeze eligible case IDs, independent p_exit/p0 input (plus only evidenced exogenous parameters), exact training counts, complete-condition train/validation/test splits, interpolation versus separately labeled endpoint extrapolation, and per-wall MAE/RMSE in p/p0 plus shock error in H. A frozen-output predictor and direct interpolation are mandatory; POD coefficient interpolation only if rank can be chosen within training/validation conditions. Never randomly split spatial stations. Report performance versus training count, acquisition uncertainty and missing cases. No numerical counts or fit thresholds are invented before the case inventory exists.

Dynamic work additionally requires measured independent excitation, synchronized physical-time inputs/outputs, clock/anti-aliasing/noise metadata, independent whole trajectories and an identifiability test. Those gates are not met by the accessible files.
