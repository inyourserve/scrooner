"""Face-admission guards for a STANDARD debt line that is printed on the
balance sheet but absent from the statement-role calc graph (Verifier
VERIFY-SLOT-RECORDS-30SET-V4, section a: the rule fired right once, AVGO
2018, and would have fired wrongly at CNP, D, WSO, ICE, TXT, NFG).

Guards (the Verifier's four):
  (iii) never an ...Abstract header row;
  (i)   only rows printed between the total-assets row and the liabilities-
        and-equity total (the liabilities zone);
  (ii)  never a row that is a calc descendant of a member in ANY role, never a
        row that has a member among its own calc descendants (a total beside
        its parts), and never a row whose next printed 'Total ...' row inside
        the zone is itself a member (a component under a member subtotal);
  (iv)  a value tie at replay: the admitted line's zone roots must sum to the
        printed LiabilitiesCurrent (current side) or Liabilities less
        LiabilitiesCurrent (noncurrent side) on the same accession, else the
        cell holds as face_admission_tie_pending. This module only emits the
        tie specification; replay30.py evaluates it.
Pure functions; stdlib only.
"""
import re
from collections import defaultdict

ABSTRACT_RX = re.compile(r"Abstract$")
TOTAL_LABEL_RX = re.compile(r"^\s*total\b", re.I)
LSE_TOTALS = ("LiabilitiesAndStockholdersEquity", "LiabilitiesAndPartnersCapital")


def all_role_children(arcs):
    """parent -> set(children) over EVERY role of the filing's calc linkbase."""
    cm = defaultdict(set)
    for (_role, parent), kids in arcs.items():
        cm[parent].update(c for c, _w, _cu in kids)
    return cm


def descendants(cm, tag, seen=None):
    seen = seen if seen is not None else set()
    for ch in cm.get(tag, ()):
        if ch not in seen:
            seen.add(ch)
            descendants(cm, ch, seen)
    return seen


def liabilities_zone(face_rows):
    """Rows after the Assets total up to and including the L&E total.
    face_rows: ordered list of dicts with tag, custom, label."""
    tags = [r["tag"] for r in face_rows]
    start = tags.index("Assets") + 1 if "Assets" in tags else None
    if start is None:
        return [], False
    zone = face_rows[start:]
    ztags = [r["tag"] for r in zone]
    for lse in LSE_TOTALS:
        if lse in ztags:
            zone = zone[: ztags.index(lse) + 1]
            break
    return zone, True


def _roots(tags, cm):
    tagset = set(tags)
    covered = set()
    for t in tags:
        covered |= descendants(cm, t) & tagset
    return [t for t in tags if t not in covered]


def tie_spec(zone, cm, side):
    """What the replay must tie for an admitted line on this side."""
    ztags = [r["tag"] for r in zone]
    if side == "current":
        if "LiabilitiesCurrent" not in ztags:
            return {"side": side, "total": None, "roots": [], "computable": False}
        span = [t for t in ztags[: ztags.index("LiabilitiesCurrent")] if not ABSTRACT_RX.search(t)]
        return {"side": side, "total": "LiabilitiesCurrent", "roots": _roots(span, cm), "computable": True}
    # noncurrent: rows after the current total up to the Liabilities total
    if "Liabilities" not in ztags:
        return {"side": side, "total": None, "roots": [], "computable": False}
    lo = ztags.index("LiabilitiesCurrent") + 1 if "LiabilitiesCurrent" in ztags else 0
    hi = ztags.index("Liabilities")
    span = [t for t in ztags[lo:hi] if not ABSTRACT_RX.search(t)]
    return {"side": side, "total": "Liabilities", "less": "LiabilitiesCurrent" if lo else None,
            "roots": _roots(span, cm), "computable": True}


def admit(tag, face_rows, arcs, member_tags, side):
    """-> (admit: bool, reason: str, tie: dict|None)."""
    if ABSTRACT_RX.search(tag):
        return False, "abstract_header_row", None
    zone, known = liabilities_zone(face_rows)
    if not known:
        return False, "no_assets_total_row_zone_unknown", None
    ztags = [r["tag"] for r in zone]
    if tag not in ztags:
        return False, "outside_liabilities_zone", None
    cm = all_role_children(arcs)
    for m in member_tags:
        if tag in descendants(cm, m):
            return False, f"cal_descendant_of_member:{m}", None
    below = descendants(cm, tag)
    hit = sorted(below & set(member_tags))
    if hit:
        return False, f"total_of_members:{','.join(hit)}", None
    # presentation: the next printed 'Total ...' row inside the zone, before
    # the side's own total, must not be a member (component under a member subtotal)
    i = ztags.index(tag)
    for r in zone[i + 1:]:
        t = r["tag"]
        if t in ("LiabilitiesCurrent", "Liabilities") or t in LSE_TOTALS:
            break
        if TOTAL_LABEL_RX.search(r.get("label") or "") or t in member_tags:
            if t in member_tags:
                return False, f"component_under_member_subtotal:{t}", None
            if any(m in descendants(cm, t) for m in member_tags):
                return False, f"component_under_subtotal_of_members:{t}", None
            break
    return True, "ok", tie_spec(zone, cm, side)
