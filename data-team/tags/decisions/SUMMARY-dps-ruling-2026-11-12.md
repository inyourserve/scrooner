# Summary: revised DPS ruling applied (Ritwik cloud, 2026-11-12)

For Dhairya. Your revised ruling is applied to the DPS rows for COF, C, CRM and DIS in `companies-51-100-exceptions-2026-11-11.csv`.

What the four rows now say:
- **Decision:** they change from not_presented to component.
- **Value:** the sum of the four printed quarterly DPS facts from the same 10-K, on the same declared or paid basis. The serve_note is 'sum of printed quarterly dividends'.
- **Coverage:** only where all four quarters are printed.

## Approver condition

As release approver, I'm attaching one condition.

**The rule:** all four quarters must be on the same share basis. If a stock split falls inside the fiscal year, the sum is blocked until the quarters are restated to one basis.

**Why:** this is condition C6 from my 2026-11-09 done-gate ruling. Founder ruling 2026-11-04 item 2 requires that same-basis check for DPS, and the release case §6 shows the check is still missing.

**What the builder needs:** a split guard that is tested and mutation-checked before any summed DPS is served.

EPS stays never-derived.

The card note is in `card-notes-51-100-2026-11-11.md`, under "Revised ruling: annual DPS".
