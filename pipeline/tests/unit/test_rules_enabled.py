from datetime import date
from decimal import Decimal

from scrooner_pipeline.common import rule_before_image as bi
from scrooner_pipeline.common.rules_enabled import enabled_rules, is_dry_run, is_enabled


def test_default_is_off():
    assert enabled_rules({}) == frozenset()
    assert not is_enabled("debt.total_debt_consistency@1", {})
    assert not is_dry_run({})


def test_exact_version_and_family_matching():
    env = {"SCROONER_RULES_ENABLED": " a.b@1 , c.d "}
    assert is_enabled("a.b@1", env) and not is_enabled("a.b@2", env)
    assert is_enabled("c.d@1", env) and is_enabled("c.d@7", env)


def test_dry_run_switch():
    assert is_dry_run({"SCROONER_RULES_DRYRUN": "1"})
    assert not is_dry_run({"SCROONER_RULES_DRYRUN": "0"})


def test_manifest_restore_and_verify():
    ch = [
        bi.PlannedChange(
            "r@1",
            "0000000001",
            1,
            "x",
            date(2026, 1, 1),
            Decimal("5"),
            None,
            "guard_hidden",
        ),
        bi.PlannedChange(
            "r@1",
            "0000000002",
            2,
            "x",
            date(2026, 1, 1),
            Decimal("7"),
            Decimal("6"),
            "guard_hidden",
        ),
    ]
    man = bi.manifest("r@1", ch, flag_state="dry_run")
    assert man["ciks"] == ["0000000001", "0000000002"] and man["cells_to_blank"] == 1
    assert "ciks=0000000001,0000000002" in bi.restore_command(man)
    restored = {
        ("0000000001", "x", date(2026, 1, 1)): Decimal("5"),
        ("0000000002", "x", date(2026, 1, 1)): Decimal("7"),
    }
    assert bi.verify_restored(ch, restored) == []
    restored[("0000000002", "x", date(2026, 1, 1))] = Decimal("6")
    assert bi.verify_restored(ch, restored) == [ch[1]]
