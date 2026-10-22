"""DESIGN ONLY (NA-15 census, card section 3.6). Nothing here runs; migrations 0107 and 0108 are
claimed in doc 53 and not written or applied.

Why a census. A hand list misses issuers (SLN was not on it); companyfacts strips the class
dimension, so per-class cover counts (RPAY Class A vs Class V, TBLA voting vs non-voting) and the
depositary-share title are only readable from the filing instance.

Reader (per company, latest periodic 10-K/10-Q/10-KT only, never 8-K/DEF 14A/S-1):
  input   accession from core.filing; the instance (or the iXBRL) via common/sec_client.py,
          ONE fetch process, declared User-Agent, shared limiter, about 5k filings at the SEC rate
          (alternative: the SEC Financial Statement and Notes text table if it carries dei text facts
          [VERIFY]); cache by accession + sha256 so a re-run fetches nothing.
  output  one row per (accession, class member): the dei cover facts
            dei:Security12bTitle, dei:TradingSymbol, dei:SecurityExchangeName,
            dei:EntityCommonStockSharesOutstanding (value, class member or NULL when undimensioned),
          plus the `shares_including_treasury` flag when the cover says "including treasury".
          The priced class is the Security12bTitle row whose TradingSymbol equals core.listing's
          priced ticker; ``ads_conversion.parse_ads_ratio`` turns its title into the ratio.
  rules   an ADR-member cover fact is stored but flagged `unit_unknown` and never summed (AMRN);
          a class with no residual economic rights is flagged `voting_only` (RPAY Class V);
          a title that does not parse is stored with ratio NULL, never guessed.

Draft DDL (0107):
  create table core.security_class_cover (
    accession_number text not null, company_id bigint not null references core.company(id),
    form text not null, period_end date not null, filing_date date not null,
    priced_ticker text, security_title text, ads_ratio numeric,        -- parsed, NULL if unparsed
    class_member text,                                                  -- NULL = undimensioned
    ordinary_shares numeric, shares_as_of date,
    includes_treasury boolean not null default false,
    unit_unknown boolean not null default false, voting_only boolean not null default false,
    source_sha256 text not null, read_at timestamptz not null default now(),
    primary key (accession_number, coalesce(class_member, '')));
Draft DDL (0108):
  create table analytics.ads_ratio (
    company_id bigint not null references core.company(id), ratio numeric not null,
    effective_from date not null, source_accession text not null,
    evidence_level text not null check (evidence_level in ('FILING-CHECKED','DATA-INFERRED')),
    announced_on date, primary key (company_id, effective_from));
`ads_conversion.ADS_TABLE` is the interim copy of 0108; the census fills it, the Verifier signs
each new company's ratio before it is `convert`-eligible (default stays hide).

Ratio-change detection (card 3.3 signals b and c): F-6/F-6/A/F-6 POS/F-6EF filed after the source
filing, or an 8-K/6-K between it and the price date announcing a change, sets
`ads_ratio_changed_since_source`. Both need the submissions index; signal c needs 8-K text (untested).
KZIA and SCNI stay flagged foreign private issuers (Chief to rule V1 scope).
"""
