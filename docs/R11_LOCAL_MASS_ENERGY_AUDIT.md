# R11: closed-field mass and energy audit

**Mass bookkeeping closes; numerical mass conservation fails in R09/R10. Complete energy auditing remains BLOCKED_WITH_EVIDENCE.** No solver was launched. All signs below are explicitly outward unless marked inward; depth=1 m.

## Exact stored mass accounting

For every stored face, add `SV_FLUX` to c0 and subtract it from c1 for interior faces. For a selected cell set, internal pairs cancel and every crossing face is retained. The all-domain, x/H>=5, downstream upper 0.5 mm band, and last-H sets close independently. Maximum observed closure discrepancy is below 1e-14 kg/s. Boundary sums reproduce the corresponding native logs within 4.2e-7 kg/s (printed precision). The complete crossing-face tables are in the local delivery.

| Closed state | Mass gap % | Reported energy gap % | Global mass L1 kg/s | Upper downstream mass L1 kg/s |
|---|---:|---:|---:|---:|
| R03 best 4k, iteration 14000 | 0.091734 | 0.072814 | 0.489923 | 0.054440 |
| R09 CFL0.5, +200 | 1.413997 | 2.028582 | 14.035043 | 5.644080 |
| R09 CFL0.1, +200 | 1.520303 | 1.936331 | 13.521586 | 4.659095 |
| R10 Roe, +200 | 1.457655 | 2.066635 | 16.196431 | 5.708322 |
| R10 Roe, +700, last complete field | 5.120165 | 6.011875 | 16.880773 | 6.100047 |

The small difference from older printed-log percentages comes from using unrounded stored fluxes, not a changed denominator. Relative gaps use |signed sum|/max(|inlet|,|outlet|). L1 is the sum of absolute cell divergence, a dimensional diagnostic rather than the solver's normalized continuity residual.

For R09 CFL0.5, downstream signed divergence is -1.477640 kg/s, upstream +1.276202 kg/s, and global -0.201438 kg/s. The upper downstream band alone is -1.594972 kg/s. Large local defects cancel in the global sum. It is incorrect to expect the band's L1 to equal the net inlet/outlet deficit; its cut surfaces and signed cancellation are essential. Wall mass flux is zero.

## Separation, shear, pressure and mesh

Across the five audited snapshots, x/H>=5 has **zero cells with negative axial velocity** and the outlet has **zero negative outward mass-flux faces**. The stored tangent wall shear has no negative downstream values. R09 CFL0.5 minimum upper-band axial velocity is 0.9791 m/s; approximate maximum outlet Mach is 0.5108. All checked outlets are subsonic. Wall-shear storage sign is retained without assuming a stress-on-fluid convention; the velocity and flux evidence are independently consistent with attached downstream flow at these snapshots. This does not prove that transient separation never occurs between saves.

R03 downstream top-wall pressure total variation is 0.021679 in p/p0 across 12 faces; R09 CFL0.5 is 0.313840 across 25 faces, with a largest adjacent jump of 0.030558. Sampling differs; these are descriptive diagnostics, not an equal-resolution convergence rate. The independently sampled reference comparison also shows the R09 downstream irregularity.

All reconstructed cell areas are positive. R09 upper-band minimum cell area is 1.72337e-8 m虏, maximum edge-length ratio about 2061, and minimum face-normal/center-connection cosine 0.08336. R03's corresponding cosine is **worse**, 0.04323, despite much smaller mass L1. These metrics flag thin/skew cells but do not isolate the cause. They are not Fluent's native orthogonal-quality or aspect-ratio definitions; no GCI or mesh independence is established. R03/R09 have different resolution and iteration history and are not a controlled mesh-error pair.

## Complete energy definition and available terms

For a fixed, stationary control volume, a consistent mean-flow convention is

`R_E = d/dt 鈭玶ho E dV + 鈭甗rho u_n (e + p_abs/rho + |u|虏/2) + q_eff路n - u路tau_eff路n + species enthalpy diffusion] dA - 鈭玈_E dV`.

Here h=e+p_abs/rho, h0=h+|u|虏/2; pressure work is already in h and must not be added a second time. For RANS, state explicitly whether E includes k: a total-mean-plus-turbulent formulation also requires the matching k transport, production/dissipation exchange and diffusion terms. Adding only mass_flux*k to a mean-energy report does not close that alternative system. Fluent's modeled energy equation and a full averaged physical energy balance are separate claims.

| Term | Solver/model evidence | Offline audit status |
|---|---|---|
| Static enthalpy | cp=1004.5 J/(kg K); all stored cell `SV_H` equal cp*T exactly in these files | Density-based enthalpy datum is 0 K; coefficient-reference temperature 288.16 K is unrelated. Boundary h flux reconstructed. |
| Mean kinetic energy | Density-based energy includes it | Reconstructed using stored boundary u,v; added once to h. |
| Pressure flow work | Included through h=e+p_abs/rho; operating pressure=0 | No independent extra p*u term added. No moving-frame pressure-work report is applicable. |
| Molecular/effective viscous work | Density-based solver includes viscous terms; stationary no-slip wall velocity is zero | Wall mechanical work is zero under the model. Exact open/interior-face stress work is absent; nonzero wall shear alone does not supply it. `include-viscous-work? #t` is not proof of saved density-solver report completeness. |
| Molecular/turbulent conduction | Constant molecular conductivity 0.0242; turbulent heat transport is modeled | Adiabatic wall reports are approximately zero. Exact interior/open normal gradients and effective conductive face fluxes are not stored. |
| Turbulence transport | SST, stored k/omega/mu_t | mass_flux*k is tabulated only as a diagnostic, **not added**. Exact k-energy convention and all matching face/source terms remain unresolved. |
| Species, reactions, radiation, particles, volumetric sources | Single air; corresponding models disabled in native summary; no specified sources | No active contribution identified; preserve model scope, do not generalize. |
| Physical storage | Steady case; no synchronized physical-time states | Physical derivative is zero only for the intended steady solution. Iterative residual is not zero in failed states. Local pseudo-time is not a measurable transient storage term. |
| Discrete energy residual / dissipation | Residual history exists; coupled flux formulation is solver-specific | No exact interior numerical energy flux or per-cell energy residual is saved. Approximate gradients would not constitute exact discrete closure. |

Source: [Fluent 24.2 energy theory](https://ansyshelp.ansys.com/public/Views/Secured/corp/v242/en/flu_th/flu_th_sec_hxfer_theory.html) and [flux reporting](https://ansyshelp.ansys.com/public/Views/Secured/corp/v242/en/flu_ug/flu_ug_FluxReport.html). The 24.1 web pages were inaccessible. The installed solver is 24.1; current files directly verify the enthalpy datum and reported arithmetic. The documentation explicitly limits the standalone viscous-work report to the pressure-based solver. A `viscous-energy-dissipation? #f` setting cannot be interpreted as disabled viscous terms in this density-based case.

## What the native heat report actually proves

Stored boundary `SV_HEAT_FLUX` sums reproduce the native Total Heat Transfer Rate within 0.1 W. Independently, `-sum(SV_FLUX * (cp*T + (u虏+v虏)/2))` reproduces each inlet/outlet report within **0.044 W**. Thus the saved reports are numerically consistent with boundary total-enthalpy convection. This does not establish that every missing open-boundary work/diffusion term is zero or that the full discrete law closes.

R09 control inward net energy is 80636.822 W. A hypothetical change of enthalpy datum by -cp*298.15 changes the unbalanced net to 20307.721 W, because `Q' = Q + delta_h * net_mass`. This algebra is demonstrated, **not used to lower or re-normalize the R03 energy threshold**. Mass conservation must close for energy-datum shifts to leave the net invariant. Both original mass and reported-energy criteria fail; full energy qualification remains unavailable.

## Root-cause conclusions

Ruled out for the audited snapshots: reversed sign convention, omitted boundary mass flux, negative cell area, and Study #5-like downstream reversed flow. Evidence supports a persistent downstream numerical defect with large cancellation and irregular pressure. Mesh geometry/gradient reconstruction, pressure-boundary treatment, turbulence-discretization coupling and solver iteration remain possible contributors; their individual causality is UNKNOWN. Temperature/geometry mismatches limit physical validation but do not explain away failed discrete mass conservation.

No new solver run, no R09/R10 rerun, no failed-field training and no release of Xu Stage H HOLD occurred. Reproduction code: [closed_field_audit.py](../cfd/closed_field_audit.py). Derived results: [r11_local_summary.json](../cfd/r11_local_summary.json).
