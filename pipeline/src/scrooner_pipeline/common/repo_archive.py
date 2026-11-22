"""Large generated repo files live in Supabase Storage (bucket repo-archive), recorded in
data-team/strategy/storage-manifest.csv (repo_path, storage_path, sha256, bytes, moved_on).

Founder rule 2026-11-20: no generated file over 5 MB goes into git. The manifest (first used by 49d6c855, Storage
cleanup 1) is the index: the LAST row for a repo_path is its current version. Stdlib only, so the stdlib scripts
(data-team/tags/library/build_library.py) load it by file path, and pipeline code imports it normally.

    resolve(repo_path)  -> a local Path holding the manifest's current version (the repo file when its sha256
                           matches, else a verified download cached under .runs/repo-archive/<sha256>/), or the
                           repo file when the manifest has no row; None when nothing exists.
    upload(path, repo_path) -> uploads a new version (content-addressed storage path, round-trip sha256 check) and
                           appends its manifest row; a version equal to the current row is a no-op.

CLI: python3 pipeline/src/scrooner_pipeline/common/repo_archive.py upload|fetch <repo_path>...
Needs SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY for any download or upload.
"""

from __future__ import annotations

import csv
import datetime as dt
import hashlib
import os
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
MANIFEST = ROOT / "data-team" / "strategy" / "storage-manifest.csv"
COLUMNS = ["repo_path", "storage_path", "sha256", "bytes", "moved_on"]
BUCKET = "repo-archive"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def latest(repo_path: str, manifest: Path = MANIFEST) -> dict | None:
    if not manifest.exists():
        return None
    row = None
    with open(manifest, newline="") as fh:
        for r in csv.DictReader(fh):
            if r["repo_path"] == repo_path:
                row = r
    return row


def _creds() -> tuple[str, str] | None:
    url, key = (
        os.environ.get("SUPABASE_URL", ""),
        os.environ.get("SUPABASE_SERVICE_ROLE_KEY", ""),
    )
    return (url.rstrip("/") + "/storage/v1/object/", key) if url and key else None


def _get(storage_path: str) -> bytes:
    c = _creds()
    if not c:
        raise RuntimeError("SUPABASE_URL / SUPABASE_SERVICE_ROLE_KEY not set")
    req = urllib.request.Request(
        c[0] + storage_path, headers={"Authorization": f"Bearer {c[1]}", "apikey": c[1]}
    )
    with urllib.request.urlopen(req, timeout=300) as r:
        return r.read()


def _put(storage_path: str, body: bytes) -> None:
    c = _creds()
    if not c:
        raise RuntimeError("SUPABASE_URL / SUPABASE_SERVICE_ROLE_KEY not set")
    req = urllib.request.Request(
        c[0] + storage_path,
        data=body,
        method="POST",
        headers={
            "Authorization": f"Bearer {c[1]}",
            "apikey": c[1],
            "Content-Type": "application/octet-stream",
            "x-upsert": "true",
        },
    )
    with urllib.request.urlopen(req, timeout=600) as r:
        r.read()


def resolve(
    repo_path: str, root: Path = ROOT, manifest: Path = MANIFEST
) -> Path | None:
    local = root / repo_path
    row = latest(repo_path, manifest)
    if row is None:
        return local if local.exists() else None
    want = row["sha256"]
    if local.exists() and sha256(local) == want:
        return local
    cached = root / ".runs" / "repo-archive" / want / Path(repo_path).name
    if cached.exists() and sha256(cached) == want:
        return cached
    try:
        body = _get(row["storage_path"])
    except Exception as e:  # no credentials or no network
        if local.exists():
            print(
                f"repo_archive: {repo_path}: cannot fetch the manifest version ({e}); using the local file",
                file=sys.stderr,
            )
            return local
        if _creds():
            raise RuntimeError(
                f"repo_archive: {repo_path}: download of {row['storage_path']} failed: {e}"
            ) from e
        print(
            f"repo_archive: {repo_path}: not in git and no storage credentials; nothing read",
            file=sys.stderr,
        )
        return None
    got = hashlib.sha256(body).hexdigest()
    if got != want:
        raise RuntimeError(
            f"repo_archive: {repo_path}: sha256 {got} != manifest {want}"
        )
    cached.parent.mkdir(parents=True, exist_ok=True)
    tmp = cached.with_suffix(cached.suffix + ".part")
    tmp.write_bytes(body)
    tmp.replace(cached)
    return cached


def upload(
    path: Path, repo_path: str, manifest: Path = MANIFEST, today: str | None = None
) -> dict:
    digest = sha256(path)
    cur = latest(repo_path, manifest)
    if cur and cur["sha256"] == digest:
        return cur
    day = today or dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d")
    storage_path = f"{BUCKET}/{day}/{digest[:12]}/{repo_path}"
    body = Path(path).read_bytes()
    _put(storage_path, body)
    if hashlib.sha256(_get(storage_path)).hexdigest() != digest:
        raise RuntimeError(
            f"repo_archive: round-trip sha256 mismatch for {storage_path}"
        )
    row = {
        "repo_path": repo_path,
        "storage_path": storage_path,
        "sha256": digest,
        "bytes": str(len(body)),
        "moved_on": day,
    }
    new = not manifest.exists() or manifest.stat().st_size == 0
    with open(manifest, "a", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=COLUMNS, lineterminator="\n")
        if new:
            w.writeheader()
        w.writerow(row)
    return row


def main(argv: list[str]) -> int:
    if len(argv) < 2 or argv[0] not in ("upload", "fetch"):
        print(__doc__)
        return 2
    for rp in argv[1:]:
        if argv[0] == "upload":
            r = upload(ROOT / rp, rp)
            print(f"{rp}: {r['storage_path']} {r['sha256']} {r['bytes']}")
        else:
            print(f"{rp}: {resolve(rp)}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
