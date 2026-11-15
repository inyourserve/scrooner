-- Read-only input for resolve_all.py: consolidated facts at each 10-K's own column (qtrs 0/4) for every element family
-- the role rules name (rules/roles.csv), batched by CIK. Built and split by tools/standard_inputs.py (the placeholders below).
-- Output rows (accession, vals, mvals, cvals):
--   vals  'tag|qtrs|value~...'            undimensioned own-period facts (notefacts.json); accretion facts (%Accretion%) ride along:
--                                         the D&A accretion-evidence rule (resolve_is.accretion_reported) reads them from here.
--   mvals 'tag|qtrs|value|segments~...'   own-period facts with exactly ONE dimension member, on a statement line (face, incl.
--                                         parenthetical); axes EquityComponents (equity-statement column), RelatedPartyTransactionsByRelatedParty
--                                         (NonrelatedParty / RelatedParty: COP AP) and Scenario (ORCL comprehensive income). memberfacts.json.
--   cvals 'tag|qtrs|value|ddate~...'      undimensioned facts of the filing's earlier columns (FY-1, FY-2), face or note, incl. parenthetical
--                                         per-share lines (LLY DPS 2016 sits in the FY2018 equity parenthetical). compfacts.json.
--   zlines 'tag|stmt|report|line|label~...' statement lines of the family elements with no own-period fact in any dimension but
--                                         values in other columns: printed dash / zero evidence (ruling 2026-11-14).
--   mvals also carries AmortizationOfIntangibleAssets by income-statement location (CSCO prints only the opex part on the face) and
--   CostOf* by ProductOrService member on an IS line (GE, RTX, TMO, TMUS print product and service cost lines with members only), and
--   capex elements by ConsolidatedEntities (VLO: lines carrying entity members only; served when they tie to the investing total),
--   interest-expense elements by ProductOrService on an IS line (CAT: Financial Products / all other), and
--   PaymentsForRepurchaseOfCommonStock by ClassOfStock (V 2016: the CF line carries class members only), and
--   revenue elements by ProductOrService member on an IS line (DE 'Other Income', WELL 'Other income' rows: resolve_is.member_row_value).
-- Families: the element regex of rules/roles.csv plus the balance-sheet / cash-flow family modules; mvals also takes the AP/AR names.
set statement_timeout='55s';
with rx as (select '^(/* element families from rules/roles.csv */)$'::text r),
fl as (select id, accession, period from fsn.filing where company_id in (select g.company_id from fsn.filing g where g.cik::bigint in (/* CIKs */)) and form in ('10-K','20-F','40-F')
  and (cik::bigint in (/* CIKs */) or not exists (select 1 from fsn.filing s where s.company_id=fsn.filing.company_id and s.period=fsn.filing.period and s.form in ('10-K','20-F','40-F') and s.cik::bigint in (/* CIKs */))) and period>='2014-06-01'),
tg as (select id, tag from fsn.tag where not custom and (tag ~ (select r from rx) or tag like '%Accretion%')),
tgm as (select id, tag from fsn.tag where not custom and (tag ~ (select r from rx) or tag ~ '^(AccountsPayable|AccountsReceivable|AccountsAndNotesReceivable|Receivables|DueTo|DueFrom)' or tag = 'NotesReceivableNet' or tag = 'PaymentsForRepurchaseOfCommonStock' or tag ~ '^(PaymentsToAcquirePropertyPlantAndEquipment|PaymentsToAcquireProductiveAssets|PaymentsForCapitalImprovements|PaymentsToAcquireOtherPropertyPlantAndEquipment|PaymentsForConstructionInProcess)$' or tag ~ '^(InterestExpense\w*|InterestAndDebtExpense|FinancingInterestExpense)$' or tag ~ '^(Revenues|RevenueFromContractWithCustomer\w*|SalesRevenueNet)$')),
own as (select fl.accession a, string_agg(concat_ws('|',t.tag,v.qtrs,v.value::text),'~') vals
  from fsn.value v join fl on fl.id=v.filing_id join tg t on t.id=v.tag_id
  where v.dim_id=0 and coalesce(v.coreg,'')='' and v.ddate=fl.period and v.qtrs in (0,4) and v.value is not null
  group by 1),
mem as (select fl.accession a, string_agg(concat_ws('|',t.tag,v.qtrs,v.value::text,d.segments),'~') mvals
  from fsn.value v join fl on fl.id=v.filing_id join tgm t on t.id=v.tag_id join fsn.dim d on d.id=v.dim_id
  where v.dim_id<>0 and coalesce(v.coreg,'')='' and v.ddate=fl.period and v.qtrs in (0,4) and v.value is not null
    and (d.segments ~ '^(EquityComponents|RelatedPartyTransactionsByRelatedParty|Scenario)=[^;=]+;$'
         or (t.tag='AmortizationOfIntangibleAssets' and d.segments ~ '^(IncomeStatementLocation|StatementOfIncomeLocationBalance|FiniteLivedIntangibleAssetsByMajorClass)=[^;=]+;$')
         or (t.tag='PaymentsForRepurchaseOfCommonStock' and v.qtrs=4 and d.segments ~ '^ClassOfStock=[^;=]+;$')
         or (t.tag='NotesReceivableNet' and v.qtrs=0 and d.segments ~ '^\w*FinancingReceivable\w*=[^;=]+;$')   -- AXP 'Financing receivables, net' by class (ruling 2026-11-16)
         or (t.tag ~ '^(PaymentsToAcquirePropertyPlantAndEquipment|PaymentsToAcquireProductiveAssets|PaymentsForCapitalImprovements|PaymentsToAcquireOtherPropertyPlantAndEquipment|PaymentsForConstructionInProcess)$' and v.qtrs=4 and d.segments ~ '^ConsolidatedEntities=[^;=]+;$')
         or (t.tag ~ '^(CostOf|Revenues$|RevenueFromContractWithCustomer|SalesRevenueNet$|InterestExpense|InterestAndDebtExpense$|FinancingInterestExpense$)' and v.qtrs=4 and d.segments ~ '^ProductOrService=[^;=]+;$'
             and exists (select 1 from fsn.line l2 where l2.filing_id=fl.id and l2.tag_id=v.tag_id and l2.stmt='IS')))
    and exists (select 1 from fsn.line l where l.filing_id=fl.id and l.tag_id=v.tag_id)
  group by 1),
cmp as (select fl.accession a, string_agg(concat_ws('|',t.tag,v.qtrs,v.value::text,v.ddate::text),'~') cvals
  from fsn.value v join fl on fl.id=v.filing_id join tg t on t.id=v.tag_id
  where v.dim_id=0 and coalesce(v.coreg,'')='' and v.ddate<fl.period and v.ddate>=fl.period-interval '3 years 2 months' and v.qtrs in (0,4) and v.value is not null
  group by 1),
zl as (select fl.accession a, string_agg(concat_ws('|',t.tag,l.stmt,l.report,l.line,translate(coalesce(l.plabel,''),'|~','/-')),'~') zlines
  from fl join fsn.line l on l.filing_id=fl.id and l.stmt in ('BS','IS','CF') join tg t on t.id=l.tag_id
  where not exists (select 1 from fsn.value v where v.filing_id=fl.id and v.tag_id=l.tag_id and v.ddate=fl.period)
    and exists (select 1 from fsn.value v where v.filing_id=fl.id and v.tag_id=l.tag_id and v.ddate<>fl.period)
  group by 1)
select fl.accession a, own.vals, mem.mvals, cmp.cvals, zl.zlines
from fl left join own on own.a=fl.accession left join mem on mem.a=fl.accession left join cmp on cmp.a=fl.accession left join zl on zl.a=fl.accession
where own.vals is not null or mem.mvals is not null or cmp.cvals is not null or zl.zlines is not null;
