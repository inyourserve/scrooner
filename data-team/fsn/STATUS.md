# FSN expert: status

Updated 2026-11-02.

## Now
- **Companies completed:** 1 of 1,000. MSFT (`companies/MSFT.md`). Pilot queue next: HD, AAPL, JPM, TRV, PLD, NEE, XOM, JNJ, WMT.
- **Tags carded (per-tag cards this programme):** 8. They are listed in `../tags/CHANGELOG.md` 2026-11-02; the earlier family cards are in `../tags/cards/`.
- **Open disagreements with our store:** 13, all MSFT.
  - Production `canonical_fact`, 5:
    - total_debt FY2016 and FY2024 wrong;
    - total_debt FY2019 missing;
    - interest_expense FY2025–26 missing;
    - EPS/pretax FY2016–17 and CFO FY2014–15 missing.
  - FSN pilot run 41490670432, 8:
    - CF identity FX;
    - revenue/COR component conflict;
    - D&A two custom lines;
    - capex/cash/debt rules missing;
    - interest reason;
    - equity 2016 vintage;
    - Q4 EPS printed;
    - Q4 printed vs derived.
  - Details and evidence: `companies/MSFT.md` §7.
- **Reference:** `FSN-GUIDE.md` (every file and column, the pitfalls on real rows, the verdicts on the seven team beliefs).

## Top 5 changes engineering should make now
1. **P-1:** add the two `…DisposalGroup…` FX tags to `fsn_store/checks.py` `CF_FX`. MSFT's CFO, dividends and buybacks FY2020+ fail today, and 19 top-100 names use the tag.
2. **P-4:** concept rules for capex, cash and total debt. The debt rule must include `CommercialPaper`; production MSFT debt is wrong for FY2016 (12,904 vs 53,461) and FY2024 (44,937 vs 51,630).
3. **P-2:** drop a revenue/COR candidate that is a calc child of another candidate ("Product" lines).
4. **P-3:** a custom calc-position slot takes one line only; "… and other" labels are `combined`.
5. **P-7:** printed Q4 from the 10-K quarterly note beats derivation, including per-share (MSFT FY2014–FY2020).
