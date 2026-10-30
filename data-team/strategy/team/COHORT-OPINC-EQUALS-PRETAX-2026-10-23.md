# Cohort: displayed operating income equals pretax income (2026-10-23)

Evidence level: DATA-INFERRED throughout (stored-vs-stored; no filing opened). Read-only DB, about 33 queries, each with `set statement_timeout=20000` and at most 10 company_ids.

## Backend breakdown (counted: Supavisor, Supavisor auth_query, PostgREST)
Start and end identical: Supavisor 4, Supavisor (auth_query) 1, PostgREST 1 = 6 (limit 12). Excluded: supabase_admin 2, mgmt-api 1, postgres_exporter 1. No query exceeded 20 s.

## Concept ids
operating_income = 3, operating_income_resolved = 249 (used: 249, else 3). income_before_tax = 12, income_before_tax_resolved = 251 (used: 251, else 12). Only these four candidates exist in analytics.canonical_concept.

## Comparison query (template; id list = 10 cohort company_ids per run)
```sql
set statement_timeout=20000;
with v as (select cf.company_id, cf.period_id,
  max(case when cf.canonical_concept_id=249 then cf.value end) oir, max(case when cf.canonical_concept_id=3 then cf.value end) oib,
  max(case when cf.canonical_concept_id=251 then cf.value end) ptr, max(case when cf.canonical_concept_id=12 then cf.value end) ptb
  from analytics.canonical_fact cf where cf.company_id in (...) and cf.canonical_concept_id in (3,249,12,251) group by 1,2),
w as (select v.company_id, p.fiscal_year, p.fiscal_period, p.end_date, coalesce(oir,oib) oi, coalesce(ptr,ptb) pt
  from v join core.period p on p.id=v.period_id
  where p.end_date>='2023-06-01' and p.fiscal_period in ('FY','Q1','Q2','Q3','Q4'))
select company_id,
  count(*) filter (where oi is not null and pt is not null) n_both, count(*) filter (where oi is not null) n_oi, count(*) filter (where pt is not null) n_pt,
  count(*) filter (where oi is not null and pt is not null and abs(oi-pt)>0.001*abs(pt) and abs(oi-pt)<=0.02*abs(pt)) n_near,
  string_agg(fiscal_year||coalesce(fiscal_period,'')||' '||end_date||' oi='||oi||' pt='||pt, '; ' order by end_date desc)
    filter (where oi is not null and pt is not null and abs(oi-pt)<=0.001*abs(pt)) hit
from w group by 1;
```
Match = within 0.1% (hit). Near-miss = 0.1% to 2% (n_near count only). Window = all FY and quarter periods ending 2023-06-01 or later (about 16 periods, covers last 3 FYs and latest quarter).

## Coverage (NOT the whole cohort)
Cohort = 986 non-excluded rows of shards.csv. Scanned: all 209 cohort companies with SIC 60-67 (financials, insurers, REITs, brokers) + the first 20 rows of the cohort + the 5 named holds. About 750 non-financial cohort companies were NOT scanned (query budget); the mechanism is overwhelmingly a financial/REIT one, but this is not proven for them.
Of the scanned financials, roughly 110 had both values for at least one period (n_both > 0). About 80 have a pretax value but NO operating income (not comparable, no match possible). Pretax is missing or sparse in analytics.canonical_fact for companies that DO have operating income, so stored-vs-stored cannot test them via concepts: AFG 2668, AMH 2971, ESS 1916, SPG 2985, FRT 391, ADC 1903, BRX 3214, NNN 1395 (0 pretax periods); ELS 1805 (2 of 15), DLR 4791 (1 of 15), 3380 / 3238 / 3882 / 5634 / 4599 (3-4 of 16).

## Matches (within 0.1%)
| Ticker | company_id | Periods matched | Values (oi = pt) | operating_income_resolved source_tags (lineage) |
|---|---|---|---|---|
| BRO | 1036 | 2023Q2, 2023Q3, 2023FY, 2024Q1, 2024Q2, 2024Q3 (6 of 6 comparable; lineage latest = 2024-09-30) | 254M, 242M, 1,146M (FY2023), 364M, 346M, 317M | derived two-input path: OperatingExpenses + Revenues |
| SF | 1313 | 2023FY, 2024FY (2 of 2 comparable) | 706.692M; 928.444M | single tag OperatingIncomeLoss |
| ELS | 1805 | 2023Q2 (1 exact; 2023Q3 is a near-miss at 1.185%) | 65.076M | single tag OperatingIncomeLoss |
| MSTR | 2820 | 2025Q4, 2026Q1 (within 0.084%, 0.034%) | -17.446B vs -17.461B; -14.470B vs -14.465B | single tag OperatingIncomeLoss. Note latest period 2026-06-30: oi -22.80B vs pt -8.22B, so NOT matching now |
| COMP | 2983 | 2023Q4 exact; 2024FY within 0.065% | -83.0M; -154.8M vs -154.9M | single tag OperatingIncomeLoss. Latest 2026-06-30: oi 124M vs pt -297M, not matching now |
| HOOD | 5613 | 2026Q1 exact (10 further near-misses) | 411M | derived two-input path: OperatingExpenses + Revenues. Latest 2026-06-30: oi 574M vs pt 1,120M, not matching now |
| GLXY | 3133 | 2024Q1 exact, value -1000 (trivial, dollar-scale artifact) | -1000 | derived two-input path: OperatingExpenses + Revenues |

Large operating companies with 0.03%-0.1% hits (AAPL 2024Q4 0.064%; AMZN 2024FY 0.031%; V 2025Q2 0.055%) are coincidental near-equality (small non-operating items), not the mechanism; listed for completeness. Most other scanned companies show only 0 to 3 near-misses.

## Near-misses (0.1% to 2%) worth a look
ELS 2023Q3 (1.185%); HOOD (10 periods); MSTR (6 incl. above); COMP (6 incl. above); 3859, 5727, 5483 (8), 1055 (8), 3932 (9), 5718 V (11). Counts only; periods not enumerated.

## Named holds
- AFG (2668): operating_income_resolved = single tag OperatingIncomeLoss, FY2025 1,073M. No pretax concept stored (0 periods), so no concept-level match is possible. Stored raw facts (core.fact) for FY2025 show IncomeLossFromContinuingOperationsBeforeIncomeTaxesDomestic 1,031M + ...Foreign 42M = 1,073M, exactly equal to the stored operating income. DATA-INFERRED: consistent with the AFG mechanism (displayed operating income equals pretax).
- ELS (1805): one exact period match (2023Q2) and one near-miss; pretax stored for only 2 of 15 periods, so most periods untestable. Single tag OperatingIncomeLoss. Latest 2026-03-31 operating income 112.368M has no stored pretax to compare.
- MOG-A (705): both values in 14 periods, no match and no near-miss. Does not appear.
- MET (3459): both values in 16 periods, no match and no near-miss. Does not appear.
- HONA (5063): both values in 2 periods, no match and no near-miss. Does not appear.

## Limits
Not scanned: roughly 750 non-financial cohort companies. Companies lacking stored pretax cannot be tested by concept (list above); only AFG was checked through raw facts, and a raw-fact comparison for the other 7 REITs/others returned no match within 2% on the batch run (tag ilike '%BeforeIncomeTax%', authoritative facts, periods since 2024-06) but that does not prove they differ, since their pretax facts may be absent. No fixes proposed.


---
# ADDENDUM: scan of the remaining non-financial cohort (approved by data chief, 2026-10-23)
Evidence level: DATA-INFERRED (stored-vs-stored; no filing opened). 76 comparison queries + 9 grouped backend checks, 10 company_ids per query, `set statement_timeout=20000` on each, one at a time, none over 20 s.

## Full frame definition
- Cohort = the 986 rows of /Users/vikash/scrooner/doc/data-moat/team/top1000/shards.csv with an empty `excluded` column (company_id column). Rows with any excluded text (including "keep:" rows) are outside the frame.
- First scan covered 230 of them (the 209 with SIC 60-67, plus the first 20 batch rows and the 5 named holds, deduplicated). This addendum scanned the other 756, in cohort-file order, batches of 10. Combined: 986 of 986 scanned, 0 not scanned.
- Concepts: operating_income_resolved 249 (else operating_income 3) vs income_before_tax_resolved 251 (else income_before_tax 12), same `period_id`, `analytics.canonical_fact`.
- Periods: every core.period with fiscal_period in (FY, Q1-Q4) and end_date >= 2023-06-01 (about 16 periods per company: last 3 fiscal years plus the latest quarters). Match = |oi - pt| <= 0.1% of |pt|; near-miss = 0.1% to 2%.

## Exact comparison query (id list replaced per batch; summary form)
```sql
set statement_timeout=20000;
with v as (select cf.company_id, cf.period_id,
  max(case when cf.canonical_concept_id=249 then cf.value end) oir, max(case when cf.canonical_concept_id=3 then cf.value end) oib,
  max(case when cf.canonical_concept_id=251 then cf.value end) ptr, max(case when cf.canonical_concept_id=12 then cf.value end) ptb
  from analytics.canonical_fact cf where cf.company_id in (<10 ids>) and cf.canonical_concept_id in (3,249,12,251) group by 1,2),
w as (select v.company_id, p.fiscal_year fy, p.fiscal_period fp, p.end_date, coalesce(oir,oib) oi, coalesce(ptr,ptb) pt
  from v join core.period p on p.id=v.period_id
  where p.end_date>='2023-06-01' and p.fiscal_period in ('FY','Q1','Q2','Q3','Q4'))
select count(distinct company_id) filter (where oi is not null and pt is not null) cos_both,
  count(distinct company_id) filter (where oi is not null and pt is null) cos_oi_only_gap,
  count(*) filter (where oi is not null and pt is not null and abs(oi-pt)>0.001*abs(pt) and abs(oi-pt)<=0.02*abs(pt)) n_near,
  string_agg(company_id||' '||fy||coalesce(fp,'')||' '||end_date||' '||oi||'='||pt, '; ' order by company_id,end_date desc)
    filter (where oi is not null and pt is not null and abs(oi-pt)<=0.001*abs(pt)) hit
from w;
```

## Results of the new scan (756 companies)
- Companies with both values in at least one period: 680. Companies with an operating-income period but no pretax value in that period (pretax gap, so untestable there): 119 (per-batch distinct counts; a company can be in both). About 76 of the 756 had no operating income at all in the window.
- Total period-level matches within 0.1%: 58 across 48 companies. Total near-misses (0.1%-2%) across the new scan: about 750 period cells (counts only, not enumerated).
- Pattern: every one of the 48 is 1 to 3 isolated periods, none a persistent run, none matching in both the latest FY and latest quarter. This looks like coincidental near-equality (little interest and non-operating items), not the AFG/ELS mechanism (a filer with no operating income line). No company in the new scan shows the BRO-style run of 6.

Matches by company (periods matched; exact = 0.000%):
- CAT 251: 2023Q2 (exact). TXN 1104: 2024Q3 (exact), 2024Q2. SNDK 4227: 2026Q3. ADBE 1488: 2026Q2 (exact). MMM 700: 2024FY. REGN 1686: 2023Q3. CMI 318: 2025Q2. TEL 5577: 2024FY.
- FAST 1544: 2025FY, 2026Q2, 2026Q3 (3). KEYS 3478: 2023FY. GRMN 3695: 2024Q4. A 3346: 2026Q3 (exact). NTAP 2133: 2027Q1 (exact). ODFL 1714: 2025FY, 2023Q2. RMD 1985: 2026Q1. GEHC 3661: 2023Q2 (exact). RKLB 2370: 2023Q2. DOV 345: 2025FY.
- XYL 2542: 2026Q1 (exact). RL 2564: 2027Q1. RS 1658: 2023FY, 2023Q2. GPC 612: 2023Q2, 2023Q3, 2023Q4 (3). TOST 4112: 2024Q4 (exact, 33M). RIVN 3315: 2025Q2. WMG 4947: 2023Q4 (exact). CDE 1168: 2025Q4. LSCC 1643: 2023Q2. FLUT 3913: 2025Q3 (exact).
- AIT 1160: 2025Q4. IONQ 2475: 2023FY. WTS 1486: 2024Q4 (exact). BWA 1850: 2024Q3, 2025Q3 (both exact). W 3675: 2025Q2 (exact). AMKR 2763: 2024Q2. GMED 4406: 2025Q4. GKOS 4278: 2025Q4. DRS 2647: 2026Q1 (exact). PCTY 3366: 2026Q3.
- GAP 605: 2024Q3 (exact). LEVI 1091: 2026Q2 (exact). SSD 1914: 2025Q4, 2023Q3. RAL 4465: 2025Q2 (exact). IONS 1690: 2025Q1. MSA 699: 2026Q1. ANF 2332: 2024FY. TTAN 3956: 2025Q4. SFM 3118: 2026Q2, 2026Q1. VAL 1195: 2023Q4 (exact).
Lineage source_tags were not pulled for these (not requested beyond the first list; none shows a persistent match, so no AFG/ELS-type company was found in the new scan).

## Combined totals
- Cohort 986; scanned 986 (230 first scan + 756 addendum); not scanned 0.
- Persistent or structural matches (operating income = pretax across many periods): BRO (6 of 6 comparable periods; derived OpEx+Revenues path) and SF (2 of 2 FY; single OperatingIncomeLoss tag) from the first scan; AFG by raw-fact check (FY2025 1,073M = domestic 1,031M + foreign 42M pretax tags; no pretax concept stored). ELS is partial (1 exact period; pretax stored for only 2 of 15 periods). Isolated single-period or tiny-run coincidences: the rest (first-scan list above plus the 48 companies here).
- Untestable by concept (operating income present, pretax concept absent): first scan 8 REITs/others (AFG, AMH, ESS, SPG, FRT, ADC, BRX, NNN) plus about 119 company-batches in the new scan with some pretax-absent period; only AFG was cross-checked through raw core.fact tags.
- Named holds unchanged: AFG (raw-fact equality), ELS (partial), MOG-A / MET / HONA (no match).

## Grouped backend breakdown (counted: Supavisor, Supavisor auth_query, PostgREST, our apps)
Start of addendum and at each of the 9 checks (before batches 0, 12, 22, 30, 40, 49, 58, 66, and end): identical every time: Supavisor 4, Supavisor (auth_query) 1, PostgREST 14.5 1 = 6 (limit 12). Excluded: supabase_admin 2, mgmt-api 1, postgres_exporter 1. End of addendum: same, 6.
