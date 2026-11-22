#!/usr/bin/env python3
"""Canary releases for the top-100 flow (SYSTEMS.md #20): run the flow on 10 fixed canaries first, compare, gate.

usage:
  top100_canary.py ids    --canaries CSV                       -> canary company ids, comma-separated
  top100_canary.py rest   --canaries CSV --ids 1,2,3           -> the ids minus the canaries (may be empty)
  top100_canary.py snapshot --canaries CSV --repo DIR --base SHA --head SHA --out before.json
  top100_canary.py compare  --before before.json --artifacts DIR --sha SHA --date YYYY-MM-DD --out-md FILE
                            [--canaries CSV]

Per canary the state is four numbers, read the same way before and after:
  open_shown           rows of the company's open-shown file (before: data-team/strategy/open-shown/<T>.csv on main,
                       no file = 0; after: publish_c<id>/open-shown.csv of the canary flow run's artifact flow-<id>)
  self_check_fail      of those rows, the ones with work = verifier_check (cells the verifier self-check opened)
  draw_check_mismatch  of those, the ones whose reason is the draw checker's ("verifier self-check draw_check:")
  certified            before: verifier_certified = yes in data-team/strategy/top100-coverage-summary.csv on main;
                       after: VERIFIER_CERTIFIED on the company's line of the run's flow_results.tsv
A canary regresses when a number goes up, when it loses certified, when its flow line carries a certified-guard
marker (HELD_CERTIFIED, RESTORE_FAILED, REPROOF_FAILED, GUARD_ERROR: the guard had to restore or could not run), or
when the run left no open-shown file or no flow line for it (no evidence is never a pass).

Expected regressions: a resolver CHANGELOG row (data-team/tags/line_map/CHANGELOG.md) added in BASE..HEAD may carry
`canary-expected: JPM:open_shown, XOM:*` (metric one of open_shown, self_check_fail, draw_check_mismatch, or *).
Those count as expected and do not block, EXCEPT on a company that was certified before: a certified company
regressing always blocks, whatever the CHANGELOG says. Exit codes of compare: 0 pass, 1 regression, 2 error.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import subprocess
import sys
from pathlib import Path

METRICS = ("open_shown", "self_check_fail", "draw_check_mismatch")
GUARD_MARKERS = ("HELD_CERTIFIED", "RESTORE_FAILED", "REPROOF_FAILED", "GUARD_ERROR")
SELF_CHECK_WORK = "verifier_check"  # display_cert.SELF_CHECK_WORK
DRAW_CHECK_REASON = "verifier self-check draw_check:"  # display_cert.SELF_CHECK_PREFIX + " draw_check:"
OPEN_SHOWN = "data-team/strategy/open-shown"
SUMMARY = "data-team/strategy/top100-coverage-summary.csv"
CHANGELOG = "data-team/tags/line_map/CHANGELOG.md"
DEFAULT_CANARIES = "data-team/tags/line_map/canary/companies.csv"
EXPECTED = re.compile(r"canary-expected:\s*([^|]*)")
PAIR = re.compile(r"([A-Z][A-Z0-9.\-]*):(open_shown|self_check_fail|draw_check_mismatch|\*)")


def load_canaries(path: Path) -> list[dict]:
    with open(path, newline="") as fh:
        rows = [r for r in csv.DictReader(fh)]
    out = []
    for r in rows:
        t, c = (r.get("ticker") or "").strip(), (r.get("company_id") or "").strip()
        if not re.fullmatch(r"[A-Z][A-Z0-9.\-]*", t) or not c.isdigit():
            raise ValueError(f"bad canary row {r}")
        out.append({"ticker": t, "company_id": c, "sector": (r.get("sector") or "").strip()})
    if len({r["company_id"] for r in out}) != len(out):
        raise ValueError("duplicate canary company_id")
    return out


def count_open_shown(rows: list[dict]) -> dict:
    return {
        "open_shown": len(rows),
        "self_check_fail": sum(1 for r in rows if (r.get("work") or "") == SELF_CHECK_WORK),
        "draw_check_mismatch": sum(
            1
            for r in rows
            if (r.get("work") or "") == SELF_CHECK_WORK and DRAW_CHECK_REASON in (r.get("reason") or "")
        ),
    }


def read_csv_rows(path: Path) -> list[dict]:
    with open(path, newline="") as fh:
        return list(csv.DictReader(fh))


def parse_expected(text: str) -> dict[str, set[str]]:
    out: dict[str, set[str]] = {}
    for m in EXPECTED.finditer(text):
        for t, metric in PAIR.findall(m.group(1)):
            out.setdefault(t, set()).add(metric)
    return out


def added_changelog_lines(repo: Path, base: str, head: str) -> str:
    if not base or not head:
        return ""
    p = subprocess.run(
        ["git", "diff", "--unified=0", f"{base}..{head}", "--", CHANGELOG],
        cwd=repo,
        capture_output=True,
        text=True,
    )
    if p.returncode != 0:
        raise RuntimeError(f"git diff failed: {p.stderr.strip()}")
    return "\n".join(
        ln[1:] for ln in p.stdout.splitlines() if ln.startswith("+") and not ln.startswith("+++")
    )


def snapshot(canaries: list[dict], repo: Path, base: str, head: str) -> dict:
    certified: dict[str, bool] = {}
    summ = repo / SUMMARY
    if summ.exists():
        for r in read_csv_rows(summ):
            certified[r.get("company_id", "")] = (r.get("verifier_certified") or "") == "yes"
    comp = {}
    for c in canaries:
        f = repo / OPEN_SHOWN / f"{c['ticker']}.csv"
        state = count_open_shown(read_csv_rows(f)) if f.exists() else count_open_shown([])
        state["certified"] = certified.get(c["company_id"], False)
        comp[c["company_id"]] = {"ticker": c["ticker"], **state}
    expected = parse_expected(added_changelog_lines(repo, base, head))
    return {
        "base": base,
        "head": head,
        "companies": comp,
        "expected": {t: sorted(m) for t, m in expected.items()},
    }


def after_state(art: Path, company_id: str) -> dict:
    """The canary flow run's result for one company, from its downloaded artifacts (any layout: searched)."""
    st: dict = {"evidence": []}
    opens = [p for p in art.rglob("open-shown.csv") if p.parent.name == f"publish_c{company_id}"]
    if opens:
        st.update(count_open_shown(read_csv_rows(opens[0])))
    else:
        st["evidence"].append("no open-shown.csv for this company in the canary run")
    line = ""
    for tsv in art.rglob("flow_results.tsv"):
        for ln in tsv.read_text().splitlines():
            parts = ln.split("\t")
            if len(parts) >= 3 and parts[1] == company_id:
                line = parts[2]
    if not line:
        st["evidence"].append("no flow result line for this company")
    elif line.startswith("NO_RESULT_LINE"):
        st["evidence"].append("chain exited early (NO_RESULT_LINE)")
    st["line"] = line
    st["certified"] = "VERIFIER_CERTIFIED" in line.split()
    st["guard"] = [m for m in GUARD_MARKERS if m in line]
    return st


def compare_one(before: dict, after: dict, expected: set[str]) -> dict:
    """One canary: list of regressions, each {metric, before, after, expected}; blocking unless all expected."""
    regs = []
    for e in after.get("evidence", []):
        regs.append({"metric": "evidence", "before": "", "after": e, "expected": False})
    for m in METRICS:
        if m in after and int(after[m]) > int(before.get(m, 0)):
            regs.append(
                {"metric": m, "before": before.get(m, 0), "after": after[m], "expected": m in expected or "*" in expected}
            )
    if before.get("certified") and not after.get("certified") and not after.get("evidence"):
        regs.append({"metric": "certified", "before": "yes", "after": "no", "expected": False})
    for g in after.get("guard", []):
        regs.append({"metric": "certified_guard", "before": "", "after": g, "expected": False})
    certified = bool(before.get("certified")) or bool(after.get("guard"))
    if certified:  # a certified company regressing always blocks, whatever the CHANGELOG lists
        for r in regs:
            r["expected"] = False
    blocking = [r for r in regs if not r["expected"]]
    return {"regressions": regs, "blocking": bool(blocking), "certified": certified}


def compare(before: dict, art: Path) -> dict:
    expected = {t: set(m) for t, m in (before.get("expected") or {}).items()}
    res = {}
    for cid, b in before["companies"].items():
        a = after_state(art, cid)
        res[cid] = {"ticker": b["ticker"], "before": b, "after": a, **compare_one(b, a, expected.get(b["ticker"], set()))}
    return res


def render_md(res: dict, sha: str, date: str, base: str) -> str:
    bad = [r for r in res.values() if r["blocking"]]
    out = [
        f"# Canary regression {date} {sha[:12]}",
        "",
        f"Resolver release / data refresh at `{sha}` (diff base `{base}`) was run by top100-auto-trigger on the canary set "
        f"(`{DEFAULT_CANARIES}`) before the wide flow. {len(bad)} of {len(res)} canaries regressed; the wide flow was NOT "
        "dispatched. Expected regressions are listed in the release's CHANGELOG row as `canary-expected: TICKER:metric`; "
        "a certified company regressing always blocks. Production rows were written for the canaries only.",
        "",
        "| ticker | company_id | certified | open_shown | self_check_fail | draw_check_mismatch | regressions |",
        "|---|---|---|---|---|---|---|",
    ]
    for cid, r in res.items():
        b, a = r["before"], r["after"]

        def cell(m):
            return f"{b.get(m, 0)} -> {a[m]}" if m in a else f"{b.get(m, 0)} -> ?"

        regs = "; ".join(
            f"{x['metric']} {x['before']} -> {x['after']}{' (expected)' if x['expected'] else ''}" for x in r["regressions"]
        ) or "none"
        cert = f"{'yes' if b.get('certified') else 'no'} -> {'yes' if a.get('certified') else 'no'}"
        out.append(
            f"| {r['ticker']} | {cid} | {cert} | {cell('open_shown')} | {cell('self_check_fail')} | "
            f"{cell('draw_check_mismatch')} | {'**BLOCKING** ' if r['blocking'] else ''}{regs} |"
        )
    out += ["", "Flow lines of the canary run:", "", "```"]
    out += [f"{cid}\t{r['after'].get('line', '')}" for cid, r in res.items()]
    out += ["```", ""]
    return "\n".join(out)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=("ids", "rest", "snapshot", "compare"))
    ap.add_argument("--canaries", default=DEFAULT_CANARIES)
    ap.add_argument("--ids", default="")
    ap.add_argument("--repo", default=".")
    ap.add_argument("--base", default="")
    ap.add_argument("--head", default="")
    ap.add_argument("--out")
    ap.add_argument("--before")
    ap.add_argument("--artifacts")
    ap.add_argument("--sha", default="")
    ap.add_argument("--date", default="")
    ap.add_argument("--out-md")
    a = ap.parse_args()
    try:
        if a.cmd in ("ids", "rest", "snapshot"):
            can = load_canaries(Path(a.repo) / a.canaries if a.cmd == "snapshot" else Path(a.canaries))
        if a.cmd == "ids":
            print(",".join(c["company_id"] for c in can))
            return 0
        if a.cmd == "rest":
            if a.ids and not re.fullmatch(r"[0-9]+(,[0-9]+)*", a.ids):
                raise ValueError("--ids must match ^[0-9]+(,[0-9]+)*$")
            cids = {c["company_id"] for c in can}
            print(",".join(x for x in dict.fromkeys(a.ids.split(",")) if x and x not in cids))
            return 0
        if a.cmd == "snapshot":
            Path(a.out).write_text(json.dumps(snapshot(can, Path(a.repo), a.base, a.head), indent=1, sort_keys=True))
            print(f"canary snapshot: {len(can)} companies -> {a.out}")
            return 0
        before = json.loads(Path(a.before).read_text())
        res = compare(before, Path(a.artifacts))
    except Exception as e:  # noqa: BLE001 -- a gate that cannot run never passes
        print(f"canary error: {type(e).__name__}: {e}", file=sys.stderr)
        return 2
    for cid, r in res.items():
        print(
            f"canary {r['ticker']} ({cid}): {'BLOCKING' if r['blocking'] else 'ok'}"
            + "".join(f"; {x['metric']} {x['before']} -> {x['after']}{' (expected)' if x['expected'] else ''}" for x in r["regressions"])
        )
    if any(r["blocking"] for r in res.values()):
        if a.out_md:
            p = Path(a.out_md)
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(render_md(res, a.sha, a.date, before.get("base", "")))
            print(f"canary FAIL: wrote {p}")
        return 1
    print("canary PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
