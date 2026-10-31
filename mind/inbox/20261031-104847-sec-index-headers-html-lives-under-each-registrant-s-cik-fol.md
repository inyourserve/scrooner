---
id: sec-index-headers-html-lives-under-each-registrant-s-cik-fol
title: SEC -index-headers.html lives under each REGISTRANT's CIK folder, not the accession prefix (filing-agent accessions 404 under the prefix)
kind: gotcha
tags: sec, edgar, headers, shared-accession, filing-agent, co-registrant
paths: pipeline/scripts/shared_accession_dryrun.py
evidence: FILING-CHECKED
created: 2026-10-31
verified: 2026-10-31
---
An accession prefix is the SUBMITTER's filer id. When a filing agent submits (Eversource and CMS combined 10-K/10-Qs since 2025-08, prefix 0001628280), https://www.sec.gov/Archives/edgar/data/<prefix>/<accnodash>/<acc>-index-headers.html returns 404, while the same path under any registrant's CIK folder (e.g. /data/72741/000162828025037369/) returns 200 with FILER blocks in order (Eversource, NSTAR Electric, CL&P, PSNH), checked live 2026-10-31. Fetch under the prefix first, then each registrant's folder. Pre-2015 accessions have no headers file at all (430 misses out of 857 in the population dry-run), so a missing header for an old filing is normal, not an error. Also: the prefix cannot vote as a 'primary' signal for agent-filed accessions because it is not a registrant; header+payload then decide.
