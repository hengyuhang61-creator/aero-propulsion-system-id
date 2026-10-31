"""Busemann supplementary-video metadata probing and shock-front tracking.

Status of the real data: the Springer supplementary videos could not be retrieved
(CDN throughput measured at 0.6-18 kB/s against ~1.1 MB segments; see
04_BUSEMANN_VIDEO_TRACKING.md). This module is therefore delivered as a tested
tool, exercised on a synthetic clip only. It makes no claim about the experiment.

Two tracking routes are implemented because the two imaging modalities carry
different information:
  * schlieren : optical density gradient. Track the leading edge of |dI/dx|.
                No absolute pressure can be recovered.
  * psp       : normalised intensity ratio. Track a threshold crossing on the
                normalised field (the paper uses R = 0.35). Without a calibration
                and reference image, intensity is NOT pressure.

Output contract:
  reliable time base  -> frame_index, time_s, shock_x_mm, shock_v_m_s, uncertainty
  unreliable time base-> frame_index, shock_x_pixel, tracking_confidence
The code refuses to emit velocities when the time base is not verified.
"""

from __future__ import annotations

import json
import subprocess
from dataclasses import dataclass, asdict
from pathlib import Path

import numpy as np


@dataclass
class VideoMeta:
    path: str
    codec: str
    width: int
    height: int
    r_frame_rate: str
    avg_frame_rate: str
    nb_frames: int
    duration_s: float
    is_vfr_suspect: bool
    container: str


def probe(path: str | Path) -> VideoMeta:
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "v:0", "-count_frames",
         "-show_entries",
         "stream=codec_name,width,height,r_frame_rate,avg_frame_rate,nb_read_frames,duration"
         ":format=format_name,duration",
         "-of", "json", str(path)],
        capture_output=True, text=True, errors="replace",
    )
    if out.returncode != 0:
        raise RuntimeError(f"ffprobe failed: {out.stderr[:300]}")
    d = json.loads(out.stdout)
    s = d["streams"][0]
    rfr, afr = s.get("r_frame_rate", "0/1"), s.get("avg_frame_rate", "0/1")
    num = lambda f: (float(f.split("/")[0]) / float(f.split("/")[1])) if "/" in f else float(f)
    dur = float(s.get("duration") or d.get("format", {}).get("duration") or 0.0)
    return VideoMeta(
        path=str(path), codec=s.get("codec_name", "?"),
        width=int(s.get("width", 0)), height=int(s.get("height", 0)),
        r_frame_rate=rfr, avg_frame_rate=afr,
        nb_frames=int(s.get("nb_read_frames") or 0), duration_s=dur,
        is_vfr_suspect=abs(num(rfr) - num(afr)) > 1e-3,
        container=d.get("format", {}).get("format_name", "?"),
    )


def read_gray(path: str | Path, max_frames: int | None = None) -> np.ndarray:
    import cv2

    cap = cv2.VideoCapture(str(path))
    frames = []
    while True:
        ok, fr = cap.read()
        if not ok:
            break
        frames.append(cv2.cvtColor(fr, cv2.COLOR_BGR2GRAY).astype(np.float32) / 255.0)
        if max_frames and len(frames) >= max_frames:
            break
    cap.release()
    if not frames:
        raise RuntimeError(f"no frames decoded from {path}")
    return np.stack(frames)


def track_schlieren(frames: np.ndarray, row_band=(0.35, 0.65), k_sigma: float = 3.0,
                    x_search=(0.05, 0.95)) -> dict:
    """Leading edge of the streamwise intensity gradient, per frame."""
    n, h, w = frames.shape
    r0, r1 = int(row_band[0] * h), int(row_band[1] * h)
    c0, c1 = int(x_search[0] * w), int(x_search[1] * w)
    xs = []
    conf = []
    for i in range(n):
        prof = frames[i, r0:r1, :].mean(axis=0)
        g = np.abs(np.gradient(prof))[c0:c1]
        thr = g.mean() + k_sigma * g.std()
        idx = np.where(g > thr)[0]
        if idx.size == 0:
            xs.append(np.nan); conf.append(0.0); continue
        xs.append(float(idx[0] + c0))
        conf.append(float(min(1.0, (g.max() - thr) / (g.std() + 1e-9) / 5.0)))
    return dict(x_pixel=np.array(xs), confidence=np.array(conf))


def track_psp_threshold(frames: np.ndarray, r_ref: float = 0.35,
                        row_band=(0.35, 0.65), x_search=(0.05, 0.95)) -> dict:
    """Crossing of the normalised intensity ratio R = r_ref (paper convention)."""
    n, h, w = frames.shape
    r0, r1 = int(row_band[0] * h), int(row_band[1] * h)
    c0, c1 = int(x_search[0] * w), int(x_search[1] * w)
    base = frames[0].mean()
    xs, conf = [], []
    for i in range(n):
        band = frames[i, r0:r1, :].mean(axis=0)
        R = band / (base + 1e-9)
        seg = R[c0:c1]
        cross = np.where(seg < r_ref)[0]
        if cross.size == 0:
            xs.append(np.nan); conf.append(0.0); continue
        xs.append(float(cross[0] + c0))
        conf.append(float(min(1.0, abs(seg.min() - r_ref) / (r_ref + 1e-9))))
    return dict(x_pixel=np.array(xs), confidence=np.array(conf))


def interpolate_manual(anchors: list[tuple[int, float]], n_frames: int) -> np.ndarray:
    """Piecewise-linear trajectory through human-annotated (frame, x) anchors."""
    a = sorted(anchors)
    f = np.array([p[0] for p in a], dtype=float)
    x = np.array([p[1] for p in a], dtype=float)
    return np.interp(np.arange(n_frames), f, x)


def write_trajectory(out_csv: Path, meta: VideoMeta, track: dict,
                     px_per_mm: float | None = None, time_base_verified: bool = False,
                     fps_override: float | None = None) -> dict:
    """Emit the contract-compliant table. Velocities require a verified time base."""
    import csv

    fps = fps_override if fps_override else (
        float(meta.r_frame_rate.split("/")[0]) / float(meta.r_frame_rate.split("/")[1])
        if "/" in meta.r_frame_rate else float(meta.r_frame_rate))
    n = len(track["x_pixel"])
    has_scale = px_per_mm is not None and px_per_mm > 0
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    with open(out_csv, "w", newline="", encoding="utf-8") as fh:
        wr = csv.writer(fh)
        if time_base_verified and has_scale:
            wr.writerow(["frame_index", "time_s", "shock_x_mm", "shock_v_m_s",
                         "uncertainty_mm", "tracking_confidence"])
            t = np.arange(n) / fps
            x_mm = track["x_pixel"] / px_per_mm
            v = np.gradient(x_mm, t) if n > 1 else np.zeros(n)
            for i in range(n):
                wr.writerow([i, f"{t[i]:.6f}", f"{x_mm[i]:.4f}", f"{v[i]:.2f}",
                             f"{1.0 / px_per_mm:.4f}", f"{track['confidence'][i]:.3f}"])
        else:
            wr.writerow(["frame_index", "shock_x_pixel", "tracking_confidence"])
            for i in range(n):
                wr.writerow([i, f"{track['x_pixel'][i]:.2f}", f"{track['confidence'][i]:.3f}"])
    return dict(rows=n, emitted="velocity" if (time_base_verified and has_scale) else "pixel_only",
                fps=fps, px_per_mm=px_per_mm,
                vfr_suspect=meta.is_vfr_suspect)


def summarize_metadata(paths: list[Path]) -> list[dict]:
    return [asdict(probe(p)) for p in paths]
