"""common/repo_archive.py: large generated files (tag library.csv) resolve to the storage-manifest version, verified."""
import csv
import hashlib

import pytest

from scrooner_pipeline.common import repo_archive as ra
from scrooner_pipeline.mapper import hide_audit as ha

RP = "data-team/tags/library/library.csv"


@pytest.fixture
def store(monkeypatch):
    objs = {}
    monkeypatch.setattr(ra, "_put", lambda p, b: objs.__setitem__(p, b))
    monkeypatch.setattr(ra, "_get", lambda p: objs[p])
    monkeypatch.setenv("SUPABASE_URL", "https://x.invalid")
    monkeypatch.setenv("SUPABASE_SERVICE_ROLE_KEY", "k")
    return objs


def test_upload_appends_one_row_per_version_and_resolve_fetches_it(tmp_path, store):
    man = tmp_path / "manifest.csv"
    man.write_text(",".join(ra.COLUMNS) + "\nold/x.gz,repo-archive/2026-11-21/old/x.gz," + "0" * 64 + ",1,2026-11-21\n")
    src = tmp_path / "build.csv"
    src.write_text("element\nA\n")
    r1 = ra.upload(src, RP, manifest=man, today="2026-11-22")
    assert r1["sha256"] == hashlib.sha256(b"element\nA\n").hexdigest()
    assert r1["storage_path"] == f"repo-archive/2026-11-22/{r1['sha256'][:12]}/{RP}"
    ra.upload(src, RP, manifest=man, today="2026-11-22")  # same content: no new row
    src.write_text("element\nB\n")
    r2 = ra.upload(src, RP, manifest=man, today="2026-11-23")
    rows = list(csv.DictReader(open(man)))
    assert [r["sha256"] for r in rows if r["repo_path"] == RP] == [r1["sha256"], r2["sha256"]]
    # not in git: resolve downloads the LAST row's version and verifies it
    root = tmp_path / "repo"
    got = ra.resolve(RP, root=root, manifest=man)
    assert got.read_text() == "element\nB\n" and ".runs/repo-archive" in str(got)
    # a stale local copy loses to the manifest version
    (root / RP).parent.mkdir(parents=True)
    (root / RP).write_text("element\nA\n")
    assert ra.resolve(RP, root=root, manifest=man).read_text() == "element\nB\n"
    # a local copy equal to the manifest version is used as is
    (root / RP).write_text("element\nB\n")
    assert ra.resolve(RP, root=root, manifest=man) == root / RP


def test_corrupt_download_is_refused(tmp_path, store):
    man = tmp_path / "manifest.csv"
    src = tmp_path / "b.csv"
    src.write_text("element\nA\n")
    r = ra.upload(src, RP, manifest=man, today="2026-11-22")
    store[r["storage_path"]] = b"tampered"
    with pytest.raises(RuntimeError, match="sha256"):
        ra.resolve(RP, root=tmp_path / "repo", manifest=man)


def test_no_manifest_row_means_the_repo_file(tmp_path):
    (tmp_path / "f.csv").write_text("x")
    assert ra.resolve("f.csv", root=tmp_path, manifest=tmp_path / "none.csv") == tmp_path / "f.csv"
    assert ra.resolve("g.csv", root=tmp_path, manifest=tmp_path / "none.csv") is None


def test_hide_audit_reads_the_library_from_the_manifest(tmp_path, monkeypatch):
    lib = tmp_path / "library.csv"
    lib.write_text("element,data_point,role_kind\nZzArchiveOnlyTag,revenue,primary\n")
    seen = []
    monkeypatch.setattr(ra, "resolve", lambda rp, *a, **k: seen.append(rp) or lib)
    monkeypatch.setattr(ha, "library_primary_tags", lambda rows: {"revenue": {r["element"] for r in rows}})
    v = ha.build_vocab(resolver_dir=tmp_path / "no-resolver")
    assert seen == [RP] and "ZzArchiveOnlyTag" in v.tags["revenue"]


def _archived_only(tmp_path, body=b"element\nA\n"):
    """A manifest row for RP with no repo copy and no cache: resolving it needs a Storage download."""
    man = tmp_path / "manifest.csv"
    digest = hashlib.sha256(body).hexdigest()
    man.write_text(",".join(ra.COLUMNS) + f"\n{RP},repo-archive/2026-11-22/{digest[:12]}/{RP},{digest},{len(body)},2026-11-22\n")
    return {"root": tmp_path / "repo", "manifest": man}


def test_archived_file_skips_when_test_storage_is_not_configured(tmp_path, monkeypatch, archived_repo_file):
    # conftest's placeholder SUPABASE_* (https://scrooner-test.invalid) must not count as configured Storage
    monkeypatch.delenv("SCROONER_TEST_STORAGE_URL", raising=False)
    monkeypatch.delenv("SCROONER_TEST_STORAGE_KEY", raising=False)
    monkeypatch.setenv("SUPABASE_URL", "https://scrooner-test.invalid")
    monkeypatch.setenv("SUPABASE_SERVICE_ROLE_KEY", "test-only-not-a-secret")
    with pytest.raises(pytest.skip.Exception, match="Storage is not configured"):
        archived_repo_file(RP, **_archived_only(tmp_path))


def test_archived_file_fails_loudly_when_test_storage_is_configured_but_unreachable(
    tmp_path, monkeypatch, archived_repo_file
):
    monkeypatch.setenv("SCROONER_TEST_STORAGE_URL", "https://scrooner-test.invalid")
    monkeypatch.setenv("SCROONER_TEST_STORAGE_KEY", "k")
    monkeypatch.setattr(ra, "_get", lambda p: (_ for _ in ()).throw(OSError("Name or service not known")))
    with pytest.raises(RuntimeError, match="download of .* failed"):
        try:
            archived_repo_file(RP, **_archived_only(tmp_path))
        except pytest.skip.Exception as e:  # a skip here would hide a real Storage failure
            pytest.fail(f"configured Storage must fail loudly, not skip: {e}")


def test_archived_file_is_downloaded_with_the_test_storage_credentials(tmp_path, monkeypatch, archived_repo_file):
    monkeypatch.setenv("SCROONER_TEST_STORAGE_URL", "https://storage.example")
    monkeypatch.setenv("SCROONER_TEST_STORAGE_KEY", "read-key")
    seen = []
    monkeypatch.setattr(ra, "_get", lambda p: seen.append(ra._creds()) or b"element\nA\n")
    got = archived_repo_file(RP, **_archived_only(tmp_path))
    assert got.read_bytes() == b"element\nA\n"
    assert seen == [("https://storage.example/storage/v1/object/", "read-key")]
