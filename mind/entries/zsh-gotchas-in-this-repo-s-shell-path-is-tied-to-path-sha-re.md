---
id: zsh-gotchas-in-this-repo-s-shell-path-is-tied-to-path-sha-re
title: zsh gotchas in this repo's shell: 'path' is tied to PATH, $sha:refs expands as a modifier, and cherry-picking a whole old branch replays commits already on main
kind: gotcha
tags: zsh, git, shell
paths: scripts/check_migrations.py
evidence: CODE-CHECKED
status: active
created: 2026-11-01
verified: 2026-11-01
---
(1) Never name a shell variable path (zsh ties it to PATH; every command then 'not found'); status is read-only. (2) git push "$sha:refs/heads/x" is parsed by zsh as $sha with a :r modifier; write "${sha}:refs/heads/x". (3) To land part of an old branch, cherry-pick only its own new commits (git cherry origin/main <branch> shows '+' ones) or checkout the tip's files for the named paths: cherry-picking a whole range replays commits already on main as add/add conflicts and an empty first pick stops the sequence silently, landing nothing (check git log origin/main..HEAD after). (4) The shared checkout /Users/vikash/scrooner can be hundreds of commits behind origin/main; edits to CLAUDE.md or docs only take effect there after refreshing the file from origin/main, and the checkout is dirty with other sessions' files so do not pull it.
