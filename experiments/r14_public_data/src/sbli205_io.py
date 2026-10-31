"""R14 SBLI2.05 UQ dataset I/O and integrity checks.

Raw originals are read-only. This module only reads them and produces
processed arrays that keep an explicit pointer back to the raw file.

Coordinate definitions (verbatim from README_UQ.pdf):
  X = x_absolute - x_scp_unperturbed   [mm]   (x_absolute origin at ramp foot)
  Y = vertical coordinate, origin on bottom wall [mm]
  Z = 21 mm for ALL cases
  U = mean streamwise velocity [m/s]
  V = mean vertical velocity [m/s]
  valid = 1 valid PIV vector, 0 = invalid (low vector yield) -> must be masked
"""

from __future__ import annotations

import os as _os

R14_ROOT = _os.environ.get("R14_ROOT", r"C:\Work\research\aviation_algorithm_r14_public_data_20261031")


import hashlib
import json
import re
from pathlib import Path

import numpy as np
import scipy.io as sio

RAW = Path(R14_ROOT + r"\data\raw\sbli205\UQ_experiment")
PROC = Path(R14_ROOT + r"\data\processed")
MANI = Path(R14_ROOT + r"\data\manifests")

CASE_RE = re.compile(r"case\s+number\s+(\d+)", re.IGNORECASE)


def sha256(path: Path, chunk: int = 1 << 20) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while True:
            b = f.read(chunk)
            if not b:
                break
            h.update(b)
    return h.hexdigest()


def parse_summary_ascii(path: Path = RAW / "ASCII" / "dataSummary") -> list[dict]:
    """Parse the tab/space delimited summary.

    NOTE (verified 2026-10-31): the ASCII header line reads
    'case number  x_bump  h_bump  Delta_x_scp  Delta_y_scp', but the numeric
    columns follow README_UQ.pdf Table 1, i.e. (h_bump, x_bump, dx, dy).
    Evidence: case 1 = 0.11, -75.20 and dataASCII_case1 header says
    'x_bump = -75.2 mm, h_bump = 0.11 mm'. The ASCII header order is therefore
    mislabelled; we parse by value semantics and keep the raw text.
    """
    rows = []
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        t = line.replace("\r", "").split()
        if len(t) != 5:
            continue
        if not t[0].isdigit():
            continue
        c, a, b, dx, dy = t
        rows.append(
            dict(
                case=int(c),
                h_bump_mm=float(a),
                x_bump_mm=float(b),
                dx_scp_mm=float(dx),
                dy_scp_mm=float(dy),
            )
        )
    rows.sort(key=lambda r: r["case"])
    assert [r["case"] for r in rows] == list(range(1, 46)), "summary case ids not 1..45"
    return rows


def load_case_mat(case: int | str) -> dict:
    name = "dataMatlab_unperturbed.mat" if case == "unperturbed" else f"dataMatlab_case{case}.mat"
    d = sio.loadmat(RAW / "Matlab" / name, squeeze_me=True)
    return {k: d[k] for k in ("X", "Y", "U", "V", "valid", "Z")}


def load_ascii_case(case: int | str) -> dict:
    name = "dataASCII_unperturbed" if case == "unperturbed" else f"dataASCII_case{case}"
    arr = np.loadtxt(RAW / "ASCII" / name, skiprows=3, usecols=(0, 1, 2, 3, 4))
    return dict(X=arr[:, 0], Y=arr[:, 1], U=arr[:, 2], V=arr[:, 3], valid=arr[:, 4])


def build(cases=(1, 2, 45), out_name: str = "sbli205_grid.npz") -> dict:
    PROC.mkdir(parents=True, exist_ok=True)
    MANI.mkdir(parents=True, exist_ok=True)
    summary = parse_summary_ascii()

    # grid identity check over all 46 fields
    ref = load_case_mat("unperturbed")
    X0, Y0 = ref["X"], ref["Y"]
    grid_identical = True
    max_dx = max_dy = 0.0
    valid_frac = {}
    U = np.full((46, *X0.shape), np.nan)
    V = np.full((46, *X0.shape), np.nan)
    M = np.zeros((46, *X0.shape), dtype=np.uint8)
    order = ["unperturbed"] + [r["case"] for r in summary]
    for i, c in enumerate(order):
        d = load_case_mat(c)
        max_dx = max(max_dx, float(np.max(np.abs(d["X"] - X0))))
        max_dy = max(max_dy, float(np.max(np.abs(d["Y"] - Y0))))
        if d["X"].shape != X0.shape:
            grid_identical = False
        m = (d["valid"] > 0).astype(np.uint8)
        M[i] = m
        U[i] = np.where(m > 0, d["U"], np.nan)
        V[i] = np.where(m > 0, d["V"], np.nan)
        valid_frac[str(c)] = float(m.mean())
    grid_identical = grid_identical and max_dx < 1e-6 and max_dy < 1e-6

    # ASCII vs MATLAB cross-check on a sample of cases
    ascii_checks = {}
    for c in cases:
        a = load_ascii_case(c)
        dm = load_case_mat(c)
        Ua = a["U"].reshape(X0.shape)
        Va = a["V"].reshape(X0.shape)
        ma = a["valid"].reshape(X0.shape)
        ascii_checks[str(c)] = dict(
            max_abs_dU=float(np.nanmax(np.abs(Ua - dm["U"]))),
            max_abs_dV=float(np.nanmax(np.abs(Va - dm["V"]))),
            valid_mismatch=int(np.sum((ma > 0) != (dm["valid"] > 0))),
        )

    np.savez_compressed(
        PROC / out_name,
        X=X0,
        Y=Y0,
        U=U,
        V=V,
        valid=M,
        order=np.array([str(o) for o in order]),
        h_bump=np.array([0.0] + [r["h_bump_mm"] for r in summary]),
        x_bump=np.array([np.nan] + [r["x_bump_mm"] for r in summary]),
        dx_scp=np.array([0.0] + [r["dx_scp_mm"] for r in summary]),
        dy_scp=np.array([0.0] + [r["dy_scp_mm"] for r in summary]),
    )

    common = np.all(M > 0, axis=0)
    meta = dict(
        source_zip=str(RAW.parent / "UQ_experiment.zip"),
        source_zip_sha256=sha256(RAW.parent / "UQ_experiment.zip"),
        n_cases=45,
        n_fields=46,
        grid_shape=list(X0.shape),
        grid_identical_across_cases=bool(grid_identical),
        max_grid_deviation_mm=dict(X=max_dx, Y=max_dy),
        X_range_mm=[float(X0.min()), float(X0.max())],
        Y_range_mm=[float(Y0.min()), float(Y0.max())],
        Z_mm=21.0,
        per_case_valid_fraction=valid_frac,
        common_valid_points=int(common.sum()),
        common_valid_fraction=float(common.mean()),
        ascii_vs_matlab=ascii_checks,
        summary_header_note=(
            "ASCII dataSummary header order (x_bump,h_bump) contradicts README Table 1 "
            "and dataASCII_caseN header lines; values parsed as (h_bump,x_bump)."
        ),
    )
    (MANI / "sbli205_dataset_meta.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
    return meta


if __name__ == "__main__":
    m = build()
    print(json.dumps({k: m[k] for k in (
        "n_cases", "n_fields", "grid_shape", "grid_identical_across_cases",
        "max_grid_deviation_mm", "X_range_mm", "Y_range_mm",
        "common_valid_points", "common_valid_fraction", "ascii_vs_matlab")}, indent=2))
