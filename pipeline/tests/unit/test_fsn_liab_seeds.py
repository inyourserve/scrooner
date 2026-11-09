"""A member of the liabilities total is never mapped AS the total (FAMILY-RELEASE-CASE-2026-11-09 §3a).

The exported seed bs.liab_cal_child@1 (calc_position, child_of total_liabilities) made the store map every custom calc
child of `Liabilities` as `total_liabilities_resolved`. Beside the printed total that is two values for one key: select
blanks the key `conflicting_values_in_filing` ("the filing prints two different values"), a false reason (production
fsn.line_map 2026-11-09: 6,469 lines in 4,479 filings). The real mapping.map_filing runs here over the committed seeds
with a cursor that serves one synthetic classified balance sheet (no database)."""

import json
from datetime import date
from pathlib import Path

from scrooner_pipeline.fsn_store import mapping

ROOT = Path(__file__).resolve().parents[3]
RULES = ROOT / "data-team" / "47-fsn-store" / "concept_rules"
V, C = "us-gaap/2023", "0000000001-24-000001"


def _rules():
    rows = []
    for f in sorted(RULES.glob("*.jsonl")):
        if not f.name.startswith("_"):
            rows += [json.loads(x) for x in f.open() if x.strip()]
    rows.sort(key=lambda r: r["priority"])
    ids = {
        n: i
        for i, n in enumerate(sorted({r["canonical_concept"] for r in rows}), start=1)
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
    return mapping.load_rules(_Conn([db])), {v: k for k, v in ids.items()}


class _Cur:
    def __init__(self, conn):
        self.conn = conn
        self.res = None

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
        self.script = script
        self.written = []

    def cursor(self):
        return _Cur(self)


# a classified balance sheet: payables (std) and a custom accrual under current liabilities; long-term debt (std) and
# a custom other liability under Liabilities; the printed Liabilities total
LINES = [
    ("2", 10, "BS", "AccountsPayableCurrent", V, False, False),
    ("2", 11, "BS", "AccruedCompensationCustom", C, True, False),
    ("2", 12, "BS", "LiabilitiesCurrent", V, False, False),
    ("2", 13, "BS", "LongTermDebtNoncurrent", V, False, False),
    ("2", 14, "BS", "OtherLiabilitiesCustom", C, True, False),
    ("2", 15, "BS", "Liabilities", V, False, False),
]
ARCS = [
    ("LiabilitiesCurrent", V, "AccountsPayableCurrent", V),
    ("LiabilitiesCurrent", V, "AccruedCompensationCustom", C),
    ("Liabilities", V, "LiabilitiesCurrent", V),
    ("Liabilities", V, "LongTermDebtNoncurrent", V),
    ("Liabilities", V, "OtherLiabilitiesCustom", C),
]


def _map():
    rules, name = _rules()
    conn = _Conn([[(date(2024, 12, 31),)], LINES, ARCS, None])
    mapping.map_filing(conn, 1, rules, write=True)
    return {(r[1], r[2]): (name.get(r[3]), r[4], r[5]) for r in conn.written}


def test_a_custom_child_of_liabilities_is_never_mapped_as_the_total():
    m = _map()
    assert m[("2", 15)][:2] == (
        "total_liabilities_resolved",
        "mapped",
    )  # the printed total
    assert m[("2", 14)][0] != "total_liabilities_resolved", m[("2", 14)]
    total = [
        k
        for k, v in m.items()
        if v[0] == "total_liabilities_resolved" and v[1] == "mapped"
    ]
    assert total == [("2", 15)]


def test_no_seed_maps_a_line_as_the_liabilities_total_by_position():
    rows = [json.loads(x) for x in (RULES / "bs.jsonl").open() if x.strip()]
    assert not [
        r["rule_id"]
        for r in rows
        if r["canonical_concept"] == "total_liabilities_resolved"
        and r["match_kind"] == "calc_position"
        and (r["position"] or {}).get("relation") == "child_of"
    ]
