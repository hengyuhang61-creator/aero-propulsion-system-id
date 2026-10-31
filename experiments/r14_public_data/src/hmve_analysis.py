"""R14 HMVE (NASA 2025, M2.5/3.0/3.5 axisymmetric + swept SBLI) profile analysis.

Data are Tecplot ASCII probe profiles: 21 streamwise stations per file, each a
wall-normal line. Variables are normalised by the freestream velocity U1:
    U/U1, V/U1, W/U1, uu/U1^2, vv/U1^2, ww/U1^2, uv/U1^2
This script extracts, per file and station:
    * edge velocity and boundary-layer thickness delta99
    * displacement thickness delta*, momentum thickness theta, shape factor H
    * minimum near-wall U/U1 (reverse flow indicator) and separation-bubble height
    * peak streamwise turbulence uu/U1^2 and peak |uv|/U1^2
It does NOT merge HMVE with SBLI2.05: the geometries, normalisations and measured
quantities differ. Cross-experiment use is limited to dimensionless statements and
is documented in 06_HMVE_CROSS_VALIDATION.md.
"""

from __future__ import annotations

import os as _os

R14_ROOT = _os.environ.get("R14_ROOT", r"C:\Work\research\aviation_algorithm_r14_public_data_20261031")


import json
import re
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(R14_ROOT)
RAW = ROOT / "data/raw/hmve/HMVE2_PIVprofiles"
OUT = ROOT / "results"

ZONE_RE = re.compile(r'ZONE T = "Probe Station ([\d.]+), x - x_i = ([-\d.]+) mm')
NAME_RE = re.compile(r"PIVprofiles_M(?P<mach>[\d.]+)_a(?P<ang>[\d.]+)_l(?P<lvl>\d+)(?:_t(?P<theta>\d+))?_Re(?P<re>[\d.]+)\.dat")


def parse_file(path: Path) -> pd.DataFrame:
    rows, station, xxi = [], None, None
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        s = line.strip()
        if s.startswith("ZONE"):
            m = ZONE_RE.search(s)
            if m:
                station, xxi = float(m.group(1)), float(m.group(2))
            continue
        if not s or s.startswith("VARIABLES") or s.startswith("#"):
            continue
        t = s.split()
        if len(t) < 9 or station is None:
            continue
        try:
            vals = [float(v) for v in t[:9]]
        except ValueError:
            continue
        rows.append(dict(station=station, x_minus_xi=xxi, x=vals[0], y=vals[1],
                         U=vals[2], V=vals[3], W=vals[4],
                         uu=vals[5], vv=vals[6], ww=vals[7], uv=vals[8]))
    return pd.DataFrame(rows)


def station_metrics(g: pd.DataFrame) -> dict:
    g = g.sort_values("y")
    y = g.y.to_numpy()
    u = g.U.to_numpy()
    v = g.V.to_numpy()
    ue = float(np.nanmax(u))
    # delta99.5: first wall-outward crossing of 0.995*Ue (the TM uses delta_99.5)
    above = np.where(u >= 0.995 * ue)[0]
    d995 = float(y[above[0]]) if above.size else np.nan
    # integrals only over the measured wall-normal extent; the unmeasured
    # 0 < y < y_min strip biases delta* and theta low (documented, not filled).
    integ = lambda f: float(np.trapezoid(f, y)) if len(y) > 2 else np.nan
    dstar = integ(1.0 - u / ue)
    theta = integ((u / ue) * (1.0 - u / ue))
    # near-wall truncation correction (first-order, assuming linear ramp 0->U(y_min))
    y0, u0 = float(y[0]), float(u[0])
    dstar_trunc = (1.0 - 0.5 * u0 / ue) * y0
    theta_trunc = (0.5 * u0 / ue) * (1.0 - 0.5 * u0 / ue) * y0
    return dict(
        y_min=y0, y_max=float(y.max()), n=int(len(y)),
        U_edge=ue, delta995_mm=d995, delta_star_mm=dstar, theta_mm=theta,
        delta_star_trunc_corr_mm=dstar_trunc, theta_trunc_corr_mm=theta_trunc,
        H=float((dstar + dstar_trunc) / (theta + theta_trunc))
        if (theta + theta_trunc) > 0 else np.nan,
        U_min=float(np.nanmin(u)), y_at_Umin=float(y[int(np.nanargmin(u))]),
        reverse_flow=bool(np.nanmin(u) < -0.01),
        uu_peak=float(np.nanmax(g.uu.to_numpy())),
        uv_abspeak=float(np.nanmax(np.abs(g.uv.to_numpy()))),
        V_max=float(np.nanmax(v)), V_min=float(np.nanmin(v)),
    )


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    recs = []
    files = sorted(RAW.glob("*/*.dat"))
    for f in files:
        m = NAME_RE.search(f.name)
        meta = m.groupdict() if m else {}
        df = parse_file(f)
        if df.empty:
            continue
        for st, g in df.groupby("station"):
            r = station_metrics(g)
            r.update(geometry=f.parent.name, file=f.name,
                     mach=float(meta.get("mach") or np.nan),
                     cone_angle_deg=float(meta.get("ang") or np.nan),
                     level=int(meta["lvl"]) if meta.get("lvl") else -1,
                     sweep_deg=float(meta["theta"]) if meta.get("theta") else 0.0,
                     Re_code=float(meta.get("re") or np.nan),
                     station=st, x_minus_xi=float(g.x_minus_xi.iloc[0]))
            recs.append(r)
    res = pd.DataFrame(recs)
    res.to_csv(OUT / "hmve_station_metrics.csv", index=False)

    # per-file summary: strongest interaction station, separation extent
    rows = []
    for (fname,), g in res.groupby(["file"]):
        g = g.sort_values("x_minus_xi")
        sep = g[g.reverse_flow]
        rows.append(dict(
            file=fname, geometry=g.geometry.iloc[0], mach=g.mach.iloc[0],
            cone_angle_deg=g.cone_angle_deg.iloc[0], sweep_deg=g.sweep_deg.iloc[0],
            Re_code=g.Re_code.iloc[0], n_stations=int(len(g)),
            x_min=float(g.x_minus_xi.min()), x_max=float(g.x_minus_xi.max()),
            n_separated=int(sep.shape[0]),
            x_sep_start=float(sep.x_minus_xi.min()) if len(sep) else np.nan,
            x_sep_end=float(sep.x_minus_xi.max()) if len(sep) else np.nan,
            sep_length_mm=float(sep.x_minus_xi.max() - sep.x_minus_xi.min()) if len(sep) else 0.0,
            U_min_global=float(g.U_min.min()),
            max_uu=float(g.uu_peak.max()),
            max_abs_uv=float(g.uv_abspeak.max()),
            delta995_max=float(g.delta995_mm.max()),
            delta_star_max=float(g.delta_star_mm.max()),
            H_upstream=float(g.sort_values("x_minus_xi").H.iloc[0]),
        ))
    summ = pd.DataFrame(rows).sort_values(["geometry", "mach", "cone_angle_deg", "Re_code"])
    summ.to_csv(OUT / "hmve_file_summary.csv", index=False)
    print(summ.to_string(index=False))
    meta = dict(
        n_files=int(len(files)),
        n_stations_total=int(len(res)),
        mach_values=sorted(res.mach.dropna().unique().tolist()),
        cone_angles=sorted(res.cone_angle_deg.dropna().unique().tolist()),
        geometries=sorted(res.geometry.unique().tolist()),
        fields=["U/U1", "V/U1", "W/U1", "uu/U1^2", "vv/U1^2", "ww/U1^2", "uv/U1^2"],
        note=("Normalisation is by freestream U1; absolute velocities and Reynolds "
              "stresses in m/s are NOT provided in this archive. Wall pressure files "
              "are not part of HMVE2_PIVprofiles.zip."),
    )
    (OUT / "hmve_meta.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
    print(json.dumps(meta, indent=2))


if __name__ == "__main__":
    main()
