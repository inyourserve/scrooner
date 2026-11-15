"""Replay check for a rule-scoped proof change (ONE-PATH step 1). READ-ONLY: never writes.

Run it under each code tree (PYTHONPATH=<tree>/pipeline/src), once at the old code and once at the new:

  python proof_scope_replay.py --ciks 0000097745,... --out old.json            # old code: every cell's verdict
  python proof_scope_replay.py --ciks ... --out new.json --select               # new code: verdicts + the cells the
                                                                                # rule change selects (scope_proofs
                                                                                # against the STORED rows)
  python proof_scope_replay.py --compare old.json new.json

compare checks: (a) every cell whose verdict differs old->new is selected (scoped == full for them, unselected are
unchanged); (b) reports selected-but-unchanged cells (safe over-selection).
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path


def cell_key(p) -> str:
    s = p.shown
    return "|".join((str(s.company_id), s.data_point_name, s.period_grain, str(s.period_start), str(s.period_end)))


def verdict_of(p) -> list:
    return [p.verdict, p.reason_code, str(p.shown.value), str(p.position_value)]


def replay(ciks: list[str], out: Path, select: bool, fsn_root: str) -> None:
    import psycopg

    from scrooner_pipeline.db.connection import get_connection
    from scrooner_pipeline.proof.identities import apply_identities, load_filing_checks, load_printed
    from scrooner_pipeline.proof.perimeter import apply_perimeter
    from scrooner_pipeline.proof.runner import StructureCache, prove_company
    from scrooner_pipeline.proof.shown import HISTORY_FLOOR

    result: dict = {"cells": {}, "selected": {}, "rules": {}}
    with get_connection() as conn:
        conn.commit()
        conn.autocommit = True
        conn.execute("set default_transaction_read_only = on")
        conn.execute("set statement_timeout = '10min'")
        ids = dict(conn.execute("select cik, id from core.company where cik = any(%s)", (ciks,)).fetchall())
        cache = StructureCache(Path(fsn_root), conn, "db")
        for cik in ciks:
            cid = ids[cik]
            cache.company = cik
            proofs = prove_company(conn, cid, cache, None)
            structures = {a: st for by in cache.loaded.values() for a, st in by.items()}
            apply_identities(proofs, load_printed(conn, cid, HISTORY_FLOOR), structures, load_filing_checks(conn, cid))
            apply_perimeter(proofs, structures)
            for p in proofs:
                result["cells"][cell_key(p)] = verdict_of(p)
            if select:
                from scrooner_pipeline.proof.rules import rules_used
                from scrooner_pipeline.proof.runner import scope_proofs

                to_write, to_stamp, kept, why = scope_proofs(conn, cid, proofs, None)
                for p in to_write:
                    result["selected"][cell_key(p)] = True
                for p in proofs:
                    result["rules"][cell_key(p)] = list(rules_used(p.shown, p.checks))
                result.setdefault("per_company", {})[cik] = {
                    "cells": len(proofs), "rewrite": len(to_write), "stamp": len(to_stamp), "kept": kept,
                    "why": dict(why),
                }
    out.write_text(json.dumps(result, indent=1))


def compare(old_p: Path, new_p: Path) -> int:
    old, new = json.loads(old_p.read_text()), json.loads(new_p.read_text())
    sel = new["selected"]
    both = old["cells"].keys() & new["cells"].keys()
    changed = {k for k in both if old["cells"][k] != new["cells"][k]}
    unselected_changed = sorted(k for k in changed if k not in sel)
    sel_in_both = [k for k in both if k in sel]
    new_only = [k for k in new["cells"] if k not in old["cells"]]
    print(f"cells old={len(old['cells'])} new={len(new['cells'])} compared={len(both)} only_in_new={len(new_only)}")
    print(f"selected for re-proof (of compared): {len(sel_in_both)}; full re-prove would re-prove {len(both)}")
    print(f"verdict changed old->new: {len(changed)}; of those selected: {len(changed) - len(unselected_changed)}")
    print(f"selected but unchanged (over-selection, harmless): {len(sel_in_both) - (len(changed) - len(unselected_changed))}")
    print(f"UNSELECTED CELLS WHOSE VERDICT CHANGED: {len(unselected_changed)}")
    for k in unselected_changed[:20]:
        print("  ", k, old["cells"][k], "->", new["cells"][k])
    c = Counter(tuple(old["cells"][k][:2]) + tuple(new["cells"][k][:2]) for k in changed)
    for kk, n in c.most_common(10):
        print("  change", kk, n)
    print("per company:", json.dumps(new.get("per_company", {}), indent=0))
    return 1 if unselected_changed else 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--ciks")
    ap.add_argument("--out")
    ap.add_argument("--select", action="store_true")
    ap.add_argument("--fsn-root", default=".cache/fsn")
    ap.add_argument("--compare", nargs=2)
    a = ap.parse_args()
    if a.compare:
        sys.exit(compare(Path(a.compare[0]), Path(a.compare[1])))
    replay([c.strip().zfill(10) for c in a.ciks.split(",")], Path(a.out), a.select, a.fsn_root)
