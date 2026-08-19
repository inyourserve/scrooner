# Day 6 — Production Company and Security Universe Evidence

> **Status:** Implementation and isolated-database validation complete; production migration and live full-universe snapshot pending an authorized deployment.  
> **Date:** 2026-08-18  
> **Policy version:** `2026-08-18.v1`  
> **Plan:** `02_Ten_Day_Product_Readiness_Plan.md`, Day 6

## Outcome

Scrooner now has a deterministic, point-in-time universe policy that assigns every candidate security one of three explicit states: `eligible`, `excluded`, or `uncertain`. Every decision carries machine-readable reason codes. The system no longer needs to collapse a CIK, company, security, and exchange listing into one ticker-shaped identity.

Migration `0016_production_universe.sql` introduces backward-compatible filer, security, snapshot, and universe-member identities. Existing `core.company` and `core.listing` columns remain intact so this change does not break the current pipeline.

No production database was modified during this work. The migration and snapshot builder were exercised on an isolated PostgreSQL database.

## Official-source boundary

The policy reflects what the official SEC surface can and cannot prove:

- SEC EDGAR data is free, its data APIs require no authentication or API key, and submissions/XBRL bulk archives are published for efficient collection. [SEC EDGAR API documentation](https://www.sec.gov/search-filings/edgar-application-programming-interfaces)
- A CIK is a permanent filer identity and is not recycled. The SEC's cumulative CIK list also includes funds, individuals, former names, and entities that no longer file, so it is not itself an investable-security universe. [SEC data-access documentation](https://www.sec.gov/search-filings/edgar-search-assistance/accessing-edgar-data)
- SEC publishes current CIK/ticker/exchange associations, but explicitly does not guarantee their accuracy or scope. They require reconciliation and snapshots rather than blind trust. [SEC CIK/ticker/exchange documentation](https://www.sec.gov/search-filings/edgar-search-assistance/accessing-edgar-data#cik-ticker-and-exchange-associations)
- SEC separately publishes mutual-fund ticker data and investment-company series/class identifiers. These are the authoritative exclusion/crosswalk sources for registered funds, although the series/class report is not comprehensive for every closed-end fund and UIT. [SEC investment-company series/class data](https://www.sec.gov/data-research/sec-markets-data/investment-company-series-class-information)
- SEC does not publish a universal permanent security-class identifier for ordinary corporate equity. Scrooner therefore creates an internal `core.security.id`, retains its bootstrap source, and does not present the ID as an SEC identifier.

The existing OpenFIGI classification remains a secondary mechanism for raw security type (`Common Stock`, `ADR`, `ETP`, preferred, debt, and similar). A missing OpenFIGI match remains inconclusive.

## Identity model

| Identity | Meaning | Stable key/source |
|---|---|---|
| `core.company` | Economic/legal company record used by existing analytics | Internal ID; current model remains backward compatible |
| `core.filer` | SEC filing entity | SEC CIK; multiple filers can map to one company in the new schema |
| `core.security` | Issued security or share class | Internal ID with `source_key` and classification provenance |
| `core.listing` | Ticker on a trading venue over an effective interval | Listing ID, exchange, ticker, `effective_from`, `effective_to`, linked security |
| `core.universe_snapshot` | Policy decision set as known on a date | `(as_of, policy_version)` |
| `core.universe_member` | One listing's decision in one snapshot | Status, reasons, primary flag, and deterministic order |

`core.company.cik` and `core.listing.company_id` are retained as transitional compatibility fields. New universe code uses the explicit filer and security records.

## Eligibility policy

### Included

- Active domestic reporting companies
- Common equity on a recognized US national securities exchange
- Banks, insurers, REITs, and BDCs when their security and exchange pass the same common-equity rules
- Multiple legitimate common share classes as separate eligible securities

Banks, insurers, REITs, and BDCs are not excluded merely because their financial statements require sector-aware metrics.

### Excluded

- Confirmed delisted companies
- Confirmed registered funds, ETFs, and exchange-traded products
- Preferred shares
- Warrants and rights
- Units
- Debt and ETNs
- OTC/Pink/non-national-exchange quotations
- Confirmed SPACs or shells

### Uncertain, requiring an explicit decision or stronger evidence

- ADRs and 20-F/40-F filers, because the canonical product decision is still open
- Missing or unrecognized security types
- Missing or unrecognized exchanges
- Stale, unknown, or missing company status
- SIC `6770` blank-check candidates without confirming evidence
- Foreign depositary interests such as CDIs
- Multiple equally ranked share classes when selecting one company-level primary listing

SIC `6770` is a review signal, not definitive proof by itself. A confirmed SPAC/shell is excluded; an unconfirmed SIC-only candidate remains uncertain.

## Primary-listing policy

Primary selection operates only among eligible securities for the same company:

1. Prefer NYSE.
2. Then Nasdaq.
3. Then NYSE American.
4. Then NYSE Arca.
5. Then Cboe BZX.
6. If exactly one eligible candidate has the best exchange priority, mark it primary.
7. If multiple share classes tie at the best priority, select none and add `primary_ambiguous_multiple_share_classes` to each.

The system never breaks an economically meaningful multi-class tie alphabetically. Output ordering does use CIK, ticker, and listing ID so repeated builds are stable.

## Point-in-time behavior

Every persisted decision belongs to an `as_of` date and policy version. Rerunning today's key replaces only today's members and reproduces the same logical output. Once the date changes, the prior snapshot is preserved and a new snapshot is created.

The builder refuses retroactive dates. Rebuilding “2025” from today's current listings and company status would introduce look-ahead and survivorship bias while appearing historically precise. Historical screens must use a snapshot actually persisted on the relevant date. Scrooner cannot honestly backfill eligibility for dates before its observation history; those dates remain unavailable until a separate historical listing source is adopted.

While testing this behavior, a real pre-existing ticker-history bug was found in `company_master/history.py`: the code detected a ticker disappearing between submissions snapshots, but its result dictionary contained only current tickers, so the historical ticker never received its discovered `effective_to`. It now retains every observed ticker and closes the disappeared listing on the newer snapshot date. A permanent regression test covers `OLD -> NEW`.

This fix is essential for historical universe reconstruction and ticker-reuse safety. It does not invent a date for changes that occurred before Scrooner's observation window.

## Isolated snapshot evidence

A representative official-source-shaped fixture was loaded into a clean PostgreSQL database after all 16 migrations. It contains domestic common stocks, two Alphabet-style share classes, an ADR/20-F filer, bank common and preferred securities, a registered fund/ETP, an OTC security, a SIC-6770 candidate, a stale company, and a confirmed delisted company.

Result:

```text
candidates: 11
eligible: 4
excluded: 4
uncertain: 3
primary: 2
snapshot_id: 1
```

Representative decisions:

| Candidate | Status | Primary | Material reason |
|---|---:|---:|---|
| AAPL common | Eligible | Yes | Domestic common equity on Nasdaq |
| JPM common | Eligible | Yes | Domestic bank common equity on NYSE |
| JPM preferred | Excluded | No | Preferred security |
| GOOG / GOOGL | Eligible | Neither | Multiple equally ranked share classes |
| TSM ADR / 20-F | Uncertain | No | ADR and foreign-filer decisions remain open |
| Registered fund ETP | Excluded | No | Registered fund and fund security |
| SIC-6770 candidate | Uncertain | No | Confirmation required before SPAC/shell exclusion |
| OTC common | Excluded | No | Not a national-exchange listing |
| Stale common | Uncertain | No | Stale company status |
| Delisted common | Excluded | No | Confirmed company delisting |

The snapshot was rerun for the same date and policy version. It reused snapshot ID `1`, remained at 11 members, and retained the same logical fingerprint:

```text
b8d532cb1d29706b7f71a0f70baaa19e
```

This is validation data, not a claim that Scrooner's production universe contains only 11 candidates.

## Automated verification

Day 6 added 25 unit tests covering:

- Every included/excluded/uncertain category above
- Domestic, foreign-private, Canadian MJDS, registered-fund, and unknown filing regimes
- Bank, insurer, REIT, and BDC inclusion
- Determinism independent of input order
- Exchange-priority primary selection
- Multi-class primary ambiguity
- Historical ticker closure
- Rejection of retroactive snapshot construction

Results:

```text
Day 6 tests: 25 passed
Pipeline: 103 passed, 1 live test deselected
Migrations: 16 files, contiguous 0001-0016
Clean PostgreSQL migration application: passed
Representative snapshot persistence: passed
Snapshot idempotency/fingerprint: passed
```

## Commands

After applying migration `0016` to the target environment:

```bash
cd pipeline
.venv/bin/scrooner-company-master build-universe
```

The date defaults to the current date. An explicit `--as-of` is accepted only when it equals today; retroactive builds fail closed.

## Day 6 Definition of Done

| Gate | Result |
|---|---|
| Separate company, filer, security, and listing identities | PASS |
| Explicit rules for all requested security/company categories | PASS |
| Every candidate receives a status and reasons | PASS |
| Multi-security CIKs are not collapsed | PASS |
| Deterministic, rerunnable snapshots | PASS |
| Point-in-time snapshot identity | PASS |
| Retroactive look-ahead prevented | PASS — only today's state can create today's snapshot |
| Ticker disappearance closes historical listing | PASS |
| Uncertain cases measurable and inspectable | PASS |
| ADR/20-F/40-F decision surfaced | PASS — deliberately remains uncertain |
| Representative isolated snapshot | PASS |
| Live full production snapshot | PENDING — requires migration deployment and current production data run |

## Consultant assessment

Day 6's design and implementation are complete, and the policy has executable evidence. The operational production gate is intentionally not claimed: migration `0016` must be reviewed/applied to the target database and `build-universe` must then run against the current collected population. That run should publish counts by status, reason, exchange, security type, filing regime, and multi-class company before Day 7 selects its stratified 100-company pilot.
