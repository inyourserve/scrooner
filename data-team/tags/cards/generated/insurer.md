# Rules: insurer (GENERATED from rules/insurer.csv and exam/results/ledger.csv — do not edit by hand)

1 rules. Stats = replay rows with hand-verified keys (fires / wrong / accuracy).

## (structural)

| Rule | Kind | Scope | When | Then | Evidence | Fires | Wrong | Accuracy |
|---|---|---|---|---|---|---|---|---|
| insurer.detect | sector_detect | insurer | `{"any_of":["PremiumsEarnedNet","LiabilityForFuturePolicyBenefits","LiabilityForUnpaidClaimsAndClaimsAdjustmentExpense"]}` | `{"group":"insurer"}` | sector-faces.md | 0 | 0 |  |

