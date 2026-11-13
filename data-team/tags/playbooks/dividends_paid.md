# Playbook: dividends_paid_resolved

Method: [README](README.md). Measured 2026-11-09 on 632 latest 10-Ks, DATA-INFERRED (FSN rows). Rules today: `cf.dividends_paid_common_tag@1..3` (founder ruling 2026-11-01: "dividends and dividend equivalents" is common; no Verifier draw yet per the rule evidence).

## 1. Mapped: 455 of 632

| Rank | Tag | Companies |
|---|---|---|
| 1 | `PaymentsOfDividendsCommonStock` | 273 |
| 2 | `PaymentsOfDividends` | 157 |
| 3 | `PaymentsOfOrdinaryDividends` | 25 |

## 2. The 177 gap companies
Most of them pay no dividend (no dividend line on the CF face). That is a valid absent line, and the cash-flow lane's absent-line reasons cover it. Unmapped dividend-shaped CF lines in the 632:

| Tag | Companies | Labels | Read |
|---|---|---|---|
| `PaymentsOfCapitalDistribution` | 7 (+ some with no line_map) | "Common dividends paid" (947484), "Distributions" (1383650), "Distributions to common stockholders" (1581068), "Distributions paid to preferred shareholders, common shareholders, restricted share unitholders and unvested LTIP unitholders" (1393311), "Distributions to partners" (2046386), "Dividends to Diamondback" (2074176, a parent), "Distributions to members of Pla-Fit Holdings" (1637207: an Up-C, NCI), "Distributions to or on behalf of Symbotic Holdings LLC partners" (1837240: Up-C, NCI) | **mixed perimeter**: REIT/partnership common distributions, but also Up-C member distributions (NCI) and payments to a parent. Never safe as one tag; the label decides |
| `PaymentsOfDividendsMinorityInterest` | 2 | "Dividends paid to non-controlling interests" | NCI: never common dividends |
| custom `DividendsOrSubcoDistributionsPaid` (2012383), `DividendsPaidToNonControllingInterests` (818686) | 1 each | | first: a combined common+subco perimeter; second: NCI |

## 3. Structural signature
A financing-block CF line (calc child of `NetCashProvidedByUsedInFinancingActivities`, weight −1), label matching `dividend|distribution` and naming common/ordinary shareholders or no class at all, and NOT matching `preferred|noncontrolling|minority|subsidiar|partners|members|unitholders|parent|received|from (equity|affiliat|unconsol)`. "Dividends and dividend equivalents" is common (founder ruling 2026-11-01; AAPL).

## 4. Candidates (not approved)
1. `PaymentsOfCapitalDistribution` with a label naming common stockholders, or a REIT with no other distribution line (1581068 "Distributions to common stockholders", 947484 "Common dividends paid"). Exclude the Up-C member and parent patterns by label.
2. A combined preferred+common line (1393311) is a perimeter case: hold it, or split it using `DividendsPreferredStock` from the equity statement (a derivation; Standardization Lead).

## 5. Traps
- Dividends **received** (investing or operating) and dividends paid to NCI share the word.
- Up-C structures (Pla-Fit, Symbotic) pay "distributions" to LLC members: NCI, not shareholders.
- `PaymentsOfDividends` (157 companies) can include preferred dividends; the card-level check is whether the filing also prints a separate preferred line (then the total includes it only if it is the parent in the calc).
- Declared vs paid: the equity statement's `DividendsCommonStock` / `DividendsCommonStockCash` is **declared**, which differs from cash paid around year-end; never a substitute.
