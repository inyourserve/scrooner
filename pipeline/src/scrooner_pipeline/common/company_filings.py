"""Which filings belong to a company: ONE shared rule (ONE-PATH step 2, 2026-11-16).

A company's filing set is NOT "rows whose cik column equals the company's CIK". It is

  1. its own filings under its current CIK, minus the filings in its 'exclude' windows
     (core.company_history_source relation 'exclude': a legal acquirer's pre-merger filings that are
     another entity's, never this company's history);
  2. plus the filings of every predecessor CIK (relation 'predecessor') whose period lies inside that
     predecessor's window (holding-company reorganisations and mergers: XOM, AVGO, DIS, MRVL, LIN, BLK, ...);
  3. successor wins for a shared period: a predecessor-CIK filing is dropped when the company's own CIK
     filed the same form for the same period (the amendment flag is ignored: a 10-K/A counts as its 10-K),
     UNLESS the successor's report is a shell: its valued face lines (fsn.line on BS/IS/CF with a value in the
     filing's own column) are under 25% of the predecessor's. The predecessor then wins, reason
     'shell_successor_report' (Linde FY2017 0001707925-18-000004, 15 lines, against Praxair's real statements
     0000884905-18-000014). Applied identically in Python and in both CTEs.

The window rule is the one the store loader (fsn_store/shard.owners_of, jobs/fsn._db_history), the
normalizer (normalizer/predecessors.Route.contains) and the tag-map writer (mapper/company_tag_map,
_merge_predecessor_facts) already apply: the period of the filing (fsn.filing.period / core.filing.
period_of_report) inside [valid_from, valid_to], an exclude window always beats it, the period is never
replaced by the filing date.

Python: `company_filings(conn, company_id_or_ids, ...)`. SQL: `fsn_filings_cte(...)` / `core_filings_cte(...)`
return a CTE text that SQL callers (the Tag Expert's extract SQL, the proof, the loaders) embed, so Python and
SQL cannot drift; tests/unit/test_company_filings*.py check that every embedded copy is the canonical text.
The CTE is named `company_filings` (fsn) / `company_core_filings` (core) and carries:
  fsn : id (fsn.filing.id), company_id, cik (the COMPANY's cik), filer_cik (the cik column of the row),
        accession, form, period, fy, fp, filed, via ('own' | 'predecessor'), reason
  core: id (core.filing.id), company_id, cik (the company's), filer_cik (raw.sec_submissions.cik or None),
        accession, form, period, filed, via, reason ('shell_successor_report' on a predecessor report that won a
        period the successor also filed, else null)

Read-only. A caller that needs the SEC document URL still needs the filer CIK (`filer_cik`): the document
lives under the CIK that filed it.
"""

from __future__ import annotations

from datetime import date
from typing import Iterable, NamedTuple

import psycopg

_WHERE_TOKEN = "{company_where}"

# the company's exclude window covers a period (an own-CIK filing there belongs to another entity)
_EXCLUDED = """exists (select 1 from core.company_history_source x
                 where x.company_id = co.id and x.relation = 'exclude'
                   and {p} between x.valid_from and x.valid_to)"""

# valued face lines of one filing: fsn.line rows on BS/IS/CF (not parenthetical) that carry a non-dimensional value in
# the filing's own column (fsn.value at ddate = the filing's period, an instant for BS, a year for IS/CF: the extract's lv). `{acc}` is an SQL expression for the accession.
_FACE = """(select count(*) from fsn.filing ff join fsn.line fln on fln.filing_id = ff.id
          where ff.accession = {acc} and fln.stmt in ('BS', 'IS', 'CF') and not fln.inpth
            and exists (select 1 from fsn.value fv where fv.filing_id = fln.filing_id and fv.tag_id = fln.tag_id
                        and fv.dim_id = 0 and coalesce(fv.coreg, '') = '' and fv.ddate = ff.period
                        and fv.qtrs = (case when fln.stmt = 'BS' then 0 else 4 end)
                        and fv.value is not null))"""

# a successor report is a SHELL when its valued face lines are under 25% of the predecessor's for the same period and
# form (Linde FY2017: 15 lines against Praxair's real statements): the predecessor's report then wins the period
_SHELL = "({s} * 4 < {p})"

_FSN_TEMPLATE = f"""company_filings as (
 select f.id, co.id as company_id, co.cik, f.cik as filer_cik, f.accession, f.form, f.period, f.fy, f.fp, f.filed,
        case when f.cik = co.cik then 'own' else 'predecessor' end as via,
        case when f.cik <> co.cik and exists (select 1 from fsn.filing s
                         where s.cik = co.cik and s.period = f.period
                           and replace(s.form, '/A', '') = replace(f.form, '/A', '')
                           and not {_EXCLUDED.format(p="s.period")})
             then 'shell_successor_report' end as reason
 from core.company co
 join fsn.filing f on f.cik = any(array[co.cik] || array(
      select h.source_cik from core.company_history_source h where h.company_id = co.id and h.relation = 'predecessor'))
 where {_WHERE_TOKEN}
   and (
     (f.cik = co.cik and not {_EXCLUDED.format(p="f.period")}
      and not exists (select 1 from fsn.filing p
                      where p.cik = any(array(select h.source_cik from core.company_history_source h
                              where h.company_id = co.id and h.relation = 'predecessor'
                                and f.period between h.valid_from and h.valid_to))
                        and p.period = f.period and replace(p.form, '/A', '') = replace(f.form, '/A', '')
                        and {_SHELL.format(s=_FACE.format(acc="f.accession"), p=_FACE.format(acc="p.accession"))}))
     or (f.cik <> co.cik
         and exists (select 1 from core.company_history_source h
                     where h.company_id = co.id and h.relation = 'predecessor' and h.source_cik = f.cik
                       and f.period between h.valid_from and h.valid_to)
         and not exists (select 1 from fsn.filing s
                         where s.cik = co.cik and s.period = f.period
                           and replace(s.form, '/A', '') = replace(f.form, '/A', '')
                           and not {_EXCLUDED.format(p="s.period")}
                           and not {_SHELL.format(s=_FACE.format(acc="s.accession"), p=_FACE.format(acc="f.accession"))}))
   )
)"""

# core.filing carries no lines: the shell test reads the same accession's fsn lines (no fsn rows: no flip)
_CORE_TEMPLATE = f"""company_core_filings as (
 select fl.id, co.id as company_id, co.cik, s.cik as filer_cik, fl.accession_number as accession, fl.form,
        fl.period_of_report as period, fl.filing_date as filed,
        case when s.cik is null or s.cik = co.cik then 'own' else 'predecessor' end as via,
        case when s.cik is not null and s.cik <> co.cik and exists (select 1 from core.filing o
                         left join raw.sec_submissions os on os.id = o.raw_submission_id
                         where o.company_id = co.id and (os.cik is null or os.cik = co.cik)
                           and o.period_of_report = fl.period_of_report
                           and replace(o.form, '/A', '') = replace(fl.form, '/A', '')
                           and not {_EXCLUDED.format(p="o.period_of_report")})
             then 'shell_successor_report' end as reason
 from core.company co
 join core.filing fl on fl.company_id = any(array[co.id] || array(
      select pc.id from core.company pc join core.company_history_source h
        on h.source_cik = pc.cik and h.company_id = co.id and h.relation = 'predecessor'))
 left join raw.sec_submissions s on s.id = fl.raw_submission_id
 where {_WHERE_TOKEN}
   and (
     ((s.cik is null or s.cik = co.cik) and fl.company_id = co.id
      and not {_EXCLUDED.format(p="fl.period_of_report")}
      and not exists (select 1 from core.filing p
                      join raw.sec_submissions ps on ps.id = p.raw_submission_id
                      where p.company_id = any(array[co.id] || array(
                              select pc.id from core.company pc join core.company_history_source h2
                                on h2.source_cik = pc.cik and h2.company_id = co.id and h2.relation = 'predecessor'))
                        and ps.cik <> co.cik
                        and exists (select 1 from core.company_history_source h
                              where h.company_id = co.id and h.relation = 'predecessor' and h.source_cik = ps.cik
                                and p.period_of_report between h.valid_from and h.valid_to)
                        and p.period_of_report = fl.period_of_report
                        and replace(p.form, '/A', '') = replace(fl.form, '/A', '')
                        and (case when ps.cik <> co.cik and p.period_of_report = fl.period_of_report
                                       and replace(p.form, '/A', '') = replace(fl.form, '/A', '')
                                  then {_SHELL.format(s=_FACE.format(acc="fl.accession_number"), p=_FACE.format(acc="p.accession_number"))}
                                  else false end)))
     or (s.cik is not null and s.cik <> co.cik
         and exists (select 1 from core.company_history_source h
                     where h.company_id = co.id and h.relation = 'predecessor' and h.source_cik = s.cik
                       and fl.period_of_report between h.valid_from and h.valid_to)
         and not exists (select 1 from core.filing o
                         left join raw.sec_submissions os on os.id = o.raw_submission_id
                         where o.company_id = co.id and (os.cik is null or os.cik = co.cik)
                           and o.period_of_report = fl.period_of_report
                           and replace(o.form, '/A', '') = replace(fl.form, '/A', '')
                           and not {_EXCLUDED.format(p="o.period_of_report")}
                           and not (case when o.period_of_report = fl.period_of_report
                                              and replace(o.form, '/A', '') = replace(fl.form, '/A', '')
                                         then {_SHELL.format(s=_FACE.format(acc="o.accession_number"), p=_FACE.format(acc="fl.accession_number"))}
                                         else false end)))
   )
)"""


def fsn_filings_cte(company_where: str) -> str:
    """The canonical fsn.filing CTE `company_filings`. `company_where` is a predicate over core.company aliased
    `co` that picks the companies, e.g. "co.id = any(%s)" or "co.cik::bigint in (__CIKS__)"."""
    return _FSN_TEMPLATE.replace(_WHERE_TOKEN, company_where)


def core_filings_cte(company_where: str) -> str:
    """The canonical core.filing CTE `company_core_filings` (see fsn_filings_cte)."""
    return _CORE_TEMPLATE.replace(_WHERE_TOKEN, company_where)


class CompanyFiling(NamedTuple):
    source: str  # 'fsn' | 'core'
    id: int  # fsn.filing.id / core.filing.id
    company_id: int
    cik: str  # the company's current CIK
    filer_cik: (
        str | None
    )  # the cik that filed it (a predecessor's for via == 'predecessor')
    accession: str
    form: str
    period: date | None
    filed: date | None
    via: str  # 'own' | 'predecessor'
    reason: str | None = (
        None  # 'shell_successor_report': the successor's report for this period is a shell
    )


def company_filings(
    conn: psycopg.Connection,
    company_id: int | Iterable[int],
    *,
    source: str = "both",
    forms: Iterable[str] | None = None,
    min_period: date | None = None,
) -> list[CompanyFiling]:
    """Every filing of the company (or companies) in fsn.filing (`source` 'fsn'), core.filing ('core') or both,
    under its current CIK plus its predecessor CIKs inside their windows, successor winning shared periods.
    Ordered by (company_id, period, accession). Reads only."""
    if source not in ("fsn", "core", "both"):
        raise ValueError(f"source must be fsn, core or both: {source!r}")
    ids = [company_id] if isinstance(company_id, int) else sorted(set(company_id))
    out: list[CompanyFiling] = []
    where = "co.id = any(%(ids)s)"
    extra = ""
    params: dict = {"ids": ids}
    if forms is not None:
        extra += " and form = any(%(forms)s)"
        params["forms"] = list(forms)
    if min_period is not None:
        extra += " and period >= %(minp)s"
        params["minp"] = min_period
    if source in ("fsn", "both"):
        sql = (
            "with "
            + fsn_filings_cte(where)
            + " select id, company_id, cik, filer_cik, accession, form, period, filed, via, reason from company_filings"
            f" where true{extra}"
        )
        for r in conn.execute(sql, params).fetchall():
            out.append(CompanyFiling("fsn", *r))
    if source in ("core", "both"):
        sql = (
            "with "
            + core_filings_cte(where)
            + " select id, company_id, cik, filer_cik, accession, form, period, filed, via, reason from company_core_filings"
            f" where true{extra}"
        )
        for r in conn.execute(sql, params).fetchall():
            out.append(CompanyFiling("core", *r))
    out.sort(key=lambda f: (f.source, f.company_id, f.period or date.min, f.accession))
    return out


def company_filing_accessions(
    conn: psycopg.Connection, company_id: int | Iterable[int], **kw
) -> set[str]:
    """The accession numbers of company_filings (fsn and core together by default)."""
    return {f.accession for f in company_filings(conn, company_id, **kw)}
