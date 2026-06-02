# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
npm run build    # Compile TypeScript → dist/
npm start        # Run compiled HTTP server (dist/index.js)
npm run dev      # Run via ts-node without compiling (development)
```

No test or lint scripts are configured.

## Architecture

This is a **Bharat Vistaar MCP Server** — a [Model Context Protocol](https://modelcontextprotocol.io) server that exposes Indian agricultural scheme search as an AI-accessible tool. It bridges MCP clients (AI assistants) to the Beckn/Vistaar protocol APIs run by the Government of India.

### Two transport modes

| Entry point | Transport | Use case |
|---|---|---|
| `src/index.ts` | HTTP (Express, port 3000) | Production / remote AI clients |
| `src/stdio.ts` | Stdio | Local testing / Claude Desktop config |

The HTTP server creates a **new MCP server + transport per request** (stateless). Each `/mcp` POST is fully independent. API key auth is required (Bearer token or `x-api-key` header; key set via `MCP_API_KEY` env var).

### Tool system

**Production:** all 29 Vistaar tools are implemented in `python/` (FastMCP, `server.py`). The bharat-oan-api agent uses this server via streamable HTTP.

**Legacy TypeScript:** `src/tools/registry.ts` registers tools on the Node server. Only `schemes-info` remains in TS; prefer adding tools in `python/vistaar_mcp/tools/`.

### Beckn protocol integration

`src/config.ts` holds all Beckn protocol constants (domain, BAP/BPP IDs, endpoint URL). The `schemes-info` tool constructs a Beckn `search` request with a generated UUID per call, POSTs it to `https://seeker-client-vistaar.da.gov.in/search`, and returns the raw JSON response.

### Environment variables

Copy `.env.example` to `.env`:

```
PORT=3000
MCP_API_KEY=your-secret-api-key-here
```
