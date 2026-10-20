"""Top-1000 certification invariant suite (data-team/34, P1).

Read-only checks over every stored value of a company, one module per
invariant group:

  ties.py              I1 balance identity, I2 statement ties
  sign.py              I3 sign policy
  scale.py             I4 scale and plausibility
  period_integrity.py  I5 period lengths, quarter sums, label shift
  source_integrity.py  I6 source form / authority / unit / value-equals-source
  currency.py          I7 age of displayed values and of metric inputs
  composition.py       I8 total debt composition, per-share by subtraction
  splits.py            I9 split consistency
  sector.py            I10 sector template evidence

Every check is a pure function of `model.CompanyData`; `loader.py` is the only
module that reads the database and `runner.py` the only one that writes (and
only the two certification tables, only with --apply).
"""
