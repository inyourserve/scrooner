"""The tools' SEC pacing: the ONE machine-wide budget of pipeline/src/scrooner_pipeline/common/sec_rate.py
(2 requests per second in total, flock-shared across processes), not a per-script sleep. Stdlib only on both sides,
so it works under the system python3 the tools run with. Call sec_pace.wait() right before every sec.gov request, or use sec_pace.fetch(url).
CLI: python3 -I data-team/tags/line_map/tools/sec_pace.py fetch URL OUTFILE (see sec_rate.main)."""
import os, sys

_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..'))
_SRC = os.path.join(_ROOT, 'pipeline', 'src')
if _SRC not in sys.path:
    sys.path.insert(0, _SRC)
from scrooner_pipeline.common import sec_rate  # noqa: E402

CEILING = sec_rate.SEC_RATE_CEILING


def wait():
    sec_rate.wait()


def fetch(url, timeout=60):
    return sec_rate.fetch(url, timeout)


if __name__ == '__main__':
    raise SystemExit(sec_rate.main())
