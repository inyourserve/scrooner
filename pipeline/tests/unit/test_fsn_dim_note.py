"""Dimensional-note allowlist: generator, shard rule and the insert-only load (decision 2026-11-14, option B)."""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path
from uuid import uuid4

import psycopg
import pytest

from scrooner_pipeline.fsn_store import dim_note, dim_note_allowlist as al, shard

ROOT = Path(__file__).resolve().parents[3]
ADSH = "0001413329-23-000025"
OTHER = "0000000000-23-000001"
AM = "AmortizationOfIntangibleAssets"
NO_DIM = "0x00000000"


def _zst(path: Path, rows: list[list[str]]) -> None:
    body = "\n".join("\t".join(r) for r in rows) + "\n"
    path.write_bytes(subprocess.run(["zstd", "-q", "-c"], input=body.encode(), capture_output=True, check=True).stdout)


def _period(cache: Path, period: str = "2023q1", adsh: str = ADSH) -> dict[str, Path]:
    """A one-filing period: Revenues on the IS (with a dimensional statement fact), PM R60 amortization by location
    (a NOTE tag: no statement pre row), and a dimensional note fact of a tag no rule names."""
    d = cache / period
    d.mkdir(parents=True)
    t = {
        "sub": [
            ["adsh", "cik", "form", "aciks", "period", "fy", "fp", "fye", "filed", "accepted"],
            [adsh, "1413329", "10-K", "", "20221231", "2022", "FY", "1231", "20230214", "2023-02-14 16:00:00"],
            [OTHER, "999", "10-K", "", "20221231", "2022", "FY", "1231", "20230214", "2023-02-14 16:00:00"],
        ],
        "pre": [
            ["adsh", "report", "line", "stmt", "inpth", "tag", "version", "prole", "plabel", "negating"],
            [adsh, "4", "1", "IS", "0", "Revenues", "us-gaap/2022", "", "Net revenues", "0"],
            [adsh, "60", "26", "", "0", AM, "us-gaap/2022", "", "Amortization of intangibles", "0"],
        ],
        "num": [
            ["adsh", "tag", "version", "ddate", "qtrs", "uom", "dimh", "iprx", "value", "coreg", "footnote", "durp", "datp", "dcml"],
            [adsh, "Revenues", "us-gaap/2022", "20221231", "4", "USD", NO_DIM, "0", "100", "", "", "1", "0", "-6"],
            [adsh, "Revenues", "us-gaap/2022", "20221231", "4", "USD", "0xaaa", "0", "60", "", "", "1", "0", "-6"],
            [adsh, AM, "us-gaap/2022", "20221231", "4", "USD", "0xbbb", "0", "58000000", "", "", "1", "0", "-6"],
            [adsh, AM, "us-gaap/2022", "20221231", "4", "USD", "0xccc", "0", "101000000", "", "", "1", "0", "-6"],
            [adsh, "DerivativeNotionalAmount", "invest/2013", "20221231", "0", "USD", "0xddd", "0", "7", "", "", "0", "0", "-6"],
            [adsh, AM, "us-gaap/2022", "20221231", "4", "USD", "0xeee", "0", "5", "", "", "1", "0", "-6"],
            [OTHER, AM, "us-gaap/2022", "20221231", "4", "USD", "0xbbb", "0", "9", "", "", "1", "0", "-6"],
        ],
        "cal": [["adsh", "grp", "arc", "negative", "ptag", "pversion", "ctag", "cversion"]],
        "ren": [["adsh", "report", "rfile", "menucat", "shortname", "longname", "roleuri", "parentreport", "ultparentrpt"]],
        "tag": [
            ["tag", "version", "custom", "abstract", "datatype", "iord", "crdr", "tlabel"],
            ["Revenues", "us-gaap/2022", "0", "0", "monetary", "D", "C", "Revenues"],
            [AM, "us-gaap/2022", "0", "0", "monetary", "D", "D", "Amortization"],
            ["DerivativeNotionalAmount", "invest/2013", "0", "0", "monetary", "I", "", "Notional"],
        ],
        "dim": [
            ["dimhash", "segments", "segt"],
            ["0xaaa", "ProductOrService=Product;", "0"],
            ["0xbbb", "IncomeStatementLocation=CostOfSales;", "0"],
            ["0xccc", "IncomeStatementLocation=MarketingAdministrationAndResearchCosts;", "0"],
            ["0xddd", "Counterparty=A;", "0"],
            ["0xeee", "StatementGeographicalAxis=US;Other=B;", "0"],  # two dimensions: no rule matches
        ],
    }
    out = {}
    for name, rows in t.items():
        out[name] = d / f"{period}_{name}.tsv.zst"
        _zst(out[name], rows)
    return out


@pytest.mark.unit
def test_rules_are_rebuilt_at_run_time_never_read_from_a_snapshot(monkeypatch):
    """The load step must see the CURRENT extract_notefacts.sql: a committed snapshot (dim_note_rules.json) could lag."""
    calls = []
    fresh = [{"source": "t", "tag_re": "^OnlyInTheFreshBuild$", "seg_re": "^A=[^;=]+;$", "qtrs": None}]
    monkeypatch.setattr(al, "build", lambda root: calls.append(root) or fresh)
    monkeypatch.setattr(al, "RULES_FILE", Path("/nonexistent/snapshot.json"))
    al.current.cache_clear()
    try:
        r = al.current()
        assert calls == [al.REPO_ROOT] and r.matches("OnlyInTheFreshBuild", "A=m;", 4)
        assert not r.matches("AmortizationOfIntangibleAssets", "IncomeStatementLocation=CostOfSales;", 4)
        assert al.keep_dimensional("a", "OnlyInTheFreshBuild", "v", "A=m;", 4, set())  # the shard's predicate uses it
    finally:
        al.current.cache_clear()


@pytest.mark.unit
def test_the_current_rules_follow_the_mem_cte_axes_incl_capex_and_interest():
    al.current.cache_clear()
    r = al.current()
    assert r.matches("AmortizationOfIntangibleAssets", "IncomeStatementLocation=CostOfSales;", 4)
    sql = (ROOT / "data-team/tags/line_map/tools/extract_notefacts.sql").read_text(encoding="utf-8")
    for axis in re.findall(r"d\.segments ~ '\^\(?([A-Za-z|]+)", sql):  # every axis the CTE names is in the rules
        first = axis.split("|")[0]
        assert any(first in x["seg_re"] for x in r.spec), first


@pytest.mark.unit
def test_generator_reads_the_mem_cte_not_a_copied_list():
    rules = al.cte_rules(ROOT)
    src = [r for r in rules if r["source"] == "extract_notefacts.mem"]
    assert any(r["seg_re"].startswith("^(IncomeStatementLocation|StatementOfIncomeLocationBalance|FiniteLived") and r["tag_re"] == "^AmortizationOfIntangibleAssets$" for r in src)
    assert any(r["seg_re"] == "^ProductOrService=[^;=]+;$" and r["qtrs"] == 4 for r in src)
    # resolver .54: a filer's own amortization-of-intangibles element by income-statement location (CRM), matched case-insensitively
    assert any(r["tag_re"] == r"(?i)^AmortizationOf\w*Intangible\w*$" and r["seg_re"].startswith("^(IncomeStatementLocation|") for r in src)
    assert al.current().matches("AmortizationOfPurchasedIntangiblesFromBusinessCombinations", "IncomeStatementLocation=CostOfSales;", 4)
    assert not al.current().matches("AmortizationOfPurchasedIntangiblesFromBusinessCombinations", "ProductOrService=Foo;", 4)
    assert any("EquityComponents" in r["seg_re"] and "AccountsPayable|AccountsReceivable" in r["tag_re"] for r in src)  # the tgm domain
    assert any(r["source"] == "extract_legalentity" for r in rules)
    # a changed CTE changes the rules: a new disjunct is picked up with no list to edit
    base = al._standard_inputs(ROOT).build_sql([1])
    anchor = "or ((t.tag='AmortizationOfIntangibleAssets'"
    assert anchor in base  # if the CTE is reshaped again, move this anchor, do not weaken the test
    sql = base.replace(anchor, "or (t.tag='NewTag' and d.segments ~ '^NewAxis=[^;=]+;$') " + anchor)
    assert any(r["tag_re"] == "^NewTag$" for r in al.cte_rules(ROOT, sql))


@pytest.mark.unit
def test_resolver_parts_become_rules_by_axis(tmp_path):
    (tmp_path / "resolver-x.csv").write_text(
        "nodes\n" '"Revenues[ProductOrService=Other]=5 [NOTE]; Assets=3 [R2.htm:3] | why: x"\n'
    )
    assert al.resolver_rules(tmp_path) == [
        {"source": "resolver_parts", "tag_re": "^(Revenues)$", "seg_re": "^ProductOrService=[^;=]+;$", "qtrs": None}
    ]


@pytest.mark.unit
def test_rules_match_tag_segments_and_qtrs():
    rules = al.Rules(
        [
            {"tag_re": "^X$", "seg_re": "^A=[^;=]+;$", "qtrs": 4},
            {"tag_re": "^Y$", "seg_re": "^B=[^;=]+;$", "qtrs": None},
        ]
    )
    assert rules.matches("X", "A=m;", 4) and not rules.matches("X", "A=m;", 0)
    assert rules.matches("Y", "B=m;", 0) and not rules.matches("Y", "A=m;", 0)
    assert not rules.matches("X", "A=m;B=n;", 4)  # a second dimension is not the single-member rule


@pytest.mark.unit
def test_shard_keeps_allowlisted_dimensional_note_facts_and_drops_the_rest(tmp_path):
    al.current.cache_clear()
    cache = tmp_path / "cache"
    _period(cache)
    w = shard.Writer(tmp_path / "out")
    stats = shard.shard_period("2023q1", {"0001413329"}, cache, w)
    w.flush()
    from scrooner_pipeline.fsn_store.company_dir import zst_rows

    kept = [(r["tag"], r["dimh"], r["value"]) for r in zst_rows(tmp_path / "out/0001413329/num.tsv.zst")]
    assert (AM, "0xbbb", "58000000") in kept and (AM, "0xccc", "101000000") in kept  # PM R60, the case
    assert ("Revenues", "0xaaa", "60") in kept and ("Revenues", NO_DIM, "100") in kept  # statement rules unchanged
    assert all(k[1] not in ("0xddd", "0xeee") for k in kept)  # no rule names them
    assert stats["num_dropped_dim_note"] == 2  # DerivativeNotionalAmount, the two-dimension amortization
    assert {r["dimhash"] for r in zst_rows(tmp_path / "out/0001413329/dim.tsv.zst")} == {"0xaaa", "0xbbb", "0xccc"}


def _one(conn, sql, params=()):
    return conn.execute(sql, params).fetchone()[0]


@pytest.fixture
def conn(isolated_database_url):
    c = psycopg.connect(isolated_database_url)
    if _one(c, "select count(*) from information_schema.tables where table_schema = 'fsn' and table_name in ('filing', 'value')") != 2:
        c.close()
        pytest.skip("needs migration 0118")
    yield c
    c.close()


def _seed(conn, isolated_database_url):
    cid = _one(conn, "insert into core.company (cik, company_name) values ('0001413329', 'PM TEST') returning id")
    fid = _one(
        conn,
        "insert into fsn.filing (accession, company_id, cik, form, period, fsn_set) values (%s, %s, '0001413329', '10-K', '2022-12-31', '2023q1') returning id",
        (ADSH, cid),
    )
    # the statement-rule facts the shard already stored
    tid = _one(conn, "insert into fsn.tag (tag, version, custom, abstract) values ('Revenues', 'us-gaap/2022', false, false) returning id")
    did = _one(conn, "insert into fsn.dim (dimh, segments, segt) values ('0xaaa', 'ProductOrService=Product;', false) returning id")
    conn.execute(
        "insert into fsn.value (filing_id, company_id, tag_id, ddate, qtrs, uom, dim_id, iprx, coreg, value) values (%s, %s, %s, '2022-12-31', 4, 'USD', %s, 0, '', 60)",
        (fid, cid, tid, did),
    )
    conn.commit()
    return cid, fid


def _fetch(cache_files):
    def fetch(period, table, cache, prefix):
        if prefix:
            raise FileNotFoundError(prefix)
        return cache_files[table]

    return fetch


@pytest.mark.integration
def test_insert_only_dry_run_writes_nothing_apply_adds_once_and_rerun_adds_nothing(conn, isolated_database_url, tmp_path):
    cid, fid = _seed(conn, isolated_database_url)
    before = _one(conn, "select count(*) from fsn.value")
    refs = (_one(conn, "select count(*) from fsn.tag"), _one(conn, "select count(*) from fsn.dim"))

    def run(apply):
        files = _period(tmp_path / uuid4().hex)
        return dim_note.run(
            lambda: psycopg.connect(isolated_database_url), [cid], _fetch(files), tmp_path, apply=apply
        )

    dry = run(False)
    assert dry["mode"] == "dry-run" and dry["rows_to_add"] == 2 and dry["per_company"] == {cid: 2}
    assert _one(conn, "select count(*) from fsn.value") == before  # nothing written
    assert (_one(conn, "select count(*) from fsn.tag"), _one(conn, "select count(*) from fsn.dim")) == refs
    done = run(True)
    assert done["rows_added"] == 2 and done["per_company"] == {cid: 2}
    rows = conn.execute(
        "select d.segments, v.value, v.company_id, v.filing_id from fsn.value v join fsn.dim d on d.id = v.dim_id join fsn.tag t on t.id = v.tag_id where t.tag = %s order by 1",
        (AM,),
    ).fetchall()
    assert [(r[0], int(r[1])) for r in rows] == [
        ("IncomeStatementLocation=CostOfSales;", 58000000),
        ("IncomeStatementLocation=MarketingAdministrationAndResearchCosts;", 101000000),
    ] and all(r[2] == cid and r[3] == fid for r in rows)
    assert _one(conn, "select count(*) from fsn.value") == before + 2
    again = run(True)  # idempotent: the unique key means a rerun adds nothing
    assert again["rows_added"] == 0 and again["already_present"] == 2
    assert _one(conn, "select count(*) from fsn.value") == before + 2
    assert _one(conn, "select count(*) from fsn.filing") == 1  # no reload, no delete
    # the statement-rule fact the shard stored is untouched
    assert _one(conn, "select value from fsn.value v join fsn.dim d on d.id = v.dim_id where d.dimh = '0xaaa'") == 60


@pytest.mark.integration
def test_a_period_in_both_bucket_folders_is_read_from_both(conn, isolated_database_url, tmp_path):
    """XOM 0000034088: its filings sit only in predecessors/<set>, beside a cohort folder of the same period."""
    cid, fid = _seed(conn, isolated_database_url)
    pred_adsh = "0000034088-23-000020"
    fid2 = _one(
        conn,
        "insert into fsn.filing (accession, company_id, cik, form, period, fsn_set) values (%s, %s, '0000034088', '10-K', '2021-12-31', '2023q1') returning id",
        (pred_adsh, cid),
    )
    # (a different period than the own filing: the successor wins a shared period)
    # the predecessor window is what makes the 0000034088 filing this company's (common/company_filings.py)
    conn.execute(
        "insert into core.company_history_source (company_id, source_cik, relation, source_name, valid_from, valid_to, reason)"
        " values (%s, '0000034088', 'predecessor', 'XOM', '2014-01-01', '2026-03-31', 'test')",
        (cid,),
    )
    conn.commit()
    base = _period(tmp_path / "base")  # holds ADSH only
    pred = _period(tmp_path / "pred", adsh=pred_adsh)  # holds pred_adsh only
    pred_rows = {k: v for k, v in pred.items()}

    def fetch(period, table, cache, prefix):
        return (pred_rows if prefix else base)[table]

    res = dim_note.run(lambda: psycopg.connect(isolated_database_url), [cid], fetch, tmp_path, apply=False)
    assert res["rows_to_add"] == 4 and res["per_company"] == {cid: 4}  # 2 per folder: both folders were read
    assert fid2 != fid


@pytest.mark.unit
def test_comparative_column_member_facts_are_candidates_too(tmp_path):
    """No ddate filter: a prior-year column of the filing (GEV AR 7,409 + 80 at the FY-1 date) is kept like the own period."""
    files = _period(tmp_path / "c")
    rows = [r.split("\t") for r in subprocess.run(["zstd", "-dc", str(files["num"])], capture_output=True, check=True).stdout.decode().splitlines()]
    prior = [*rows[3]]
    prior[3] = "20211231"  # the AmortizationOfIntangibleAssets / CostOfSales row, one fiscal year earlier
    prior[8] = "55000000"
    _zst(files["num"], [*rows, prior])
    got, _, _ = dim_note.candidates(files, {ADSH})
    assert {(r["ddate"], r["value"]) for r in got if r["dimh"] == "0xbbb"} == {("20221231", "58000000"), ("20211231", "55000000")}
