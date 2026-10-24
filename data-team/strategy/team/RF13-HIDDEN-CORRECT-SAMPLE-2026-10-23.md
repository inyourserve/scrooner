# RF-13 hidden-correct sample (2026-10-23)

Worker: read-only measurement subagent. DB: Supabase MCP `execute_sql` only (project yaqvssrpkieutdklmdjr), about 92 queries, each starting `set statement_timeout=20000`, each scoped to 10 company_ids; no writes. SEC: only the cached R-page fetches of `top1000/tools/sec_rpages.py` (0.6 s sleep, User-Agent `Scrooner research inyourserve@gmail.com`). No proposals for fixes are made here.

## Result in one paragraph
Frame: **66 company-periods at 66 companies** (of 842 non-bank companies; 7.8%) meet the RF-13 trigger on their latest fiscal-year period (DATA-INFERRED). Seeded sample of 40 of them, each checked against the filing's income statement (FILING-CHECKED): **7 HIDDEN-CORRECT (17.5%, Wilson 95% interval 8.7%-32%)**, 33 HIDDEN-WRONG (82.5%), 0 UNDECIDABLE. Of the 33 wrong, 8 are a "sub-line" pattern (stored is a recognized subtotal such as revenue from contracts with customers, while the statement's labelled total adds other revenue); the other 25 are not close to any presented total. Scaling to the frame: about 7 known + 26 unsampled x 17.5% = roughly 12 hidden-correct company-periods of 66 (about 9 to 15 using the Wilson bounds on the unsampled 26). The earlier doc 37 sample (15 of 22 displayed periods correct) is a different population (displayed periods, not triggered ones); this sample is conditional on the trigger.

## Method
1. Companies: `doc/data-moat/team/top1000/shards.csv`, 1,014 rows; dropped 28 rows marked excluded (986 left); dropped SIC 6000-6411 (my financial exclusion rule: banks, savings, credit, brokers, exchanges, insurers; REITs and real estate at 6500+ are NOT excluded) leaving **842 companies**. Id list: scratch `ids.txt` (also in the appendix).
2. Period: for each company the latest `core.period` with `fiscal_period='FY'` and `end_date >= 2024-01-01` that carries any revenue-family tag (10-K year only; no 10-Q quarter, see limits).
3. Revenue-family tags (my assumption; the guard's own list was not available to read): us-gaap `Revenues`, `RevenueFromContractWithCustomerExcludingAssessedTax`, `RevenueFromContractWithCustomerIncludingAssessedTax`, `SalesRevenueNet`, `RevenuesNetOfInterestExpense`, `RegulatedAndUnregulatedOperatingRevenue`. Component tags (SalesRevenueGoodsNet/ServicesNet) left out because they would trigger falsely. Value per (company, period, tag) = `max(core.fact.value)` over all filings and `is_authoritative` states.
4. Trigger: at least two distinct tags in that period and no pair with `|a-b| <= 1% x max(|a|,|b|)`. Stored value = `analytics.canonical_fact` for concept `revenue` at that `period_id`.
5. Sample: Python `random.seed(20261023)`; `random.sample(frame, 40)` over the frame list in the order below.
6. Check: opened each sampled filing's income statement R-page (via FilingSummary / R2-R9 scan), read the statement's revenue lines, compared with stored. HIDDEN-CORRECT = stored equals the statement's total (top-line) revenue line, where "Net sales" counts as the total when the statement shows gross Sales less excise taxes. HIDDEN-WRONG = stored is a different figure; **WRONG-SUBLINE** is a subset where stored equals a presented subtotal (reader may prefer to treat these as arguable). UNDECIDABLE = no single total (none found).

## Seed, frame size, backend breakdown
- Seed: **20261023**.
- Frame size: **66 company-periods, 66 companies** (842 companies scanned in 85 chunks of at most 10 ids; 0 chunks timed out; no query exceeded 20 s).
- Pooler/app backend sum (Supavisor + Supavisor auth_query + PostgREST), grouped query `select coalesce(nullif(application_name,''),'(none)') app, usename, count(*) n from pg_stat_activity where backend_type='client backend' group by 1,2 order by 3 desc`:
  - Start (after the revised rule): Supabase Storage API 10, Supavisor 5, mgmt-api 1, postgres_exporter 1, PostgREST 1, pgbouncer 1, Supavisor auth_query 1, supabase_admin 1; sum counted = 7.
  - Mid-run (after about 33 chunks and again after about 64 chunks): Supavisor 4, supabase_admin 1, mgmt-api 1, postgres_exporter 1, PostgREST 1, Supavisor auth_query 1; sum = 6.
  - End: identical to mid-run, sum = 6. Never above 12. (Before the rule was revised, a first count showed 18 client backends in total including Storage API, and I stopped then.)

## Exact frame query (one per chunk of 10 company_ids; `<<10 ids>>` replaced per chunk)
```sql
set statement_timeout=20000; with t as (select f.company_id, f.period_id, p.end_date, c.tag, max(f.value) v, (array_agg(fl.accession_number order by fl.filing_date desc))[1] acc from core.fact f join core.concept c on c.id=f.concept_id join core.period p on p.id=f.period_id join core.filing fl on fl.id=f.filing_id where f.company_id in (<<10 ids>>) and c.taxonomy='us-gaap' and c.tag in ('Revenues','RevenueFromContractWithCustomerExcludingAssessedTax','RevenueFromContractWithCustomerIncludingAssessedTax','SalesRevenueNet','RevenuesNetOfInterestExpense','RegulatedAndUnregulatedOperatingRevenue') and p.fiscal_period='FY' and p.end_date>='2024-01-01' group by 1,2,3,4), lat as (select company_id, max(end_date) e from t group by 1), s as (select t.* from t join lat on lat.company_id=t.company_id and lat.e=t.end_date) select s.company_id, s.end_date, s.period_id, (select string_agg(tag||'='||v::text||'@'||acc, '; ') from s s2 where s2.company_id=s.company_id) tags, (select cf.value from analytics.canonical_fact cf join analytics.canonical_concept cc on cc.id=cf.canonical_concept_id where cf.company_id=s.company_id and cf.period_id=s.period_id and cc.name='revenue' limit 1) stored from s where not exists (select 1 from s a join s b on a.company_id=b.company_id and a.tag<b.tag where a.company_id=s.company_id and abs(a.v-b.v)<=0.01*greatest(abs(a.v),abs(b.v))) group by s.company_id,s.end_date,s.period_id having count(*)>=2
```
(Latest FY is chosen per company inside the query as `max(end_date)` among the six tags. Run once per chunk; chunk id lists are in the appendix.)

## Frame (66 triggered company-periods, DATA-INFERRED)
company_id | ticker | FY end | stored revenue | tags filed (value) | accession
---|---|---|---|---|---
1086 | CVX | 2025-12-31 | 184,432,000,000 | 606=184432000000 Revenues=189031000000 | 0000093410-26-000078
4056 | COP | 2025-12-31 | 51,824,000,000 | 606=51824000000 Revenues=58944000000 | 0001163165-26-000009
1400 | NEE | 2025-12-31 | 25,800,000,000 | RegUnreg=27412000000 606Incl=25800000000 | 0000753308-26-000015
1421 | WELL | 2025-12-31 | 8,452,996,000 | 606=8452996000 Revenues=10838034000 | 0000766704-26-000010
1587 | FCX | 2025-12-31 | 25,186,000,000 | 606=25186000000 Revenues=25915000000 | 0000831259-26-000012
5023 | DUK | 2025-12-31 | 31,741,000,000 | RegUnreg=32237000000 606Incl=31741000000 | 0001326160-26-000014
3465 | MELI | 2025-12-31 | 20,335,000,000 | 606=20335000000 Revenues=28893000000 | 0001099590-26-000006
1150 | WMB | 2025-12-31 | 14,899,000,000 | 606=14899000000 Revenues=11950000000 | 0000107263-26-000006
2854 | AMT | 2025-12-31 | 935,900,000 | 606=935900000 Revenues=10644600000 | 0001053507-26-000035
2340 | KMI | 2025-12-31 | 15,202,000,000 | 606=15202000000 Revenues=16937000000 | 0001506307-26-000011
5947 | GM | 2025-12-31 | 167,971,000,000 | 606=167971000000 Revenues=185019000000 | 0001467858-26-000013
2951 | RSG | 2025-12-31 | 16,591,000,000 | 606=16591000000 Revenues=19027000000 | 0001060391-26-000094
638 | IMO | 2025-12-31 | 47,078,000,000 | 606Incl=38678000000 Revenues=47078000000 | 0000049938-26-000009
3030 | URI | 2025-12-31 | 3,695,000,000 | 606=3695000000 Revenues=16099000000 | 0001067701-26-000007
4283 | BE | 2025-12-31 | 2,001,614,000 | 606=2001614000 Revenues=2023994000 | 0001628280-26-006516
101 | LNG | 2025-12-31 | 19,464,000,000 | 606=19464000000 Revenues=19976000000 | 0000003570-26-000005
2860 | MPLX | 2025-12-31 | 9,726,000,000 | 606=9726000000 Revenues=12998000000 | 0001552000-26-000009
3331 | DVN | 2025-12-31 | 16,786,000,000 | 606=16786000000 Revenues=17188000000 | 0001193125-26-056485
140 | ADM | 2025-12-31 | 24,956,000,000 | 606=24956000000 Revenues=80269000000 | 0000007084-26-000011
1324 | PAYX | 2026-05-31 | 6,301,100,000 | 606=6301100000 Revenues=6512000000 | 0001193125-26-307785
2133 | NTAP | 2026-04-24 | 6,925,000,000 | 606=6925000000 Revenues=6237000000 | 0001193125-26-259683
3893 | CBRE | 2025-12-31 | 39,900,000,000 | 606=39900000000 Revenues=40550000000 | 0001138118-26-000005
2835 | CCI | 2025-12-31 | 215,000,000 | 606=215000000 Revenues=4264000000 | 0001051470-26-000016
4967 | SUNB | 2026-04-30 | 2,509,000,000 | 606=2509000000 Revenues=11154000000 | 0001628280-26-044888
4725 | EXR | 2025-12-31 | 129,476,000 | 606=129476000 Revenues=3377542000 | 0001289490-26-000011
1926 | PPL | 2025-12-31 | 9,170,000,000 | 606=9170000000 Revenues=9042000000 | 0000922224-26-000008
243 | STZ | 2026-02-28 | 9,139,000,000 | 606Excl=9139000000 606Incl=9755500000 | 0000016918-26-000011
2275 | NRG | 2025-12-31 | 30,347,000,000 | 606=30347000000 Revenues=30713000000 | 0001013871-26-000004
4016 | BG | 2025-12-31 | 16,944,000,000 | 606=16944000000 Revenues=70329000000 | 0001628280-26-009842
2515 | SBAC | 2025-12-31 | 244,498,000 | 606=244498000 Revenues=2815139000 | 0001034054-26-000002
1075 | SNA | 2026-01-03 | 4,709,300,000 | 606=4709300000 Revenues=5156100000 | 0000091440-26-000045
4903 | EVRG | 2025-12-31 | 5,705,100,000 | 606=5705100000 Revenues=5961600000 | 0001711269-26-000017
5693 | OVV | 2025-12-31 | 8,663,000,000 | 606=8663000000 Revenues=8908000000 | 0001193125-26-064309
1916 | ESS | 2025-12-31 | 9,381,000 | 606=9381000 Revenues=1887345000 | 0000920522-26-000003
3764 | TLN | 2025-12-31 | 2,518,000,000 | 606=2518000000 Revenues=2581000000 | 0001622536-26-000017
3024 | CNH | 2025-12-31 | 15,346,000,000 | 606=15346000000 Revenues=18095000000 | 0001567094-26-000006
622 | HAS | 2025-12-28 | 4,701,300,000 | 606=4701300000 Revenues=5365900000 | 0000046080-26-000011
3354 | CHTR | 2025-12-31 | 54,774,000,000 | 606Incl=889000000 Revenues=54774000000 | 0001091667-26-000017
217 | BF-A | 2026-04-30 | 3,928,000,000 | 606Excl=3928000000 606Incl=5082000000 | 0000014693-26-000024
1419 | DOC | 2025-12-31 | 603,989,000 | 606=603989000 Revenues=2822512000 | 0001628280-26-005044
5831 | AR | 2025-12-31 | 5,275,823,000 | 606Incl=5137234000 Revenues=5275823000 | 0001104659-26-013386
3885 | AHR | 2025-12-31 | 2,094,506,000 | 606=2094506000 Revenues=2260123000 | 0001193125-26-082692
1016 | UDR | 2025-12-31 | 11,361,000 | 606=11361000 Revenues=1712317000 | 0000074208-26-000013
335 | DDS | 2026-01-31 | 6,473,623,000 | 606=6473623000 Revenues=6563336000 | 0000028917-26-000006
1202 | RRC | 2025-12-31 | 2,988,164,000 | 606=2988164000 Revenues=3115515000 | 0001193125-26-067292
2368 | OGE | 2025-12-31 | 3,190,900,000 | 606=3190900000 Revenues=3260100000 | 0001193125-26-055414
1608 | FCFS | 2025-12-31 | 1,668,410,000 | 606=1668410000 Revenues=3661043000 | 0000840489-26-000032
353 | FLS | 2025-12-31 | 4,729,260,000 | 606=4729260000 Revenues=0 | 0000030625-26-000003
1397 | VICR | 2025-12-31 | 407,701,000 | 606=407701000 Revenues=452701000 | 0001193125-26-085102
3341 | CTRE | 2025-12-31 | 1,225,000 | 606=1225000 Revenues=476393000 | 0001628280-26-007664
3366 | PCTY | 2026-06-30 | 1,651,362,000 | 606=1651362000 Revenues=1771326000 | 0001591698-26-000069
4786 | VNOM | 2025-12-31 | 1,346,000,000 | 606=1346000000 Revenues=1395000000 | 0002074176-26-000010
1748 | UGI | 2025-09-30 | 7,147,000,000 | 606=7147000000 Revenues=7287000000 | 0000884614-25-000053
3070 | REXR | 2025-12-31 | 589,000 | 606=589000 Revenues=1003133000 | 0001571283-26-000006
712 | NFG | 2025-09-30 | 2,219,117,000 | 606=2219117000 Revenues=2277541000 | 0000070145-25-000039
2918 | IDA | 2025-12-31 | 1,746,972,000 | 606=1746972000 RegUnreg=1812997000 | 0001057877-26-000028
301 | TAP | 2025-12-31 | 13,040,300,000 | 606Excl=13040300000 606Incl=11140800000 | 0000024545-26-000006
2500 | MTDR | 2025-12-31 | 3,656,514,000 | 606=3656514000 Revenues=3696277000 | 0001520006-26-000002
1923 | SSRM | 2025-12-31 | 1,603,200,000 | 606=1603200000 Revenues=1629637000 | 0000921638-26-000035
5440 | LYFT | 2025-12-31 | 5,895,475,000 | 606=5895475000 Revenues=6316261000 | 0001628280-26-006960
1484 | M | 2026-01-31 | 21,764,000,000 | 606=21764000000 Revenues=22621000000 | 0001628280-26-021721
4869 | WEX | 2025-12-31 | 1,845,400,000 | 606=1845400000 Revenues=2660800000 | 0001309108-26-000010
1195 | VAL | 2025-12-31 | 11,900,000 | 606=11900000 Revenues=2369000000 | 0000314808-26-000029
1296 | MUR | 2025-12-31 | 2,689,845,000 | 606=2689845000 Revenues=2718823000 | 0001628280-26-011709
5389 | HR | 2025-12-31 | 28,215,000 | 606=28215000 Revenues=1180546000 | 0001360604-26-000018
3805 | BKH | 2025-12-31 | 2,286,200,000 | 606=2286200000 Revenues=2310000000 | 0001193125-26-046028

## The 40 sampled rows (statement figures FILING-CHECKED on the cited R-page; stored and tags DATA-INFERRED)
Units for the statement column are as printed on the page (M = millions, K = thousands); stored and tag values are in dollars. "Picked" = which family the stored value equals (606 = a RevenueFromContractWithCustomer tag, Revenues = the `Revenues` tag).

ticker | FY end | stored | tags filed (value) | statement total | accession | locator | picked | verdict | note
---|---|---|---|---|---|---|---|---|---
OVV | 2025-12-31 | 8,663,000,000 | 606=8663000000 Revenues=8908000000 | Total Revenues 8,908M | 0001193125-26-064309 | R2 (income statement R-page) | 606 | WRONG-SUBLINE | stored = "Revenues" 8,663M subline; labelled total adds other revenue
ESS | 2025-12-31 | 9,381,000 | 606=9381000 Revenues=1887345000 | Total revenues 1,887,345K | 0000920522-26-000003 | R5 (income statement R-page) | 606 | WRONG | 
PPL | 2025-12-31 | 9,170,000,000 | 606=9170000000 Revenues=9042000000 | Operating Revenues 9,042M | 0000922224-26-000008 | R2 (income statement R-page) | 606 | WRONG | stored 9,170M matches no line read
TLN | 2025-12-31 | 2,518,000,000 | 606=2518000000 Revenues=2581000000 | Operating revenues 2,581M | 0001622536-26-000017 | R3 (income statement R-page) | 606 | WRONG | stored 2,518M
CCI | 2025-12-31 | 215,000,000 | 606=215000000 Revenues=4264000000 | Net Revenues 4,264M | 0001051470-26-000016 | R5 (income statement R-page) | 606 | WRONG | stored 215M = services and other revenues
LNG | 2025-12-31 | 19,464,000,000 | 606=19464000000 Revenues=19976000000 | Revenues 19,976M | 0000003570-26-000005 | R3 (income statement R-page) | 606 | WRONG | stored 19,464M
HAS | 2025-12-28 | 4,701,300,000 | 606=4701300000 Revenues=5365900000 | Net revenues 4,701.3M | 0000046080-26-000011 | R5 (income statement R-page) | 606 | HIDDEN-CORRECT | only revenue line; stored = 606 tag; Revenues 5,365.9M not a statement line read
SUNB | 2026-04-30 | 2,509,000,000 | 606=2509000000 Revenues=11154000000 | Total revenues 11,154.0M | 0001628280-26-044888 | R5 (income statement R-page) | 606 | WRONG | stored 2,509M
COP | 2025-12-31 | 51,824,000,000 | 606=51824000000 Revenues=58944000000 | Total revenues and other income 61,548M (Sales and other operating revenues 58,944M) | 0001163165-26-000009 | R3 (income statement R-page) | 606 | WRONG | stored 51,824M matches neither
STZ | 2026-02-28 | 9,139,000,000 | 606Excl=9139000000 606Incl=9755500000 | Net sales 9,139.0M (Sales 9,755.5M less excise 616.5M) | 0000016918-26-000011 | R5 (income statement R-page) | 606 | HIDDEN-CORRECT | stored = net sales; gross Sales is a different line
FCX | 2025-12-31 | 25,186,000,000 | 606=25186000000 Revenues=25915000000 | Revenues 25,915M | 0000831259-26-000012 | R3 (income statement R-page) | 606 | WRONG | stored 25,186M
MUR | 2025-12-31 | 2,689,845,000 | 606=2689845000 Revenues=2718823000 | Total revenues and other income 2,718,823K (Total revenue from sales to customers 2,689,845K) | 0001628280-26-011709 | R5 (income statement R-page) | 606 | WRONG-SUBLINE | stored = customer-sales subtotal
PCTY | 2026-06-30 | 1,651,362,000 | 606=1651362000 Revenues=1771326000 | Total revenues 1,771,326K | 0001591698-26-000069 | R5 (income statement R-page) | 606 | WRONG | stored = Recurring and other revenue 1,651,362K
URI | 2025-12-31 | 3,695,000,000 | 606=3695000000 Revenues=16099000000 | Total revenues 16,099M | 0001067701-26-000007 | R5 (income statement R-page) | 606 | WRONG | stored 3,695M
PAYX | 2026-05-31 | 6,301,100,000 | 606=6301100000 Revenues=6512000000 | Total revenue 6,512.0M (Total service revenue 6,301.1M) | 0001193125-26-307785 | R2 (income statement R-page) | 606 | WRONG-SUBLINE | stored = service revenue subtotal
WEX | 2025-12-31 | 1,845,400,000 | 606=1845400000 Revenues=2660800000 | Total revenues 2,660.8M | 0001309108-26-000010 | R3 (income statement R-page) | 606 | WRONG | stored 1,845.4M
ADM | 2025-12-31 | 24,956,000,000 | 606=24956000000 Revenues=80269000000 | Revenues 80,269M | 0000007084-26-000011 | R3 (income statement R-page) | 606 | WRONG | stored 24,956M
CHTR | 2025-12-31 | 54,774,000,000 | 606Incl=889000000 Revenues=54774000000 | REVENUES 54,774M | 0001091667-26-000017 | R5 (income statement R-page) | Revenues | HIDDEN-CORRECT | stored = Revenues tag; 606-Incl tag (889M) is a small piece
MPLX | 2025-12-31 | 9,726,000,000 | 606=9726000000 Revenues=12998000000 | Total revenues and other income 12,998M | 0001552000-26-000009 | R3 (income statement R-page) | 606 | WRONG | stored 9,726M
LYFT | 2025-12-31 | 5,895,475,000 | 606=5895475000 Revenues=6316261000 | Revenue 6,316,261K | 0001628280-26-006960 | R5 (income statement R-page) | 606 | WRONG | stored 5,895,475K
REXR | 2025-12-31 | 589,000 | 606=589000 Revenues=1003133000 | TOTAL REVENUES 1,003,133K | 0001571283-26-000006 | R5 (income statement R-page) | 606 | WRONG | stored 589K
NEE | 2025-12-31 | 25,800,000,000 | RegUnreg=27412000000 606Incl=25800000000 | OPERATING REVENUES 27,412M | 0000753308-26-000015 | R3 (income statement R-page) | 606 | WRONG-SUBLINE | stored = 606-Incl 25,800M (customer revenue)
FCFS | 2025-12-31 | 1,668,410,000 | 606=1668410000 Revenues=3661043000 | Total revenue 3,661,043K | 0000840489-26-000032 | R5 (income statement R-page) | 606 | WRONG | stored = retail merchandise sales 1,668,410K
NFG | 2025-09-30 | 2,219,117,000 | 606=2219117000 Revenues=2277541000 | Operating Revenues 2,277,541K | 0000070145-25-000039 | R3 (income statement R-page) | 606 | WRONG | stored 2,219,117K
MTDR | 2025-12-31 | 3,656,514,000 | 606=3656514000 Revenues=3696277000 | Total revenues 3,696,277K (Revenues subline 3,656,514K) | 0001520006-26-000002 | R5 (income statement R-page) | 606 | WRONG-SUBLINE | stored = subline
KMI | 2025-12-31 | 15,202,000,000 | 606=15202000000 Revenues=16937000000 | Revenues 16,937M | 0001506307-26-000011 | R3 (income statement R-page) | 606 | WRONG | stored 15,202M
SBAC | 2025-12-31 | 244,498,000 | 606=244498000 Revenues=2815139000 | Total revenues 2,815,139K | 0001034054-26-000002 | R4 (income statement R-page) | 606 | WRONG | stored 244,498K
BF-A | 2026-04-30 | 3,928,000,000 | 606Excl=3928000000 606Incl=5082000000 | Net sales 3,928M (Sales 5,082M gross) | 0000014693-26-000024 | R3 (income statement R-page) | 606 | HIDDEN-CORRECT | stored = net sales (606-Excl)
EXR | 2025-12-31 | 129,476,000 | 606=129476000 Revenues=3377542000 | Total revenues 3,377,542K | 0001289490-26-000011 | R5 (income statement R-page) | 606 | WRONG | stored 129,476K
AR | 2025-12-31 | 5,275,823,000 | 606Incl=5137234000 Revenues=5275823000 | Total revenue 5,275,823K | 0001104659-26-013386 | R4 (income statement R-page) | Revenues | HIDDEN-CORRECT | stored = Revenues tag
CTRE | 2025-12-31 | 1,225,000 | 606=1225000 Revenues=476393000 | Total revenues 476,393K | 0001628280-26-007664 | R5 (income statement R-page) | 606 | WRONG | stored 1,225K
WELL | 2025-12-31 | 8,452,996,000 | 606=8452996000 Revenues=10838034000 | Total revenues 10,838,034K | 0000766704-26-000010 | R4 (income statement R-page) | 606 | WRONG | stored = resident fees and services 8,452,996K
CNH | 2025-12-31 | 15,346,000,000 | 606=15346000000 Revenues=18095000000 | Total Revenues 18,095M (Net sales 15,346M) | 0001567094-26-000006 | R3 (income statement R-page) | 606 | WRONG-SUBLINE | stored = net sales subtotal
BE | 2025-12-31 | 2,001,614,000 | 606=2001614000 Revenues=2023994000 | Total revenue 2,023,994K | 0001628280-26-006516 | R5 (income statement R-page) | 606 | WRONG | stored 2,001,614K
TAP | 2025-12-31 | 13,040,300,000 | 606Excl=13040300000 606Incl=11140800000 | Net sales 11,140.8M (Sales 13,040.3M gross) | 0000024545-26-000006 | R3 (income statement R-page) | 606 | WRONG | stored = gross Sales incl. excise tax
AMT | 2025-12-31 | 935,900,000 | 606=935900000 Revenues=10644600000 | Total operating revenues 10,644.6M | 0001053507-26-000035 | R5 (income statement R-page) | 606 | WRONG | stored 935.9M
EVRG | 2025-12-31 | 5,705,100,000 | 606=5705100000 Revenues=5961600000 | OPERATING REVENUES 5,961.6M | 0001711269-26-000017 | R3 (income statement R-page) | 606 | WRONG-SUBLINE | stored 5,705.1M = 606 tag
VICR | 2025-12-31 | 407,701,000 | 606=407701000 Revenues=452701000 | Total net revenues 407,701K (Total net revenues and patent litigation settlement 452,701K) | 0001193125-26-085102 | R4 (income statement R-page) | 606 | HIDDEN-CORRECT | stored = Total net revenues line; settlement is a separate line
RSG | 2025-12-31 | 16,591,000,000 | 606=16591000000 Revenues=19027000000 | Revenue 16,591,000K | 0001060391-26-000094 | R5 (income statement R-page) | 606 | HIDDEN-CORRECT | stored = 606 tag
OGE | 2025-12-31 | 3,190,900,000 | 606=3190900000 Revenues=3260100000 | Operating revenues 3,260.1M (Revenues from contracts 3,190.9M) | 0001193125-26-055414 | R2 (income statement R-page) | 606 | WRONG-SUBLINE | stored = contract-revenue subline

## Counts (FILING-CHECKED rows, n = 40)
- HIDDEN-CORRECT 7 of 40 = 17.5%, Wilson 95% interval 8.7% to 32.0% (normal approximation would give about 5.7% to 29.3%): HAS, STZ, CHTR, BF-A, AR, VICR, RSG.
- HIDDEN-WRONG 33 of 40 = 82.5%: 25 plain WRONG, 8 WRONG-SUBLINE (OVV, MUR, PAYX, NEE, MTDR, CNH, EVRG, OGE). If a reader counts the 8 sub-line rows as defensible, hidden-correct rises to 15 of 40 = 37.5% (Wilson 24.2% to 53.0%).
- UNDECIDABLE 0 of 40.
- Split by what stored picked: stored equals a 606 tag in 38 rows: 5 correct (13.2%, Wilson 5.8% to 27.3%), 33 wrong. Stored equals `Revenues` in 2 rows: 2 correct (CHTR, AR); two rows is too few for an interval (Wilson lower bound about 34%). No sampled row picked `RegulatedAndUnregulatedOperatingRevenue` as stored.
- Sampling note: 40 of 66 frame rows were drawn (61%), so the interval above is conservative (no finite-population correction applied).
- Pattern seen in the 33 wrong rows (FILING-CHECKED, descriptive only): in many, stored is a single sub-line of the statement (a segment, a service line, a lease line) of a total that the `Revenues` tag does carry (for example REXR 589K vs 1,003,133K total, SBAC 244,498K vs 2,815,139K, CCI 215M vs 4,264M).

## Limits
- Latest 10-K fiscal-year period only; the 10-Q quarter was not done (cost). Hidden-correct share for quarters is unmeasured.
- Frame = top-1000 shard companies, not the full 5,000-company population; SIC 6000-6411 excluded by my rule, so REITs and similar remain (several frame rows are REITs; the guard's own bank exclusion may differ). 986 minus 144 financial = 842.
- Tag list is my assumption; including or excluding tags (for example `SalesRevenueNet`, `Revenues` of value 0 as in FLS, which is in the frame but was not sampled) changes the frame size.
- `core.fact` may hold facts for more than one filing per period; I took `max(value)` per tag, which can pick a restated or different-context figure; "same context" was approximated by the same `period_id`, not checked against XBRL dimensions.
- Statement reads use `sec_rpages.rows()` which keeps only the first four cells of each row, and the first value cell is sometimes blank when a footnote column exists; I read the 12-month column in the 2025 or 2026 position and sanity-checked against the prior-year columns, but did not re-read each value in the XBRL instance. One reader, no second parser.
- A few multi-registrant filings (EVRG, PPL, NEE) show parent and subsidiary blocks; I used the first (parent) block. EVRG was confirmed on the parent statement (R3).
- Judgment calls: Net sales vs gross Sales (STZ, BF-A counted correct, TAP counted wrong because stored equals gross Sales while Net sales is 11,140.8M); VICR counted correct because stored equals its "Total net revenues" line even though a following line adds a patent settlement. Different judgments move 3 rows.
- Stored value is `canonical_fact` revenue; `revenue_sanity_resolved` was not checked separately.

## Appendix: chunk id lists (85 chunks, 842 company_ids)
```
2733,3,9,4,2328,5050,5116,4945,666,1321
1134,85,5351,5718,1164,3932,2848,643,1086,4969
1857,1649,279,5203,1042,1182,251,1263,608,134
5761,1236,3007,3083,5058,1123,1105,1104,4015,1207
2726,4841,3418,3398,1213,644,2683,3569,1732,128
5261,4227,1358,76,1516,1028,4056,1196,1117,683
4630,1030,2124,1400,1421,1158,1190,1359,2852,207
2540,5480,3886,2787,5943,2376,2529,1975,1700,684
1413,4077,4447,215,3155,1025,3639,687,1145,2725
1949,2717,171,1185,303,671,1583,3982,2929,2007
1653,5941,2785,1587,3485,1554,3240,1488,5023,2832
607,3465,1567,1178,1595,367,5338,105,1534,1740
1817,2956,2854,4553,1150,700,1323,2944,1686,1560
3343,3510,5698,1068,361,2961,4398,4095,3291,637
706,241,1379,283,2340,5947,1750,3849,3898,1059
1253,318,4057,1823,2951,327,4541,2798,1436,89
2985,3918,638,3030,1759,4432,1176,4283,1492,5607
4791,5577,101,4586,1316,2606,2860,1544,1021,5762
1013,2765,2576,3538,3478,1292,3331,1629,4744,2
3695,3001,5063,1335,4115,5634,195,1677,4655,417
1102,2553,5632,3470,3895,329,5170,1427,3346,1983
1550,1009,2432,5779,5069,1974,8,1166,5606,1555
4114,1670,2025,3587,1695,1369,4619,2087,4929,5735
2776,5969,2641,5150,1577,140,2133,1324,1095,3596
1714,1733,3893,2031,2107,2921,1737,3831,659,5893
2385,3739,1462,1449,4904,2572,654,2081,2165,2835
1543,2476,628,2396,1985,1699,3908,375,2353,4935
5663,1673,4994,2895,4239,3365,5511,1142,2151,3048
3661,1113,2926,4081,4237,4967,4526,5568,2370,4719
1897,341,10,4725,1310,1825,3385,1355,3940,620
3439,3283,629,4530,2286,5585,1144,5874,1973,5747
2487,3800,345,1926,3814,4197,2665,3710,4814,2378
1834,1913,1337,1382,5721,2335,1498,2793,5875,3880
1191,5771,4813,1981,2542,632,3907,4627,3652,2198
5380,1038,4017,2706,1972,5010,645,347,2564,1840
3215,5822,243,3733,1717,3600,4294,4090,2275,5132
5421,3713,1804,5347,4066,713,1343,5691,1563,3489
1022,3132,3522,1658,1647,4425,5497,2128,4225,4016
3607,1055,5306,5563,2169,2515,5716,4220,1415,1153
1083,4903,4212,5693,1075,373,5713,249,4112,4514
319,3873,612,1917,3703,4990,5804,646,3869,1004
3098,1170,2191,610,1227,4232,4316,5542,1712,1589
2011,1916,1898,4330,2801,626,365,3325,4926,3315
1565,3764,183,1955,1538,3174,648,3113,4947,2703
3000,5948,1054,4574,1168,5002,1841,5161,1978,2746
4380,3700,1716,1112,225,3338,4036,2511,2440,3539
1643,678,1654,3856,3260,2336,2802,1874,1630,3024
3473,667,2865,1147,5905,2580,3354,1087,2345,622
4439,1669,2607,1776,1891,4032,2699,4385,231,1875
217,5038,1074,7,3589,1863,4297,3171,173,1067
617,1469,2904,1419,193,1171,3312,2658,5738,5257
2889,1388,3913,1691,1163,4972,2813,1454,1064,3284
1416,2092,682,3053,4337,1483,4223,5307,1160,3205
103,2475,5580,1947,1486,3736,3309,1850,5831,2982
1805,705,1862,3455,3885,1031,3675,5212,3164,3234
5724,3126,1610,5971,3353,4403,1138,2971,1896,631
5022,3187,1016,1066,4720,1229,720,1274,147,4434
1444,1257,2273,2259,4344,1696,2788,5430,635,2162
275,4474,3434,2998,5802,2763,2052,335,3998,2491
4406,3745,5678,1049,1308,343,4668,1202,3099,1842
1347,3660,2708,1789,2368,2528,3966,4278,5018,3774
3520,1778,4833,1899,2073,201,1946,1365,2647,2569
4086,1821,1793,4906,1904,4689,1608,3406,5750,391
2520,1056,1636,3955,3256,1854,1397,353,4230,5880
5461,4172,1588,5526,4795,3366,2246,3614,3341,4188
2970,5494,1128,142,3336,1254,2518,3214,1027,4786
2088,3582,1903,5514,1063,2111,1748,5727,3176,3070
3220,3092,1072,1870,1639,2602,1495,605,4455,5944
4613,1395,1091,4691,703,2625,1439,1718,1816,5237
123,5869,4186,5457,1925,1107,3928,4883,2965,5830
702,5821,712,2918,4055,1684,3238,3057,4124,4658
301,1876,175,2584,4465,2549,1073,3249,4479,2149
1725,1914,5222,1467,655,3678,287,4491,2500,2059
1690,1892,145,3087,5207,4255,3496,95,3690,1992
3922,2508,2983,699,1512,2409,1412,2034,295,1177
1298,4596,5149,2371,261,3463,3969,2964,3213,4981
1871,2517,1131,2332,2407,1923,5119,1675,4693,5544
4005,4067,5574,4637,5037,5289,5440,2017,4009,5904
1484,3976,3545,5686,4869,3730,3956,5500,4117,2751
5448,2139,5810,3512,3028,1830,1456,4707,1568,3118
4787,4706,205,5389,4647,1296,4082,1195,2003,1611
1672,1041,235,5133,1763,4916,3149,3351,4100,606
3805,4044,1103,4362,1640,647,4860,269,1181,2271
5103,1772,3967,3010,5029,1867,4162,3067,5396,2441
5164,1100
```
