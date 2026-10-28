# R10 single-variable flux experiment

**SCIENTIFIC_HOLD; frozen improvement hypothesis NOT SUPPORTED.** One new experiment was attempted. No restart, CFL scan, second physical case, or physical-time simulation was performed.

## Frozen hypothesis and control

R09 saved face fluxes localized 80.5778% of the control endpoint's absolute mass-divergence sum to x/H>=5 and 40.2142% to its downstream upper 0.5 mm strip. Wall fluxes were zero and no outlet reverse flux was found. This motivates testing sensitivity to the discrete convective flux formulation; it does not establish a unique root cause.

Hypothesis: switching AUSM to Roe-FDS at fixed mesh, initial state and CFL materially reduces this local imbalance. The sole numerical change was `coupled-flux-method 1 -> 0`, verified from Fluent 24.1's native menu and saved settings. CFL remains 0.5; 16,000-cell geometry, SST, ideal-gas properties, second-order flow/k/omega, boundary conditions and four processes remain unchanged. The initial case/data copies have the same hashes as the R09 control inputs. The 0-step readback has identical cell fields and mesh/boundary hashes; five derived face arrays differ only at scaled <7.9e-13, explicitly recorded rather than claimed bitwise equal.

Matched comparison is at +200 iterations against existing R09 control_cfl05. The pre-run criterion required the absolute local face-divergence L1 to be <=80% of control, smaller global L1, no greater mass gap and legal fields. A lower *fraction* alone would not pass because the denominator can worsen.

| At +200 | AUSM control | Roe-FDS test |
|---|---:|---:|
| Global absolute face-divergence sum kg/s | 14.035042538 | 16.196430636 |
| Upper-downstream absolute L1 ratio to control | 1.000000 | 1.011382031 |
| Mass gap | 1.413995% | 1.457655% |
| Continuity residual | 2.5290 | 2.5808 |

The local absolute diagnostic worsened by approximately 1.14%, so the proposed remedy failed. The negative result does not prove that all flux formulations are irrelevant, nor isolate geometry versus boundary discretization.

## Bounded extension and stop

The frozen maximum was 1,200 added iterations / 900 seconds, with native reports every 25 iterations and planned checkpoints at 0, 200, 700 and 1,200. Qualification windows were 201–700 and 701–1,200, with 20 uniformly spaced monitor samples each. Stops included >10% mass gap, invalid fields, native errors, continuity residual >100, 120 seconds without iteration progress, or deadline. Original files were never output targets.

At +1,150, mass was +14.237832 / -12.712075 kg/s: **10.716217% gap**. Reported total-heat flux was +3,972,750.7 / -3,506,717.4 W with negligible wall terms: **11.730746% gap**. Tmin=213.273688 K, Tmax=287.214909 K and minimum density=0.703062545 kg/m3 were finite/positive. The deterministic controller triggered the mass-gap stop at about 69 seconds. Final console output reaches +1,175 due to the polling/termination interval; the receipt's last-observed iteration was 6,158, while the stable log ends at 6,175. Neither is relabeled +1,200.

| Window | Samples | Completeness | Maximum mass gap | Maximum reported energy gap |
|---|---:|---|---:|---:|
| 201–700 | 20 | Complete | 5.930909% | 6.789481% |
| 701–1,200 | 18 | Incomplete, ends 1,150 | 10.716217% | 11.730746% |

The first window already fails conservation. The incomplete second window is not used to certify drift. No 1,200 checkpoint exists; **700 is the last complete saved native state**. Complete energy decomposition, converged NASA wall errors and grid uncertainty are not accepted. No shock-motion time series is inferred from steady iterations.

## Preserved failures and operational limits

Controller checks for normal completion, deadline, stall and an injected native error passed on deterministic subprocess fixtures. In the real stop, the launcher/solver tree exited but two detached MPI helpers remained. They were identified by the pre-run empty process inventory, creation time and exact PID, stopped separately, and absence was checked before HDF analysis. Thus the simple controller is **not certified for unattended Fluent cleanup**. No remote notification or human-read receipt is claimed.

The first readback audit demanded bitwise equality of all derived face arrays and failed; the investigation found exact cell-state equality and roundoff-scale face reconstruction. The explicit scaled 1e-11 readback tolerance applies only to derived faces, not to physical gates. The failure and revised criterion are preserved in the local audit record.

The contract, journal, launcher, native logs, input/output hashes, paired checkpoints and cleanup receipt remain local. [Public machine summary](r10_summary.json) contains the measured diagnostics. Reproduction of the native solve requires those proprietary assets and a licensed Fluent 2024 R1 environment. Do not rerun this failed test merely to fill its iteration budget.
