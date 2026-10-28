# R11: bounded data eligibility audit

Audit date: 2026-10-28. **BLOCKED_WITH_EVIDENCE** for cross-condition surrogate training and dynamic identification. Public numeric files support a conditional steady pressure comparison; this is not evidence that a suitable training database is currently obtainable. Two candidates received detailed qualification. No author was contacted and no AI agent was delegated.

## Candidate 1: the 31 Sajben experimental backpressure settings

Primary record: [Virginia Tech, research summary, 21 August 2001](https://archive.aoe.vt.edu/shosder/main/mdo/21Aug01.html), HTTP 200, archived and hashed. The author reports receiving two files from Sajben, containing mean upper/lower wall pressure at 31 exit/inlet-total pressure ratios from 0.7166 to 0.8624. The page also reports inlet/exit boundary-layer profiles (top: four ratios; bottom: two) and streamwise velocity profiles for two ratios. Those counts must not be added to 31 as extra independent wall-pressure conditions.

| Qualification field | Evidence and limit |
|---|---|
| Physical geometry | Sajben transonic rectangular diffuser; nominal stations x/H=-4.04 and 8.65. As-built wall, suction configuration and physical-exit metadata need reconciliation with the original two files. Hosder's later manuscript distinguishes the physical exit at 14.44H. |
| Real experiment or CFD | The 31 curves are described as experimental measurements. The same page's 12 GASP runs per grid are CFD, a separate set that cannot substitute for them. |
| Independent input | Steady outlet-static/inlet-total pressure ratio is an externally set operating parameter. No controlled dynamic input is described. The exact reference plane and per-case p0, T0 must be verified from the files. |
| Outputs | Mean upper/lower wall static pressures versus position; shock position would be a derived estimator with station-spacing uncertainty, not a directly measured extra channel. |
| Time, synchronization, noise | Time-averaged curves, not physical-time sequences. Acquisition rates, averaging windows, synchronization, calibration uncertainty and repeated-run covariance UNKNOWN from this record. |
| Independent conditions | 31 claimed; **zero newly acquired** numeric conditions. Actual distinct usable IDs and duplicate ratios cannot be verified. Existing NASA weak/strong curves remain two settings only. |
| Download and format | Page has 15 links, all JPG images (one duplicated); no numeric file link or filename. Parent directory returns 404. Original two-file format UNKNOWN. No original download URL can honestly be supplied. |
| License/reuse | No explicit permission for unseen files established. Public readability of the note is not a dataset redistribution license. No raw data mirrored. |
| Closest method/result | [Hosder et al. (2006)](https://doi.org/10.1016/j.compfluid.2005.04.006), checked in the [author manuscript](https://archive.aoe.vt.edu/shosder/main/caf_revised/caf_revised.pdf), studies grid, turbulence, geometry and outlet uncertainty in 2D GASP. It explicitly distinguishes uncertainty comparison from validation. It is not a 31-condition surrogate benchmark. |

Local searches covered existing research data and the prior Codex takeover outputs before public-source checks. The retained inventory contains the existing NASA weak/strong pressure files, meshes and source notes, but no 31-condition table. Bounded GitHub, Zenodo and Mendeley searches did not identify the missing original files. This is **failure to obtain**, not proof of nonexistence. Exact searched paths, query results, page-link audit and retrieval errors are in the private evidence delivery.

**Verdict:** highest-value static candidate, but file availability, per-case equivalence and reuse permission block qualification.

## Candidate 2: Schram and Narayanaswamy (2026), Busemann unstart

Primary full text: [Unstart dynamics of hypersonic Busemann inlet at non-zero angles of attack](https://link.springer.com/article/10.1007/s00348-026-04215-0), DOI 10.1007/s00348-026-04215-0; HTTP 200, archived and hashed. Methods, results, data availability and supplement links checked.

| Qualification field | Evidence and limit |
|---|---|
| Geometry/conditions | True axisymmetric truncated Busemann inlet experiment; tunnel M=3.7, design M=5.5, frontal diameter 44 mm, throat 25.5 mm, nominal 3:1 area contraction. Geometric angles -5, 0, +3 degrees, estimated tolerance ±0.13 degrees; angles not formally flow-measured. Different geometry from Sajben. |
| Independent excitation | Counter-injected jet controlled by a high-bandwidth solenoid. Jet-line static pressure 40 cm upstream of the orifice is calibrated to jet mass flow. This is an exogenous input; isolator pressure alone would be an endogenous response. |
| Outputs and definition | Fast PSP surface-pressure fields and derived shock-foot trajectory; external schlieren. Shock locator uses normalized intensity threshold R=0.35 with sensitivity analysis. Raw pixel calibration, units and coordinates have not been obtained. |
| Timing/synchronization | PSP 20 kHz (50 microseconds), schlieren 10 kHz (100 microseconds), common solenoid trigger reported. Input-channel sampling rate, actual clock alignment and usable record lengths remain UNKNOWN without numeric records. |
| Noise and repetition | Paper reports mass-flow uncertainty 0.2367 g/s, ±7 ms rise-time variation across three repeats, and shock-speed uncertainty ±14 m/s. These are different uncertainty definitions, not interchangeable error bars or a raw noise model. |
| Internal consistency | Calibration instrument stated maximum is 20.007 g/s, while discussed repeats use 27 g/s. Raw calibration/extrapolation metadata must resolve this before treating the input magnitude as qualified. |
| Independent settings | Five illustrated response/angle settings: weak and strong at 0/+3 degrees, strong at -5. Three same-setting repeats do not create three extra input settings. Full campaign count UNKNOWN; no numeric trajectories acquired. |
| Download/format | Full article is accessible. Data availability requires contacting the corresponding author. Five supplements are MP4 videos; none is a synchronized numeric input/output table. No usable raw-data download URL was found. |
| License/reuse | Article CC BY 4.0 does not establish a license for unprovided raw records. Raw-data schema and permissions UNKNOWN. |
| Closest published method/result | The paper itself tracks threshold-based shock motion and compares input transience, pressure and propagation across angles/responses; reports roughly 20% variation in strong-unstart duration. It does not supply a ready ARX/NARX identification benchmark. |

**Verdict:** physically promising dynamic experiment, but not publicly downloadable numeric training data. No contact message was sent.

## Screened sources: not additional deep audits

| Source and actual access | Physical information / count | Why it does not pass |
|---|---|---|
| [NASA weak pressure](https://www.grc.nasa.gov/www/wind/valid/transdif/transdif02/sajwpres.data), [strong pressure](https://www.grc.nasa.gov/www/wind/valid/transdif/transdif02/sajspres.data) | Existing local ASCII measured curves, two nominal ratios 0.82/0.72, H=0.04399788 m, header T0=300 K. Reused and hashed, not downloaded again. | Suitable for R08 contrast/R11 diagnostic only. No time resolution/synchronization or excitation series. Raw redistribution rights not newly established. |
| [NASA Study #3](https://www.grc.nasa.gov/www/wind/valid/transdif/transdif03/transdif03.html) | Numeric GENPLOT reference curves actually downloaded/read; weak CFD at T0=525.6 R. | Numerical reference, not new experimental settings. [Study #5](https://www.grc.nasa.gov/www/wind/valid/transdif/transdif05/transdif05.html) CFF binary access limits are documented separately. |
| [Bustard et al. 2024](https://doi.org/10.1007/s00348-024-03836-7), full text HTTP 200 | True OIWPS/Indiana inlet, M5.7, Re=8.5/10.2 million per metre (two settings), PSP10 kHz, pressure transducers250 kHz. Temperature correction, calibration and spectral noise are discussed. | No controlled jet input in this study; downloadable synchronized arrays/clock metadata not obtained. Data via author email; raw license/schema UNKNOWN. Closest method is PSP shock tracking, coherence and conditional pressure correlations. |
| [Johnson and Narayanaswamy, 2026 volume](https://doi.org/10.1007/s00348-025-04156-0), published December 2025, full text HTTP 200 | True Busemann restart experiment using jet removal, PSP/schlieren10 kHz; gradient-based shock tracking. Independent campaign count and raw input noise/clock records not obtained. | Data-availability text says no datasets generated/analyzed despite experimental results. Contradiction retained; videos/text are not numeric records. Raw format/license UNKNOWN. |
| [Notre Dame record 28792508](https://curate.nd.edu/articles/dataset/Global_Measurements_of_Inlet_Isolator_Dynamics_and_Optimization_of_Unstart_Detection/28792508), [metadata API](https://api.figshare.com/v2/articles/28792508) HTTP 200 | Metadata type is thesis, not raw experiment data. Only listed attachment is BUSTARDAN42025D.pdf, 8,202,764 bytes; [file URL](https://ndownloader.figshare.com/files/54249413). | The URL segment says dataset but payload is one PDF, All Rights Reserved. File itself was not downloaded in this audit. No channel schema, trajectories or independent counts; reject as a raw-data source. |

Search stopped after two detailed candidates and these bounded checks. A PDF, figure, video, repository label or author statement of possession does not increase the eligible sample count.

## Exactly one next priority

**Perform a file-level qualification of the two original VT/Sajben 31-condition tables, if supplied by their custodian through an authorized channel.** The experiment is to determine whether the claimed 31 conditions are actually usable: hash originals; parse every case; reconcile station coordinates, p0/T0, outlet plane, geometry/suction, calibration/uncertainty, duplicates and reuse rights; report the number of independent consistent conditions. Do not restart the same web search. No contact is authorized by this report.

Acceptance requires the actual numeric files and sufficient metadata, not an assurance they exist. If access remains unavailable after one specifically authorized custodian/access attempt, stop the Sajben surrogate route rather than generate replacement failed CFD. If it passes, the next modeling work becomes the whole-condition static comparison described in [algorithm eligibility](R11_ALGORITHM_ELIGIBILITY.md). More CFD tuning has no identified causal intervention; dynamic models lack accessible synchronized input/output records; Silverbox and a new platform do not answer this aviation question.
