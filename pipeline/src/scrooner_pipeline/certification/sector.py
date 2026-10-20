"""I10 sector template evidence (the cheap part).

Banks are the only family with a stored suppression rule today
(common/sector_applicability.py), so I10 covers banks only:

  bank_shows_suppressed_metric  a company in the bank population shows a value
                                for a metric the suppression list hides. The
                                runner passes the metrics AFTER the serve-time
                                suppression, so a hit means the suppression
                                path did not run for that cell.
  bank_sic_without_evidence     SIC 6020-6036 but the company files no
                                NoninterestExpense / deposit tags: it is not
                                treated as a bank and keeps every bank-hostile
                                metric (review: confirm the family on the filing).
  bank_evidence_without_sic     files the bank tags but SIC is outside the bank
                                range: the family is unproven (PGR files a bank
                                tag and is an insurer, ledger 2026-10-18), so
                                this is only a review prompt.

Not covered (no stored rule to test against): insurers, REITs, asset managers,
utilities, MLPs. They stay `not implemented` in the certification report.
"""

from __future__ import annotations

from scrooner_pipeline.common.sector_applicability import BANK_SUPPRESSED_METRICS

from .model import REVIEW, WRONG_VALUE, CompanyData, Finding, finding


def check(data: CompanyData) -> list[Finding]:
    out: list[Finding] = []
    if data.is_bank:
        for m in data.metrics:
            reason = BANK_SUPPRESSED_METRICS.get(m.name)
            if reason is not None and m.value is not None:
                out.append(
                    finding(data, "I10", WRONG_VALUE, "bank_shows_suppressed_metric", m.name,
                            stored=m.value, period_end=m.period_end, label=m.label,
                            should_show=reason, sic=data.sic)
                )
    if data.bank_sic_without_evidence:
        out.append(
            finding(data, "I10", REVIEW, "bank_sic_without_evidence", "sector_template",
                    sic=data.sic, note="SIC in 6020-6036 but no bank tag evidence; family unconfirmed")
        )
    if data.bank_evidence_without_sic:
        out.append(
            finding(data, "I10", REVIEW, "bank_evidence_without_sic", "sector_template",
                    sic=data.sic, note="files bank tags but SIC is not a bank SIC; family unconfirmed")
        )
    return out
