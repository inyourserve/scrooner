#!/usr/bin/env python3
"""Scoreboard generator (WO-7, Data Triage). Reads a CELL EXTRACT and writes
  scoreboard/<date>.csv          long format: H header rows, K KPI rows, R reconciliation rows, M movement rows
  scoreboard/defects/<date>.defects.csv.gz   proxy defect register (source = proxy)
  scoreboard/cells/<date>.cells.csv.gz       the extract itself (the history; tables are rebuilt in place)
  scoreboard/MANIFEST.sha256, CHAIN.md       appended only
Published files are immutable (AT-7.14): an existing file is never overwritten; a correction is
<date>.rN.csv (--erratum N) with the reason, and the original stays.

Rules it enforces: RT-1 must pass first (exit 1 otherwise); a figure with no source is NOT_COMPUTABLE
with the dependency named, never 0 or blank (AT-7.11); every row has a version, a denominator id and a
status (AT-7.9); unmapped reasons must be 0 before the register is written (AT-7.7).

usage: build_scoreboard.py [--cells PATH] [--as-of YYYY-MM-DD] [--prev-cells PATH] [--prev-defects PATH]
                           [--ref-end PATH] [--out-dir DIR] [--erratum N --reason TEXT] [--check-only]
"""

from __future__ import annotations

import argparse
import csv
import io
import subprocess
import sys
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import rt1_reconcile  # noqa: E402
import sb_lib as L  # noqa: E402

COLUMNS = [
    "scoreboard_date",
    "section",
    "k_id",
    "k_version",
    "segment",
    "denominator_id",
    "numerator",
    "denominator",
    "value",
    "unit",
    "status",
    "evidence_class",
    "watermark",
    "query_file",
    "query_sha256",
    "extract_sha256",
    "note",
]
STATUSES = ("MEASURED", "PROXY", "REPORTED", "NOT_COMPUTABLE", "NOT_RUN")
GENERATOR_VERSION = "build_scoreboard@1"

# Baselines taken from documents (REPORTED, not recomputed here). Source: doc 44 as quoted in
# data-team/strategy/team/WO-REVIEW-data-triage.md K4b / K12 rows.
DOC44_PERIOD_GAPS = [
    ("no_mapped_tag", 8324),
    ("q4_not_derived", 5767),
    ("quarter_not_derived", 5320),
    ("no_line_item_filed", 1876),
    ("not_in_sec_feed", 1796),
    ("filing_not_processed", 851),
    ("conflict_material", 785),
    ("conflict_split", 59),
    ("not_resolved", 25),
    ("conflict_rounding", 3),
]
DOC44_BUILD_ASSUMED = "2026-10-20T18:52:00Z"
# Product head K1c proxy (doc 49 section 7.10): valued concept cells whose latest period is older
# than 2025-07-01. Cutoff is a proxy for common/staleness.py. NOT recomputed (the export has no periods).
PRODUCT_K1C_OLDER_CELLS = 5436


class Rows:
    def __init__(self, as_of: str, extract_sha: str, qsha_default: str):
        self.as_of, self.sha, self.qsha = as_of, extract_sha, qsha_default
        self.rows: list[dict] = []

    def add(
        self,
        section,
        k_id,
        ver,
        seg,
        den_id,
        num,
        den,
        value,
        unit,
        status,
        ev,
        wm="",
        qfile="scripts/build_scoreboard.py",
        qsha=None,
        note="",
    ):
        self.rows.append(
            {
                "scoreboard_date": self.as_of,
                "section": section,
                "k_id": k_id,
                "k_version": ver,
                "segment": seg,
                "denominator_id": den_id,
                "numerator": "" if num is None else num,
                "denominator": "" if den is None else den,
                "value": "" if value is None else value,
                "unit": unit,
                "status": status,
                "evidence_class": ev,
                "watermark": wm,
                "query_file": qfile,
                "query_sha256": qsha or self.qsha,
                "extract_sha256": self.sha,
                "note": note,
            }
        )

    def nc(
        self,
        section,
        k_id,
        ver,
        seg,
        den_id,
        unit,
        why,
        status="NOT_COMPUTABLE",
        qfile="",
        qsha="",
    ):
        self.add(
            section,
            k_id,
            ver,
            seg,
            den_id,
            None,
            None,
            None,
            unit,
            status,
            "n/a",
            qfile=qfile or "scripts/build_scoreboard.py",
            qsha=qsha or self.qsha,
            note=why,
        )


def sql_sha(name: str) -> str:
    return L.sha256_file(L.SB_DIR / "sql" / name)


def script_sha() -> str:
    b = (L.SCRIPTS / "build_scoreboard.py").read_bytes() + (
        L.SCRIPTS / "sb_lib.py"
    ).read_bytes()
    return L.sha256_bytes(b)


def query_files_sha() -> str:
    parts = []
    for p in sorted((L.SB_DIR / "sql").glob("*.sql")) + [
        L.SCRIPTS / "build_scoreboard.py",
        L.SCRIPTS / "sb_lib.py",
        L.SCRIPTS / "rt1_reconcile.py",
    ]:
        parts.append(p.name.encode() + b"=" + L.sha256_file(p).encode())
    return L.sha256_bytes(b"\n".join(parts))


def git_head() -> str:
    try:
        return subprocess.check_output(
            ["git", "-C", str(L.REPO), "rev-parse", "HEAD"],
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
    except Exception:  # noqa: BLE001
        return "unknown"


def grid_report(ext: L.Extract, ids, names):
    """D0 grid vs the extract: cells absent from the table (kept in D0), cells outside D0."""
    idset, nameset = set(ids), set(names)
    present = {k for k in ext.cells if k[0] in idset and k[1] in nameset}
    absent_cells = [
        (c, n)
        for c in ids
        for n in names
        if (c, n) not in ext.cells or ext.cells[(c, n)]["absent"]
    ]
    outside = [k for k in ext.cells if k[0] not in idset or k[1] not in nameset]
    return absent_cells, outside, present


def build(
    ext: L.Extract,
    as_of: str,
    extract_path: Path,
    prev: L.Extract | None,
    ref_end: dict | None,
    out_dir: Path,
):
    graph = L.load_graph()
    ids, cohort = L.load_cohort()
    names = L.read_lines(L.D0_NAMES_FILE)
    removed = set(L.read_lines(L.D0E_REMOVED_FILE))
    keep = set(names) - removed
    ext_sha = L.sha256_decompressed(extract_path)
    qsha = script_sha()
    R = Rows(as_of, ext_sha, qsha)

    absent_cells, outside, _present = grid_report(ext, ids, names)
    # build the effective D0 grid: an absent cell counts as blank-and-absent, never dropped
    t0 = L.tally(ext, graph, names=set(names))
    t_e = L.tally(ext, graph, names=keep)
    valued_total, blank_listed = t0["valued"], t0["blank"]
    D0 = len(ids) * len(names)
    n_abs = len(absent_cells)
    # tally counts only listed cells; absent grid cells are blank by construction
    blank_total = D0 - valued_total
    wm = (
        f"export:{ext_sha[:16]};build_ASSUMED:{DOC44_BUILD_ASSUMED}"
        if ext_sha == L.EXPORT_SHA256
        else f"extract:{ext_sha[:16]}"
    )

    is_export = ext_sha == L.EXPORT_SHA256
    # ---- H ----
    H = lambda k, v, st, ev, note="", unit="text": R.add(
        "H", k, "1", "all", "D0", None, None, v, unit, st, ev, wm="", note=note
    )
    H("H.scoreboard_published_on", date.today().isoformat(), "MEASURED", "MEASURED")
    H("H.generator_version", GENERATOR_VERSION, "MEASURED", "MEASURED")
    if is_export:
        H(
            "H.coverage_checked_at",
            DOC44_BUILD_ASSUMED,
            "REPORTED",
            "ASSUMED",
            "doc 44 text; the export has no checked_at column, so the file hash is its identity",
        )
    else:
        R.nc(
            "H",
            "H.coverage_checked_at",
            "1",
            "all",
            "D0",
            "text",
            "read it from the extract header.json (extract_live.py)",
        )
    for k, why in [
        ("H.snapshot_date", "needs a database read (sql/H_headers.sql)"),
        ("H.period_gap_checked_at", "needs a database read (sql/H_headers.sql)"),
        (
            "H.certification_checks_run_at",
            "0097 not applied (Data Head, 2026-10-22); table analytics.company_certification absent",
        ),
        (
            "H.certify_run_id",
            "0097 amendment (suite_version, certify_run_id, rule_id: F8) not applied",
        ),
        ("H.suite_version", "0097 amendment (F8) not applied"),
        ("H.template_version", "templates not frozen (Gate C, WO-1.6 design review)"),
        ("H.definition_version", "no definition layer frozen; accountant not named"),
    ]:
        R.nc("H", k, "1", "all", "D0", "text", why)
    H(
        "H.register_version",
        "FREEZE-REGISTER-2026-10-22 (PROPOSED, not approved)",
        "REPORTED",
        "ASSUMED",
        "the register is for founder approval; this row is NOT an approval",
    )
    H(
        "H.cohort_ids_hash",
        L.id_list_hash(ids),
        "MEASURED",
        "MEASURED",
        "sha256 of sorted numeric ids, first 16 hex",
    )
    H("H.datapoints_hash", L.name_list_hash(names), "MEASURED", "MEASURED")
    H(
        "H.d0e_removed_hash",
        L.name_list_hash(removed),
        "MEASURED",
        "MEASURED",
        "30 removed data points",
    )
    H("H.graph_sha256", L.sha256_file(L.GRAPH), "MEASURED", "MEASURED")
    H("H.shards_sha256", L.sha256_file(L.SHARDS), "MEASURED", "MEASURED")
    H(
        "H.reason_class_map_sha256",
        L.sha256_file(L.REASON_MAP),
        "MEASURED",
        "MEASURED",
        "frozen reason_class_map v1",
    )
    H(
        "H.query_files_git_sha",
        git_head(),
        "MEASURED",
        "MEASURED",
        "HEAD of the repo when generated (the parent of the commit that publishes this file)",
    )
    H(
        "H.query_files_sha256",
        query_files_sha(),
        "MEASURED",
        "MEASURED",
        "sql/*.sql and the three scripts",
    )
    H("H.extract_sha256", ext_sha, "MEASURED", "MEASURED")
    R.nc(
        "H",
        "H.db_connections_at_start",
        "1",
        "all",
        "D0",
        "count",
        "no database was used: this scoreboard is a file replay"
        if is_export
        else "see extract header.json",
        status="NOT_RUN",
    )

    # ---- R: reconciliation ----
    rt1 = rt1_reconcile.run()
    rt1_fail = [r for r in rt1 if not r["passed"]]
    R.add(
        "R",
        "RT-1",
        "1",
        "all",
        "D0",
        len(rt1) - len(rt1_fail),
        len(rt1),
        "PASS" if not rt1_fail else "FAIL",
        "equalities",
        "MEASURED",
        "MEASURED",
        wm=wm,
        qfile="scripts/rt1_reconcile.py",
        qsha=L.sha256_file(L.SCRIPTS / "rt1_reconcile.py"),
        note="exact equality of the committed 2026-10-20 export with doc 44; no number is published unless PASS",
    )
    R.add(
        "R",
        "D0.cells",
        "1",
        "all",
        "D0",
        D0,
        D0,
        D0,
        "cells",
        "MEASURED",
        "MEASURED",
        wm=wm,
        note=f"{len(ids)} companies x {len(names)} data points (cohort file v1)",
    )
    R.add(
        "R",
        "D0.absent_from_table",
        "1",
        "all",
        "D0",
        n_abs,
        D0,
        n_abs,
        "cells",
        "MEASURED",
        "MEASURED",
        wm=wm,
        note="grid cells with no row in the extract; kept in D0 as blank, never dropped. ids: "
        + ",".join(str(i) for i in sorted({c for c, _ in absent_cells})[:50]),
    )
    R.add(
        "R",
        "D0.outside_grid",
        "1",
        "all",
        "D0",
        len(outside),
        None,
        len(outside),
        "cells",
        "MEASURED",
        "MEASURED",
        wm=wm,
        note="extract cells whose company or data point is not in D0 (not counted anywhere)",
    )
    R.add(
        "R",
        "D0e.removed_rows",
        "1",
        "all",
        "D0e",
        len(removed) * len(ids),
        D0,
        len(removed) * len(ids),
        "cells",
        "MEASURED",
        "MEASURED",
        wm=wm,
        note=f"{len(removed)} data points x {len(ids)} companies (F-1; founder decision pending)",
    )
    R.add(
        "R",
        "D0e.cells",
        "1",
        "all",
        "D0e",
        D0 - len(removed) * len(ids),
        D0,
        D0 - len(removed) * len(ids),
        "cells",
        "MEASURED",
        "MEASURED",
        wm=wm,
        note="D0 minus F-1 removal",
    )
    R.nc(
        "R",
        "D1.cells",
        "1",
        "all",
        "D1",
        "cells",
        "template denominator: needs groups v2 and templates v1 (Gate C, design review AT-1.6a)",
    )
    R.nc(
        "R",
        "RT-2",
        "1",
        "all",
        "D0",
        "cells",
        "live extract E0/E1 not taken (database held for scrooner-4d); cell-level diff against this export runs when E0 exists",
        status="NOT_RUN",
    )
    R.nc(
        "R",
        "RT-3",
        "1",
        "all",
        "D0",
        "text",
        "period-gap and K12 baselines need live queries",
        status="NOT_RUN",
    )

    # ---- K1 ----
    qk = "scripts/build_scoreboard.py"

    def k1(seg, den_id, tl, absent=0):
        d = tl["cells"] + absent
        R.add(
            "K",
            "K1",
            "1",
            seg,
            den_id,
            tl["valued"],
            d,
            L.pct(tl["valued"], d),
            "percent",
            "MEASURED",
            "MEASURED",
            wm=wm,
            qfile=qk,
            note="coverage table as stored (mixed semantics, F2: concept rows = any period). Never quote without K1c beside it",
        )

    k1("all", "D0", t0, n_abs)
    k1("all", "D0e", t_e, 0)
    R.add(
        "K",
        "K1.valued",
        "1",
        "all",
        "D0",
        valued_total,
        D0,
        valued_total,
        "cells",
        "MEASURED",
        "MEASURED",
        wm=wm,
        qfile=qk,
    )
    R.add(
        "K",
        "K1.blank",
        "1",
        "all",
        "D0",
        blank_total,
        D0,
        blank_total,
        "cells",
        "MEASURED",
        "MEASURED",
        wm=wm,
        qfile=qk,
        note="blank listed + absent_from_table",
    )
    R.add(
        "K",
        "K1.valued",
        "1",
        "all",
        "D0e",
        t_e["valued"],
        t_e["cells"],
        t_e["valued"],
        "cells",
        "MEASURED",
        "MEASURED",
        wm=wm,
        qfile=qk,
    )
    R.add(
        "K",
        "K1.blank",
        "1",
        "all",
        "D0e",
        t_e["blank"],
        t_e["cells"],
        t_e["blank"],
        "cells",
        "MEASURED",
        "MEASURED",
        wm=wm,
        qfile=qk,
    )
    ctype = {"concept": L.CONCEPT_KINDS, "metric": L.METRIC_KINDS}
    for tname, kinds in ctype.items():
        cells = sum(t0["by_kind"][k]["cells"] for k in kinds)
        v = sum(t0["by_kind"][k]["valued"] for k in kinds)
        R.add(
            "K",
            "K1",
            "1",
            f"type:{tname}",
            "D0",
            v,
            cells,
            L.pct(v, cells),
            "percent",
            "MEASURED",
            "DATA-INFERRED",
            wm=wm,
            qfile=qk,
            note="type from dependency-graph kind, not the registry data_point_type (the authority; confirm in T3)",
        )
    for k in L.KIND_ORDER:
        c = t0["by_kind"][k]
        R.add(
            "K",
            "K1",
            "1",
            f"kind:{k}",
            "D0",
            c["valued"],
            c["cells"],
            L.pct(c["valued"], c["cells"]),
            "percent",
            "MEASURED",
            "MEASURED",
            wm=wm,
            qfile=qk,
        )
    # DRAFT groups (superseded v1 draft): shown as DRAFT, never as K13
    try:
        grp = {
            int(r["company_id"]): r["group"]
            for r in csv.DictReader(open(L.GROUPS_DRAFT, newline=""))
        }
        byg = defaultdict(Counter)
        for (cid, dp), c in ext.cells.items():
            if dp in set(names) and cid in grp:
                byg[grp[cid]]["cells"] += 1
                byg[grp[cid]]["valued"] += 1 if c["has_value"] else 0
        for g in sorted(byg):
            R.add(
                "K",
                "K1",
                "1",
                f"group_DRAFT:{g}",
                "D0",
                byg[g]["valued"],
                byg[g]["cells"],
                L.pct(byg[g]["valued"], byg[g]["cells"]),
                "percent",
                "PROXY",
                "DATA-INFERRED",
                wm=wm,
                qfile=qk,
                note="group_assignment_draft.csv is DRAFT and superseded by v2; not a K13 figure",
            )
    except FileNotFoundError:
        pass

    # ---- K1c / K7 / K1h / K1a / K1b ----
    has_periods = any(c["latest_end"] for c in ext.cells.values() if c["has_value"])
    if has_periods and ref_end is not None:
        ann, qtr = L.staleness_thresholds()
        stale = 0
        for (cid, dp), c in ext.cells.items():
            if (
                dp in set(names)
                and c["has_value"]
                and L.is_stale(
                    c["latest_label"], c["latest_end"], ref_end.get(cid, ""), ann, qtr
                )
            ):
                stale += 1
        R.add(
            "K",
            "K7",
            "1",
            "all",
            "D0",
            stale,
            valued_total,
            stale,
            "cells",
            "MEASURED",
            "MEASURED",
            wm=wm,
            qfile="sql/K7_reference_end.sql",
            qsha=sql_sha("K7_reference_end.sql"),
            note=f"thresholds read from common/staleness.py: annual>{ann}d, quarterly/TTM>{qtr}d; parity test AT-7.12 runs separately",
        )
        R.add(
            "K",
            "K1c",
            "1",
            "all",
            "D0",
            valued_total - stale,
            D0,
            L.pct(valued_total - stale, D0),
            "percent",
            "MEASURED",
            "MEASURED",
            wm=wm,
            qfile="sql/K7_reference_end.sql",
            qsha=sql_sha("K7_reference_end.sql"),
            note="valued AND current; the honest headline, quoted beside K1@1",
        )
    else:
        why = (
            "the committed export has no period columns and no K7 reference dates; needs Q0b "
            "(sql/Q0b_*.sql) + sql/K7_reference_end.sql from a live extract (E0)"
        )
        R.nc(
            "K",
            "K7",
            "1",
            "all",
            "D0",
            "cells",
            why,
            qfile="sql/K7_reference_end.sql",
            qsha=sql_sha("K7_reference_end.sql"),
        )
        R.nc(
            "K",
            "K1c",
            "1",
            "all",
            "D0",
            "percent",
            why,
            qfile="sql/Q0b_concept_latest_period.sql",
            qsha=sql_sha("Q0b_concept_latest_period.sql"),
        )
        if is_export:
            num = valued_total - PRODUCT_K1C_OLDER_CELLS
            R.add(
                "K",
                "K1c.product_head_proxy",
                "1",
                "all",
                "D0",
                num,
                D0,
                L.pct(num, D0),
                "percent",
                "REPORTED",
                "ASSUMED",
                wm=wm,
                qfile="doc 49 section 7.10 (not a query)",
                qsha="n/a",
                note=f"Product head proxy, NOT recomputed: {valued_total} valued minus {PRODUCT_K1C_OLDER_CELLS} concept cells "
                "with latest period before 2025-07-01 (cutoff is a proxy for common/staleness.py). Replaced by the measured K1c at E0",
            )
    if has_periods and any(c["any_period"] != "" for c in ext.cells.values()):
        h = sum(
            1
            for (cid, dp), c in ext.cells.items()
            if c["type"] == "metric"
            and c["any_period"] in ("t", "true", "True")
            and not c["has_value"]
        )
        R.add(
            "K",
            "K1h",
            "1",
            "all",
            "D0",
            h,
            None,
            h,
            "cells",
            "MEASURED",
            "MEASURED",
            wm=wm,
            note="metric rows: ever valued, latest period blank",
        )
    else:
        R.nc(
            "K",
            "K1h",
            "1",
            "all",
            "D0",
            "cells",
            "0096 not applied (has_value_any_period absent); needs apply + one rebuild",
            qfile="sql/Q0_base_cells.sql",
            qsha=sql_sha("Q0_base_cells.sql"),
        )
    R.nc(
        "K",
        "K1a",
        "1",
        "all",
        "D0",
        "cells",
        "= valued minus K1b; K1b needs cell_state (Gate C)",
    )
    R.nc(
        "K",
        "K1b",
        "1",
        "all",
        "D0",
        "cells",
        "cells hidden by a guard, per rule id: needs cell_state (Gate C); today only the serve-time staleness guard via K7",
    )

    # ---- K2 ----
    def k2(seg, den_id, count, blanks):
        R.add(
            "K",
            "K2",
            "1",
            seg,
            den_id,
            count,
            blanks,
            count,
            "cells",
            "MEASURED",
            "MEASURED",
            wm=wm,
            qfile=qk,
            note=f"reasonless blanks (null gap_reason); {L.pct(count, blanks)}% of blanks",
        )

    k2("all", "D0", t0["reasonless"] + n_abs, blank_total)
    k2("all", "D0e", t_e["reasonless"], t_e["blank"])
    for k in (
        "leaf_concept",
        "metric",
        "resolved_concept",
        "derived_concept",
        "price_metric",
        "external_source",
    ):
        c = t0["by_kind"][k]
        k2(f"kind:{k}", "D0", c["reasonless"], c["blank"])
    R.nc(
        "K",
        "K2",
        "2",
        "all",
        "D0",
        "cells",
        "unclassified cells in cell_state; Gate C target 0",
    )
    vwr = Counter(
        dp for (cid, dp), c in ext.cells.items() if c["has_value"] and c["reason"]
    )
    R.add(
        "K",
        "K2c",
        "1",
        "all",
        "D0",
        sum(vwr.values()),
        valued_total,
        sum(vwr.values()),
        "cells",
        "MEASURED",
        "MEASURED",
        wm=wm,
        qfile=qk,
        note="valued cells that carry a reason (F6); NOT counted in K2; routed to the Verifier (W13 candidate)",
    )
    for dp, n in sorted(vwr.items()):
        R.add(
            "K",
            "K2c",
            "1",
            f"dp:{dp}",
            "D0",
            n,
            None,
            n,
            "cells",
            "MEASURED",
            "MEASURED",
            wm=wm,
            qfile=qk,
        )

    # ---- K3 .. K14 ----
    R.nc(
        "K",
        "K3",
        "1",
        "all",
        "D1",
        "percent",
        "template coverage: needs cell_state + groups v2 + templates v1 + both heads' dated sign lines (AT-1.6a)",
    )

    # K4 proxy
    rmap = L.load_reason_map()
    clf = L.Classifier(ext, graph, rmap)
    defects, by_class, by_owner = [], Counter(), Counter()
    name_set = set(names)
    for cid, dp in sorted(ext.cells):
        if dp not in name_set:
            continue
        c = ext.cells[(cid, dp)]
        if c["has_value"] and not c["reason"]:
            continue
        cls, owner, rf, note = clf.classify(cid, dp)
        state = "valued_with_reason" if c["has_value"] else "blank"
        defects.append(
            (
                cid,
                dp,
                graph.get(dp, {}).get("kind", "?"),
                state,
                c["reason"],
                cls,
                owner,
                rf,
                note,
            )
        )
        if not c["has_value"]:
            by_class[cls] += 1
            by_owner[owner] += 1
    for cid, dp in absent_cells:
        defects.append(
            (
                cid,
                dp,
                graph.get(dp, {}).get("kind", "?"),
                "absent_from_table",
                "",
                "unclassified",
                "triage",
                "",
                "absent_from_table",
            )
        )
        by_class["unclassified"] += 1
        by_owner["triage"] += 1
    R.add(
        "K",
        "K4.unmapped_reasons",
        "1",
        "all",
        "D0",
        sum(clf.unmapped.values()),
        None,
        sum(clf.unmapped.values()),
        "cells",
        "MEASURED",
        "MEASURED",
        wm=wm,
        qfile=qk,
        note="reason patterns with no row in the frozen map; must be 0 before the register is published: "
        + ";".join(sorted(clf.unmapped)),
    )
    if clf.unmapped:
        raise SystemExit(
            f"UNMAPPED reason patterns, register not published: {sorted(clf.unmapped)}"
        )
    for cls in L.CLASSES:
        R.add(
            "K",
            "K4",
            "proxy@1",
            f"class:{cls}",
            "D0",
            by_class.get(cls, 0),
            blank_total,
            by_class.get(cls, 0),
            "cells",
            "PROXY",
            "DATA-INFERRED",
            wm=wm,
            qfile=qk,
            note="blank cells by proxy class; a cascade inherits its blocking input's class; NOT counted as covered or as defects in the headline until calibrated",
        )
    for ow in L.OWNERS:
        R.add(
            "K",
            "K4",
            "proxy@1",
            f"owner:{ow}",
            "D0",
            by_owner.get(ow, 0),
            blank_total,
            by_owner.get(ow, 0),
            "cells",
            "PROXY",
            "DATA-INFERRED",
            wm=wm,
            qfile=qk,
        )

    # K4b / K12 baselines REPORTED + live NC
    for cause, n in DOC44_PERIOD_GAPS:
        R.add(
            "K",
            "K4b",
            "1",
            f"cause:{cause}",
            "D0",
            n,
            None,
            n,
            "periods",
            "REPORTED",
            "ASSUMED",
            wm="doc44",
            qfile="sql/K4b_period_gaps.sql",
            qsha=sql_sha("K4b_period_gaps.sql"),
            note="doc 44 baseline as quoted in the Triage review, NOT recomputed; unit = missing period, never added to cells",
        )
    R.nc(
        "K",
        "K4b",
        "1",
        "live",
        "D0",
        "periods",
        "live period_gap read not taken (database held); sql/K4b_period_gaps.sql",
        qfile="sql/K4b_period_gaps.sql",
        qsha=sql_sha("K4b_period_gaps.sql"),
    )
    R.nc(
        "K",
        "K4c",
        "1",
        "all",
        "D0",
        "findings",
        "live read not taken; after 0097 also certification findings",
        qfile="sql/K4c_findings.sql",
        qsha=sql_sha("K4c_findings.sql"),
    )
    R.add(
        "K",
        "K12a",
        "1",
        "all",
        "D0",
        89,
        None,
        89,
        "filings",
        "REPORTED",
        "ASSUMED",
        wm="doc44",
        qfile="sql/K12a_zero_fact_filings.sql",
        qsha=sql_sha("K12a_zero_fact_filings.sql"),
        note="doc 44 baseline: 89 periodic filings since 2026-07-01 with zero facts, in 89 companies; NOT recomputed",
    )
    R.nc(
        "K",
        "K12a",
        "1",
        "live",
        "D0",
        "filings",
        "live read not taken (database held)",
        qfile="sql/K12a_zero_fact_filings.sql",
        qsha=sql_sha("K12a_zero_fact_filings.sql"),
    )
    R.nc(
        "K",
        "K12b",
        "1",
        "all",
        "D0",
        "companies",
        "live read not taken (database held). Doc 46 quotes 88 companies: UNRECONCILED with K12a's 89 until measured",
        qfile="sql/K12b_newest_filing_lag.sql",
        qsha=sql_sha("K12b_newest_filing_lag.sql"),
    )
    for k, why in [
        (
            "K5a",
            "regression list A20 does not exist yet (columns in the review section 1.3)",
        ),
        (
            "K5b",
            "INPUT: Verifier sample outcomes with observed/sample_seed/frame_size; Triage draws the frame",
        ),
        ("K6", "INPUT: Verifier guard samples (hidden_wrong/hidden_correct fields)"),
        (
            "K8",
            "0097 not applied; analytics.company_certification absent; every company is uncertified by absence, which is not 'checked and not certified'",
        ),
        ("K9", "INPUT: effort log (REPORTED at best, never independent)"),
        ("K10", "needs cell_state rule ids on state rows and a closed_by flag"),
        (
            "K11",
            "needs 0097 + Verifier precision/recall samples per rule; Triage draws the frames",
        ),
        (
            "K13",
            "INPUT: Sector Analyst audit outcomes against group_assignment_v2.csv (not yet produced)",
        ),
        ("K14a", "needs 0097 certification states"),
        (
            "K14b",
            "removed from the Gate A-E tree 2026-10-22 (app.usage_event has no company dimension; WO-10)",
        ),
    ]:
        R.nc("K", k, "1", "all", "D0", "n/a", why)

    # ---- M ----
    if prev is None:
        for k in (
            "M.value_appeared",
            "M.value_disappeared",
            "M.reason_changed",
            "M.company_absent_from_table",
            "M.cell_new",
            "M.tripwire_k1_0.5pt",
            "M.proxy_bias",
        ):
            R.nc(
                "M",
                k,
                "1",
                "all",
                "D0",
                "cells",
                "first scoreboard: no earlier extract to compare"
                if k != "M.proxy_bias"
                else "needs cell_state (two weeks of overlap with the proxy)",
                status="NOT_RUN",
            )
    else:
        diffs = L.diff_extracts(prev, ext)
        cnt = Counter(c for _, c, _, _ in diffs)
        for k in (
            "value_appeared",
            "value_disappeared",
            "reason_changed",
            "company_absent_from_table",
            "cell_new",
        ):
            R.add(
                "M",
                f"M.{k}",
                "1",
                "all",
                "D0",
                cnt.get(k, 0),
                None,
                cnt.get(k, 0),
                "cells",
                "MEASURED",
                "MEASURED",
                wm=wm,
                qfile=qk,
                note="cell-level vs the previous extract; causes (period_rollover, rebuild_code_change) need Q0b + commit list: unexplained until classified",
            )
        tp = L.tally(prev, graph, names=name_set)
        d_pct = (t0["valued"] * 1000 // D0 - tp["valued"] * 1000 // D0) / 10
        R.add(
            "M",
            "M.tripwire_k1_0.5pt",
            "1",
            "all",
            "D0",
            None,
            None,
            "YES" if abs(d_pct) >= 0.5 else "NO",
            "flag",
            "MEASURED",
            "MEASURED",
            wm=wm,
            qfile=qk,
            note=f"K1 moved {d_pct:+.1f} points; a move of 0.5 points or more forces the diff to be read",
        )
        R.nc(
            "M",
            "M.proxy_bias",
            "1",
            "all",
            "D0",
            "cells",
            "needs cell_state",
            status="NOT_RUN",
        )
    return R, defects, absent_cells


GAMING_MSG = "GAMING CHECK RED"


def gaming_check(
    prev_valued: int, prev_den: int, valued: int, den: int, chain_row_exists: bool
):
    """AT-7.13: if the percentage rose, the valued count must have risen; a changed denominator needs a
    chain row. Returns (ok, message)."""
    up_pct = valued * prev_den > prev_valued * den
    if up_pct and valued <= prev_valued:
        return (
            False,
            f"{GAMING_MSG}: percentage rose but valued count did not ({prev_valued}->{valued})",
        )
    if den != prev_den and not chain_row_exists:
        return (
            False,
            f"{GAMING_MSG}: denominator changed {prev_den}->{den} without a chain row",
        )
    return True, "ok"


def validate_rows(rows):
    """AT-7.9 and AT-7.11. Returns list of violation strings."""
    bad = []
    for i, r in enumerate(rows):
        if not r["k_version"] or not r["denominator_id"] or r["status"] not in STATUSES:
            bad.append(
                f"row {i} {r['k_id']}: missing version, denominator id or valid status"
            )
        if r["value"] == "" and r["status"] not in ("NOT_COMPUTABLE", "NOT_RUN"):
            bad.append(f"row {i} {r['k_id']}: empty value with status {r['status']}")
        if r["status"] in ("NOT_COMPUTABLE", "NOT_RUN") and not r["note"]:
            bad.append(f"row {i} {r['k_id']}: {r['status']} without a reason")
        if r["status"] in ("NOT_COMPUTABLE", "NOT_RUN") and r["value"] != "":
            bad.append(f"row {i} {r['k_id']}: {r['status']} but value is set")
        if not r["query_file"] or not r["query_sha256"]:
            bad.append(f"row {i} {r['k_id']}: no query file/hash")
    return bad


def to_csv(rows) -> str:
    sio = io.StringIO()
    w = csv.DictWriter(sio, fieldnames=COLUMNS, lineterminator="\n")
    w.writeheader()
    w.writerows(rows)
    return sio.getvalue()


def defects_csv(defects, as_of, ticker, prev_first_seen) -> str:
    sio = io.StringIO()
    w = csv.writer(sio, lineterminator="\n")
    w.writerow(
        [
            "company_id",
            "ticker",
            "data_point_name",
            "kind",
            "proxy_state",
            "gap_reason",
            "defect_class",
            "owner",
            "rf_id",
            "source",
            "proxy_note",
            "first_seen_scoreboard",
            "last_seen_scoreboard",
        ]
    )
    for cid, dp, kind, state, reason, cls, owner, rf, note in defects:
        first = prev_first_seen.get((cid, dp), as_of)
        w.writerow(
            [
                cid,
                ticker.get(cid, ""),
                dp,
                kind,
                state,
                reason,
                cls,
                owner,
                rf,
                "proxy",
                note,
                first,
                as_of,
            ]
        )
    return sio.getvalue()


def manifest_append(out_dir: Path, files):
    """Append-only MANIFEST.sha256; a listed file whose hash changed is a hard error (AT-7.14)."""
    mf = out_dir / "MANIFEST.sha256"
    known = {}
    if mf.exists():
        for ln in mf.read_text().splitlines():
            if ln.strip():
                h, _, p = ln.partition("  ")
                known[p] = h
    new = []
    for f in files:
        rel = str(Path(f).relative_to(out_dir))
        h = L.sha256_file(Path(f))
        if rel in known and known[rel] != h:
            raise SystemExit(
                f"IMMUTABILITY VIOLATION: {rel} changed since it was published (AT-7.14)"
            )
        if rel not in known:
            new.append(f"{h}  {rel}")
    if new:
        with open(mf, "a") as fh:
            fh.write("\n".join(new) + "\n")
    return len(new)


def verify_manifest(out_dir: Path):
    mf = out_dir / "MANIFEST.sha256"
    bad = []
    for ln in mf.read_text().splitlines():
        if not ln.strip():
            continue
        h, _, p = ln.partition("  ")
        fp = out_dir / p
        if not fp.exists() or L.sha256_file(fp) != h:
            bad.append(p)
    return bad


CHAIN_HEADER = """# Denominator and definition chain (generated by scripts/build_scoreboard.py; never hand-edited)

D0 (cohort file v1: 986 companies x 163 data points, fixed forever) -> D0e (minus the 30 F-1 rows) -> D1 (template cells, Gate C).
Every scoreboard publishes all three where computable; a denominator never shrinks without a row here.
Definitions: K1@1 = coverage table as stored (frozen; equals doc 44). K1c@1 = valued AND current (honest headline).
K2@1 = null gap_reason. Targets are in TARGETS.csv (versioned, never edit history).

"""


def chain_section(as_of, t0, t_e, D0, D0e, removed, n_abs):
    return (
        f"## {as_of}\n\n| step | cells | valued | pct | note |\n|---|---|---|---|---|\n"
        f"| D0 | {D0:,} | {t0['valued']:,} | {L.pct(t0['valued'], D0)}% | 986 x 163; absent_from_table {n_abs} |\n"
        f"| minus F-1 | -{D0 - D0e:,} | -{t0['valued'] - t_e['valued']:,} | | {len(removed)} data points (hash {L.name_list_hash(removed)}) |\n"
        f"| D0e | {D0e:,} | {t_e['valued']:,} | {L.pct(t_e['valued'], D0e)}% | economic-line cells (founder F-1 pending) |\n"
        f"| D1 | NOT_COMPUTABLE | | | needs groups v2 and templates v1 (Gate C) |\n\n"
    )


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--cells", type=Path, default=L.EXPORT_GZ)
    ap.add_argument("--as-of", default="2026-10-20")
    ap.add_argument("--prev-cells", type=Path)
    ap.add_argument("--prev-defects", type=Path)
    ap.add_argument(
        "--ref-end", type=Path, help="csv company_id,ref_end from extract_live.py"
    )
    ap.add_argument("--out-dir", type=Path, default=L.SB_DIR)
    ap.add_argument("--erratum", type=int)
    ap.add_argument("--reason", default="")
    ap.add_argument(
        "--check-only",
        action="store_true",
        help="run RT-1 + build in memory, write nothing",
    )
    a = ap.parse_args(argv)

    rt = rt1_reconcile.run()
    if any(not r["passed"] for r in rt):
        print("RT-1 FAILED: no number is published.", file=sys.stderr)
        for r in rt:
            if not r["passed"]:
                print(
                    "  FAIL", r["check"], r["expected"], r["observed"], file=sys.stderr
                )
        return 1

    ext = L.Extract(a.cells)
    prev = L.Extract(a.prev_cells) if a.prev_cells else None
    ref = None
    if a.ref_end:
        ref = {
            int(r["company_id"]): r["ref_end"]
            for r in csv.DictReader(open(a.ref_end, newline=""))
        }
    out = a.out_dir
    R, defects, absent_cells = build(ext, a.as_of, a.cells, prev, ref, out)
    bad = validate_rows(R.rows)
    if bad:
        print("SCOREBOARD INVALID:\n  " + "\n  ".join(bad), file=sys.stderr)
        return 1
    if a.erratum is not None:
        if not a.reason:
            print("--erratum needs --reason", file=sys.stderr)
            return 1
        for r in R.rows:
            r["note"] = (
                r["note"]
                + f" | ERRATUM r{a.erratum} supersedes {a.as_of}.csv: {a.reason}"
            ).strip(" |")
    fname = f"{a.as_of}.csv" if a.erratum is None else f"{a.as_of}.r{a.erratum}.csv"
    ids, cohort = L.load_cohort()
    ticker = {cid: row["ticker"] for cid, row in cohort.items()}
    prev_first = {}
    if a.prev_defects:
        with L.open_text(a.prev_defects) as fh:
            for r in csv.DictReader(fh):
                prev_first[(int(r["company_id"]), r["data_point_name"])] = r[
                    "first_seen_scoreboard"
                ]
    if a.check_only:
        print(
            f"OK (check only): {len(R.rows)} rows, {len(defects)} proxy defect rows, RT-1 passed"
        )
        return 0

    target = out / fname
    if target.exists():
        print(
            f"REFUSING to overwrite published {target} (AT-7.14); use --erratum N",
            file=sys.stderr,
        )
        return 1
    (out / "defects").mkdir(exist_ok=True)
    (out / "cells").mkdir(exist_ok=True)
    target.write_text(to_csv(R.rows))
    files = [target]
    dpath = out / "defects" / f"{a.as_of}.defects.csv.gz"
    if not dpath.exists() and a.erratum is None:
        L.write_gz_deterministic(
            defects_csv(defects, a.as_of, ticker, prev_first), dpath
        )
    if dpath.exists():
        files.append(dpath)
    cpath = out / "cells" / f"{a.as_of}.cells.csv.gz"
    if not cpath.exists():
        if str(a.cells).endswith(".gz"):
            cpath.write_bytes(Path(a.cells).read_bytes())
        else:
            L.write_gz_deterministic(Path(a.cells).read_text(), cpath)
    files.append(cpath)
    for extra in (
        "reason_class_map.csv",
        "TARGETS.csv",
        "maps/d0_datapoints.txt",
        "maps/d0e_removed_30.txt",
    ):
        if (out / extra).exists():
            files.append(out / extra)
    chain = out / "CHAIN.md"
    graph = L.load_graph()
    removed = set(L.read_lines(L.D0E_REMOVED_FILE))
    keep = set(L.read_lines(L.D0_NAMES_FILE)) - removed
    names = L.read_lines(L.D0_NAMES_FILE)
    t0 = L.tally(ext, graph, names=set(names))
    t_e = L.tally(ext, graph, names=keep)
    head = chain.read_text() if chain.exists() else CHAIN_HEADER
    if f"## {a.as_of}\n" not in head and a.erratum is None:
        D0 = len(ids) * len(names)
        chain.write_text(
            head
            + chain_section(
                a.as_of,
                t0,
                t_e,
                D0,
                D0 - len(removed) * len(ids),
                removed,
                len(absent_cells),
            )
        )
    if chain.exists():
        files.append(chain)
    n = manifest_append(out, files)
    print(
        f"wrote {target} ({len(R.rows)} rows); {len(defects)} proxy defect rows; manifest +{n}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
