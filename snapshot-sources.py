"""Copy source files into data/raw and write a provenance manifest.

Run from anywhere:
    python snapshot-sources.py

What it does:
  1. Copies the OMB consolidated data files from the sources/ clones
     into data/raw/omb-2024 and data/raw/omb-2025.
  2. Writes data/raw/manifest.csv covering those copies and every file
     in agency-files/. One row per file: path, source URL, OMB commit,
     retrieval date, size, SHA-256 hash, and detected encoding.

Safe to rerun. Copies are overwritten only when the source changed,
and the manifest is rebuilt each time.

Before running, fill in AGENCY_SOURCES below for each agency file.
"""

import csv
import hashlib
import shutil
import subprocess
from datetime import date, datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parent
RAW = ROOT / "data" / "raw"
MANIFEST = RAW / "manifest.csv"

OMB = [
    {
        "clone": ROOT / "sources" / "2024-Federal-AI-Use-Case-Inventory",
        "url": "https://github.com/ombegov/2024-Federal-AI-Use-Case-Inventory",
        "dest": RAW / "omb-2024",
        "files": [
            "data/2024_consolidated_ai_inventory_raw.csv",
            "data/2024_consolidated_ai_inventory_raw_v2.csv",
            "validation/data_dictionary.yaml",
        ],
    },
    {
        "clone": ROOT / "sources" / "2025-Federal-Agency-AI-Use-Case-Inventory",
        "url": "https://github.com/ombegov/2025-Federal-Agency-AI-Use-Case-Inventory",
        "dest": RAW / "omb-2025",
        "files": [
            "Data/2025_individually_reported_AI_use_cases.csv",
            "Data/2025_consolidated_COTS_AI_use_cases.csv",
            "Validation/data_dictionary.md",
            "Validation/data_standardization_report.md",
            "Validation/data_standardization_report_AI_COTS.md",
            "Validation/data_sourcing_summary.md",
        ],
    },
]

# Source URL and retrieval date for each agency file, keyed by file name.
# For archived files, paste the full Wayback Machine capture URL.
# Date format: YYYY-MM-DD. Leave a value blank if unknown.
AGENCY_SOURCES = {
    "FINAL_2024 DOJ AI Use Case Inventory_01-21-25.csv": {
        "url": "",
        "retrieved": "",
    },
}


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def encoding(path):
    data = path.read_bytes()
    if path.suffix.lower() not in {".csv", ".md", ".yaml", ".yml", ".json", ".txt"}:
        return "binary"
    if data.startswith(b"\xef\xbb\xbf"):
        return "utf-8-sig"
    try:
        data.decode("utf-8")
        return "utf-8"
    except UnicodeDecodeError:
        pass
    try:
        data.decode("cp1252")
        return "cp1252"
    except UnicodeDecodeError:
        return "mixed or unknown"


def commit(clone):
    try:
        out = subprocess.run(
            ["git", "-C", str(clone), "log", "-1", "--format=%H %cs"],
            capture_output=True, text=True, check=True,
        )
        sha, day = out.stdout.strip().split()
        return sha, day
    except (subprocess.CalledProcessError, FileNotFoundError, ValueError):
        return "", ""


def copy_if_changed(src, dst):
    dst.parent.mkdir(parents=True, exist_ok=True)
    if dst.exists() and sha256(dst) == sha256(src):
        return "unchanged"
    shutil.copy2(src, dst)
    return "copied"


def main():
    rows = []
    today = date.today().isoformat()

    for repo in OMB:
        sha, commit_day = commit(repo["clone"])
        if not sha:
            print(f"warning: could not read git commit for {repo['clone']}")
        for rel in repo["files"]:
            src = repo["clone"] / rel
            if not src.exists():
                print(f"missing, skipped: {src}")
                continue
            dst = repo["dest"] / Path(rel).name
            status = copy_if_changed(src, dst)
            print(f"{status:9}  {dst.relative_to(ROOT)}")
            rows.append({
                "path": dst.relative_to(ROOT).as_posix(),
                "source_url": f"{repo['url']}/blob/{sha}/{rel}" if sha else repo["url"],
                "omb_commit": sha,
                "omb_commit_date": commit_day,
                "retrieved": datetime.fromtimestamp(src.stat().st_mtime).date().isoformat(),
                "bytes": dst.stat().st_size,
                "sha256": sha256(dst),
                "encoding": encoding(dst),
            })

    agency_root = ROOT / "agency-files"
    for f in sorted(agency_root.rglob("*")):
        if not f.is_file():
            continue
        meta = AGENCY_SOURCES.get(f.name, {})
        if not meta.get("url"):
            print(f"note: no source URL recorded for {f.relative_to(ROOT)}")
        rows.append({
            "path": f.relative_to(ROOT).as_posix(),
            "source_url": meta.get("url", ""),
            "omb_commit": "",
            "omb_commit_date": "",
            "retrieved": meta.get("retrieved", ""),
            "bytes": f.stat().st_size,
            "sha256": sha256(f),
            "encoding": encoding(f),
        })

    RAW.mkdir(parents=True, exist_ok=True)
    with open(MANIFEST, "w", newline="", encoding="utf-8") as out:
        w = csv.DictWriter(out, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)

    print()
    print(f"manifest written: {MANIFEST.relative_to(ROOT)}  ({len(rows)} files, built {today})")
    print()
    print("encodings:")
    for r in rows:
        print(f"  {r['encoding']:16} {r['path']}")


if __name__ == "__main__":
    main()
