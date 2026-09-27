"""Sector bucket mapping (doc 10 Sec 12, doc 26 Sec 2.8, doc 28), built
2026-08-21. Scoped by doc 26 as "a curated SIC->sector mapping table, a
bounded, one-time reference-data task, not a data-collection one" -- SIC
code is already captured (Company Master 4a), just too coarse/dated on
its own to be a useful investor-facing "sector" (e.g. AAPL's own SIC,
"3571 Electronic Computers", predates the iPhone).

Deliberately NOT GICS -- GICS is S&P/MSCI's licensed taxonomy, already
ruled out in doc 26/DATA_COVERAGE.md. SIC major-group ranges themselves
are public domain (the classification the SEC's own EDGAR company search
already groups by), so this maps SIC code RANGES to a small,
investor-recognizable set of sector names inspired by (but not
reproducing) GICS's naming, built from first principles against the
real SIC codes actually present in this project's data (checked live
before writing the ranges) rather than an abstract textbook list.

A code with no matching range (or a null/malformed sic_code) resolves to
"Other" -- never guessed into an unrelated bucket, same "null/honest
default over a wrong-but-plausible guess" discipline as everywhere else
in this project.
"""

import psycopg
import structlog

logger = structlog.get_logger()

# (min_code, max_code, sector) -- checked in order, first match wins.
# Ranges deliberately overlap-free and sorted ascending.
SECTOR_RANGES: list[tuple[int, int, str]] = [
    (100, 999, "Materials"),  # Agriculture/Forestry/Fishing -- resource production
    (1000, 1099, "Materials"),  # Metal mining
    (1100, 1299, "Energy"),  # Coal mining
    (1300, 1399, "Energy"),  # Oil & gas extraction
    (1400, 1499, "Materials"),  # Nonmetallic mineral mining
    (1500, 1799, "Industrials"),  # Construction
    (2000, 2199, "Consumer Staples"),  # Food, beverages, tobacco
    (2200, 2399, "Consumer Discretionary"),  # Textiles, apparel
    (2400, 2499, "Materials"),  # Lumber & wood
    (2500, 2599, "Consumer Discretionary"),  # Furniture
    (2600, 2699, "Materials"),  # Paper
    (2700, 2799, "Consumer Discretionary"),  # Printing & publishing
    (2800, 2833, "Materials"),  # Industrial/agricultural chemicals
    (2834, 2836, "Healthcare"),  # Pharmaceutical preparations, biologicals
    (2837, 2839, "Healthcare"),
    (2840, 2844, "Consumer Staples"),  # Soaps, cosmetics, toiletries
    (2845, 2899, "Materials"),  # Other chemical products
    (2900, 2999, "Energy"),  # Petroleum refining
    (3021, 3021, "Consumer Discretionary"),  # Rubber & plastics footwear (e.g. Nike) --
    # carved out of the surrounding 3000-3099 industrial-rubber/plastics range: footwear
    # is a consumer brand business, not a materials company, even though its SIC major
    # group (30, rubber & plastics products) is shared with tires/gaskets/hose. Found
    # live checking a real company (Nike, SIC 3021) before trusting the broader range.
    (3000, 3099, "Materials"),  # Rubber & plastics (tires, gaskets, industrial)
    (3100, 3199, "Consumer Discretionary"),  # Leather & footwear
    (3200, 3299, "Materials"),  # Stone, glass, concrete
    (3300, 3399, "Materials"),  # Primary metals
    (3400, 3499, "Industrials"),  # Fabricated metal products
    (3500, 3569, "Industrials"),  # Industrial machinery
    (3570, 3579, "Technology"),  # Computer & office equipment
    (3580, 3599, "Industrials"),  # Other machinery
    (3600, 3699, "Technology"),  # Electronic & electrical equipment
    (3700, 3716, "Consumer Discretionary"),  # Motor vehicles
    (3717, 3799, "Industrials"),  # Aircraft, ships, railroad equipment
    (3800, 3839, "Industrials"),  # Measuring/controlling instruments
    (3840, 3851, "Healthcare"),  # Surgical, medical, dental, ophthalmic
    (3852, 3899, "Consumer Discretionary"),  # Photographic, misc instruments
    (3900, 3999, "Consumer Discretionary"),  # Misc manufacturing (toys, sporting goods)
    (4000, 4099, "Industrials"),  # Railroads
    (4100, 4299, "Industrials"),  # Local/trucking transit
    (4400, 4499, "Industrials"),  # Water transportation
    (4500, 4599, "Industrials"),  # Air transportation
    (4600, 4699, "Energy"),  # Pipelines
    (4700, 4799, "Industrials"),  # Transportation services
    (4800, 4899, "Communication Services"),  # Telephone, broadcasting
    (4900, 4999, "Utilities"),  # Electric, gas, sanitary services
    (5000, 5199, "Industrials"),  # Wholesale trade
    (
        5200,
        5399,
        "Consumer Discretionary",
    ),  # Retail -- building materials, department stores
    (5400, 5499, "Consumer Staples"),  # Retail -- food stores
    (5500, 5799, "Consumer Discretionary"),  # Retail -- auto, apparel, furniture
    (5800, 5899, "Consumer Discretionary"),  # Retail -- eating & drinking places
    (5900, 5999, "Consumer Discretionary"),  # Retail -- misc
    (6000, 6099, "Financials"),  # Depository institutions (banks)
    (6100, 6299, "Financials"),  # Credit, brokers
    (6300, 6499, "Financials"),  # Insurance
    (6500, 6599, "Real Estate"),
    (6770, 6770, "Other"),  # Blank Checks -- carved out of the surrounding 6700-6799
    # "Real Estate" range: this code is a legacy pre-merger SPAC/shell classification,
    # not a real-estate holding company, and SEC never requires a post-merger operating
    # company to update it. Real evidence checked live 2026-09-06 before carving out:
    # 848 of ~6,900 active companies (12%) carry this code, and a random sample was
    # dominated by still-unmerged SPAC shells (SPACSphere, Jackson Acquisition, FIGX
    # Capital, GigCapital8, Columbus Acquisition, ...) with zero real-estate business in
    # common -- the same "carve out the real exception, don't force it into a
    # convenient-looking range" pattern as the Nike/3021 footwear carve-out below.
    (6700, 6799, "Real Estate"),  # Holding/investment offices, REITs
    (7000, 7099, "Consumer Discretionary"),  # Hotels
    (7200, 7369, "Industrials"),  # Business/personal services
    (7370, 7379, "Technology"),  # Computer programming, data processing, software
    (7389, 7389, "Other"),  # Business Services, NEC -- carved out of the surrounding
    # 7380-7799 "Industrials" range. Real evidence checked live 2026-09-06 (cross-checked
    # against yfinance's own sector/industry field, dev-tool use per
    # doc/planning/y-finance.md sec. 3.4/4, never a production dependency): a 25-company
    # random sample of this single code included Uber (mobility), MercadoLibre
    # (e-commerce), FIS/Shift4/Repay/Payoneer (payments/fintech), TriNet/Resources
    # Connection (HR/staffing), Maximus/ExlService (BPO), comScore (media analytics),
    # Xometry (manufacturing marketplace) -- no coherent sector, real or "Industrials,"
    # covers more than a small minority of it. Honest "Other" beats a confident-looking
    # wrong bucket, same discipline as the null-sector default below.
    (7380, 7799, "Industrials"),  # Other business services, auto repair/rental
    (7800, 7999, "Communication Services"),  # Motion pictures, amusement & recreation
    (8000, 8099, "Healthcare"),  # Health services
    (8200, 8299, "Consumer Discretionary"),  # Educational services
    (8600, 8999, "Industrials"),  # Membership orgs, engineering/management services
    (9100, 9729, "Government"),  # Public administration
]

OTHER = "Other"

# Curated per-company override, CIKs only (zero-padded to 10 digits, matching
# core.company.cik) -- SIC 7389 ("Business Services, NEC," carved out to "Other"
# above) has no coherent sector as a whole, but this one sub-cluster is a real,
# well-known exception: card networks and financial-data/credit companies. Found
# live 2026-09-06 by fetching yfinance's own sector/industry field for the full
# 112-company SIC 7389 population -- a bounded, one-time reference-data lookup,
# dev-tool use only, never a production dependency (doc/planning/y-finance.md sec.
# 3.4/4) -- then hand-reviewing which ones classify as "Credit Services" /
# "Financial Data & Stock Exchanges" / "Capital Markets" under Yahoo's own
# "Financial Services" sector. This project writes its own sector name
# ("Financials," not Yahoo's), same "inspired by, not reproducing" discipline as
# the whole SECTOR_RANGES table -- Yahoo's classification is a reference used to
# inform the decision, never copied or stored as a fact. Small, reviewed allowlist,
# same "automate detection, keep acceptance human" discipline as Company Master
# 4a's ticker-change-date confirmations.
SIC_7389_FINANCIALS_OVERRIDE_CIKS: set[str] = {
    "0000849145",  # Heritage Global Inc. (HGBL)
    "0001141391",  # Mastercard Inc (MA)
    "0001408198",  # MSCI Inc. (MSCI)
    "0001633917",  # PayPal Holdings, Inc. (PYPL)
    "0001101433",  # QuoteMedia Inc (QMCI)
    "0001662991",  # Sezzle Inc. (SEZL)
    "0001192323",  # Superstar Platforms Inc. (SPST)
    "0001403161",  # Visa Inc. (V)
    "0001365135",  # Western Union Co (WU)
}


def classify_sector(sic_code: str | None, cik: str | None = None) -> tuple[str, str]:
    """Returns (sector, reason). reason is always a real, traceable
    explanation -- either the matched range or why it fell through."""
    if cik is not None and cik in SIC_7389_FINANCIALS_OVERRIDE_CIKS:
        return "Financials", "sic_7389_financials_override"
    if sic_code is None or not sic_code.strip():
        return OTHER, "no_sic_code"
    try:
        code = int(sic_code)
    except ValueError:
        return OTHER, f"non_numeric_sic_code:{sic_code}"
    for lo, hi, sector in SECTOR_RANGES:
        if lo <= code <= hi:
            return sector, f"sic_range:{lo}-{hi}"
    return OTHER, f"unmapped_sic_code:{code}"


def update_sector(conn: psycopg.Connection, ciks: set[str]) -> dict:
    with conn.cursor() as cur:
        cur.execute(
            "select id, cik, sic_code from core.company where cik = any(%s)",
            (sorted(ciks),),
        )
        rows = cur.fetchall()

    stats: dict[str, int] = {"considered": 0, "no_company": 0}
    updates: list[dict] = []
    id_by_cik = {cik: (company_id, sic_code) for company_id, cik, sic_code in rows}

    for cik in sorted(ciks):
        stats["considered"] += 1
        hit = id_by_cik.get(cik)
        if hit is None:
            stats["no_company"] += 1
            continue
        company_id, sic_code = hit
        sector, reason = classify_sector(sic_code, cik=cik)
        stats[sector] = stats.get(sector, 0) + 1
        updates.append(
            {"company_id": company_id, "sector": sector, "sector_reason": reason}
        )

    if updates:
        with conn.cursor() as cur:
            cur.executemany(
                "update core.company set sector = %(sector)s, sector_reason = %(sector_reason)s where id = %(company_id)s",
                updates,
            )
        conn.commit()

    logger.info("company_master.sector.done", **stats)
    return stats
