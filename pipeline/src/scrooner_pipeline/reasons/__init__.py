"""Visible-reason rules for blank cells (root fix #3, top-1000 cohort).

A rule READS evidence (a template membership, a filing-line presentation row,
a tag-agnostic absence over everything the company filed, an input cell that
already has a state) and WRITES a closure: frozen state + wording key +
evidence reference. It never fabricates a value and never fabricates a reason:
a blank cell that no rule can evidence stays `defect(unclassified, triage)` and
is reported as residue with its data point.

Nothing in this package writes to a database. `dry_run` is the only entry
point; `to_blank_reason_row` only shapes a closure into the columns of
analytics.cell_blank_reason (migration 0100, not applied).
"""
