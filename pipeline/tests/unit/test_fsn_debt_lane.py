"""Total debt on the FSN store comes from the Verifier-passed debt lane, run whole (FAMILY-RELEASE-CASE-2026-11-09 §2).

Before: six calc_position seeds mapped ANY custom child of current liabilities as total_debt_resolved (production
fsn.line_map 2026-11-09: 7,335 lines, 5,441 filings, 236 companies; "Accounts payable and accrued liabilities" served as
total debt), standard debt lines stayed unmapped, and select never sums. Now the seeds are gone and
fsn_store.debt runs era_detect -> assemble_fsn -> replay_debt_fsn (company mode) and turns its cells into store cells.

Fixture: the real AMZN company directory (pipeline/tests/fixtures/fsn_company_bs/0001018724, rows copied from the SEC
FSN data sets). Expected values are the Verifier's (VERIFY-DEBT-RELEASE1-AMZN-2026-11-04 3/3: 2023-12-31 = 58,314 +
8,494 + finance leases 12,109 = 78,917), read from the committed report_v4.json, not retyped."""

import json
import shutil
import subprocess
from datetime import UTC, date, datetime
from decimal import Decimal
from pathlib import Path

import psycopg
import pytest

from scrooner_pipeline.common import cell_contract
from scrooner_pipeline.fsn_store import debt, load, mapping, pilot
from scrooner_pipeline.fsn_store import select as sel

ROOT = Path(__file__).resolve().parents[3]
FX = ROOT / "pipeline" / "tests" / "fixtures" / "fsn_company_bs" / "0001018724"
V4 = (
    ROOT
    / "pipeline"
    / "scripts"
    / "slot_records"
    / "results"
    / "debt_fsn_pilot_v1"
    / "report_v4.json"
)
RULES = ROOT / "data-team" / "47-fsn-store" / "concept_rules"


@pytest.fixture(scope="module")
def lane(tmp_path_factory):
    root = tmp_path_factory.mktemp("debt")
    shutil.copytree(FX, root / "companies" / FX.name)
    rep = debt.run_lane(root / "companies", root / "work")
    return debt.load_replay(rep)[1018724]


def _filings(lane_cells):
    accs = sorted({c["accession"] for c in lane_cells})
    return {
        i: sel.Filing(
            i,
            a,
            datetime(2020, 1, 1 + i, tzinfo=UTC),
            "10-K",
            date(2020, 1, 1),
            2020,
            "FY",
        )
        for i, a in enumerate(accs, start=1)
    }


def test_lane_cells_become_store_cells_with_the_verifier_values(lane):
    v4 = next(
        c
        for c in json.loads(V4.read_text())["cells"]
        if c["ticker"] == "AMZN" and c["period_end"] == "2023-12-31"
    )
    filings = _filings(lane)
    cells = {(c.ddate, c.state): c for c in debt.debt_cells(None, lane, filings)}
    got = cells[(date(2023, 12, 31), "value")]
    assert got.concept == "total_debt_resolved" and got.qtrs == 0
    assert got.value == Decimal(v4["slot_lease_inclusive"]) == Decimal(78_917_000_000)
    assert filings[got.filing_id].accession == v4["accession"]
    assert got.rule_id == debt.RULE_VALUE
    assert got.input_refs["note_finance_lease_added"] == v4["note_finance_lease_added"]
    row = sel.to_row(got, 1, filings)
    assert row["value"] == "78917000000" and row["state"] == "value"


def test_every_lane_hold_is_a_valid_reasoned_blank(lane):
    filings = _filings(lane)
    holds = [c for c in debt.debt_cells(None, lane, filings) if c.state == "defect"]
    assert holds, "the AMZN fixture holds 2018-12-31 (custom lease line not proven)"
    for c in holds:
        row = sel.to_row(c, 1, filings)
        assert row["reason_code"] in debt.HOLDS and row["reason_text"]
        assert (
            row["defect_class"] in cell_contract.DEFECT_CLASSES
            and row["owner"] in cell_contract.OWNERS
        )
        assert row["value"] is None
    assert {c.reason_code for c in holds} == {"debt_lease_member_unverified"}


def test_every_lane_verdict_is_mapped():
    """a new hold verdict in replay_debt_fsn must get a reason here (debt_cells raises on an unknown verdict)"""
    src = (
        ROOT / "pipeline" / "scripts" / "slot_records" / "replay_debt_fsn.py"
    ).read_text()
    import re

    verdicts = set(re.findall(r'verdict = "([a-z_]+)"', src))
    assert verdicts and verdicts <= set(debt.HOLDS), verdicts - set(debt.HOLDS)
    with pytest.raises(ValueError):
        debt.debt_cells(
            None,
            [
                {
                    "cik": 1,
                    "period_end": "2020-12-31",
                    "accession": "a",
                    "verdict": "new_hold",
                }
            ],
            {
                1: sel.Filing(
                    1,
                    "a",
                    datetime(2021, 1, 1, tzinfo=UTC),
                    "10-K",
                    date(2020, 12, 31),
                    2020,
                    "FY",
                )
            },
        )


def test_summed_tags_name_every_summed_fact():
    own, earlier = debt.summed_tags(
        {
            "members": [
                ["CommercialPaper", "borrowing", "current"],
                ["LongTermDebtNoncurrent", "borrowing", "noncurrent"],
                ["OperatingLeaseLiabilityNoncurrent", "operating_lease", "noncurrent"],
            ],
            "note_current_portion_added": "5",
            "note_flag": "lease_tags_from_earlier_copy:0000000001-24-000001:FinanceLeaseLiabilityCurrent;"
            "note_finance_lease_added:FinanceLeaseLiability-FinanceLeaseLiabilityNoncurrent=12",
        }
    )
    assert own == {
        "CommercialPaper",
        "LongTermDebtNoncurrent",
        "LongTermDebtCurrent",
        "FinanceLeaseLiability",
        "FinanceLeaseLiabilityNoncurrent",
    }
    assert earlier == {"0000000001-24-000001": {"FinanceLeaseLiabilityCurrent"}}


# ---------------------------------------------------------------- the seeds no longer map anything as total debt
class _Cur:
    def __init__(self, conn):
        self.conn = conn

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False

    def execute(self, sql, params=None):
        self.res = self.conn.script.pop(0)

    def executemany(self, sql, rows):
        self.conn.written.extend(rows)

    def fetchall(self):
        return self.res

    def fetchone(self):
        return self.res[0]


class _Conn:
    def __init__(self, script):
        self.script, self.written = script, []

    def cursor(self):
        return _Cur(self)


def test_a_custom_current_liability_is_never_mapped_as_total_debt():
    """the production misfire: a custom accrual under current liabilities became total debt (bs.debt_member_parent@1)"""
    rows = []
    for f in sorted(RULES.glob("*.jsonl")):
        if not f.name.startswith("_"):
            rows += [json.loads(x) for x in f.open() if x.strip()]
    rows.sort(key=lambda r: r["priority"])
    ids = {
        n: i
        for i, n in enumerate(
            sorted({r["canonical_concept"] for r in rows} | {"total_debt_resolved"}), 1
        )
    }
    db = [
        (
            i,
            r["canonical_concept"],
            ids[r["canonical_concept"]],
            r["stmt"],
            r["match_kind"],
            r.get("tag"),
            r.get("position"),
            r.get("components"),
            r["priority"],
            r.get("era_from"),
            r.get("era_to"),
            r["rule_id"],
            r.get("tag_pattern"),
        )
        for i, r in enumerate(rows)
    ]
    rules = mapping.load_rules(_Conn([db]))
    v, c = "us-gaap/2023", "0000000001-24-000001"
    lines = [
        ("2", 10, "BS", "AccountsPayableCurrent", v, False, False),
        ("2", 11, "BS", "AccruedCompensationCustom", c, True, False),
        ("2", 12, "BS", "LiabilitiesCurrent", v, False, False),
        ("2", 13, "BS", "LongTermDebtNoncurrent", v, False, False),
        ("2", 14, "BS", "Liabilities", v, False, False),
    ]
    arcs = [
        ("LiabilitiesCurrent", v, "AccountsPayableCurrent", v),
        ("LiabilitiesCurrent", v, "AccruedCompensationCustom", c),
        ("Liabilities", v, "LiabilitiesCurrent", v),
        ("Liabilities", v, "LongTermDebtNoncurrent", v),
    ]
    conn = _Conn([[(date(2024, 12, 31),)], lines, arcs, None])
    mapping.map_filing(conn, 1, rules, write=True)
    assert not [r for r in conn.written if r[3] == ids["total_debt_resolved"]]


def test_the_debt_seeds_are_retired_from_databases_seeded_earlier():
    from scrooner_pipeline.fsn_store import rules

    ids = set(rules.retired_ids(RULES / "_retired.txt"))
    assert {
        "bs.debt_member_parent@1",
        "bs.debt_member_parent@2",
        "bs.debt_finance_lease_member@1",
        "bs.debt_finance_lease_member@2",
        "bs.debt_combined_member@1",
        "bs.debt_combined_member@2",
    } <= ids


# ---------------------------------------------------------------- the store side, end to end on a database
def _one(conn, sql, params=()):
    return conn.execute(sql, params).fetchone()[0]


@pytest.fixture
def conn(isolated_database_url):
    c = psycopg.connect(isolated_database_url)
    if (
        _one(
            c,
            "select count(*) from information_schema.tables where table_schema = 'fsn' and table_name = 'value'",
        )
        != 1
    ):
        c.close()
        pytest.skip("needs migration 0118")
    yield c
    c.close()


@pytest.mark.integration
def test_pilot_serves_total_debt_from_the_lane_with_fsn_value_lineage(
    conn, lane, tmp_path
):
    conn.execute(
        "insert into analytics.canonical_concept (name, statement, combination_mode) values ('total_debt_resolved', "
        "'balance_sheet', 'first_match') on conflict (name) do nothing"
    )
    cid = _one(
        conn,
        "insert into core.company (cik, company_name) values ('0001018724', 'AMZN TEST') returning id",
    )
    conn.commit()
    d = tmp_path / FX.name
    shutil.copytree(FX, d)
    m = json.loads((d / "manifest.json").read_text())
    m["input_sha256"] = m[
        "source_input_sha256"
    ]  # the fixture names its source shard's hash
    (d / "manifest.json").write_text(json.dumps(m))
    for t in d.glob(
        "*.tsv"
    ):  # the loader reads <table>.tsv.zst (FORMATS-v1 §1); the fixture is plain .tsv
        t.with_suffix(".tsv.zst").write_bytes(
            subprocess.run(
                ["zstd", "-q", "-c", str(t)], capture_output=True, check=True
            ).stdout
        )
    assert load.load_company(conn, d, loader_commit="test")["filings"] == 2
    conn.commit()
    cal = tmp_path / "calendar.csv.gz"
    import gzip

    with gzip.open(cal, "wt") as fh:
        fh.write(
            "company_id,cik,fiscal_year,fiscal_period,period_type,period_start,period_end\n"
        )
    rep = pilot.report_company(conn, cid, cal, set(), debt_lane=lane)
    td = {
        r["fsn_end"]: r
        for r in rep["_cells"]
        if r["data_point_name"] == "total_debt_resolved"
    }
    got = td["2023-12-31"]
    assert got["state"] == "value" and got["value"] == "78917000000"
    assert (
        got["accession"] == "0001018724-24-000008" and got["rule_id"] == debt.RULE_VALUE
    )
    # lineage: the face LTD, the note current portion and the note finance-lease total, from fsn.value of that filing
    tags = {
        r[0]
        for r in conn.execute(
            "select t.tag from fsn.value v join fsn.tag t on t.id = v.tag_id where v.id = any(%s)",
            (got["source_value_ids"],),
        ).fetchall()
    }
    assert {
        "LongTermDebtNoncurrent",
        "LongTermDebtCurrent",
        "FinanceLeaseLiability",
    } <= tags
    total = sum(
        Decimal(r[0])
        for r in conn.execute(
            "select v.value from fsn.value v join fsn.tag t on t.id = v.tag_id where v.id = any(%s) "
            "and t.tag in ('LongTermDebtNoncurrent', 'LongTermDebtCurrent', 'FinanceLeaseLiability')",
            (got["source_value_ids"],),
        ).fetchall()
    )
    assert total == Decimal(got["value"])
    assert (
        td["2018-12-31"]["state"] == "defect"
        and td["2018-12-31"]["reason_code"] == "debt_lease_member_unverified"
    )
    assert not [
        g
        for g in rep["_gaps"]
        if g["data_point"] == "total_debt_resolved" and g["period_end"] == "2023-12-31"
    ]


# ---------------------------------------------------------------- a parenthetical is never a balance-sheet line
def _parenthetical_company(root: Path) -> Path:
    """One 10-K: two face debt lines and MSFT's parenthetical 'Short-term investments, securities loaned'
    (us-gaap:SecuritiesLoaned, inpth=1; FY2016 10-K 0001193125-16-662209 R6, Tag Expert 2026-11-09)."""
    d = root / "0000000001"
    d.mkdir(parents=True)
    a = "0000000001-16-000001"
    (d / "manifest.json").write_text('{"cik": "0000000001"}')
    (d / "sub.tsv").write_text(
        "fsn_set\tadsh\tcik\tform\tperiod\tfiled\taccepted\taciks\tfye\n"
        f"2016q3\t{a}\t1\t10-K\t20160630\t20160801\t2016-08-01 16:00:00.0\t\t0630\n"
    )
    face = [
        ("Assets", "Total assets"),
        ("ShortTermBorrowings", "Short-term debt"),
        ("LongTermDebtNoncurrent", "Long-term debt"),
        ("Liabilities", "Total liabilities"),
        ("LiabilitiesAndStockholdersEquity", "Total"),
    ]
    pre = "adsh\treport\tline\tstmt\tinpth\ttag\tversion\tprole\tplabel\tnegating\n"
    pre += "".join(
        f"{a}\t2\t{i}\tBS\t0\t{t}\tus-gaap/2016\tterseLabel\t{lab}\t0\n"
        for i, (t, lab) in enumerate(face, 1)
    )
    pre += f"{a}\t3\t1\tBS\t1\tSecuritiesLoaned\tus-gaap/2016\tterseLabel\tShort-term investments, securities loaned\t0\n"
    (d / "pre.tsv").write_text(pre)
    vals = {
        "Assets": 1000,
        "ShortTermBorrowings": 100,
        "LongTermDebtNoncurrent": 400,
        "Liabilities": 600,
        "LiabilitiesAndStockholdersEquity": 1000,
        "SecuritiesLoaned": 204,
    }
    (d / "num.tsv").write_text(
        "adsh\ttag\tversion\tddate\tqtrs\tuom\tdimh\tiprx\tvalue\tfootnote\tfootlen\tdimn\tcoreg\tdurp\tdatp\tdcml\n"
        + "".join(
            f"{a}\t{t}\tus-gaap/2016\t20160630\t0\tUSD\t0x00000000\t0\t{v}\t\t\t\t\t\t\t-6\n"
            for t, v in vals.items()
        )
    )
    (d / "cal.tsv").write_text(
        "adsh\tgrp\tarc\tnegative\tptag\tpversion\tctag\tcversion\n"
        + "".join(
            f"{a}\t1\t{i}\t1\tLiabilities\tus-gaap/2016\t{t}\tus-gaap/2016\n"
            for i, t in enumerate(("ShortTermBorrowings", "LongTermDebtNoncurrent"), 1)
        )
    )
    return d


def test_a_parenthetical_line_never_makes_a_debt_record_dirty(tmp_path):
    d = _parenthetical_company(tmp_path / "companies")
    rep = debt.run_lane(tmp_path / "companies", tmp_path / "work")
    recs = [
        json.loads(x) for x in (rep.parent / "records.jsonl").read_text().splitlines()
    ]
    assert recs and all(r["coverage_clean"] for r in recs), [
        r["uncovered_candidates"] for r in recs
    ]
    assert not any(
        c["verdict"] == "not_computable_uncovered_candidates"
        for c in json.loads(rep.read_text())["cells"]
    )
    # the face lines are still read; only the parenthetical is gone
    import sys

    sys.path.insert(0, str(ROOT / "pipeline" / "scripts" / "slot_records"))
    import fsn_company_bs as fc

    (f,) = fc.instants(d, debt_only=True)
    assert {r["tag"] for r in f["bs"]} == {
        "Assets",
        "ShortTermBorrowings",
        "LongTermDebtNoncurrent",
        "Liabilities",
        "LiabilitiesAndStockholdersEquity",
    }
