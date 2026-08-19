# pipeline/

Scrooner's data pipeline: SEC EDGAR → Collector → Normalizer → Mapper/Metrics. Currently **Collector-only** — see [`CLAUDE.md`](CLAUDE.md) and [`../doc/execution-plans/08_Scrooner_Collector_Execution_Plan.md`](../doc/execution-plans/08_Scrooner_Collector_Execution_Plan.md) for the active build plan.

Python 3.12, managed with [uv](https://github.com/astral-sh/uv), scoped to this folder:

```
cd pipeline
uv sync
cp .env.example .env   # fill in DATABASE_URL / SUPABASE_URL / SEC_USER_AGENT
```
