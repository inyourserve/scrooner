"""Regenerates stage2e_flags_off.json from the Stage 2e code of origin/main
(commit e271b9c, before W3/WO-23): the corpus below is run through THAT
module's resolve_authoritative_for_company with a mock cursor and the final
is_authoritative map and stats are stored. The golden test then requires the
current module with every flag OFF to reproduce them exactly.

  git show e271b9c:pipeline/src/scrooner_pipeline/normalizer/dedupe.py > /tmp/legacy_dedupe.py
  python tests/fixtures/golden/make_stage2e_golden.py /tmp/legacy_dedupe.py
"""

import hashlib
import importlib.util
import json
import random
import sys
from datetime import date
from decimal import Decimal
from pathlib import Path

FORMS = ["10-K", "10-Q", "10-K/A", "DEF 14A", "8-K", "S-1", "20-F"]


def corpus(seed: int = 42, companies: int = 40) -> dict[int, list[tuple]]:
    """company_id -> rows (fact_id, concept, unit, period, value, filing_date, filing_id, form, is_auth, is_derived),
    sorted the way the loader sorts them."""
    rng = random.Random(seed)
    out, fid = {}, 0
    for cid in range(1, companies + 1):
        rows = []
        for g in range(rng.randint(5, 40)):
            for _ in range(rng.randint(1, 5)):
                fid += 1
                rows.append(
                    (
                        fid,
                        g % 7,
                        1,
                        g,
                        Decimal(rng.choice([100, 100, 101, 5000, 5000000, 5000100, 3372772000, 3372800000])),
                        date(2020 + rng.randint(0, 5), 1 + rng.randint(0, 11), 1 + rng.randint(0, 27)),
                        fid,
                        rng.choice(FORMS),
                        True,  # Stage 2d default
                        rng.choice([True, False]),
                    )
                )
        rows.sort(key=lambda r: (r[1], r[2], r[3], r[5], r[0]))
        out[cid] = rows
    return out


class Cur:
    def __init__(self, conn):
        self.conn = conn

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False

    def execute(self, sql, params=()):
        n = " ".join(sql.split())
        if n.startswith("select f.id"):
            self.rows = [r[:7] if self.conn.legacy else r for r in self.conn.data[params[0]]]
        elif "set is_authoritative = true" in n:
            for f in params[0]:
                self.conn.auth[f] = True
        elif "set is_authoritative = false" in n:
            for f in params[0]:
                self.conn.auth[f] = False
        else:
            raise AssertionError(n)

    def fetchall(self):
        return self.rows


class Conn:
    def __init__(self, data, legacy):
        self.data, self.legacy = data, legacy
        self.auth = {r[0]: True for rows in data.values() for r in rows}

    def cursor(self):
        return Cur(self)

    def commit(self):
        pass


def run(module, legacy: bool) -> dict:
    data = corpus()
    conn = Conn(data, legacy)
    stats = {}
    for cid in data:
        s = module.resolve_authoritative_for_company(conn, cid)
        stats[cid] = {k: s[k] for k in ("duplicate_groups", "agreed_duplicate_groups", "conflict_groups")}
    return {"authority": {str(k): v for k, v in sorted(conn.auth.items())}, "stats": {str(k): v for k, v in stats.items()}}


if __name__ == "__main__":
    spec = importlib.util.spec_from_file_location("legacy_dedupe", sys.argv[1])
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    result = run(mod, legacy=True)
    blob = json.dumps(result, sort_keys=True)
    result["sha256"] = hashlib.sha256(blob.encode()).hexdigest()
    Path(__file__).with_name("stage2e_flags_off.json").write_text(json.dumps(result, sort_keys=True))
    print(len(result["authority"]), "facts", result["sha256"])
