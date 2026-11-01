"""fsn_store.extract_sec: SEC set URL and the byte-exact filter to extra CIKs' filings."""

from __future__ import annotations

import io
import zipfile

import pytest
from scrooner_pipeline.fsn_store import extract_sec as ex


def _zip(tables: dict[str, list[str]]) -> zipfile.ZipFile:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as z:
        for name, lines in tables.items():
            z.writestr(f"{name}.tsv", "\n".join(lines) + "\n")
    buf.seek(0)
    return zipfile.ZipFile(buf)


@pytest.mark.unit
def test_sec_url_quarterly_and_monthly_sets():
    assert ex.sec_url("2024q1").endswith("/2024q1_notes.zip")
    assert ex.sec_url("2025m01").endswith("/2025_01_notes.zip")


@pytest.mark.unit
def test_filter_keeps_only_the_ciks_filings_and_what_they_reference():
    zf = _zip(
        {
            "sub": ["adsh\tcik\tform\taciks", "A1\t34088\t10-K\t", "B1\t320193\t10-K\t", "C1\t999\t10-Q\t34088"],
            "pre": ["adsh\treport\tline\tstmt\ttag\tversion", "A1\t2\t1\tIS\tRevenues\tus-gaap/2024", "B1\t2\t1\tIS\tRevenues\tus-gaap/2024"],
            "num": [
                "adsh\ttag\tversion\tddate\tqtrs\tuom\tdimh\tvalue",
                "A1\tRevenues\tus-gaap/2024\t20241231\t4\tUSD\t0x00000000\t339247000000.0000",
                "A1\tRevenues\tus-gaap/2024\t20241231\t4\tUSD\t0xabc\t1.0000",
                "B1\tRevenues\tus-gaap/2024\t20241231\t4\tUSD\t0x00000000\t5",
            ],
            "cal": ["adsh\tgrp\tarc\tnegative\tptag\tpversion\tctag\tcversion", "A1\t1\t1\t1\tProfitLoss\tus-gaap/2024\tRevenues\tus-gaap/2024"],
            "ren": ["adsh\treport\trfile\tmenucat", "A1\t2\tH\tS", "B1\t2\tH\tS"],
            "tag": ["tag\tversion\tcustom", "Revenues\tus-gaap/2024\t0", "ProfitLoss\tus-gaap/2024\t0", "Other\tus-gaap/2024\t0"],
            "dim": ["dimhash\tsegments\tsegt", "0xabc\tSeg=A;\t0", "0xdef\tSeg=B;\t0"],
        }
    )
    out = ex.filter_set(zf, {"0000034088"})
    assert [r[0] for r in out["sub"][1:]] == [b"A1", b"C1"]  # registrant and co-registrant
    assert len(out["pre"]) == 2 and len(out["ren"]) == 2 and len(out["cal"]) == 2
    assert [r[-1] for r in out["num"][1:]] == [b"339247000000.0000", b"1.0000"]  # byte-exact values
    assert {r[0] for r in out["tag"][1:]} == {b"Revenues", b"ProfitLoss"}
    assert [r[0] for r in out["dim"][1:]] == [b"0xabc"]
