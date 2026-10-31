"""R14 manifest builder: hashes every retained original and writes the catalog.

Raw files are never modified. Each entry records source URL, download date,
size and SHA256 so that a third party can re-verify the exact bytes used.
"""

from __future__ import annotations

import os as _os

R14_ROOT = _os.environ.get("R14_ROOT", r"C:\Work\research\aviation_algorithm_r14_public_data_20261031")


import csv
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(R14_ROOT)

SOURCES = {
    "UQ_experiment.zip": (
        "https://www.nasa.gov/wp-content/uploads/2025/10/uq-experiment.zip",
        "NASA TMBWG SBLI2.05 UQ database (Campo & Eaton, Stanford)",
        "NASA public data page; no explicit redistribution licence stated on the page",
    ),
    "README_UQ.pdf": (
        "https://tmbwg.github.io/turbmodels/Other_exp_Data/SBLI2.05/README_UQ.pdf",
        "Dataset README, variable definitions",
        "NASA TMBWG public documentation",
    ),
    "Campo_thesis.pdf": (
        "https://tmbwg.github.io/turbmodels/Other_exp_Data/SBLI2.05/Campo_thesis.pdf",
        "Campo PhD thesis 2014 (provided with author permission)",
        "Author permission for distribution via TMBWG page",
    ),
    "HMVE2_PIVprofiles.zip": (
        "https://ntrs.nasa.gov/api/citations/20250008885/downloads/HMVE2_PIVprofiles.zip",
        "NASA HMVE 2025 PIV profiles, M2.5/3.0/3.5",
        "NASA public NTRS record, public distribution",
    ),
    "Reising_TM-20250008885.pdf": (
        "https://ntrs.nasa.gov/api/citations/20250008885/downloads/Reising_TM-20250008885_Final.pdf",
        "NASA/TM-20250008885, HMVE 2025 test entry",
        "NASA public NTRS record",
    ),
}


def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def main() -> None:
    (ROOT / "data/manifests").mkdir(parents=True, exist_ok=True)
    rows, sums = [], []
    targets = [
        ("sbli205", ROOT / "data/raw/sbli205/UQ_experiment.zip"),
        ("sbli205", ROOT / "papers/README_UQ.pdf"),
        ("sbli205", ROOT / "papers/Campo_thesis.pdf"),
        ("hmve", ROOT / "data/raw/hmve/HMVE2_PIVprofiles.zip"),
        ("hmve", ROOT / "papers/Reising_TM-20250008885.pdf"),
    ]
    for tag, p in targets:
        if not p.exists():
            rows.append(dict(dataset=tag, file=p.name, path=str(p), status="MISSING",
                             bytes=0, sha256=""))
            continue
        digest = sha256(p)
        url, desc, lic = SOURCES.get(p.name, ("", "", ""))
        rows.append(dict(dataset=tag, file=p.name, path=str(p), status="VERIFIED_DOWNLOADED",
                         bytes=p.stat().st_size, sha256=digest, source_url=url,
                         description=desc, license=lic,
                         downloaded_utc=datetime.fromtimestamp(p.stat().st_mtime, timezone.utc)
                         .strftime("%Y-%m-%dT%H:%M:%SZ")))
        sums.append(f"{digest}  {p.relative_to(ROOT).as_posix()}")

    # extracted HMVE profiles (small, hash each)
    for p in sorted((ROOT / "data/raw/hmve/HMVE2_PIVprofiles").rglob("*.dat")):
        digest = sha256(p)
        rows.append(dict(dataset="hmve", file=p.name, path=str(p), status="VERIFIED_DOWNLOADED",
                         bytes=p.stat().st_size, sha256=digest,
                         source_url=SOURCES["HMVE2_PIVprofiles.zip"][0],
                         description="PIV probe profile (Tecplot ASCII)", license="NASA public",
                         downloaded_utc=""))
        sums.append(f"{digest}  {p.relative_to(ROOT).as_posix()}")

    # videos, if present
    for p in sorted(ROOT.glob("data/raw/busemann*/*.mp4")) + sorted(ROOT.glob("data/raw/busemann*/*.avi")):
        digest = sha256(p)
        rows.append(dict(dataset=p.parent.name, file=p.name, path=str(p),
                         status="VERIFIED_DOWNLOADED", bytes=p.stat().st_size, sha256=digest,
                         source_url="Springer supplementary material (CDN rendition)",
                         description="Supplementary video, transcoded delivery copy",
                         license="Springer supplementary material; article CC BY where stated",
                         downloaded_utc=""))
        sums.append(f"{digest}  {p.relative_to(ROOT).as_posix()}")

    fields = ["dataset", "file", "path", "status", "bytes", "sha256", "source_url",
              "description", "license", "downloaded_utc"]
    with open(ROOT / "01_DATA_CATALOG.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, "") for k in fields})
    (ROOT / "SHA256SUMS.txt").write_text("\n".join(sums) + "\n", encoding="utf-8")
    (ROOT / "manifest.json").write_text(
        json.dumps(dict(
            generated_utc=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            n_entries=len(rows),
            n_verified=sum(1 for r in rows if r["status"] == "VERIFIED_DOWNLOADED"),
            total_bytes=sum(r.get("bytes", 0) for r in rows),
            entries=rows,
        ), indent=2), encoding="utf-8")
    print(f"entries={len(rows)} verified={sum(1 for r in rows if r['status']=='VERIFIED_DOWNLOADED')}")
    print(f"total_bytes={sum(r.get('bytes',0) for r in rows)}")


if __name__ == "__main__":
    main()
