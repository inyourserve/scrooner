"""SEC XBRL Frames API fetch (doc 45 follow-on, 2026-09-08). One call
returns EVERY filer's value for one (taxonomy, tag, unit, period) --
verified live before building: 1,696 companies for us-gaap:Revenues
CY2026Q1, 5,543 for us-gaap:Assets CY2026Q1I (instant concepts need an
'I' suffix on the period code; duration concepts don't).

Reuses common/sec_client.py directly -- same User-Agent, same shared
8 req/s aggregate rate limit as every other SEC EDGAR call this project
makes. This is standard SEC access, not a new external dependency."""

from dataclasses import dataclass

import structlog

from scrooner_pipeline.common.sec_client import SECClient

logger = structlog.get_logger()

FRAMES_BASE_URL = "https://data.sec.gov/api/xbrl/frames"


@dataclass
class FramesRow:
    cik: int
    entity_name: str
    value: float
    period_start: str | None
    period_end: str
    accession: str


def period_code(year: int, quarter: int, instant: bool) -> str:
    """CY2026Q1 for a duration concept, CY2026Q1I for instant -- verified
    live against both real shapes before trusting this format string."""
    suffix = "I" if instant else ""
    return f"CY{year}Q{quarter}{suffix}"


def fetch_frame(
    client: SECClient,
    taxonomy: str,
    tag: str,
    unit: str,
    year: int,
    quarter: int,
    instant: bool,
) -> list[FramesRow]:
    period = period_code(year, quarter, instant)
    url = f"{FRAMES_BASE_URL}/{taxonomy}/{tag}/{unit}/{period}.json"
    try:
        data = client.get_json(url)
    except Exception as e:
        logger.warning(
            "frames.fetch_failed",
            taxonomy=taxonomy,
            tag=tag,
            period=period,
            error=str(e),
        )
        return []
    return [
        FramesRow(
            cik=row["cik"],
            entity_name=row.get("entityName", ""),
            value=row["val"],
            period_start=row.get("start"),
            period_end=row["end"],
            accession=row.get("accn", ""),
        )
        for row in data.get("data", [])
    ]
