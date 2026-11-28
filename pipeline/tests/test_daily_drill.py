"""scripts/ci/daily_drill.py: batch choice, gates and the report on a tiny fixture (no database, no network)."""
import csv
import importlib.util
import pathlib
import subprocess
import sys
from datetime import date

ROOT = pathlib.Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location("daily_drill", ROOT / "scripts/ci/daily_drill.py")
dd = importlib.util.module_from_spec(spec)
spec.loader.exec_module(dd)

RANKING = [dict(rank=i, ticker=f"T{i}", cik=str(1000 + i), name=f"N{i}") for i in range(1, 51)]


def test_pick_skips_certified_rolls_and_wraps():
    cert = {"T1", "T2"}
    d0 = dd.EPOCH
    a = dd.pick(RANKING, cert, d0, 20)
    assert [r["rank"] for r in a] == list(range(3, 23))
    b = dd.pick(RANKING, cert, date.fromordinal(d0.toordinal() + 1), 20)
    assert [r["rank"] for r in b] == list(range(23, 43))
    c = dd.pick(RANKING, cert, date.fromordinal(d0.toordinal() + 2), 20)
    assert [r["rank"] for r in c] == list(range(43, 51)) + list(range(3, 15))
    assert dd.pick(RANKING, cert, d0, 20) == a
    assert not {r["ticker"] for r in a + b + c} & cert


def test_certified_tickers_reads_certificate_names(tmp_path):
    for n in ("MSFT-certificate-2026-11-14.md", "MSFT-final-draw-2026-11-14.md", "BRK.B-certificate-2026-11-20.md"):
        (tmp_path / n).write_text("x")
    assert dd.certified_tickers(str(tmp_path)) == {"MSFT", "BRK.B"}


def test_pick_cli_as_ci_invokes_it(tmp_path):
    rk = tmp_path / "rank.csv"
    rk.write_text("company_id,cik,ticker,name,source,mcap_bn_basis,flags\n2733,0001045810,NVDA,NVIDIA,cohort_v1 (shards.csv rank 1),1,\n"
                  "3,0000320193,AAPL,Apple,cohort_v1 (shards.csv rank 2),1,\n")
    ap = tmp_path / "ap"
    ap.mkdir()
    (ap / "AAPL-certificate-2026-11-14.md").write_text("x")
    out = tmp_path / "out"
    subprocess.run([sys.executable, str(ROOT / "scripts/ci/daily_drill.py"), "pick", "--ranking", str(rk), "--approvals", str(ap),
                    "--date", "2026-11-17", "--out", str(out), "--n", "5"], check=True)
    assert (out / "ciks.txt").read_text().strip() == "1045810"
    assert (out / "tk.csv").read_text().strip() == "NVDA,0001045810"


def R(tk, dp, pe, status, value="", acc="A1", tags="", nodes="", why=""):
    return dict(ticker=tk, cik="1", accession=acc, period_end=pe, data_point=dp, status=status, tags=tags, value=value, nodes=nodes, why=why, flags="")


def test_same_is_rounding_aware():
    assert dd.same(dd.D("1000000"), dd.D("1000000"))
    assert dd.same(dd.D("27700000000"), dd.D("27699999000"))
    assert not dd.same(dd.D("27700000000"), dd.D("27900000000"))
    assert not dd.same(None, dd.D("1"))


def P(dp, pe, v, acc="A1", tag="T"):
    return dict(cik="1", data_point=dp, grain="FY", period_end=pe, verdict="PROVEN", shown_value=v, shown_tag=tag, shown_accession=acc, position_value="", reason_code="")


def test_gates_classify_and_count(tmp_path):
    rows = [R("AA", "revenue", "2024-12-31", "mapped", "100000000", tags="Revenues", nodes="Revenues=100000000 [R4.htm:2]"),
            R("AA", "net_income", "2024-12-31", "no_role", why="no node"),
            R("AA", "cost_of_revenue", "2024-12-31", "mapped", "5300000", tags="CostOfRevenue", nodes="CostOfRevenue=5300000 [R4.htm:3]"),
            R("AA", "total_assets", "2024-12-31", "mapped", "9000000", tags="Assets")]
    batch = [dict(rank=1, ticker="AA", cik="1", name="x")]
    proofs = [P("revenue", "2024-12-31", "100000000"), P("net_income", "2024-12-31", "7000000"),
              P("cost_of_revenue", "2024-12-31", "6400000"), P("revenue", "2023-12-31", "90000000", "A0")]
    checks = [dict(cik="1", accession="A1", stmt="IS", ddate="2024-12-31", qtrs="4", check_id="calc:CostOfRevenue:IS", lhs="5300000", rhs="6400000", tol="1000")]
    reads = tmp_path / "reads"
    reads.mkdir()
    (reads / "AA-docmap-2026-11-12.csv").write_text(
        "ticker,data_point,status,tags,stmt,r_page,label,fy0_printed,fy0_api,fy1_printed,fy1_api,match,era_from_note,evidence_class,note\n"
        "AA,revenue,mapped,us-gaap:Revenues,IS,R4.htm,Rev,100000000,100000000,90000000,90000000,Y,x,FILING-CHECKED,period 2024-01-01..2024-12-31\n"
        "AA,total_assets,mapped,us-gaap:Assets,BS,R2.htm,TA,9000000,9000000,,,Y,x,FILING-CHECKED,period 2024-01-01..2024-12-31\n"
        "AA,gross_profit,mapped,us-gaap:GrossProfit,IS,R4.htm,GP,1,1,,,Y,x,DATA-INFERRED,period 2024-01-01..2024-12-31\n")
    roles = tmp_path / "roles.csv"
    roles.write_text("data_point,stmt,parent,alternatives,combined_if,note_ok,custom_label,ruling,fallback\n")
    fam = tmp_path / "fam.txt"
    fam.write_text("# c\nCostOf\\w*\n")
    filings = [dict(a="A1", cik="1", p="2024-12-31",
                    lines="IS|4|2|Revenues|0|0||Rev|100000000~IS|4|9|WeirdLine|1|0||Weird|42~IS|4|3|CostOfRevenue|0|0||Cost|5300000", calc="")]
    items, st = dd.build(rows, filings, proofs, checks, str(reads), str(roles), str(fam), "2026-11-17", batch)
    assert st["proof"]["proof_compared"] == 4 and st["proof"]["proof_agree"] == 1
    kinds = {(i["kind"], i["data_point"], i["class"]) for i in items}
    assert ("proof_disagree", "net_income", "rule_gap") in kinds
    assert ("proof_disagree", "cost_of_revenue", "filer_error") in kinds
    assert ("proof_disagree", "revenue", "data_gap") in kinds
    assert ("no_role", "net_income", "rule_gap") in kinds
    assert st["docmap"]["docmap_compared"] == 3 and st["docmap"]["docmap_agree"] == 2
    assert st["docmap"]["docmap_not_filing_checked"] == 1
    assert ("docmap_disagree", "revenue", "data_gap") in kinds
    assert [i["tag"] for i in items if i["kind"] == "new_element_family"] == ["WeirdLine"]
    assert ("filer_check_failed", "cost_of_revenue", "filer_error") in kinds
    out = tmp_path / "drills"
    dd.write_report(items, st, batch, str(out), "2026-11-17")
    md = (out / "2026-11-17.md").read_text()
    assert "Coverage (value or reason): 75.00%" in md and "25.00% (1/4)" in md
    got = list(csv.DictReader(open(out / "2026-11-17.csv")))
    assert got and set(got[0]) == set(dd.COLS) and {r["class"] for r in got} <= {"rule_gap", "data_gap", "filer_error"}


def test_no_key_is_not_reported_as_zero():
    assert dd.pct(0, 0) == "n/a (no key)" and dd.pct(1, 2) == "50.00%"


def test_attempts_file_counts_each_gate_per_company_and_data_point(tmp_path):
    rows = [R("AA", "revenue", "2024-12-31", "mapped", "100000000", tags="Revenues"),
            R("AA", "net_income", "2024-12-31", "no_role", why="no node")]
    batch = [dict(rank=1, ticker="AA", cik="1", name="x")]
    proofs = [P("revenue", "2024-12-31", "100000000"), P("net_income", "2024-12-31", "7000000"), P("revenue", "2023-12-31", "9", "A0"),
              dict(P("gross_profit", "2024-12-31", ""), verdict="NOT_PRESENTED")]
    roles = tmp_path / "roles.csv"
    roles.write_text("data_point,stmt,parent,alternatives,combined_if,note_ok,custom_label,ruling,fallback\n")
    fam = tmp_path / "fam.txt"
    fam.write_text("")
    items, st = dd.build(rows, [], proofs, [], str(tmp_path / "none"), str(roles), str(fam), "2026-11-17", batch)
    out = tmp_path / "drills"
    dd.write_report(items, st, batch, str(out), "2026-11-17")
    got = {(r["data_point"], r["gate"]): r for r in csv.DictReader(open(out / "2026-11-17-attempts.csv"))}
    assert list(next(iter(got.values()))) == dd.ATT_COLS
    rev = got[("revenue", "proof")]
    assert (rev["compared"], rev["agree"], rev["data_gap"], rev["rule_gap"], rev["evidence_label"]) == ("2", "1", "1", "0", "DATA-INFERRED")
    ni = got[("net_income", "proof")]
    assert (ni["compared"], ni["agree"], ni["rule_gap"]) == ("1", "0", "1")
    assert (got[("gross_profit", "proof_np")]["compared"], got[("gross_profit", "proof_np")]["agree"]) == ("1", "1")
    # every compared key is counted exactly once, matching the report's proof totals
    assert sum(int(r["compared"]) for r in got.values()) == st["proof"]["proof_compared"] + st["proof"]["proof_np_compared"]


def test_drill_workflow_feeds_pattern_intake_on_main_with_30_tries():
    wf = (ROOT / ".github/workflows/pipeline-daily-drill.yml").read_text()
    assert '"$RUNNER_TEMP/$DAY-attempts.csv" data-team/tags/drills/' in wf
    step = wf[wf.index("Drill misses -> pattern intake"):]
    assert "pattern_intake.py\" --drills" in step and "git archive origin/drills data-team/tags/drills" in step
    assert "seq 1 30" in step and "git push -q origin HEAD:main" in step
    assert "pattern-intake.csv" in step and "drill-class-accuracy.csv" in step
    # the loop is committed by the same step: proposals, their status rows and the eligibility file are staged and allowed
    for f in ('auto-map-eligible.csv', '$R/drill-auto.csv', '$R/STATUS.csv'):
        assert step.count(f) >= 2, f
    assert "vars.DAILY_DRILL == 'true'" in wf   # the founder's switch is untouched


def test_proof_resolved_names_match_resolver_data_points(tmp_path):
    """cell_proof names the resolved layer (total_assets_resolved, revenue_sanity_resolved); the resolver uses the base name."""
    rows = [R("AA", "total_assets", "2024-12-31", "mapped", "9000000", tags="Assets"),
            R("AA", "revenue", "2024-12-31", "mapped", "100000000", tags="Revenues")]
    batch = [dict(rank=1, ticker="AA", cik="1", name="x")]
    proofs = [P("total_assets_resolved", "2024-12-31", "9000000"), P("revenue_sanity_resolved", "2024-12-31", "100000000"),
              P("cfo_resolved", "2024-12-31", "5")]
    roles = tmp_path / "roles.csv"
    roles.write_text("data_point,stmt,parent,alternatives,combined_if,note_ok,custom_label,ruling,fallback\n")
    fam = tmp_path / "fam.txt"
    fam.write_text("")
    items, st = dd.build(rows, [], proofs, [], str(tmp_path / "none"), str(roles), str(fam), "2026-11-17", batch)
    assert st["proof"]["proof_compared"] == 3 and st["proof"]["proof_agree"] == 2
    assert [(i["data_point"], i["class"]) for i in items] == [("cfo", "data_gap")]


def test_every_resolved_catalog_concept_maps_to_a_registry_data_point():
    """The shared rule (certification.model.base_name) sends each *_resolved concept to a metric-registry data point."""
    reg = {r["data_point"] for r in csv.DictReader(open(ROOT / "pipeline/src/scrooner_pipeline/metrics/registry/data_points.csv"))}
    cat = [r["name"] for r in csv.DictReader(open(ROOT / "data-team/47-fsn-store/company_tag_map/concepts_catalog.csv"))
           if r["name"].endswith("_resolved")]
    assert len(cat) >= 28
    assert [c for c in cat if dd.base_name(c) not in reg] == ["employee_count_resolved"]   # not a template data point


def test_family_gate_skips_elements_read_or_decided_anywhere(tmp_path):
    # ACN FY2015: total_assets is served from the FY2016 print (row accession A16), so the own filing's Assets line was called
    # unread; an element the rule store already decides (LiabilitiesAndStockholdersEquity: identity line) is no new family either
    roles = tmp_path / "roles.csv"
    roles.write_text("data_point,stmt,parent,alternatives,combined_if,note_ok,custom_label,ruling,fallback\n")
    fam = tmp_path / "families.txt"
    fam.write_text("")
    rules = tmp_path / "rules"
    rules.mkdir()
    (rules / "bs.csv").write_text(
        "rule_id,version,namespace,data_point,scope,era,kind,when,then,precedence,evidence,author,date,note\n"
        'lib.bs.LiabilitiesAndStockholdersEquity,1,bs,,all,,tag,"{""stmt"":""BS"",""tag"":""LiabilitiesAndStockholdersEquity"",""order"":2}",'
        '"{""decision"":""excluded"",""concept"":"""",""parent_concept"":"""",""reason_class"":""identity_check_line""}",data point,explicit,x,2026-11-28,\n')
    known, fams = dd.known_tags(str(roles), str(fam), rules_dir=str(rules), resolver_dir=str(tmp_path / "none"))
    assert "LiabilitiesAndStockholdersEquity" in known

    class Res:
        rows = [dict(accession="A16", nodes="Assets=18202647000 [R2.htm:25@A16]", tags="Assets", status="mapped")]

    line = lambda tag, lb: f"BS|2|1|{tag}|0|0|terseLabel|{lb}|1"
    filings = [dict(a="A15", cik="1467373", p="2015-08-31",
                    lines="~".join([line("Assets", "Total assets"), line("LiabilitiesAndStockholdersEquity", "Total"), line("BrandNewElement", "New line")]))]
    out, n = dd.gate_families(Res(), filings, {"1467373": "ACN"}, known, fams, "2026-11-28")
    assert [o["tag"] for o in out] == ["BrandNewElement"] and n == 1
