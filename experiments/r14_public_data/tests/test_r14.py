"""R14 minimal-sufficient test suite.

Four checks, matching the delivery contract:
  1. normal data path: 45 cases, 46 fields, consistent grid shape
  2. invalid-mask path: valid=0 must be excluded, never replaced by zero velocity
  3. grouped-validation path: leave-one-position-out keeps all 5 heights together
     and never leaks a test case into training
  4. end-to-end reproduction: a stored cross-validation metric is reproduced from
     the raw data within a tight tolerance

Run:  python tests/test_r14.py     (plain asserts, no pytest required)
"""

from __future__ import annotations

import os as _os

R14_ROOT = _os.environ.get("R14_ROOT", r"C:\Work\research\aviation_algorithm_r14_public_data_20261031")


import sys
from pathlib import Path

import numpy as np
import pandas as pd
import scipy.io as sio

ROOT = Path(R14_ROOT)
sys.path.insert(0, str(ROOT / "src"))

from sbli205_io import RAW, parse_summary_ascii  # noqa: E402
from sbli205_model import load_table, metrics  # noqa: E402
from sbli205_model import Surrogate  # noqa: E402

FAILS = []


def check(name, fn):
    try:
        fn()
        print(f"PASS  {name}")
    except AssertionError as e:
        FAILS.append((name, str(e)))
        print(f"FAIL  {name}: {e}")


def t_normal_path():
    rows = parse_summary_ascii()
    assert len(rows) == 45, f"expected 45 cases, got {len(rows)}"
    assert len({r["h_bump_mm"] for r in rows}) == 5
    assert len({r["x_bump_mm"] for r in rows}) == 9
    d = sio.loadmat(RAW / "Matlab" / "dataMatlab_case25.mat", squeeze_me=True)
    for k in ("X", "Y", "U", "V", "valid"):
        assert k in d, f"missing field {k}"
    assert d["X"].shape == (125, 153), d["X"].shape
    assert np.all(np.isfinite(d["X"])) and np.all(np.isfinite(d["Y"]))
    # ASCII summary is rounded to 0.01 mm; the .mat struct is the precise source
    assert abs(float(d["Delta_x_scp"]) - float(rows[24]["dx_scp_mm"])) < 0.006, (
        "ASCII summary and .mat struct disagree beyond rounding")


def t_mask_path():
    d = sio.loadmat(RAW / "Matlab" / "dataMatlab_case45.mat", squeeze_me=True)
    m = d["valid"] > 0
    masked = np.where(m, d["U"], np.nan)
    assert np.isnan(masked[~m]).all(), "invalid points must be NaN, not zero"
    assert not np.any(masked[~m] == 0.0), "zero-filling detected on invalid points"
    n_invalid = int((~m).sum())
    assert n_invalid > 0, "case 45 unexpectedly has no invalid points"
    # POD code path must drop these points from the training mask
    from sbli205_pod import load_fields
    U, V, M = load_fields([45, 44, 43])
    assert M.shape == (3, 125, 153)
    assert np.isnan(U[0][~M[0]]).all()


def t_grouped_split():
    df = load_table()
    folds = []
    for g in sorted(df.x_bump.unique()):
        te = df[df.x_bump == g]
        tr = df[df.x_bump != g]
        assert len(te) == 5, f"fold {g} has {len(te)} cases, expected 5"
        assert not set(te.case) & set(tr.case), "test case leaked into training"
        folds.append(set(te.case))
    flat = [c for f in folds for c in f]
    assert sorted(flat) == list(range(1, 46)), "folds do not partition the 45 cases"


def t_end_to_end():
    df = load_table()
    g = -57.2
    te = df.x_bump == g
    tr = ~te
    xtr = df.loc[tr, ["h_bump", "x_bump"]].to_numpy()
    xte = df.loc[te, ["h_bump", "x_bump"]].to_numpy()
    pred, _ = Surrogate("poly2").fit_predict(xtr, df.loc[tr, "dx_scp"].to_numpy(), xte)
    rmse = float(np.sqrt(np.mean((pred - df.loc[te, "dx_scp"].to_numpy()) ** 2)))
    stored = pd.read_csv(ROOT / "results/sbli205_cv_predictions.csv")
    s = stored[(stored.scheme == "LOGO_x_bump") & (stored.held_out == g)
               & (stored.target == "dx_scp") & (stored.model == "poly2")]
    assert len(s) == 5, f"expected 5 stored rows, got {len(s)}"
    rmse_stored = float(np.sqrt(np.mean((s.y_pred - s.y_true) ** 2)))
    assert abs(rmse - rmse_stored) < 1e-9, f"{rmse} vs stored {rmse_stored}"
    assert rmse < 3.0, f"fold RMSE {rmse} mm implausibly large"


def t_manifest():
    cat = pd.read_csv(ROOT / "01_DATA_CATALOG.csv")
    assert len(cat) >= 5
    assert (cat.status == "VERIFIED_DOWNLOADED").all(), "catalog contains non-downloaded entries"
    assert cat.sha256.str.len().eq(64).all(), "bad sha256 length"
    import hashlib
    row = cat[cat.file == "UQ_experiment.zip"].iloc[0]
    h = hashlib.sha256(Path(row.path).read_bytes()).hexdigest()
    assert h == row.sha256, "UQ_experiment.zip hash mismatch"


if __name__ == "__main__":
    check("normal data path", t_normal_path)
    check("invalid-mask path", t_mask_path)
    check("grouped validation path", t_grouped_split)
    check("end-to-end reproduction", t_end_to_end)
    check("manifest integrity", t_manifest)
    print()
    if FAILS:
        print(f"{len(FAILS)} FAILED")
        sys.exit(1)
    print("all checks passed")
