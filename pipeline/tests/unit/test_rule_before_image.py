from datetime import date
from decimal import Decimal

from scrooner_pipeline.common import rule_before_image as bi


def test_manifest_restore_and_verify():
    ch = [
        bi.PlannedChange(
            "r.x@1",
            "0000000001",
            1,
            "x",
            date(2026, 1, 1),
            Decimal("5"),
            None,
            "guard_hidden",
        ),
        bi.PlannedChange(
            "r.x@1",
            "0000000002",
            2,
            "x",
            date(2026, 1, 1),
            Decimal("7"),
            Decimal("6"),
            "guard_hidden",
        ),
    ]
    man = bi.manifest("r.x@1", ch, flag_state="dry_run")
    assert man["ciks"] == ["0000000001", "0000000002"] and man["cells_to_blank"] == 1
    assert "ciks=0000000001,0000000002" in bi.restore_command(man)
    restored = {
        ("0000000001", "x", date(2026, 1, 1)): Decimal("5"),
        ("0000000002", "x", date(2026, 1, 1)): Decimal("7"),
    }
    assert bi.verify_restored(ch, restored) == []
    restored[("0000000002", "x", date(2026, 1, 1))] = Decimal("6")
    assert bi.verify_restored(ch, restored) == [ch[1]]
