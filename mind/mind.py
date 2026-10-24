#!/usr/bin/env python3
"""Scrooner mind: one shared, searchable, self-pruning memory for every agent and session.

Stdlib only. Entries are atomic markdown files (mind/entries). Agents search first, fetch one
entry instead of reading whole docs, and write what they learn to mind/inbox (one file per
capture, so concurrent sessions never conflict). Usage, misses and feedback are logged and
drive pruning (`lint`) and gap-finding (`stats`).
"""
import argparse
import datetime as dt
import hashlib
import json
import math
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parent
ENT, INBOX, LOG = ROOT / "entries", ROOT / "inbox", ROOT / "log"
LEDGER = REPO / "data-team" / "22-FILING-LESSONS-LEDGER.md"
KINDS = {"rule", "lesson", "howto", "decision", "gotcha", "reference"}
EVIDENCE = {"FILING-CHECKED", "DATA-INFERRED", "ASSUMED", "CODE-CHECKED", "DOC-CITED"}  # DOC-CITED: migrated from a canonical doc, not re-verified
STOP = set("the a an of to in is it and or for on with as at by be this that from are was not no".split())
DUP_JACCARD = 0.6
COLD_DAYS, STALE_DAYS = 60, 90


def today() -> str:
    return dt.date.today().isoformat()


def toks(text: str) -> list[str]:
    out = []
    for w in re.findall(r"[a-z0-9_]+", text.lower()):
        parts = [w] + (w.split("_") if "_" in w else [])
        out += [p for p in parts if len(p) > 1 and p not in STOP]
    return out


def parse(path: Path) -> dict:
    raw = path.read_text()
    meta, body = {}, raw
    if raw.startswith("---\n"):
        head, _, body = raw[4:].partition("\n---\n")
        for line in head.splitlines():
            k, _, v = line.partition(":")
            meta[k.strip()] = v.strip()
    for k in ("tags", "paths"):
        meta[k] = [x.strip() for x in meta.get(k, "").split(",") if x.strip()]
    meta["body"], meta["file"] = body.strip(), path
    meta.setdefault("status", "active")
    return meta


def dump(e: dict) -> str:
    keys = ["id", "title", "kind", "tags", "paths", "evidence", "status", "source", "created", "verified", "pinned"]
    lines = []
    for k in keys:
        v = e.get(k)
        if v in (None, "", []):
            continue
        lines.append(f"{k}: {', '.join(v) if isinstance(v, list) else v}")
    return "---\n" + "\n".join(lines) + "\n---\n" + e["body"].strip() + "\n"


def load(directory: Path) -> list[dict]:
    return [parse(p) for p in sorted(directory.glob("*.md"))] if directory.exists() else []


def log(name: str, **row) -> None:
    LOG.mkdir(exist_ok=True)
    with open(LOG / f"{name}.jsonl", "a") as f:
        f.write(json.dumps({"ts": dt.datetime.now().isoformat(timespec="seconds"), **row}) + "\n")


def read_log(name: str) -> list[dict]:
    p = LOG / f"{name}.jsonl"
    return [json.loads(x) for x in p.read_text().splitlines() if x.strip()] if p.exists() else []


def rank(query: str, entries: list[dict]) -> list[tuple[float, dict]]:
    q = set(toks(query))
    n = len(entries) or 1
    docs = []
    for e in entries:
        head = Counter(toks(e.get("title", "") + " " + " ".join(e["tags"])))
        body = Counter(toks(e["body"]))
        docs.append((e, head, body))
    df = Counter(t for _, h, b in docs for t in set(h) | set(b))
    scored = []
    for e, head, body in docs:
        s = 0.0
        for t in q:
            idf = math.log(1 + n / (1 + df[t]))
            s += idf * (3 * min(head[t], 2) + (1 + math.log(body[t]) if body[t] else 0))
        if s > 0:
            scored.append((s, e))
    return sorted(scored, key=lambda x: -x[0])


def jaccard(a: dict, b: dict) -> float:
    x, y = set(toks(a["title"] + " " + a["body"])), set(toks(b["title"] + " " + b["body"]))
    return len(x & y) / len(x | y) if x and y else 0.0


def slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")[:60]


# ---------------------------------------------------------------- commands
def cmd_search(a):
    entries = [e for e in load(ENT) if a.all or e["status"] in ("active", "disputed")]
    hits = rank(a.query, entries)[: a.k]
    log("search", q=a.query, n=len(hits), ids=[e["id"] for _, e in hits])
    if not hits:
        print("NO MATCH (logged as a knowledge gap). After you solve it, run: mind add ...")
        return
    for _, e in hits:
        flag = "" if e["status"] == "active" else f" [{e['status'].upper()}]"
        print(f"{e['id']} | {e.get('kind','?')} | {e.get('evidence','?')}{flag} | {e['title']}")
    print(f"-> `mind get <id>` for the full entry ({len(hits)} shown, entries total {len(entries)})")


def cmd_get(a):
    for e in load(ENT):
        if e["id"] == a.id:
            log("get", id=a.id)
            print(e["file"].read_text())
            if e["status"] != "active":
                print(f"WARNING: status is {e['status']}; verify before relying on it.")
            return
    sys.exit(f"no entry {a.id}")


def similar(new: dict, entries: list[dict]):
    best = max(((jaccard(new, e), e) for e in entries), key=lambda x: x[0], default=(0, None))
    return best if best[0] >= DUP_JACCARD else (0, None)


def cmd_add(a):
    body = sys.stdin.read() if a.body == "-" else a.body
    if a.kind not in KINDS or a.evidence not in EVIDENCE:
        sys.exit(f"kind must be one of {sorted(KINDS)}; evidence one of {sorted(EVIDENCE)}")
    e = {"id": slug(a.title), "title": a.title, "kind": a.kind, "evidence": a.evidence,
         "tags": [t.strip() for t in a.tags.split(",") if t.strip()],
         "paths": [p.strip() for p in a.paths.split(",") if p.strip()],
         "source": a.source, "created": today(), "verified": today(), "body": body}
    score, dup = similar(e, load(ENT))
    if dup:
        print(f"NOTE: {score:.0%} similar to existing '{dup['id']}'. Prefer `mind amend {dup['id']}` over a duplicate.")
    INBOX.mkdir(exist_ok=True)
    out = INBOX / f"{dt.datetime.now():%Y%m%d-%H%M%S}-{e['id']}.md"
    out.write_text(dump(e))
    print(f"captured -> {out.relative_to(REPO)} (curator promotes it; it is searchable only after promotion)")


def cmd_amend(a):
    for e in load(ENT):
        if e["id"] == a.id:
            e["body"] += f"\n\n[{today()}] {a.note}"
            e["verified"] = today()
            e["status"] = "active"
            e["file"].write_text(dump(e))
            log("amend", id=a.id)
            print(f"amended {a.id}")
            return
    sys.exit(f"no entry {a.id}")


def cmd_promote(a):
    files = sorted(INBOX.glob("*.md")) if a.all else [Path(a.file)]
    existing = load(ENT)
    for f in files:
        e = parse(f)
        e["body"] = e["body"].strip()
        if any(x["id"] == e["id"] for x in existing):
            print(f"SKIP {f.name}: id exists ({e['id']}); use amend")
            continue
        score, dup = similar(e, existing)
        if dup and not a.force:
            print(f"SKIP {f.name}: {score:.0%} duplicate of {dup['id']} (amend it, or --force)")
            continue
        ENT.mkdir(exist_ok=True)
        (ENT / f"{e['id']}.md").write_text(dump(e))
        f.unlink()
        existing.append(e)
        log("promote", id=e["id"])
        print(f"PROMOTED {e['id']}")


def cmd_feedback(a):
    log("feedback", id=a.id, verdict=a.verdict, note=a.note)
    if a.verdict in ("wrong", "stale"):
        for e in load(ENT):
            if e["id"] == a.id:
                e["status"] = "disputed"
                e["file"].write_text(dump(e))
    print(f"recorded {a.verdict} for {a.id}" + (" -> status disputed, curator will review" if a.verdict != "helped" else ""))


def cmd_brief(a):
    entries = load(ENT)
    pinned = [e for e in entries if e.get("pinned") == "true" and e["status"] == "active"]
    print("MIND [BETA, optional]: shared team memory; use it if it helps, verify against sources")
    print('- Optional, before long research: python3 mind/mind.py search "<topic>"  then  get <id>')
    print('- Optional, after learning something durable: python3 mind/mind.py add --title ... --kind ... --evidence ... --body ...')
    print("- Optional one-liner at the end: python3 mind/mind.py rate 0-5 (0 = did not use it; the mind is a tool, not a boundary)")
    print("- Entry wrong or outdated: python3 mind/mind.py feedback <id> wrong --note ...")
    for e in pinned:
        print(f"* {e['title']}  [{e['id']}]")
    gaps = Counter(m["q"] for m in read_log("search") if m["n"] == 0).most_common(3)
    if gaps:
        print("Known gaps (searched, nothing found): " + "; ".join(q for q, _ in gaps))
    print(f"({len(entries)} entries, {len(list(INBOX.glob('*.md')))} awaiting promotion)")


def cmd_lint(a):
    entries, errors, notes = load(ENT), [], []
    gets = Counter(h["id"] for h in read_log("get"))
    now = dt.date.today()
    for e in entries:
        for k in ("id", "title", "kind", "evidence", "created"):
            if not e.get(k):
                errors.append(f"{e['file'].name}: missing {k}")
        if e.get("kind") not in KINDS or e.get("evidence") not in EVIDENCE:
            errors.append(f"{e['id']}: bad kind/evidence")
        for p in e["paths"]:
            if not (REPO / p.split("#")[0]).exists():
                errors.append(f"{e['id']}: path no longer exists: {p}  (fix or supersede)")
        if e["status"] == "disputed":
            notes.append(f"{e['id']}: DISPUTED, needs review")
        try:
            age = (now - dt.date.fromisoformat(e.get("verified", e["created"]))).days
        except ValueError:
            age = 0
        if age > STALE_DAYS and e.get("evidence") != "FILING-CHECKED":
            notes.append(f"{e['id']}: not re-verified in {age}d")
        if age > COLD_DAYS and gets[e["id"]] == 0 and e.get("pinned") != "true":
            notes.append(f"{e['id']}: never fetched in {age}d (cold; candidate to merge or retire)")
    for i, x in enumerate(entries):
        for y in entries[i + 1:]:
            if jaccard(x, y) >= DUP_JACCARD:
                notes.append(f"possible duplicates: {x['id']} <-> {y['id']}")
    backlog = len(list(INBOX.glob("*.md")))
    if backlog > 20:
        notes.append(f"inbox backlog {backlog}: run promote")
    for line in errors:
        print("ERROR", line)
    for line in notes:
        print("note ", line)
    print(f"{len(entries)} entries, {len(errors)} errors, {len(notes)} notes")
    sys.exit(1 if errors else 0)


def cmd_stats(a):
    entries, searches, gets = load(ENT), read_log("search"), read_log("get")
    print(f"entries {len(entries)} | inbox {len(list(INBOX.glob('*.md')))} | searches {len(searches)} | fetches {len(gets)}")
    if searches:
        miss = sum(1 for s in searches if s["n"] == 0)
        print(f"search hit rate {1 - miss / len(searches):.0%}")
    served = sum(len(e["body"]) for e in entries if any(g["id"] == e["id"] for g in gets))
    print(f"top fetched: {Counter(g['id'] for g in gets).most_common(5)}")
    print(f"top gaps: {Counter(s['q'] for s in searches if s['n'] == 0).most_common(5)}")
    fb = Counter(f['verdict'] for f in read_log('feedback'))
    print(f"feedback: {dict(fb)}")
    print(f"(distinct entry text ever served ~{served // 4} tokens; compare against what a full-doc read would cost)")


def cmd_ingest_ledger(a):
    """Seed entries from the existing filing-lessons ledger table. Idempotent."""
    made = 0
    ENT.mkdir(exist_ok=True)
    for line in LEDGER.read_text().splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split(" | ")]
        if len(cells) != 4 or not re.match(r"\d{4}-\d{2}", cells[0]):
            continue
        date, case, rule, proof = cells
        eid = "ledger-" + slug(rule)[:40] + "-" + hashlib.sha1(case.encode()).hexdigest()[:6]
        path = ENT / f"{eid}.md"
        if path.exists():
            continue
        acc = bool(re.search(r"\d{10}-\d{2}-\d{6}", proof))
        e = {"id": eid, "title": rule, "kind": "lesson", "tags": ["ledger", "sec", "xbrl"],
             "paths": ["data-team/22-FILING-LESSONS-LEDGER.md"],
             "evidence": "FILING-CHECKED" if acc else "DATA-INFERRED",
             "source": "data-team/22-FILING-LESSONS-LEDGER.md", "created": date + ("-01" if len(date) == 7 else ""),
             "verified": today(), "body": f"Case: {case}\n\nProof: {proof}"}
        path.write_text(dump(e))
        made += 1
    print(f"ingested {made} ledger rows")


def cmd_ingest_md(a):
    """Migrate '- **Title.** body' bullets from a markdown doc into entries. Idempotent; text is copied verbatim."""
    src = REPO / a.file
    ENT.mkdir(exist_ok=True)
    made = 0
    for line in src.read_text().splitlines():
        m = re.match(r"- \*\*(.+?)\*\*\s*(.*)", line)
        if not m:
            continue
        title, rest = m.group(1).strip().rstrip(".:"), m.group(2).strip()
        if len(title) < 12:
            continue
        eid = slug(title)[:48] + "-" + hashlib.sha1(line.encode()).hexdigest()[:6]
        path = ENT / f"{eid}.md"
        if path.exists():
            continue
        e = {"id": eid, "title": title[:160], "kind": a.kind, "tags": [t for t in a.tags.split(",") if t],
             "paths": [a.file], "evidence": "DOC-CITED", "source": a.file, "created": today(),
             "verified": today(), "body": rest or title}
        path.write_text(dump(e))
        made += 1
    print(f"ingested {made} bullets from {a.file}")


def cmd_baseline(a):
    """What an always-loaded doc costs vs. what a mind lookup costs (chars/4 token estimate)."""
    docs = [REPO / f for f in a.files]
    for d in docs:
        print(f"{d.relative_to(REPO)}: ~{len(d.read_text()) // 4} tokens loaded every session")
    es = load(ENT)
    if es:
        sizes = sorted(len(e["body"]) // 4 + 20 for e in es)
        print(f"mind: {len(es)} entries, median ~{sizes[len(sizes)//2]} tokens, a typical lookup (search + 1 get) ~{200 + sizes[len(sizes)//2]} tokens")


def compute_score(searches, gets, feedback, ratings):
    """Pure. Each component is None until it has MIN_N signals; the score reweights over what exists."""
    MIN_N = 5
    comp = {}
    if len(searches) >= MIN_N:
        comp["hit_rate"] = (sum(1 for s in searches if s["n"] > 0) / len(searches), len(searches), 30)
    judged = [f for f in feedback if f["verdict"] in ("helped", "wrong", "stale")]
    if len(judged) >= MIN_N:
        comp["precision"] = (sum(1 for f in judged if f["verdict"] == "helped") / len(judged), len(judged), 30)
    used = [r for r in ratings if r["rating"] > 0]
    if len(used) >= MIN_N:
        comp["session_rating"] = (sum(r["rating"] for r in used) / len(used) / 5, len(used), 40)
    wsum = sum(w for _, _, w in comp.values())
    score = round(100 * sum(v * w for v, _, w in comp.values()) / wsum) if wsum else None
    adoption = (len(used), len(ratings))
    return score, comp, adoption


def cmd_rate(a):
    """One line, any session: 0 = did not use / not relevant (neutral, never penalised), 1-5 = how helpful it was."""
    log("rate", rating=a.rating, note=a.note, outside=a.outside)
    print(f"recorded rating {a.rating}" + (" (solved by going beyond the mind: that is fine and welcome)" if a.outside else ""))


def cmd_scorecard(a):
    searches, gets, fb, ratings = read_log("search"), read_log("get"), read_log("feedback"), read_log("rate")
    score, comp, (used, total) = compute_score(searches, gets, fb, ratings)
    print("MIND SCORECARD (beta; measurement only, never a rule)")
    print(f"score: {score if score is not None else 'n/a (needs >=5 signals per component)'}")
    for name, (v, n, w) in comp.items():
        print(f"  {name}: {v:.0%} (n={n}, weight {w})")
    print(f"sessions rated: {total}, of which used the mind: {used}; beyond-the-mind wins: {sum(1 for r in ratings if r.get('outside'))}")
    net = Counter()
    for f in fb:
        net[f["id"]] += {"helped": 1, "wrong": -3, "stale": -2}.get(f["verdict"], 0)
    if net:
        print("most helpful:", [i for i, v in net.most_common(3) if v > 0])
        print("needs review:", [i for i, v in sorted(net.items(), key=lambda x: x[1])[:3] if v < 0])
    print("top gaps:", Counter(s["q"] for s in searches if s["n"] == 0).most_common(3))
    if a.write:
        f = ROOT / "SCORECARD.md"
        if not f.exists():
            f.write_text("# Mind scorecard history (beta)\n\n| date | score | entries | searches | rated sessions | used it |\n|---|---|---|---|---|---|\n")
        with open(f, "a") as h:
            h.write(f"| {today()} | {score if score is not None else 'n/a'} | {len(load(ENT))} | {len(searches)} | {total} | {used} |\n")
        print(f"appended snapshot to {f.relative_to(REPO)}")


def main():
    p = argparse.ArgumentParser(prog="mind")
    s = p.add_subparsers(dest="cmd", required=True)
    x = s.add_parser("search"); x.add_argument("query"); x.add_argument("-k", type=int, default=5); x.add_argument("--all", action="store_true"); x.set_defaults(f=cmd_search)
    x = s.add_parser("get"); x.add_argument("id"); x.set_defaults(f=cmd_get)
    x = s.add_parser("add"); x.add_argument("--title", required=True); x.add_argument("--kind", required=True); x.add_argument("--evidence", required=True)
    x.add_argument("--tags", default=""); x.add_argument("--paths", default=""); x.add_argument("--source", default=""); x.add_argument("--body", default="-"); x.set_defaults(f=cmd_add)
    x = s.add_parser("amend"); x.add_argument("id"); x.add_argument("--note", required=True); x.set_defaults(f=cmd_amend)
    x = s.add_parser("promote"); x.add_argument("file", nargs="?"); x.add_argument("--all", action="store_true"); x.add_argument("--force", action="store_true"); x.set_defaults(f=cmd_promote)
    x = s.add_parser("feedback"); x.add_argument("id"); x.add_argument("verdict", choices=["helped", "wrong", "stale"]); x.add_argument("--note", default=""); x.set_defaults(f=cmd_feedback)
    x = s.add_parser("ingest-md"); x.add_argument("file"); x.add_argument("--kind", default="gotcha"); x.add_argument("--tags", default=""); x.set_defaults(f=cmd_ingest_md)
    x = s.add_parser("baseline"); x.add_argument("files", nargs="*", default=["CLAUDE.md", "pipeline/CLAUDE.md"]); x.set_defaults(f=cmd_baseline)
    x = s.add_parser("rate"); x.add_argument("rating", type=int, choices=range(0, 6)); x.add_argument("--note", default=""); x.add_argument("--outside", action="store_true", help="solved it by going beyond the mind"); x.set_defaults(f=cmd_rate)
    x = s.add_parser("scorecard"); x.add_argument("--write", action="store_true"); x.set_defaults(f=cmd_scorecard)
    for name, fn in (("brief", cmd_brief), ("lint", cmd_lint), ("stats", cmd_stats), ("ingest-ledger", cmd_ingest_ledger)):
        s.add_parser(name).set_defaults(f=fn)
    a = p.parse_args()
    if a.cmd == "promote" and not (a.all or a.file):
        p.error("promote needs a file or --all")
    a.f(a)


if __name__ == "__main__":
    main()
