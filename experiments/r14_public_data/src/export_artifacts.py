"""Export the case table and one POD reconstruction example used by the figures."""

from __future__ import annotations

import os as _os

R14_ROOT = _os.environ.get("R14_ROOT", r"C:\Work\research\aviation_algorithm_r14_public_data_20261031")


from pathlib import Path

import numpy as np
import pandas as pd
import scipy.io as sio

import sys
sys.path.insert(0, str(Path(__file__).parent))
from sbli205_io import parse_summary_ascii, RAW  # noqa: E402
from sbli205_pod import fit_pod, load_fields, predict_coeffs  # noqa: E402

ROOT = Path(R14_ROOT)
RES = ROOT / "results"


def main() -> None:
    RES.mkdir(exist_ok=True)
    rows = parse_summary_ascii()
    df = pd.DataFrame(rows).rename(columns={"h_bump_mm": "h_bump", "x_bump_mm": "x_bump",
                                        "dx_scp_mm": "dx_scp", "dy_scp_mm": "dy_scp"})
    df = df.sort_values("case").reset_index(drop=True)
    df.to_csv(RES / "sbli205_cases.csv", index=False)
    print(df.head(3).to_string(index=False), "\n...", len(df), "cases")

    # POD example: hold out x = -57.2 (strongest documented field disturbance)
    hold = -57.2
    tr = df.x_bump != hold
    te = df.x_bump == hold
    Utr, Vtr, Mtr = load_fields(df.loc[tr, "case"].to_numpy())
    Ute, Vte, Mte = load_fields(df.loc[te, "case"].to_numpy())
    mask = np.all(Mtr, axis=0)
    mean, modes, s, var, r = fit_pod(Utr, Vtr, mask, fixed_rank=8)
    Atr = np.concatenate([Utr[:, mask], Vtr[:, mask]], axis=1)
    Ctr = (Atr - mean) @ modes.T
    Xtr = df.loc[tr, ["h_bump", "x_bump"]].to_numpy()
    Xte = df.loc[te, ["h_bump", "x_bump"]].to_numpy()
    Cte = predict_coeffs(Xtr, Ctr, Xte)
    # pick the case with the largest |dx_scp| inside the held-out group
    idx = int(np.argmax(np.abs(df.loc[te, "dx_scp"].to_numpy())))
    case = int(df.loc[te, "case"].to_numpy()[idx])
    rec = mean + Cte[idx] @ modes
    Upod = rec[: mask.sum()]
    Umeas = Ute[idx]
    d = sio.loadmat(RAW / "Matlab" / f"dataMatlab_case{case}.mat", squeeze_me=True)
    X, Y = d["X"], d["Y"]
    full_meas = np.where(Mte[idx], Umeas, np.nan)
    full_pod = np.full_like(full_meas, np.nan)
    full_pod[mask] = Upod
    em = mask & Mte[idx]
    np.savez_compressed(
        RES / "pod_example_fields.npz",
        X=X, Y=Y, U_meas=full_meas, U_pod=full_pod,
        mask=(em & mask), case=case, rank=r,
        held_out_x=hold,
    )
    print(f"POD example: case {case}, rank {r}, points {int((em & mask).sum())}")


if __name__ == "__main__":
    main()
