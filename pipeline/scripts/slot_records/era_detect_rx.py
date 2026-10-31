"""The candidate net shared by era_detect.py and the face-admission checks
(kept here so era_detect.py, a script with top-level side effects, is not
imported)."""
import re

DEBT_RX = re.compile(
    r"Debt|Borrow|Loan|NotesPayable|NotesAndLoans|CommercialPaper|"
    r"Lines?OfCredit|Lease|Convertible|FinanceObligation"
)
LABEL_RX = re.compile(
    r"debt|borrow|loan|notes? payable|lease|commercial paper|credit facilit|convertible",
    re.I,
)
EXCLUDE_RX = re.compile(
    r"PreferredStock|CommonStock|Equity|TreasuryStock|RetainedEarnings|"
    r"AccumulatedOtherComprehensive|CommitmentsAndContingencies|"
    r"DebtSecurities|SecuritiesBorrowed|OtherThanLongtermDebt|"
    r"TemporaryEquity|RedeemableNoncontrolling|RightOfUseAsset"
)
