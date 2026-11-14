---
id: structural-load-loader-causes-signed-nodes-in-bracket-text-l
title: Structural-load LOADER causes: signed nodes, ';' in bracket text, library combined line, held library rows, before-first-10-K
kind: gotcha
tags: structural-load, resolver, loader
paths: pipeline/src/scrooner_pipeline/mapper/structural_loader.py
evidence: DATA-INFERRED
source: commits fa287b97 ac0d66dd bd21767b
created: 2026-11-14
verified: 2026-11-14
---
Of 448 LOADER open cells: 100 were only unrun (direct serving already served them); the loader dropped signed '-Tag' nodes (BA/AMD/MCD opex), read ';' inside a node bracket as a split (lease parts), rejected accession-empty before_first_10k rows, let a library held_* not_presented 'agree' with a structural not_presented, and dropped value claims beside a library combined line. Fixed once in structural_loader.py. Still open: member parts (Tag[Member]), printed_zero with no stored fact, member_face_fact (ABT/KO), fix rows winning cells, later-filing restated prints kept by apply_direct.
