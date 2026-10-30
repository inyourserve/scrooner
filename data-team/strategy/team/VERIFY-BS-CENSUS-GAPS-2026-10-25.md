# Verify: BS census unexplained identity gaps (origin/work/scrooner-25/slot-records, bs_census_unexplained_gaps.json), 2026-10-25

Verifier 2. Three instants per company, balance-sheet R page of each accession. FILING-CHECKED.

## Result: every printed Total liabilities is right (27 of 27). Each gap is a face line between liabilities and equity (mezzanine) or a cross-check misread; none is a wrong shown value.
| Company | Instants (accession) | Printed TL | Line explaining the gap |
|---|---|---|---|
| Jefferies (96223) | 2015-03-31 (0000096223-15-000012), 2019-02-28 (-19-000022), 2022-11-30 (-23-000009) | right (52,322,692 = 41,308,780 + 168,541 + 125,000 + 10,720,371) | MEZZANINE EQUITY: "Mandatorily redeemable convertible preferred shares" 125,000K (custom `luk_MandatorilyRedeemableConvertiblePreferredShares`) + "Redeemable noncontrolling interests" (custom `luk_RedeemableNoncontrollingInterests...`; 168,541 / 20,189 / 6,461K) |
| Sun Communities (912593) | 2015-09-30 (-15-000111), 2019-09-30 (-19-000130), 2023-09-30 (-23-000229) | right (preferred OP units mandatorily redeemable 45,903 are INSIDE TL in 2015) | temporary equity on class members: Series A-4 preferred stock 68,633 + A-4 preferred OP units 20,982 = 89,615 (2015); common RNCI 27,461 + A-4 31,402 + A-4 OP 9,540 + Series D OP 51,248 = 119,651 (2019); "Temporary equity" 304.5M (2023) |
| LabCorp (920148) | 2015-03-31, 2020-12-31, 2026-06-30 | right | "Noncontrolling interest" in mezzanine on custom `lh_NoncontrollingInterestMezzanineEquity` (16.2 / 20.7 / 16.4M) |
| Alexandria RE (1035443) | 2015-03-31, 2017-06-30, 2019-09-30 | right (8,405,221 = 4,608,369 + RNCI 14,282 + equity 3,782,570) | negative gap = cross-check error: it subtracts "Series D cumulative convertible preferred stock" (237,163 / 74,386 / 57,461K, `ConvertiblePreferredStockNonredeemableOrRedeemableIssuerOptionValue`), which is INSIDE stockholders' equity |
| Booking (1075531) | 2016-09-30, 2017-12-31, 2021-06-30 | right | "Convertible debt" shown in temporary equity below Total liabilities (34,504K / 2,963K / 5M) |
| Ares (1176948) | 2015-03-31 (0001047469-15-004661), 2022-12-31, 2026-06-30 | right | "Redeemable interest" tagged only with LegalEntityAxis members (Consolidated Funds 915,017 + Ares Operating Group 24,077 = 939,094 in 2015; 1,013,282 + 93,129 in 2022; AOG 25,648 in 2026) |
| Maplebear (1579091) | 2023-09-30, 2025-03-31, 2026-06-30 | right | "Series A redeemable convertible preferred stock" 175 / 188 / 200M, class-member only |
| Advanced Drainage Systems (1604028) | 2015-03-31 (0001193125-16-521419), 2018-09-30, 2021-12-31 | right (2,555,759 = 1,535,249 + mezzanine 205,742 + equity 814,768) | negative gap = cross-check over-counts mezzanine (redeemable convertible preferred plus another component of "Total mezzanine equity"); face ties |
| Broadcom (1730168) | 2019-11-03, 2021-05-02, 2022-07-31 | right as printed | "Preferred stock dividend obligation" 29 / 27 / 27M, printed below Total liabilities and outside equity (custom line) |

## For scrooner-25
- Mezzanine read from class-member or entity-member facts (Sun, Ares, Maplebear) and from custom tags (Jefferies, LabCorp, Booking) closes 7 of 9.
- Alexandria and ADS: the cross-check must not treat a preferred line inside the equity section (Alexandria) or a subtotal component (ADS) as an extra mezzanine term.
- Broadcom: the dividend obligation sits outside the filer's Total liabilities; keep the printed total, record the line in the mezzanine/other slot.
