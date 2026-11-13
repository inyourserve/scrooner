set local statement_timeout='120s';
with f as (select distinct on (cik) id, cik, period from fsn.filing where form='10-K' and cik in (<CIKS>) order by cik, period desc),
t as (select id, tag from fsn.tag where tag in ('InvestmentIncomeInterest','InterestIncomeOther','InvestmentIncomeInterestAndDividend','InterestAndOtherIncome','InvestmentIncomeNet','AmortizationOfIntangibleAssets','AdjustmentForAmortization','IncomeTaxesPaidNet','IncomeTaxesPaid','InterestPaidNet','InterestPaid','ShareBasedCompensation','AllocatedShareBasedCompensationExpense','CommonStockDividendsPerShareDeclared','CommonStockDividendsPerShareCashPaid','WeightedAverageNumberOfSharesOutstandingBasic','WeightedAverageNumberOfDilutedSharesOutstanding','WeightedAverageNumberOfShareOutstandingBasicAndDiluted','CommonStockSharesOutstanding','InterestExpense','InterestExpenseNonoperating','InterestExpenseDebt','Goodwill','ResearchAndDevelopmentExpense','LongTermDebt','LongTermDebtCurrent','LongTermDebtNoncurrent','FinanceLeaseLiability','OperatingLeaseLiability'))
select f.cik, string_agg(distinct t.tag || '=' || v.qtrs || ':' || round(v.value, 4)::text, '|') facts
from f join fsn.value v on v.filing_id = f.id join t on t.id = v.tag_id
where v.dim_id = 0 and v.coreg = '' and v.iprx = 0 and v.ddate = f.period
group by f.cik;
