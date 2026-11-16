"""parse_deprecations reads the FASB taxonomy deprecations file (element / replacement_element) that the
company x tag x metric rebuild loads; the rebuild failed 9 runs on 2026-11-16 with KeyError 'tag'."""

from scrooner_pipeline.mapper.tag_library_rebuild import (
    DEPRECATIONS_CSV,
    parse_deprecations,
)


def test_taxonomy_layout_gives_deprecated_by_and_replaces(tmp_path):
    p = tmp_path / "d.csv"
    p.write_text(
        "element,deprecated_in_year,deprecated_date,replacement_element,source,chain\n"
        "SalesRevenueNet,2018,,RevenueFromContractWithCustomerExcludingAssessedTax,x,\n"
        "SalesRevenueGoodsNet,2018,,RevenueFromContractWithCustomerExcludingAssessedTax,x,\n"
        "ASU201501TransitionAbstract,2019,,,x,\n"
    )
    d = parse_deprecations(p)
    assert d["SalesRevenueNet"] == (
        "RevenueFromContractWithCustomerExcludingAssessedTax",
        None,
    )
    assert d["ASU201501TransitionAbstract"] == (None, None)
    assert d["RevenueFromContractWithCustomerExcludingAssessedTax"] == (
        None,
        "SalesRevenueGoodsNet;SalesRevenueNet",
    )


def test_older_tag_layout_still_read(tmp_path):
    p = tmp_path / "d.csv"
    p.write_text("tag,deprecated_by,replaces\nA,B,\nB,,A\n")
    assert parse_deprecations(p) == {"A": ("B", None), "B": (None, "A")}


def test_committed_taxonomy_file_parses():
    d = parse_deprecations(DEPRECATIONS_CSV)
    assert (
        len(d) > 1000
        and any(v[0] for v in d.values())
        and any(v[1] for v in d.values())
    )
