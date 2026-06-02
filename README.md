# MCP-OAN — Bharat Vistaar MCP Server

Model Context Protocol server for the Bharat Vistaar agricultural assistant. Tool definitions and handlers live here; [bharat-oan-api](https://github.com/OpenAgriNet/bharat-oan-api) connects as an MCP client.

## Servers

| Path | Transport | Port (default) | Tools |
|------|-----------|----------------|-------|
| [`python/`](python/) | Streamable HTTP | 3001 | **All 29** Vistaar tools (production) |
| [`src/`](src/) | HTTP `/mcp` + SSE | 3000 | Legacy TypeScript (`schemes-info` only) |

## Quick start (Python — recommended)

```bash
cd python
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # same credentials as bharat-oan-api
python server.py
```

Endpoint: `http://localhost:3001/mcp`

### bharat-oan-api

```env
MCP_SERVER_URL=http://localhost:3001/mcp
MCP_API_KEY=
MCP_TIMEOUT_SECONDS=120
```

The API does **not** call MCP `tools/list` at runtime. It uses a shared manifest:

| Repo | Path |
|------|------|
| MCP-OAN (canonical) | `shared/vistaar_tools_manifest.json` |
| bharat-oan-api (copy) | `agents/data/vistaar_tools_manifest.json` |

Regenerate after adding tools in `python/server.py`:

```bash
python/scripts/export_vistaar_tools_manifest.py
# In bharat-oan-api (sibling checkout):
./scripts/sync-vistaar-tools-manifest.sh
```

## TypeScript server (optional / legacy)

```bash
npm install
npm run build
cp .env.example .env
npm start
```

See [CLAUDE.md](CLAUDE.md) for TypeScript layout details.