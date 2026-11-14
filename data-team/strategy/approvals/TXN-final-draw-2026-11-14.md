# TXN final draw (Ritwik cloud, approver, 2026-11-14): FAIL

**Checked:** `data-team/strategy/certification/TXN-coverage-2026-11-14.csv` at main **ab86bbeb** (506 cells: 475 PROVEN, 31 REASON), proof code `cell_proof_v14_2026-11-14` at that commit. Seed: `txn-final-ab86bbeb`. All checks are against the SEC filings.

| Check | Result |
|---|---|
| 32 random PROVEN cells | **31/32.** 20 matched by script and 11 by hand (the script misread CF column offsets and the quarterly columns on the FY2017 income statement). 1 error: amortization_of_intangibles FY2025 |
| 5 random REASON cells | 5/5 on substance. Each cites its own year's 10-K and the page shows the reason: interest income only inside 'Other income (expense), net' (FY2019 R2, FY2024 R3); CF 'Accounts payable and accrued expenses' combined (FY2023 and FY2024 R8); BS shows only issued and treasury shares (FY2016 R5) |
| REASON cells cite a filing presenting their year | 31/31 (fixed since the v12 pre-check) |
| Locators | **11 cells have no R page:** shares_outstanding REASON FY2015-2025 |
| total_debt, all 11 FY, full perimeter | 11/11. Face current + long-term debt. FY2019-25 filings carry no finance or capital lease facts; FY2015-18 lease, commitment and debt detail pages show no capital-lease amount |

## Failing items

**1. amortization_of_intangibles FY2024 and FY2025 serve the wrong line** (2 cells; FY2025 was drawn).

| FY | Served value | Served tag | Filing evidence |
|---|---|---|---|
| 2015-2021 | 319 to 142 | AmortizationOfIntangibleAssets | 'Amortization of acquisition-related intangibles' |
| 2022-2023 | 0 | same | same line |
| 2024 | 72 | CapitalizedComputerSoftwareAmortization1 | 'Amortization of capitalized software' (FY2024 10-K R8) |
| 2025 | 81 | CapitalizedComputerSoftwareAmortization1 | 'Amortization of capitalized software' (FY2025 10-K R7) |

- Capitalized-software amortization is a different line, not acquired-intangible amortization. The FY2021 10-K (0000097476-22-000009 R8) prints both lines side by side: acquired intangibles 142, capitalized software 57.
- The TXN docmap's note says "prior 10-Ks tagged the same line AmortizationOfIntangibleAssets". The FY2021 filing contradicts that note.
- **Fix:** FY2024-25 should carry the acquired-intangible figure, which the filings no longer print once it reached 0. That makes these cells REASON not_presented (citing each year's CF), or 0 if a later filing prints a 0 comparative. The docmap row needs correcting too.
- **Tag Expert call:** if capitalized-software amortization is meant to be inside amortization_of_intangibles, every year needs both lines summed. As served, the series switches concept in 2024.

**2. Locators.** The 11 shares_outstanding REASON cells (FY2015-25) have an accession but no R page. Cite the BS page that shows only issued and treasury shares for each year, e.g. FY2016: 0001564590-17-002142 R5.

## To certify

1. Fix item 1 (2 cells) and the docmap row.
2. Add the 11 R pages.
3. Send the new hash. I then re-check the changed cells, the amortization series, and a fresh 5-cell PROVEN top-up.

The other 31 PROVEN, 5 REASON and 11 total_debt checks stand. Evidence: `TXN-final-draw-2026-11-14-proven.txt` beside this file.
