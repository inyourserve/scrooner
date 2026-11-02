# Tag card: FinanceLeaseLiability

Written 2026-11-02 by the FSN expert. Family: debt / leases (INDEX.md "FinanceLeaseLiability*": lease, not debt unless policy says so).

## Meaning
- **What it is:** the present value of the lessee's discounted obligation for finance-lease payments (ASC 842). The total; current and noncurrent have their own tags.
- **Period type:** instant.
- **Balance:** credit.

## Who uses it
- **On the BS face for none of the 101 companies in our extract** (DI: zero BS/IS/CF pre lines).
- Typically a **note** fact. MSFT, from Q1 FY2018 0001564590-17-020171 (ASC 842 early adoption):
  - 2,538 (FY2017), 4,301, 6,574, 9,496, 12,541, 14,902, 17,067, 27,145 (FY2024), 46,172 (FY2025), 66,594 (FY2026), $M.
  - MSFT: "Finance leases are included in property and equipment, other current liabilities, and other long-term liabilities" (LesseeLeasesPolicyTextBlock, 0001564590-17-020171).

## Rule
- "Total debt including finance leases" needs this note value. The face does not show it as a line.
- Add it as its own labelled component; never infer it from "Other liabilities".
