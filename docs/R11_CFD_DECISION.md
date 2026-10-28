# R11: no new CFD justified

Decision: **NO_NEW_CFD_JUSTIFIED**. Decision gate PASS; new solver execution NOT_EXECUTED. No Fluent process was started in R11 and no new run contract was activated.

The [closed-field audit](R11_LOCAL_MASS_ENERGY_AUDIT.md) closes stored mass accounting, exposing a genuine downstream numerical defect rather than missing boundaries. It does not isolate mesh reconstruction, boundary treatment, turbulence coupling or iteration as the unique cause. R03 has a worse minimum geometric cosine yet much lower residual. The [reference audit](R11_REFERENCE_PHYSICS_AUDIT.md) shows that Study #5's exit-reaching separation is absent from the local saved weak-shock fields. Its extension also changes the pressure specification and published numerical settings. It is not an evidence-backed single-variable remedy for R10.

Temperature/experimental geometry mismatches prevent strict validation; correcting them would alter the physical case, without demonstrated resolution of local conservation failure. A solver restart merely to obtain missing energy fluxes would be another run without the required intervention evidence. No new solver, converter platform, strong case or mesh sweep is justified here.

R03 criteria remain frozen: mass and complete-energy gaps <=0.5%; two separate 500-iteration throughflow-mean windows drift <=0.5%; normalized wall-pressure drift <=0.005; admissible finite fields, outlet Mach/backflow and supporting residual histories. Physical comparison additionally requires per-wall MAE<=0.05 and shock difference<=0.5H; grid/boundary uncertainty remains separate. R09/R10 fail, and missing stability windows cannot be created from snapshots. The conditional R11 pressure agreement does not qualify the flow.

Any future authorized run must first freeze a single falsifiable hypothesis, exact hashed baseline and inputs, changed/fixed variables, full flux export/monitor definitions, unchanged acceptance, iteration/time limits, stop conditions and owned-process/MPI cleanup. No such experiment is presented as ready now. Xu Stage H stays on scientific HOLD; original case/data and prior failed runs are preserved.
