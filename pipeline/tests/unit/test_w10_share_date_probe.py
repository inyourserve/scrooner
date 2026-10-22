"""Pure parts of the W10 share-date probe."""

import importlib.util
from datetime import date
from pathlib import Path

PATH = Path(__file__).resolve().parents[2] / "scripts" / "w10_share_date_probe.py"
spec = importlib.util.spec_from_file_location("w10_probe", PATH)
probe = importlib.util.module_from_spec(spec)
spec.loader.exec_module(probe)

BS = date(2026, 6, 27)


def test_classes_match_the_aapl_shape_and_the_edges():
    assert (
        probe.classify(BS, [BS, date(2026, 7, 17)]) == "bs_date_count"
    )  # AAPL: both dates exist
    assert probe.classify(BS, [date(2026, 7, 17)]) == "cover_after_only"
    assert (
        probe.classify(BS, [date(2026, 10, 25)]) == "cover_after_only"
    )  # exactly 120 days
    assert probe.classify(BS, [date(2026, 10, 26)]) == "later_only"
    assert probe.classify(BS, [date(2026, 3, 28)]) == "none_at_or_after"
    assert probe.classify(BS, []) == "none_at_or_after"


def test_summary_counts():
    rows = [
        {
            "bs_date": BS,
            "share_count_class": "bs_date_count",
            "bvps_latest_end": BS,
            "bvps_latest_valued": False,
            "bvps_has_older_valued": True,
        },
        {
            "bs_date": BS,
            "share_count_class": "cover_after_only",
            "bvps_latest_end": BS,
            "bvps_latest_valued": True,
            "bvps_has_older_valued": True,
        },
        {
            "bs_date": None,
            "share_count_class": "no_equity_instant",
            "bvps_latest_end": None,
            "bvps_latest_valued": False,
            "bvps_has_older_valued": False,
        },
    ]
    s = probe.summarize(rows)
    assert (
        s["companies_in_population"] == 3
        and s["companies_with_latest_equity_instant"] == 2
    )
    assert s["share_count_class"] == {"bs_date_count": 1, "cover_after_only": 1}
    assert (
        s["bvps_newest_row_blank"] == 1
        and s["bvps_newest_blank_with_older_valued_row"] == 1
    )
