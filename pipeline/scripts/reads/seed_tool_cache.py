"""Seed the shared reader's cache (data-team/companies/reads/tools/docmap.py) from documents sec_fetch.py already
stored, so the shared tool does not fetch them again. The tool's cache key is re.sub(r"\\W", "_", url)[-150:] and its
cache holds the response text. usage: seed_tool_cache.py <sec_docs_dir> <cache_dir>"""

import gzip
import re
import sys
from pathlib import Path


def key(url: str) -> str:
    return re.sub(r"\W", "_", url)[-150:]


def main(src: Path, cache: Path) -> None:
    cache.mkdir(parents=True, exist_ok=True)
    n = 0
    for cikdir in sorted(p for p in src.iterdir() if p.is_dir()):
        cik = cikdir.name
        cf = cikdir / "companyfacts.json.gz"
        if cf.exists():
            url = f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json"
            (cache / key(url)).write_text(
                gzip.decompress(cf.read_bytes()).decode("utf8", "ignore"),
                encoding="utf8",
            )
            n += 1
        for accdir in sorted(p for p in cikdir.iterdir() if p.is_dir()):
            base = f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{accdir.name.replace('-', '')}/"
            for f in accdir.iterdir():
                name, body = f.name, f.read_bytes()
                if name.endswith(".gz"):
                    name, body = name[:-3], gzip.decompress(body)
                (cache / key(base + name)).write_text(
                    body.decode("utf8", "ignore"), encoding="utf8"
                )
                n += 1
    print(f"seeded {n} cache entries")


if __name__ == "__main__":
    main(Path(sys.argv[1]), Path(sys.argv[2]))
