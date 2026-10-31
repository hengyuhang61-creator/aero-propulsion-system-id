"""R14 SBLI2.05 UQ: shock-crossing-point regression with grouped cross-validation.

Design decisions (frozen before seeing test results):
  * Inputs  : h_bump [mm] in {0.11,0.28,0.48,0.66,0.89}, x_bump [mm] in 9 levels.
  * Targets : dx_scp, dy_scp [mm] relative to the unperturbed interaction.
  * Fitting uses the 45 perturbed cases only. The unperturbed case is a physical
    consistency check (prediction at h=0 must approach 0), not a training point,
    because its x_bump is undefined.
  * No random 80/20 split is used. Validation is grouped:
      - LOGO-X : leave one x_bump level out (5 cases per fold, 9 folds)
      - LOGO-H : leave one h_bump level out (9 cases per fold, 5 folds)
  * All scaling/standardisation and hyper-parameter selection happen inside the
    training fold only.

The thesis (Campo 2014, ch.4) reports parametric/qualitative trends for the UQ
campaign and does not publish a closed-form polynomial response surface for
dx_scp/dy_scp. The polynomial models here are therefore *reconstructed
baselines*, not a reproduction of a published formula.
"""

from __future__ import annotations

import os as _os

R14_ROOT = _os.environ.get("R14_ROOT", r"C:\Work\research\aviation_algorithm_r14_public_data_20261031")


import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.interpolate import griddata
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import RBF, ConstantKernel, Matern, WhiteKernel
from sklearn.linear_model import LinearRegression
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import PolynomialFeatures, StandardScaler

ROOT = Path(R14_ROOT)
SUMMARY = ROOT / "data/raw/sbli205/UQ_experiment/ASCII/dataSummary"
OUT = ROOT / "results"


def load_table() -> pd.DataFrame:
    """Load the 45-case design table at full precision.

    The ASCII dataSummary is rounded to 0.01 mm; dataSummary.mat carries the
    unrounded values (e.g. case 25: -4.76416856 vs -4.76). We use the .mat
    vectors and keep the ASCII file as the human-readable cross-check.
    """
    import scipy.io as sio

    mat = sio.loadmat(
        ROOT / "data/raw/sbli205/UQ_experiment/Matlab/dataSummary.mat", squeeze_me=True
    )
    df = pd.DataFrame(
        dict(
            case=np.asarray(mat["case_number_vector"], dtype=int).ravel(),
            x_bump=np.asarray(mat["x_bump_vector"], dtype=float).ravel(),
            h_bump=np.asarray(mat["h_bump_vector"], dtype=float).ravel(),
            dx_scp=np.asarray(mat["Delta_x_scp_vector"], dtype=float).ravel(),
            dy_scp=np.asarray(mat["Delta_y_scp_vector"], dtype=float).ravel(),
        )
    ).sort_values("case").reset_index(drop=True)
    assert len(df) == 45
    assert df.h_bump.nunique() == 5 and df.x_bump.nunique() == 9
    ascii_tbl = pd.read_csv(ROOT / "results/sbli205_cases.csv") if (
        ROOT / "results/sbli205_cases.csv"
    ).exists() else None
    if ascii_tbl is not None:
        d = np.abs(df.dx_scp.to_numpy() - ascii_tbl.dx_scp.to_numpy())
        assert d.max() < 0.006, "ASCII summary and .mat vectors disagree beyond rounding"
    return df


def make_poly(degree: int):
    return make_pipeline(
        PolynomialFeatures(degree=degree, include_bias=False),
        StandardScaler(),
        LinearRegression(),
    )


def make_gpr(seed: int = 0):
    kernel = ConstantKernel(1.0, (1e-2, 1e3)) * Matern(
        length_scale=[10.0, 10.0], length_scale_bounds=(1e-1, 1e4), nu=2.5
    ) + WhiteKernel(noise_level=1e-2, noise_level_bounds=(1e-6, 1e1))
    return GaussianProcessRegressor(
        kernel=kernel, normalize_y=True, n_restarts_optimizer=8, random_state=seed
    )


def interp_predict(xtr: np.ndarray, ytr: np.ndarray, xte: np.ndarray) -> tuple[np.ndarray, str]:
    """Linear 2-D interpolation; falls back to nearest outside the convex hull."""
    out = griddata(xtr, ytr, xte, method="linear")
    kind = "linear"
    if np.any(~np.isfinite(out)):
        near = griddata(xtr, ytr, xte, method="nearest")
        out = np.where(np.isfinite(out), out, near)
        kind = "linear+nearest_fallback"
    return out, kind


class Surrogate:
    """Wrap one model family so CV code is identical for all of them."""

    def __init__(self, name: str):
        self.name = name

    def fit_predict(self, xtr, ytr, xte):
        if self.name == "poly2":
            m = make_poly(2).fit(xtr, ytr)
            return m.predict(xte), "ols_quadratic"
        if self.name == "poly3":
            m = make_poly(3).fit(xtr, ytr)
            return m.predict(xte), "ols_cubic"
        if self.name == "interp":
            return interp_predict(xtr, ytr, xte)
        if self.name == "gpr":
            m = make_gpr().fit(xtr, ytr)
            return m.predict(xte), "gpr_matern52"
        raise ValueError(self.name)


def metrics(y: np.ndarray, p: np.ndarray) -> dict:
    e = p - y
    return dict(
        mae=float(np.mean(np.abs(e))),
        rmse=float(np.sqrt(np.mean(e**2))),
        max_abs=float(np.max(np.abs(e))),
        bias=float(np.mean(e)),
        n=int(y.size),
    )


def grouped_cv(df: pd.DataFrame, group_col: str, model_names) -> pd.DataFrame:
    recs = []
    for g in sorted(df[group_col].unique()):
        te = df[group_col] == g
        tr = ~te
        xtr = df.loc[tr, ["h_bump", "x_bump"]].to_numpy()
        xte = df.loc[te, ["h_bump", "x_bump"]].to_numpy()
        for tgt in ("dx_scp", "dy_scp"):
            ytr = df.loc[tr, tgt].to_numpy()
            yte = df.loc[te, tgt].to_numpy()
            for name in model_names:
                pred, kind = Surrogate(name).fit_predict(xtr, ytr, xte)
                for i, (idx, yv, pv) in enumerate(zip(df.index[te], yte, pred)):
                    recs.append(
                        dict(
                            scheme=f"LOGO_{group_col}",
                            held_out=g,
                            case=int(df.loc[idx, "case"]),
                            h_bump=float(df.loc[idx, "h_bump"]),
                            x_bump=float(df.loc[idx, "x_bump"]),
                            target=tgt,
                            model=name,
                            method=kind,
                            y_true=float(yv),
                            y_pred=float(pv),
                            error=float(pv - yv),
                        )
                    )
    return pd.DataFrame(recs)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    df = load_table()
    models = ["poly2", "poly3", "interp", "gpr"]

    all_cv = []
    for gcol in ("x_bump", "h_bump"):
        all_cv.append(grouped_cv(df, gcol, models))
    cv = pd.concat(all_cv, ignore_index=True)
    cv.to_csv(OUT / "sbli205_cv_predictions.csv", index=False)

    # aggregate metrics
    rows = []
    for (scheme, target, model), sub in cv.groupby(["scheme", "target", "model"]):
        m = metrics(sub.y_true.to_numpy(), sub.y_pred.to_numpy())
        m.update(scheme=scheme, target=target, model=model)
        rows.append(m)
    agg = pd.DataFrame(rows)[["scheme", "target", "model", "n", "mae", "rmse", "max_abs", "bias"]]
    agg = agg.sort_values(["scheme", "target", "rmse"]).reset_index(drop=True)
    agg.to_csv(OUT / "sbli205_cv_metrics.csv", index=False)

    # extrapolation flag: in LOGO_x, the held-out x is outside the training x-range
    # only when it is the global min or max. Interior held-out positions are
    # interpolation in x but extrapolation in the h-x design box edge.
    xmin, xmax = df.x_bump.min(), df.x_bump.max()
    cv["x_position_type"] = np.where(
        cv.held_out.isin([xmin, xmax]) & (cv.scheme == "LOGO_x_bump"),
        "boundary_extrapolation",
        "interior",
    )
    br = []
    for (scheme, target, model, ptype), sub in cv.groupby(
        ["scheme", "target", "model", "x_position_type"]
    ):
        m = metrics(sub.y_true.to_numpy(), sub.y_pred.to_numpy())
        m.update(scheme=scheme, target=target, model=model, position_type=ptype)
        br.append(m)
    pd.DataFrame(br).to_csv(OUT / "sbli205_cv_by_position_type.csv", index=False)

    # full-data fits + h=0 consistency check + a-priori trend diagnostics
    full = {}
    xtr = df[["h_bump", "x_bump"]].to_numpy()
    for name in models:
        entry = {}
        for tgt in ("dx_scp", "dy_scp"):
            pred, kind = Surrogate(name).fit_predict(
                xtr, df[tgt].to_numpy(), np.array([[0.0, -57.2]])
            )
            entry[tgt] = dict(pred_at_h0_1mm=float(pred[0]), method=kind)
        full[name] = entry

    summary = dict(
        n_cases=int(len(df)),
        h_levels=sorted(df.h_bump.unique().tolist()),
        x_levels=sorted(df.x_bump.unique().tolist()),
        target_ranges=dict(
            dx_scp=[float(df.dx_scp.min()), float(df.dx_scp.max())],
            dy_scp=[float(df.dy_scp.min()), float(df.dy_scp.max())],
        ),
        best_model_by_scheme={
            f"{s}|{t}": m
            for (s, t), m in agg.sort_values("rmse")
            .groupby(["scheme", "target"])
            .first()["model"]
            .to_dict()
            .items()
        },
        h0_consistency=full,
        note=(
            "Polynomial baselines are reconstructed; Campo (2014) ch.4 does not publish "
            "a closed-form response surface for dx_scp/dy_scp."
        ),
    )
    (OUT / "sbli205_model_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")

    print(agg.to_string(index=False))
    print("\n--- h=0 consistency (should be ~0) ---")
    print(json.dumps(full, indent=2))


if __name__ == "__main__":
    main()
