---
id: scaling-the-bs-totals-slot-family-to-1-000-companies-71-of-e
title: Scaling the BS-totals slot family to 1,000 companies: 71% of eras print a Liabilities total (no cal needed), 297 companies need one filer cal, custom-tag values should come from FSDS num rows, not 16k instance reads
kind: lesson
evidence: DATA-INFERRED
created: 2026-10-25
verified: 2026-10-25
---
bs_totals_detect over the full cohort (2026-10-25, local FSDS asset): 999 companies, 41,635 filings, 13,873 eras (median 13 per company; set-based or per-form fingerprints only reduce to 11,591, so eras are real face changes). 9,912 eras print a Liabilities total (printed_total rule, zero fetches); 702 companies print it in every era. 3,961 face-sum eras across 297 companies need the filer's calc graph: ONE cal per company, borrowed across its eras and identity-gated, costs ~600-1,200 sec.gov requests instead of 7,360. Custom liability lines appear in 5,996 eras at 649 companies (176 of them in face-sum eras); reading each instant's instance (~46 per company) would be ~16,000 requests, so the scalable source for custom-tag face values is the FSDS num.txt rows for the cohort (standard + custom, undimensioned; ~47 quarterly zips, streamed one at a time and deleted), with the instance reader kept for dimensioned mezzanine lines and spot checks.
