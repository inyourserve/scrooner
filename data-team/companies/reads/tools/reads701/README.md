# Reader used for ranks 701-800 (FSN expert session)

`read2.py <outdir> <db_export.json> <ranks.json> <rank>...`: index, statement reports and FSN line tags from our DB (fsn.filing, fsn.report, fsn.line);
R pages from sec.gov (statements only, 0.4 req/s, SEC_USER_AGENT from the environment); companyfacts from data.sec.gov.
Rulings applied (Dhairya 2026-11-12): shares_outstanding = CommonStockSharesOutstanding at the BS date (never the dei cover); a wider receivables tag is AR only as the single receivables line; operating_expenses never includes cost of revenue (printed total excluding COGS, else the component sum of every line between GP and OI tied to GP - OI; a total including COGS is combined); eras FY2015 to latest for every data point (FY2015 10-K always opened). Every batch is hand-checked against the shared reader (tools/docmap.py) and each difference is decided on the R page.
