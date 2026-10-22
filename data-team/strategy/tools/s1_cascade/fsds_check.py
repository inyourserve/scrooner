import csv,pickle,re,collections,sys
sys.path.insert(0,'.')
csv.field_size_limit(10**9)
X='/private/tmp/claude-501/-Users-vikash-scrooner/99c20ae4-2938-4dd5-8ec6-924194f63d67/scratchpad/fsds/x/'
res=pickle.load(open('final.pkl','rb'))
from agg import bucket
ciks={}
for r in csv.DictReader(open('/Users/vikash/scrooner/data-team/strategy/data/group_assignment_draft.csv')): ciks[int(r['cik'])]=int(r['company_id'])
best={}
for r in csv.DictReader(open(X+'sub.txt'),delimiter='\t'):
    if r['form'] not in('10-K','10-Q'): continue
    ck=int(r['cik'])
    if ck not in ciks: continue
    key=(r['form']=='10-K', r['filed'])   # prefer 10-K, then latest
    if ck not in best or key>best[ck][0]: best[ck]=(key,r['adsh'])
adsh2c={v[1]:ciks[k] for k,v in best.items()}
print('cohort companies with FSDS filing:',len(adsh2c))
pre=collections.defaultdict(list)
for r in csv.DictReader(open(X+'pre.txt'),delimiter='\t',quoting=csv.QUOTE_NONE):
    c=adsh2c.get(r['adsh'])
    if c: pre[c].append((r['stmt'],r['tag'],r['plabel']))
M=collections.defaultdict(set)
for l in open('mapped_tags.tsv'):
    f=l.rstrip('\n').split('\t'); M[f[0]].add(f[2])
PL={
 'capex':('CF',r'^(PaymentsToAcquire(PropertyPlantAndEquipment|ProductiveAssets|OtherPropertyPlantAndEquipment|RealEstate|Software|OilAndGasPropertyAndEquipment|ImprovementsAndEquipment)|PaymentsForCapitalImprovements|PaymentsToDevelopSoftware|PaymentsToAcquireAndDevelopRealEstate|PaymentsToAcquireInvestmentsRealEstate)$'),
 'dividends_paid':('CF',r'^(PaymentsOfDividends|PaymentsOfOrdinaryDividends|PaymentsOfDividendsCommonStock|PaymentsOfCapitalDistribution|PaymentsOfDividendsPreferredStockAndPreferenceStock)$'),
 'dividends_per_share':('IS|EQ|CF|CI',r'^(CommonStockDividendsPerShareDeclared|CommonStockDividendsPerShareCashPaid|DistributionMadeToLimitedPartnerDistributionsPaidPerUnit)$'),
 'share_buybacks':('CF|EQ',r'^(PaymentsForRepurchaseOfCommonStock|PaymentsForRepurchaseOfEquity|StockRepurchasedDuringPeriodValue|StockRepurchasedAndRetiredDuringPeriodValue|PaymentsForRepurchaseOfCommonStockAndTaxWithholdings)$'),
 'interest_expense':('IS',r'^(InterestExpense|InterestExpenseDebt|InterestAndDebtExpense|InterestExpenseNonoperating|InterestExpenseLongTermDebt|InterestExpenseOperating|InterestExpenseRelatedParty|InterestExpenseOther|InterestExpenseDebtExcludingAmortization)$'),
 'depreciation_and_amortization':('CF',r'^(DepreciationDepletionAndAmortization|DepreciationAndAmortization|DepreciationAmortizationAndAccretionNet|Depreciation|DepreciationAmortizationAndOther|AmortizationOfIntangibleAssets|DepreciationNonproduction|DepreciationAndAmortizationOther)$'),
 'cfo':('CF',r'^NetCashProvidedByUsedInOperatingActivities(ContinuingOperations)?$'),
 'sbc':('CF|IS',r'^(ShareBasedCompensation|AllocatedShareBasedCompensationExpense|RestrictedStockExpense|ShareBasedCompensationExpense|StockIssuedDuringPeriodValueShareBasedCompensation)$'),
 'operating_income':('IS',r'^OperatingIncomeLoss$'),
 'income_before_tax':('IS',r'^IncomeLossFromContinuingOperationsBeforeIncomeTaxes'),
 'sga_expense':('IS',r'^(SellingGeneralAndAdministrativeExpense|GeneralAndAdministrativeExpense|SellingGeneralAndAdministrativeExpensesIncluding.*)$'),
 'total_debt':('BS',r'^(LongTermDebt|LongTermDebtNoncurrent|LongTermDebtCurrent|DebtCurrent|NotesPayable|ConvertibleNotesPayable|SeniorNotes|LongTermNotesPayable|ConvertibleDebtNoncurrent|LongTermLineOfCredit|DebtLongtermAndShorttermCombinedAmount|LineOfCredit|NotesPayableCurrent|SecuredDebt|UnsecuredDebt|LongTermDebtAndCapitalLeaseObligations|ConvertibleDebt|ConvertibleDebtCurrent|NotesAndLoansPayable|LongTermNotesAndLoans)$'),
 'interest_income':('IS',r'^(InvestmentIncomeInterest|InterestIncomeOther|InterestAndOtherIncome|InvestmentIncomeNet|InterestIncomeOperating|InvestmentIncomeInterestAndDividend|InterestAndDividendIncomeOperating)$'),
 'revenue':('IS',r'^(Revenues|RevenueFromContractWithCustomer.*|SalesRevenueNet|RevenuesNetOfInterestExpense|RegulatedAndUnregulatedOperatingRevenue)$'),
}
UNEV=('UNEVIDENCED','FIX_vocab_candidate_tags')
pairs=collections.defaultdict(lambda:collections.defaultdict(set))
for a in res:
    for leaf,cz in a['causes']:
        b=bucket(cz)
        l=leaf
        if l in('total_debt_split','total_debt_resolved'): l='total_debt'
        if l.endswith('_resolved') and l[:-9] in PL: l=l[:-9]
        if b=='UNEVIDENCED': pairs[l][('stopped' if cz.startswith('PERIOD') else 'blank_never')].add(a['company_id'])
        elif cz.startswith('FIX_vocab'): pairs[l]['blank_vocab_candidates'].add(a['company_id'])
        elif cz.startswith('PERIOD') and b=='FIX' and 'candidate' in cz: pairs[l]['stopped_with_newer_candidate'].add(a['company_id'])
rows=[]
for l,d in sorted(pairs.items(),key=lambda x:-sum(len(v) for v in x[1].values())):
    if l not in PL: continue
    st,pat=PL[l]; rx=re.compile(pat); stx=re.compile('^('+st+')$')
    for k,cs in d.items():
        n=0; mp=0; ot=0; none=0; tags=collections.Counter()
        for c in cs:
            if c not in pre: continue
            n+=1
            tg=[t for s,t,pl in pre[c] if stx.match(s) and rx.search(t)]
            if any(t in M[l] for t in tg): mp+=1
            elif tg: ot+=1; tags[tg[0]]+=1
            else: none+=1
        rows.append((l,k,len(cs),n,mp,ot,none,tags.most_common(3)))
for r in rows: print(r)
pickle.dump(rows,open('fsds_rows.pkl','wb'))
