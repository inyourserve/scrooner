# Scrooner

The easiest way to screen US companies using complex fundamental logic in plain English — deterministic, traceable results computed from normalized SEC filing data, not an AI-generated opinion.

## Local development

The stock screener needs both the Next.js frontend and the FastAPI screening
service. Start them together from the repository root:

```bash
./scripts/dev.sh
```

Then open `http://localhost:3000`. The frontend runs on port 3000 and the
internal screening service runs on `127.0.0.1:8000`.

- Project context for contributors and AI agents: [`CLAUDE.md`](CLAUDE.md)
- Canonical product/architecture/decision docs: [`doc/`](doc/)
