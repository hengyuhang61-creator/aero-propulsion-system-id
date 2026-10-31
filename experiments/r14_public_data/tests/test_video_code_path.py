"""Code-path validation of the shock tracker on a SYNTHETIC clip.

This is NOT experimental data and NOT a physics result. It only proves that the
tracking and output-contract code recovers a known moving edge, and that the
writer refuses to emit velocities without a verified time base and pixel scale.
"""

from __future__ import annotations

import os as _os

R14_ROOT = _os.environ.get("R14_ROOT", r"C:\Work\research\aviation_algorithm_r14_public_data_20261031")


import csv
import subprocess
import sys
from pathlib import Path

import numpy as np

ROOT = Path(R14_ROOT)
sys.path.insert(0, str(ROOT / "src"))

from busemann_video import (  # noqa: E402
    interpolate_manual, probe, track_psp_threshold, track_schlieren, write_trajectory,
)

TMP = ROOT / "results" / "synthetic_video_test"
FAILS = []


def check(name, fn):
    try:
        fn(); print(f"PASS  {name}")
    except AssertionError as e:
        FAILS.append(name); print(f"FAIL  {name}: {e}")


def make_clip(path: Path, n=40, h=180, w=320, px_per_frame=2.0, start=120.0) -> np.ndarray:
    import cv2

    path.parent.mkdir(parents=True, exist_ok=True)
    vw = cv2.VideoWriter(str(path), cv2.VideoWriter_fourcc(*"mp4v"), 10.0, (w, h), False)
    truth = []
    for i in range(n):
        img = np.full((h, w), 40, np.uint8)
        x = int(start + px_per_frame * i)
        img[:, x:] = 220                     # bright downstream region
        img[:, max(0, x - 1):x + 1] = 10     # dark shock line
        vw.write(img)
        truth.append(x)
    vw.release()
    return np.array(truth, dtype=float)


def t_metadata():
    p = TMP / "synthetic.mp4"
    if not p.exists():
        make_clip(p)
    m = probe(p)
    assert m.nb_frames == 40, f"expected 40 frames, got {m.nb_frames}"
    assert (m.width, m.height) == (320, 180), (m.width, m.height)
    assert not m.is_vfr_suspect, "synthetic CFR clip mis-flagged as VFR"


def t_tracking_accuracy():
    from busemann_video import read_gray
    p = TMP / "synthetic.mp4"
    truth = make_clip(p)
    frames = read_gray(p)
    tr = track_schlieren(frames, row_band=(0.2, 0.8), x_search=(0.0, 1.0))
    ok = np.isfinite(tr["x_pixel"])
    assert ok.sum() > 30, f"only {ok.sum()} frames tracked"
    err = np.abs(tr["x_pixel"][ok] - truth[ok])
    assert err.max() <= 3.0, f"max tracking error {err.max():.1f} px"
    assert err.mean() <= 1.5, f"mean tracking error {err.mean():.1f} px"
    # PSP route on the same synthetic contrast step
    tp = track_psp_threshold(frames, r_ref=0.35, row_band=(0.2, 0.8), x_search=(0.0, 1.0))
    okp = np.isfinite(tp["x_pixel"])
    assert okp.sum() > 30, "PSP-threshold route failed to track the synthetic step"


def t_manual_anchor():
    x = interpolate_manual([(0, 100.0), (10, 120.0), (20, 140.0)], 21)
    assert x[0] == 100.0 and x[20] == 140.0 and abs(x[5] - 110.0) < 1e-9


def t_output_contract():
    from busemann_video import read_gray
    p = TMP / "synthetic.mp4"
    m = probe(p)
    frames = read_gray(p)
    tr = track_schlieren(frames, row_band=(0.2, 0.8), x_search=(0.0, 1.0))
    # without verified time base / scale -> pixel only
    a = write_trajectory(TMP / "out_pixel.csv", m, tr)
    hdr = next(csv.reader(open(TMP / "out_pixel.csv", encoding="utf-8")))
    assert hdr == ["frame_index", "shock_x_pixel", "tracking_confidence"], hdr
    assert a["emitted"] == "pixel_only"
    # with both -> velocity columns
    b = write_trajectory(TMP / "out_velocity.csv", m, tr, px_per_mm=4.5, time_base_verified=True)
    hdr2 = next(csv.reader(open(TMP / "out_velocity.csv", encoding="utf-8")))
    assert "shock_v_m_s" in hdr2 and b["emitted"] == "velocity", hdr2


if __name__ == "__main__":
    check("video metadata via ffprobe", t_metadata)
    check("tracker accuracy vs known truth", t_tracking_accuracy)
    check("manual anchor interpolation", t_manual_anchor)
    check("output contract (pixel vs velocity)", t_output_contract)
    print()
    if FAILS:
        print(f"{len(FAILS)} FAILED"); sys.exit(1)
    print("all synthetic code-path checks passed (not experimental evidence)")
