"""Download the Springer supplementary videos through their Movingimage player.

The article page embeds an iframe per supplementary file; the player page exposes
tokenised URLs. We take the highest-bitrate progressive MP4 when the player offers
one, otherwise the HLS variant list is downloaded with ffmpeg.

IMPORTANT PROVENANCE NOTE
These are CDN delivery renditions (transcoded, possibly frame-rate converted),
not the authors' original acquisition files. Any timing derived from them is
therefore a delivery-timeline quantity and is flagged as such in the R14 report.
"""

from __future__ import annotations

import os as _os

R14_ROOT = _os.environ.get("R14_ROOT", r"C:\Work\research\aviation_algorithm_r14_public_data_20261031")


import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(R14_ROOT)
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"


def player_sources(video_id: str, player_id: str, channel: str) -> dict:
    url = (
        f"https://e.video-cdn.net/watch?video-id={video_id}"
        f"&player-id={player_id}&channel-id={channel}"
    )
    html = subprocess.run(
        ["curl", "-sS", "-L", "-A", UA, "--max-time", "60", url],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    ).stdout
    mp4s = sorted(set(re.findall(r'https://asset-out-cdn[^"]+?\.mp4[^"]*', html)))
    hls = sorted(set(re.findall(r'https://vod\.video-cdn\.net[^"]+?master\.m3u8[^"]*', html)))
    clean = lambda s: s.replace("\\u0026", "&").replace("&amp;", "&")
    return dict(mp4=[clean(u) for u in mp4s], hls=[clean(u) for u in hls])


def download(url: str, dest: Path) -> dict:
    dest.parent.mkdir(parents=True, exist_ok=True)
    if url.endswith(".m3u8") or "m3u8" in url:
        cmd = ["ffmpeg", "-y", "-loglevel", "error", "-i", url, "-c", "copy", str(dest)]
    else:
        cmd = ["curl", "-sS", "-L", "-f", "-A", UA, "--max-time", "1800", "-o", str(dest), url]
    r = subprocess.run(cmd, capture_output=True, text=True, errors="replace")
    return dict(ok=dest.exists() and dest.stat().st_size > 0,
                bytes=dest.stat().st_size if dest.exists() else 0,
                rc=r.returncode, err=(r.stderr or "")[-400:])


def main(html_name: str, outdir: str, tag: str) -> None:
    html = (ROOT / "logs" / html_name).read_text(encoding="utf-8", errors="replace")
    ids = re.findall(
        r'data-video-selector="" id="MOESM(\d)">.*?video-id=([A-Za-z0-9_-]+)&amp;player-id=([A-Za-z0-9_-]+)&amp;channel-id=(\d+)',
        html, flags=re.S,
    )
    log = []
    for n, vid, pid, ch in ids:
        src = player_sources(vid, pid, ch)
        entry = dict(moesm=int(n), video_id=vid, n_mp4=len(src["mp4"]), n_hls=len(src["hls"]))
        if src["mp4"]:
            # highest bitrate first (formats are ordered aaa596, aaa828, aaa1656, aaa2356)
            url = src["mp4"][-1]
            dest = ROOT / outdir / f"{tag}_MOESM{n}_{vid}.mp4"
            entry.update(download(url, dest), dest=str(dest), kind="progressive_mp4")
        elif src["hls"]:
            dest = ROOT / outdir / f"{tag}_MOESM{n}_{vid}.mp4"
            entry.update(download(src["hls"][0], dest), dest=str(dest), kind="hls_remux")
        else:
            entry.update(ok=False, bytes=0, kind="no_source_found")
        log.append(entry)
        print(json.dumps(entry))
    (ROOT / "logs" / f"video_download_{tag}.json").write_text(json.dumps(log, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], sys.argv[3])
