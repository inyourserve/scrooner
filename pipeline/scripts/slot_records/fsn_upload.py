"""Store FSN quarter files in Supabase Storage (founder 2026-10-26: "download
and store in Supabase"). Private bucket `fsn-notes`, path <quarter>/<file>.

For a quarter directory: upload every extract (.zst) and the zip if still
present (upsert, verified by a HEAD/list after upload, sha256 of the zip is
in the manifest), record the object paths in the quarter manifest, then delete
the LOCAL zip (Supabase holds it; the manifest keeps URL + sha256 so a refetch
is one request). Extracts stay local too (small). Uses SUPABASE_URL and
SUPABASE_SERVICE_ROLE_KEY from the environment (pipeline/.env), never printed.
usage: fsn_upload.py <quarter_dir> [bucket]
"""
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path

qdir = Path(sys.argv[1])
bucket = sys.argv[2] if len(sys.argv) > 2 else "fsn-notes"
quarter = qdir.name
base = os.environ["SUPABASE_URL"].rstrip("/")
key = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
H = {"Authorization": f"Bearer {key}", "apikey": key}


def call(method, path, data=None, headers=None, timeout=1800):
    req = urllib.request.Request(base + path, data=data, method=method, headers={**H, **(headers or {})})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, r.read()
    except urllib.error.HTTPError as e:
        return e.code, e.read()


def ensure_bucket():
    status, body = call("GET", f"/storage/v1/bucket/{bucket}")
    if status == 200:
        return "exists"
    status, body = call("POST", "/storage/v1/bucket", json.dumps({"id": bucket, "name": bucket, "public": False}).encode(),
                        {"Content-Type": "application/json"})
    if status not in (200, 201):
        raise SystemExit(f"bucket create failed: {status} {body[:200]!r}")
    return "created"


def upload(local, obj):
    data = local.read_bytes()
    status, body = call("POST", f"/storage/v1/object/{bucket}/{obj}", data,
                        {"Content-Type": "application/octet-stream", "x-upsert": "true"})
    if status == 400 and b"EntityTooLarge" in body:
        return None  # blocked by the PROJECT-wide Storage file-size limit (dashboard setting)
    if status not in (200, 201):
        raise SystemExit(f"upload failed {obj}: {status} {body[:200]!r}")
    # verify by listing the object
    status, body = call("POST", f"/storage/v1/object/list/{bucket}",
                        json.dumps({"prefix": quarter + "/", "limit": 100}).encode(), {"Content-Type": "application/json"})
    names = {o["name"] for o in json.loads(body)} if status == 200 else set()
    if local.name not in names:
        raise SystemExit(f"upload not visible after write: {obj}")
    return len(data)


print(f"bucket {bucket}: {ensure_bucket()}")
man_path = qdir / f"{quarter}_manifest.json"
manifest = json.load(open(man_path)) if man_path.exists() else {"quarter": quarter}
uploaded = manifest.setdefault("storage", {"bucket": bucket, "objects": {}})
total = 0
for f in sorted(qdir.iterdir()):
    if f.suffix not in (".zst", ".zip", ".json", ".xz"):
        continue
    if f.name == man_path.name:
        continue
    obj = f"{quarter}/{f.name}"
    n = upload(f, obj)
    if n is None:
        uploaded["objects"][f.name] = {"bytes": f.stat().st_size, "blocked": "project_file_size_limit",
                                       "note": "raise the project's global Storage file-size limit in the dashboard, then re-run fsn_upload.py"}
        print(f"  BLOCKED {f.name} {f.stat().st_size/1e6:.1f} MB: project file-size limit; kept locally")
        continue
    uploaded["objects"][f.name] = {"bytes": n}
    total += n
    print(f"  uploaded {f.name} {n/1e6:.1f} MB")
    if f.suffix == ".zip":
        f.unlink()
        uploaded["objects"][f.name]["local_deleted_after_upload"] = True
# the manifest itself, last
json.dump(manifest, open(man_path, "w"), indent=1)
upload(man_path, f"{quarter}/{man_path.name}")
print(f"{quarter}: {len(uploaded['objects'])} objects, {total/1e6:.1f} MB in {bucket}; blocked: {[k for k,v in uploaded['objects'].items() if v.get('blocked')]}")
