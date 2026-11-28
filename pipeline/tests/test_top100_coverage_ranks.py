"""Stage 4 Prove, M6: the coverage export's rank set is a parameter (ranks 101+ get cells and display states).

A company beyond the top 100 has no docmap: it takes the registry template and every cell gets a class and a display
(OPEN `no_docmap` when the database holds nothing for it), never silently skipped. The default rank set stays 1-100."""

from __future__ import annotations

import csv
from datetime import date
from pathlib import Path

import pytest

from scrooner_pipeline.mapper import top100_coverage as t100

FIELDS = ["shard", "rank", "company_id", "cik", "ticker", "name", "sic", "excluded"]


def _shards(tmp_path: Path, n: int = 600) -> Path:
    p = tmp_path / "shards.csv"
    with p.open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=FIELDS)
        w.writeheader()
        for r in range(1, n + 1):
            w.writerow(
                {"shard": "S", "rank": r, "company_id": 10_000 + r, "cik": str(r).zfill(10),
                 "ticker": f"T{r}", "name": f"Co {r}", "sic": "3571", "excluded": ""}
            )
    return p


def test_default_rank_set_is_the_top_100(tmp_path):
    s = _shards(tmp_path)
    got = t100.universe(s)
    assert [c.rank for c in got] == list(range(1, 101))
    assert t100.load_top(s) == got


def test_ranks_and_company_ids_reach_rank_500(tmp_path):
    s = _shards(tmp_path)
    assert [c.rank for c in t100.universe(s, ranks=(101, 600))] == list(range(101, 601))
    assert [c.ticker for c in t100.universe(s, ranks=t100.parse_ranks("500"))] == ["T500"]
    # a company id at rank 500 is selectable without --ranks (the per-company flow passes ids only)
    picked = t100.select_companies(t100.universe(s, company_ids=[10_500]), [10_500])
    assert [(c.rank, c.ticker) for c in picked] == [(500, "T500")]
    with pytest.raises(SystemExit):
        t100.select_companies(t100.universe(s, ranks=(1, 100)), [10_500])
    with pytest.raises(SystemExit):
        t100.parse_ranks("200-100")


def test_company_ids_csv(tmp_path):
    p = tmp_path / "u.csv"
    p.write_text("company_id,ticker\n7,A\n3,B\n7,A\n")
    assert t100.load_company_ids_csv(p) == [3, 7]


class _Cur:
    def fetchall(self):
        return []

    def fetchone(self):
        return None

    def __iter__(self):
        return iter(())


class _Conn:
    """Every read returns no rows: the company has no proof, no served value and no stored reason."""

    def execute(self, *_a, **_k):
        return _Cur()

    def cursor(self, *_a, **_k):
        return self

    def __enter__(self):
        return self

    def __exit__(self, *_a):
        return False


def test_rank_500_company_without_docmap_gets_open_cells(tmp_path, monkeypatch):
    s = _shards(tmp_path)
    (co,) = t100.universe(s, ranks=(500, 500))
    reads = tmp_path / "reads"  # no docmap for T500
    reads.mkdir()
    monkeypatch.setattr(
        t100,
        "_fy_periods",
        lambda conn, ids, today, annual=None: {
            (cid, 2024, k): (date(2024, 1, 1) if k == "duration" else date(2024, 12, 31), date(2024, 12, 31))
            for cid in ids
            for k in ("duration", "instant")
        },
    )
    # the tag library (repo archive, fetched over the network) feeds only the hide audit's line hits
    real_vocab = t100.ha.build_vocab
    monkeypatch.setattr(
        t100.ha, "build_vocab", lambda **k: real_vocab(library_dir=tmp_path / "no-library", **k)
    )
    rows, notes = t100.build_rows_chunked(_Conn(), [co], reads, date(2026, 11, 29), {}, {}, chunk=1)
    assert rows, "a rank-500 company with no docmap must still get cells"
    assert {r["company_id"] for r in rows} == {co.company_id}
    assert {r["docmap_status"] for r in rows} == {t100.NO_DOCMAP}
    assert {(r["class"], r["reason_code"]) for r in rows} == {("BLANK", t100.NO_DOCMAP)}
    assert {r["display"] for r in rows} <= {"OPEN", t100.HIDDEN_ROW, t100.HIDDEN_YEAR}
    assert "revenue" in {r["data_point"] for r in rows}
    assert "TEMPLATE_FROM_REGISTRY" in notes[co.company_id]
    # every cell becomes a display-state row (the table write path is the dry-run's input)
    from scrooner_pipeline.mapper import cell_display_state as cds

    states = cds.state_rows(rows, list(t100.OUT_CELLS), "run", None)
    assert len(states) == len(rows) and {st[0] for st in states} == {co.company_id}


def test_chunks_are_set_based_and_keep_every_chunks_out_cells(tmp_path, monkeypatch):
    s = _shards(tmp_path)
    cos = t100.universe(s, ranks=(101, 350))
    calls: list[int] = []

    def fake(conn, part, reads_dir, today, note_lookup=None, fix_pages=None):
        calls.append(len(part))
        t100.OUT_CELLS.clear()
        t100.OUT_CELLS.append({"company_id": part[0].company_id})
        return [{"company_id": c.company_id} for c in part], {}

    monkeypatch.setattr(t100, "build_rows", fake)
    rows, _ = t100.build_rows_chunked(None, cos, tmp_path, date(2026, 11, 29), chunk=100)
    assert calls == [100, 100, 50]
    assert len(rows) == 250 and len(t100.OUT_CELLS) == 3
