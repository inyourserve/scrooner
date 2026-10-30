---
id: sec-financial-statement-and-notes-data-set-fsn-cal-tsv-repro
title: SEC Financial Statement and Notes data set (FSN): cal.tsv reproduces filers' calc linkbases exactly, 'negative' is the weight, ~11% of periodic filings (Workiva/Toppan, schema-embedded calc) have no cal rows; a quarter is ~430 MB and cohort extracts of all tables are ~22% of the zip
kind: lesson
evidence: CODE-CHECKED
created: 2026-10-25
verified: 2026-10-25
---
Pilot 2024q4 (2026-10-25, 5 requests): zip https://www.sec.gov/files/dera/data/financial-statement-notes-data-sets/2024q4_notes.zip, 430.8 MB, Accept-Ranges: bytes; the listing page is script-rendered but its HTML carries all quarter links (47 quarters 2014q1-2025q3, ~19.1 GB total, largest 2021q1 810 MB; 2025q4+ not yet published). Members: sub, tag, dim, ren, cal, pre, num, txt (+ readme, metadata). Cohort rows of every table (3,742 filings, 988 periodic) compress to 97 MB with zstd. cal.tsv columns adsh, grp, arc, negative, ptag, pversion, ctag, cversion: 'negative' IS the weight (1 or -1), not a boolean; parent/child/weight sets matched our parsed _cal.xml/.xsd/MetaLinks exactly on 9 of 9 Verifier-passed filings (JPM, BAC, EMR, GE, T, COST, ALB, MCK, DUK). 106 of 988 periodic filings have NO cal rows: filer agents 0000950170 (Workiva) and 0001558370 (Toppan), whose calc linkbase is embedded in the .xsd; pre rows exist for all 988; sub.instance names the instance so the .xsd URL is one request. num carries face AND note values incl. custom and dimensioned tags (replaces instance reads for custom lines and class-of-stock mezzanine); txt carries note text (reason evidence); dim carries members (segments, classes, legal entities); ren carries R-page layout.
