from datetime import date

import pytest

from scrooner_pipeline.normalizer.restatements import (
    link_amendments_for_company,
    supersede_facts_for_company,
)


class RestatementCursor:
    def __init__(self, conn):
        self.conn = conn
        self._rows = []

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return False

    def execute(self, sql, params=()):
        normalized = " ".join(sql.split())
        if "from core.filing where company_id = %s and is_amendment" in normalized:
            company_id = params[0]
            self._rows = [
                (f["id"], f["accession"], f["form"], f["period"], f["filing_date"])
                for f in self.conn.filings
                if f["company_id"] == company_id and f["is_amendment"]
            ]
        elif normalized.startswith("select distinct on (a.amend_id)"):
            amend_ids, base_forms, alt_forms, periods, filing_dates, company_id = params
            out = []
            for amend_id, base_form, alt_form, period, filing_date in zip(
                amend_ids, base_forms, alt_forms, periods, filing_dates
            ):
                candidates = [
                    f for f in self.conn.filings
                    if f["company_id"] == company_id
                    and f["form"] in (base_form, alt_form)
                    and f["period"] == period
                    and f["filing_date"] < filing_date
                ]
                if not candidates:
                    continue
                candidates.sort(key=lambda f: f["filing_date"], reverse=True)
                out.append((amend_id, candidates[0]["id"]))
            self._rows = out
        elif normalized.startswith("update core.filing set amends_filing_id = v.original_id"):
            amend_ids, original_ids = params
            for amend_id, original_id in zip(amend_ids, original_ids):
                self._filing(amend_id)["amends_filing_id"] = original_id
            self._rows = []
        elif "amends_filing_id is not null" in normalized:
            company_id = params[0]
            self._rows = [
                (f["id"], f["amends_filing_id"])
                for f in self.conn.filings
                if f["company_id"] == company_id and f["amends_filing_id"] is not None
            ]
        elif normalized.startswith("select af.id, of.id"):
            amend_filing_ids, original_filing_ids = params
            matches = []
            for amendment_filing_id, original_filing_id in zip(amend_filing_ids, original_filing_ids):
                for amended in self.conn.facts:
                    if amended["filing_id"] != amendment_filing_id:
                        continue
                    for original in self.conn.facts:
                        if original["filing_id"] != original_filing_id:
                            continue
                        keys = ("company_id", "concept_id", "unit_id", "period_id")
                        if all(amended[k] == original[k] for k in keys):
                            matches.append((amended["id"], original["id"]))
            self._rows = matches
        elif normalized.startswith("update core.fact set is_authoritative = true, supersedes_fact_id = v.orig_id"):
            amend_fact_ids, orig_fact_ids = params
            for amend_fact_id, orig_fact_id in zip(amend_fact_ids, orig_fact_ids):
                fact = self._fact(amend_fact_id)
                fact["is_authoritative"] = True
                fact["supersedes_fact_id"] = orig_fact_id
            self._rows = []
        elif normalized.startswith("update core.fact set is_authoritative = false where id = any"):
            (orig_fact_ids,) = params
            for orig_fact_id in orig_fact_ids:
                self._fact(orig_fact_id)["is_authoritative"] = False
            self._rows = []
        else:
            raise AssertionError(f"Unexpected SQL in restatement test: {normalized}")

    def _filing(self, filing_id):
        return next(f for f in self.conn.filings if f["id"] == filing_id)

    def _fact(self, fact_id):
        return next(f for f in self.conn.facts if f["id"] == fact_id)

    def fetchall(self):
        return list(self._rows)

    def fetchone(self):
        return self._rows[0] if self._rows else None


class RestatementConnection:
    def __init__(self, filings, facts):
        self.filings = filings
        self.facts = facts
        self.commits = 0

    def cursor(self):
        return RestatementCursor(self)

    def commit(self):
        self.commits += 1


@pytest.mark.unit
def test_formal_amendment_supersedes_matching_fact_without_deleting_history():
    filings = [
        {
            "id": 10, "company_id": 1, "accession": "original", "form": "10-K",
            "period": date(2024, 12, 31), "filing_date": date(2025, 2, 1),
            "is_amendment": False, "amends_filing_id": None,
        },
        {
            "id": 11, "company_id": 1, "accession": "amended", "form": "10-K/A",
            "period": date(2024, 12, 31), "filing_date": date(2025, 3, 1),
            "is_amendment": True, "amends_filing_id": None,
        },
    ]
    facts = [
        {"id": 100, "company_id": 1, "concept_id": 5, "unit_id": 1, "period_id": 7,
         "filing_id": 10, "is_authoritative": True, "supersedes_fact_id": None},
        {"id": 101, "company_id": 1, "concept_id": 5, "unit_id": 1, "period_id": 7,
         "filing_id": 11, "is_authoritative": False, "supersedes_fact_id": None},
    ]
    conn = RestatementConnection(filings, facts)

    assert link_amendments_for_company(conn, 1) == {"linked": 1, "unmatched": 0}
    assert supersede_facts_for_company(conn, 1) == {"superseded_pairs": 1}

    assert len(conn.facts) == 2
    assert conn.facts[0]["is_authoritative"] is False
    assert conn.facts[1]["is_authoritative"] is True
    assert conn.facts[1]["supersedes_fact_id"] == 100


@pytest.mark.unit
def test_unmatched_amendment_is_left_unlinked_instead_of_guessed():
    filings = [
        {
            "id": 11, "company_id": 1, "accession": "orphan-amendment", "form": "10-K/A",
            "period": date(2000, 12, 31), "filing_date": date(2001, 3, 1),
            "is_amendment": True, "amends_filing_id": None,
        }
    ]
    conn = RestatementConnection(filings, [])

    stats = link_amendments_for_company(conn, 1)

    assert stats == {"linked": 0, "unmatched": 1}
    assert conn.filings[0]["amends_filing_id"] is None

