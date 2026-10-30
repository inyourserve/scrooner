---
id: money-facts-can-carry-a-non-usd-unit-hovr-equity-is-cad-stor
title: Money facts can carry a non-USD unit: HOVR equity is CAD stored as if USD
kind: gotcha
tags: units, currency, hovr
paths: data-team/strategy/team/DC-SHARE-COUNT-DATE-2026-10-22.md
evidence: DATA-INFERRED
created: 2026-10-23
verified: 2026-10-23
---
HOVR files in CAD; canonical stockholders_equity facts 73183954 and 216945757 have unit cad but are read as USD. Add a USD-only check on money concepts and scan the population for non-USD money facts (not yet measured).
