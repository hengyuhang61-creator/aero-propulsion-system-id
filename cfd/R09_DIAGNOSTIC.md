# R09 numerical audit

**SCIENTIFIC_HOLD.** Both existing branches were audited without restarting Fluent. Each used the same hash-verified 16,000-cell checkpoint and added exactly 200 iterations. Only CFL differs (0.5 versus 0.1). Equal iteration counts are not equal accumulated pseudo-time.

## Signed native reports

Mass gap = abs(m_in + m_out) / max(abs(m_in), abs(m_out)). Native console signs are positive into the domain and negative out. Saved SV_FLUX uses the opposite boundary sign; the independent face sums match the printed values to their displayed precision. Wall mass flux is zero in each saved field. Native reference depth is 1 m, so the printed kg/s and W are for the modeled unit depth, not a measured full-span apparatus throughput.

Reported energy gap uses the sum over bottom, inlet, outlet and top, divided by max(abs(E_in), abs(E_out)). It is the native “Total Heat Transfer Rate” report; all original signs and wall terms are retained in the JSON. The rounded printed boundary sum differs slightly from Fluent's higher-precision Net, which is preserved separately. Neither quantity is silently replaced by an unsigned subtraction.

| CFL | Added iterations | m_in kg/s | m_out kg/s | signed mass sum kg/s | denominator kg/s | gap % | E_in W | E_out W | signed E sum W | denominator W | reported gap % |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 0.5 | 0 | 14.238023 | -13.878955 | 0.359068 | 14.238023 | 2.521895 | 3972803.9 | -3857476.9 | 115327.0 | 3972803.9 | 2.902912 |
| 0.5 | 100 | 14.242466 | -14.093224 | 0.149242 | 14.242466 | 1.047866 | 3974043.6 | -3915607.1 | 58436.5 | 3974043.6 | 1.470454 |
| 0.5 | 200 | 14.246018 | -14.044580 | 0.201438 | 14.246018 | 1.413995 | 3975034.8 | -3894398.0 | 80636.8 | 3975034.8 | 2.028581 |
| 0.1 | 0 | 14.238023 | -13.878955 | 0.359068 | 14.238023 | 2.521895 | 3972803.9 | -3857476.9 | 115327.0 | 3972803.9 | 2.902912 |
| 0.1 | 100 | 14.238997 | -13.961112 | 0.277885 | 14.238997 | 1.951577 | 3973075.7 | -3879454.2 | 93621.5 | 3973075.7 | 2.356399 |
| 0.1 | 200 | 14.239927 | -14.023437 | 0.216490 | 14.239927 | 1.520303 | 3973335.3 | -3896398.4 | 76936.9 | 3973335.3 | 1.936330 |

The initial state is a monitor, not an intermediate iteration. The only interior monitor is at +100; +200 is the endpoint. Two additional intermediate states cannot be invented from these logs.

## Residual and wall-pressure evidence

| CFL | Continuity median 1–100 | median 101–200 | final | top area mean Pa | bottom area mean Pa |
|---|---:|---:|---:|---:|---:|
| 0.5 | 2.2236000 | 2.5088500 | 2.5290 | 97971.421 | 97448.800 |
| 0.1 | 2.1898000 | 2.2087000 | 2.2130 | 97463.636 | 97355.441 |

All six residual channels, min/max and segment medians are in the machine summary. Continuity and energy medians rise in both branches. Lower CFL gives a lower final continuity residual but a larger mass gap; it is not evidence of greater physical accuracy. There is one wall-average report per branch, so within-branch wall stability is not established.

## Native offline localization and qualification

| Snapshot | Whole-domain absolute face-divergence sum (kg/s) | x/H>=5 share | downstream upper 0.5 mm share |
|---|---:|---:|---:|
| initial | 13.522284760 | 76.1170% | 33.1912% |
| control_cfl05 | 14.035042538 | 80.5778% | 40.2142% |
| test_cfl01 | 13.521585669 | 76.3965% | 34.4567% |

The face diagnostic sums signed c0/c1 contributions and checks their global sum against all boundary fluxes. It is not renamed the complete nonlinear solver residual. The separate historical SV_P_R*volume proxy was independently recomputed: 76.0074% downstream and 33.1885% in the upper strip, matching the retained R03 summary. Its timing is one diagnostic iteration after the checkpoint and its definition differs.

All three case meshes and boundary-setting hashes match. Saved states have finite positive pressure, temperature and density, zero wall mass flux, and no reversed outlet face flux. Near the downstream upper wall, no negative axial cell velocity was found. These checks do not prove attached flow everywhere or physical convergence. The maximum aspect ratio/minimum orthogonal-quality evidence remains in R03; localization alone does not exonerate the grid.

## Acceptance

| Gate | Result |
|---|---|
| Native run completion, paired case/data, recorded hashes | Verified for both existing runs |
| Mass gap <=0.5% | FAIL for both endpoints |
| Reported energy gap <=0.5% | FAIL for both endpoints |
| Complete energy accounting | NOT ESTABLISHED independently; native setting includes viscous work, but full component mapping is not qualified |
| Two 500-iteration stability windows | NOT AVAILABLE; 200 new iterations cannot substitute |
| Wall-pressure stability | NOT AVAILABLE; endpoint mean only |
| NASA same-condition field comparison and grid uncertainty | Not accepted for these unconverged states |

The launcher receipt counts UTF-8 bytes after replacement decoding, whereas the raw console uses native encoding. The 32-byte length discrepancy is exactly reproduced by that code path; it is not evidence that a log was truncated. Native output hashes and input/original hashes match.

[Recompute from completed logs](audit_r09.py) · [Machine summary](r09_summary.json) · [One subsequent bounded test](R10_FLUX_TEST.md)
