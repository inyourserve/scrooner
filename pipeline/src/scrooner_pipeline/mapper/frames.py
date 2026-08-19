"""Frames-API client (doc 11's proposed, never-built tag-coverage discovery
tool -- see doc 11 lines 176-211). "One fact, one period, across every
company that reported it" (doc 07's XBRL Frames API), the inverse of the
per-company Company Facts API this pipeline otherwise uses everywhere else.

Read-only against SEC, writes nothing -- purely a discovery aid for a human
curating mapper/concepts.py's CONCEPT_MAPPINGS list. Reuses SECClient (the
same rate limiter, User-Agent, and retry policy every other SEC call in this
codebase already goes through) rather than a second HTTP implementation.

This is exactly the query doc 11 already ran ad hoc on 2026-08-16 (Frames
API for 4 revenue tags, found 3,140+2,674+404+479 companies), made
repeatable and generalized to any (taxonomy, tag, unit, period).
"""

import structlog

from scrooner_pipeline.common.sec_client import SECClient

logger = structlog.get_logger()

FRAMES_BASE_URL = "https://data.sec.gov/api/xbrl/frames"


def fetch_frame(sec: SECClient, taxonomy: str, tag: str, unit: str, period: str) -> list[dict]:
    """Returns SEC's raw `data` array for one (taxonomy, tag, unit, period)
    -- one row per company reporting that tag for that period, each with at
    least `cik`, `entityName`, `val`. `period` follows doc 07's format:
    CY2024 (annual), CY2024Q1 (quarterly), CY2024Q1I (instantaneous)."""
    url = f"{FRAMES_BASE_URL}/{taxonomy}/{tag}/{unit}/{period}.json"
    try:
        payload = sec.get_json(url)
    except Exception:
        logger.warning("frames.fetch_failed", taxonomy=taxonomy, tag=tag, unit=unit, period=period)
        return []
    return payload.get("data", [])


def frame_company_count(sec: SECClient, taxonomy: str, tag: str, unit: str, period: str) -> int:
    """Company-count-only version of fetch_frame -- doc 11's own discovery
    workflow only ever needed the count ('how many companies use tag X'),
    not each company's individual value."""
    return len(fetch_frame(sec, taxonomy, tag, unit, period))
