# Shared Vistaar tool manifest

`vistaar_tools_manifest.json` is the single source of tool **names**, **descriptions**, and **input JSON schemas** for the Vistaar agent in bharat-oan-api.

Generate from registered FastMCP tools:

```bash
python/scripts/export_vistaar_tools_manifest.py
```

Copy into bharat-oan-api with `./scripts/sync-vistaar-tools-manifest.sh` (or set `VISTAAR_TOOLS_MANIFEST_PATH` to this file in local dev).