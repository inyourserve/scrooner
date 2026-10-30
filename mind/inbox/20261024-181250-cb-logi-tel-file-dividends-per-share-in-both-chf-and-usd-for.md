---
id: cb-logi-tel-file-dividends-per-share-in-both-chf-and-usd-for
title: CB/LOGI/TEL file dividends per share in both CHF and USD for the same context; CP files EPS in CAD
kind: gotcha
evidence: FILING-CHECKED
created: 2026-10-24
verified: 2026-10-24
---
Same tag, same context, two unitRefs (CHFPerShare and USDPerShare) at Swiss-domiciled filers: TEL 0001047469-13-010572 (0.96 CHF / 1.00 USD), CB, LOGI. Today's stored CB/LOGI DPS were CHF values. CP 10-Qs file EPS as iso4217_CAD_per_shares/cadPerShare (0000016875-16-000039). Always filter per-share units to USD.
