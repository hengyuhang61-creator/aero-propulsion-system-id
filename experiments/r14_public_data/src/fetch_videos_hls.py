"""Segment-level downloader for the Springer/Movingimage supplementary videos.

ffmpeg stalls on this CDN, so the HLS playlists are parsed directly:
  master.m3u8 -> highest-bandwidth variant -> chunklist -> segments -> concat.
The result is a delivery rendition (max 1280x720, ~2.1 Mbit/s), NOT the authors'
original file. Spatial scale claims must be re-derived, not inherited.
"""

from __future__ import annotations

import os as _os

R14_ROOT = _os.environ.get("R14_ROOT", r"C:\Work\research\aviation_algorithm_r14_public_data_20261031")


import json
import re
import subprocess
import sys
from pathlib import Path
from urllib.parse import urljoin

ROOT = Path(R14_ROOT)
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"


def curl_text(url: str, timeout: int = 60) -> str:
    return subprocess.run(
        ["curl", "-sS", "-L", "-A", UA, "--max-time", str(timeout), url],
        capture_output=True, text=True, errors="replace",
    ).stdout


def curl_file(url: str, dest: Path, timeout: int = 180) -> bool:
    dest.parent.mkdir(parents=True, exist_ok=True)
    r = subprocess.run(
        ["curl", "-sS", "-L", "-f", "-A", UA, "--max-time", str(timeout), "-o", str(dest), url],
        capture_output=True, text=True, errors="replace",
    )
    return dest.exists() and dest.stat().st_size > 0 and r.returncode == 0


def fetch_one(video_id: str, player_id: str, channel: str, dest: Path) -> dict:
    page = curl_text(
        f"https://e.video-cdn.net/watch?video-id={video_id}&player-id={player_id}&channel-id={channel}"
    )
    m = re.findall(r'https://vod\.video-cdn\.net[^"]+?master\.m3u8[^"]*', page)
    if not m:
        return dict(ok=False, reason="no master playlist")
    master_url = m[0].replace("\\u0026", "&")
    master = curl_text(master_url)
    variants = re.findall(r"BANDWIDTH=(\d+),[^\n]*\n([^\n#]+)", master)
    if not variants:
        return dict(ok=False, reason="no variants")
    bw, rel = max(variants, key=lambda v: int(v[0]))
    variant_url = urljoin(master_url, rel.strip())
    chunk = curl_text(variant_url)
    segs = [ln.strip() for ln in chunk.splitlines() if ln.strip() and not ln.startswith("#")]
    if not segs:
        return dict(ok=False, reason="no segments", variant=variant_url[:80])
    tmp = dest.parent / f"_seg_{video_id}"
    tmp.mkdir(parents=True, exist_ok=True)
    ok_n = 0
    for i, s in enumerate(segs):
        if curl_file(urljoin(variant_url, s), tmp / f"{i:05d}.ts"):
            ok_n += 1
    listfile = tmp / "list.txt"
    listfile.write_text(
        "\n".join(f"file '{(tmp / f'{i:05d}.ts').as_posix()}'" for i in range(len(segs))),
        encoding="utf-8",
    )
    r = subprocess.run(
        ["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0",
         "-i", str(listfile), "-c", "copy", str(dest)],
        capture_output=True, text=True, errors="replace",
    )
    return dict(ok=dest.exists() and dest.stat().st_size > 0, bandwidth=int(bw),
                n_segments=len(segs), n_downloaded=ok_n,
                bytes=dest.stat().st_size if dest.exists() else 0,
                ffmpeg_rc=r.returncode, err=(r.stderr or "")[-300:])


def main(html_name: str, outdir: str, tag: str) -> None:
    html = (ROOT / "logs" / html_name).read_text(encoding="utf-8", errors="replace")
    ids = re.findall(
        r'data-video-selector="" id="MOESM(\d)">.*?video-id=([A-Za-z0-9_-]+)&amp;player-id=([A-Za-z0-9_-]+)&amp;channel-id=(\d+)',
        html, flags=re.S,
    )
    log = []
    for n, vid, pid, ch in ids:
        dest = ROOT / outdir / f"{tag}_MOESM{n}_{vid}.mp4"
        res = fetch_one(vid, pid, ch, dest)
        res.update(moesm=int(n), video_id=vid, dest=str(dest), kind="hls_segment_concat")
        log.append(res)
        print(json.dumps(res), flush=True)
    (ROOT / "logs" / f"video_download_{tag}.json").write_text(
        json.dumps(log, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], sys.argv[3])
