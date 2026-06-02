# Bharat Vistaar MCP (Python)

Canonical MCP server for all 29 Vistaar agent tools. The [bharat-oan-api](https://github.com/OpenAgriNet/bharat-oan-api) agent connects as an MCP client (`MCPServerStreamableHTTP`).

## Run

```bash
cd python
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # fill credentials (same as bharat-oan-api)
python server.py
```

Default endpoint: `http://localhost:3001/mcp`

## bharat-oan-api configuration

```env
MCP_SERVER_URL=http://localhost:3001/mcp
MCP_API_KEY=your-key-if-required
MCP_TIMEOUT_SECONDS=120
```

The legacy TypeScript server in `../src/` (`schemes-info` only) is superseded by this Python server for production agent traffic.