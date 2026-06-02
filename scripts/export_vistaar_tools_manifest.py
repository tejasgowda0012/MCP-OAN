#!/usr/bin/env python3
"""Export Vistaar MCP tool schemas for bharat-oan-api (shared manifest).

Run from MCP-OAN repo root after adding tools in python/server.py:

    python/scripts/export_vistaar_tools_manifest.py

Writes: shared/vistaar_tools_manifest.json
"""
from __future__ import annotations

import asyncio
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
PYTHON_DIR = REPO_ROOT / "python"
OUT_PATH = REPO_ROOT / "shared" / "vistaar_tools_manifest.json"

sys.path.insert(0, str(PYTHON_DIR))

from server import mcp  # noqa: E402 — imports register ALL_TOOLS


async def export_manifest() -> dict:
    tools = await mcp.list_tools()
    return {
        "schema_version": 1,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source": "MCP-OAN/python/server.py",
        "tools": [
            {
                "name": t.name,
                "description": t.description or "",
                "inputSchema": t.inputSchema,
            }
            for t in sorted(tools, key=lambda x: x.name)
        ],
    }


def main() -> None:
    payload = asyncio.run(export_manifest())
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Wrote {len(payload['tools'])} tools to {OUT_PATH}")


if __name__ == "__main__":
    main()