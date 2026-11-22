---
id: one-sec-limiter-for-every-caller-common-sec-rate-py-2-req-s-
title: One SEC limiter for every caller: common/sec_rate.py, 2 req/s total per machine; tools use tools/sec_pace.py
kind: rule
tags: sec, rate-limit
paths: pipeline/src/scrooner_pipeline/common/sec_rate.py, data-team/tags/line_map/tools/sec_pace.py
evidence: CODE-CHECKED
status: active
created: 2026-11-21
verified: 2026-11-21
---
8891c531: SEC_RATE_CEILING=2.0 and one flock lock file; limiter() clamps (lowering allowed). SECClient, EdgarClient, instance_evidence.py, text_disclosure.py, lease_instances.py and the exam fetchers all go through it; INSTANCE_MIN_INTERVAL/TEXT_MIN_INTERVAL are gone. The lock is per machine, so a workflow with N parallel runners must set each runner to 2/N (onboard-company-filings: 1 req/s x 2 runners). Never add a private sleep loop for sec.gov.
