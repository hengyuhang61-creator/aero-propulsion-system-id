"""R14 SBLI2.05 UQ: POD + coefficient regression for the mean velocity field.

Strict rules implemented here:
  * The POD basis, the mean field, the common valid mask and the mode count are
    built from TRAINING cases only.
  * valid=0 points are excluded, never replaced by zero velocity.
  * Fields are compared on the array lattice (index alignment). Justification:
    the distributed grids are translated by up to 2.04 mm between x_bump groups,
    and an index-aligned comparison reproduces the physical perturbation ranking
    (corr(|dx_scp|, field RMS difference) = 0.93) better than a raw-coordinate
    alignment (0.73). See 02_DATA_ELIGIBILITY_AUDIT.md.
  * Baselines are the training mean field and the nearest training case, so that
    "POD helps" is a measured statement rather than an assumption.
"""

from __future__ import annotations

import os as _os

R14_ROOT = _os.environ.get("R14_ROOT", r"C:\Work\research\aviation_algorithm_r14_public_data_20261031")


import json
from pathlib import Path

import numpy as np
import pandas as pd
import scipy.io as sio
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import ConstantKernel, Matern, WhiteKernel

ROOT = Path(R14_ROOT)
RAW = ROOT / "data/raw/sbli205/UQ_experiment/Matlab"
SUMMARY = ROOT / "data/raw/sbli205/UQ_experiment/ASCII/dataSummary"
OUT = ROOT / "results"


def load_table() -> pd.DataFrame:
    rows = []
    for line in SUMMARY.read_text(encoding="utf-8", errors="replace").splitlines():
        t = line.replace("\r", "").split()
        if len(t) == 5 and t[0].isdigit():
            rows.append(dict(case=int(t[0]), h_bump=float(t[1]), x_bump=float(t[2]),
                             dx_scp=float(t[3]), dy_scp=float(t[4])))
    return pd.DataFrame(rows).sort_values("case").reset_index(drop=True)


def load_fields(cases):
    U, V, M = [], [], []
    for c in cases:
        d = sio.loadmat(RAW / f"dataMatlab_case{c}.mat", squeeze_me=True)
        m = d["valid"] > 0
        M.append(m)
        U.append(np.where(m, d["U"], np.nan))
        V.append(np.where(m, d["V"], np.nan))
    return np.array(U), np.array(V), np.array(M)


def gpr():
    k = ConstantKernel(1.0, (1e-2, 1e3)) * Matern(
        length_scale=[10.0, 10.0], length_scale_bounds=(1e-1, 1e4), nu=2.5
    ) + WhiteKernel(1e-4, (1e-8, 1e0))
    return GaussianProcessRegressor(kernel=k, normalize_y=True,
                                    n_restarts_optimizer=5, random_state=0)


def fit_pod(Ut, Vt, mask, energy=0.99, max_rank=12, fixed_rank=None):
    """POD on stacked (U,V) restricted to the training common mask."""
    n = Ut.shape[0]
    A = np.concatenate([Ut[:, mask], Vt[:, mask]], axis=1)  # (n, 2*N)
    mean = A.mean(axis=0)
    A0 = A - mean
    u, s, vt = np.linalg.svd(A0, full_matrices=False)
    var = s**2 / np.sum(s**2)
    r = int(np.searchsorted(np.cumsum(var), energy) + 1)
    r = min(r, max_rank, len(s))
    if fixed_rank is not None:
        r = min(int(fixed_rank), len(s))
    return mean, vt[:r], s, var, r


def predict_coeffs(Xtr, Ctr, Xte):
    preds = []
    for k in range(Ctr.shape[1]):
        g = gpr().fit(Xtr, Ctr[:, k])
        preds.append(g.predict(Xte))
    return np.column_stack(preds)


def metrics(y, p):
    e = p - y
    return dict(mae=float(np.mean(np.abs(e))), rmse=float(np.sqrt(np.mean(e**2))),
                max_abs=float(np.max(np.abs(e))), bias=float(np.mean(e)))


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    df = load_table()
    recs, recon_energy = [], []
    ranks = [4, 6, 8, 12, 16, 20]
    for g in sorted(df.x_bump.unique()):
        te = df.x_bump == g
        tr = ~te
        ctr = df.loc[tr, "case"].to_numpy()
        cte = df.loc[te, "case"].to_numpy()
        Utr, Vtr, Mtr = load_fields(ctr)
        Ute, Vte, Mte = load_fields(cte)
        mask = np.all(Mtr, axis=0)
        Atr = np.concatenate([Utr[:, mask], Vtr[:, mask]], axis=1)
        Xtr = df.loc[tr, ["h_bump", "x_bump"]].to_numpy()
        Xte = df.loc[te, ["h_bump", "x_bump"]].to_numpy()
        for rk in ranks:
            mean, modes, s, var, r = fit_pod(Utr, Vtr, mask, fixed_rank=rk)
            recon_energy.append(dict(held_out_x=float(g), rank=r,
                                     explained_variance=float(np.sum(var[:r])),
                                     common_mask_points=int(mask.sum())))
            Ctr = (Atr - mean) @ modes.T
            Cte = predict_coeffs(Xtr, Ctr, Xte)
            for i, case in enumerate(cte):
                rec = mean + Cte[i] @ modes
                Uhat = rec[: mask.sum()]
                Vhat = rec[mask.sum():]
                em = mask & Mte[i]
                Umeas, Vmeas = Ute[i][em], Vte[i][em]
                mu = metrics(Umeas, Uhat[em[mask]])
                mv = metrics(Vmeas, Vhat[em[mask]])
                recs.append(dict(scheme="LOGO_x_bump", held_out_x=float(g), case=int(case),
                                 model="pod_gpr", rank=r, n_points=int(em.sum()),
                                 U_mae=mu["mae"], U_rmse=mu["rmse"], U_max_abs=mu["max_abs"],
                                 V_mae=mv["mae"], V_rmse=mv["rmse"], V_max_abs=mv["max_abs"]))
        # baselines computed once per fold (rank-independent)
        mean, _, _, _, _ = fit_pod(Utr, Vtr, mask, fixed_rank=1)
        sc = np.array([1.0, 10.0])
        for i, case in enumerate(cte):
            em = mask & Mte[i]
            Umeas, Vmeas = Ute[i][em], Vte[i][em]
            d2 = np.sum(((Xtr - Xte[i]) * sc) ** 2, axis=1)
            nn = int(np.argmin(d2))
            for tag, (pu, pv) in {
                "train_mean": (mean[: mask.sum()][em[mask]], mean[mask.sum():][em[mask]]),
                "nearest_case": (Utr[nn][em], Vtr[nn][em]),
            }.items():
                mu, mv = metrics(Umeas, pu), metrics(Vmeas, pv)
                recs.append(dict(scheme="LOGO_x_bump", held_out_x=float(g), case=int(case),
                                 model=tag, rank=0, n_points=int(em.sum()),
                                 U_mae=mu["mae"], U_rmse=mu["rmse"], U_max_abs=mu["max_abs"],
                                 V_mae=mv["mae"], V_rmse=mv["rmse"], V_max_abs=mv["max_abs"]))
    res = pd.DataFrame(recs)
    res.to_csv(OUT / "sbli205_pod_predictions.csv", index=False)

    agg = (res.groupby(["model", "rank"])
           .agg(n_cases=("case", "nunique"),
                U_mae=("U_mae", "mean"), U_rmse=("U_rmse", "mean"),
                V_mae=("V_mae", "mean"), V_rmse=("V_rmse", "mean"),
                U_rmse_worst=("U_rmse", "max"), V_rmse_worst=("V_rmse", "max"))
           .reset_index().sort_values("U_rmse"))
    agg.to_csv(OUT / "sbli205_pod_metrics.csv", index=False)
    (OUT / "sbli205_pod_folds.json").write_text(json.dumps(recon_energy, indent=2), encoding="utf-8")
    print(agg.to_string(index=False))
    print("\nrank / explained variance per fold:")
    print(pd.DataFrame(recon_energy).to_string(index=False))


if __name__ == "__main__":
    main()
