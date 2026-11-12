"""Era split by the printed face line of each period's own filing (pure; used by era_by_face.py)."""


def face_runs(filings, face, order):
    """filings: {filing_id: (period, accepted)} for filings with lines on this statement; face: {filing_id: {competing tags
    printed}}; order: tag priority. Each period is decided by its OWN latest accepted filing: the highest-priority tag on that
    face, or OPEN when that face prints none of them. Runs break at every open period. Returns (runs [(tag, from, to)], open)."""
    latest = {}
    for fid, (p, acc) in filings.items():
        if p not in latest or acc > filings[latest[p]][1]:
            latest[p] = fid
    assign = {}
    for p, fid in latest.items():
        tags = face.get(fid, set())
        assign[p] = next((t for t in order if t in tags), None)
    decided = sorted(p for p, t in assign.items() if t)
    if not decided:
        return [], []
    runs, cur, open_p = [], None, []
    for p in sorted(assign):
        printed_somewhere = any(face.get(fid) for fid, (q, _) in filings.items() if q == p)
        if (p < decided[0] or p > decided[-1]) and not printed_somewhere:
            continue
        t = assign[p]
        if t is None:
            open_p.append(p)
            cur = None
            continue
        if cur and cur[0] == t:
            cur[2] = p
        else:
            cur = [t, p, p]
            runs.append(cur)
    return [tuple(r) for r in runs], open_p


# rows decided from a FILING-CHECKED full 10-K read or a ruling on one (often a note or a 10-K prior-year column, which the
# face of the period's own filing does not print), and debt-lane rows: the face pass never re-decides them or their concept
PROTECTED = ("read_verified", "ruling", "read_status", "debt_lane")


def face_checked(groups, rows):
    """The (company, stmt, concept) groups the face pass may re-decide: none holding a protected row of that company and concept."""
    prot = {(r["company_id"], r["canonical_concept"] or r["parent_concept"]) for r in rows
            if (r.get("decided_by") or "").split("+")[0] in PROTECTED}
    return {k: v for k, v in groups.items() if (k[0], k[2]) not in prot}
