---
id: peer-session-names-and-uds-sockets-change-on-every-session-r
title: Peer session names and uds sockets change on every session restart; re-find a peer with ListAgents and a handoff, never a saved address
kind: gotcha
tags: sessions, coordination, release
evidence: DATA-INFERRED
status: active
created: 2026-11-01
verified: 2026-11-01
---
2026-11-01: after a restart, every peer had a new name (scrooner-8a, -eb, -ca gone; this session became scrooner-c2) and the saved uds:/tmp/cc-socks/<pid>.sock paths returned ENOENT. A pending gate message (8a to release approver: 0118/0119 sha + CI + G1 fixtures) then has no route. Keep handoff state in a file on main or in scratchpad with absolute paths (e.g. the approver's apply runner and review notes), and have the owner of the lane announce its new name after a restart.
