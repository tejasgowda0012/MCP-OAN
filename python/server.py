"""
Bharat Vistaar MCP server (Python / FastMCP).

Exposes all Vistaar agent tools over streamable HTTP for the bharat-oan-api Pydantic AI client.
Run: uv run server.py  or  python server.py
"""
from __future__ import annotations

import asyncio
import contextvars
import inspect
import os
from pathlib import Path
from typing import Any, Callable

from dotenv import load_dotenv
from mcp.server.fastmcp import Context, FastMCP

load_dotenv(Path(__file__).resolve().parent / ".env")

from vistaar_mcp.deps import FarmerContext
from vistaar_mcp.tools import (
    analyze_crop_image,
    check_pmfby_grievance_otp,
    check_pmfby_status_with_otp,
    check_pm_kisan_status_with_otp,
    check_shc_status,
    check_smam_scheme_status,
    forward_geocode,
    get_mandi_prices,
    get_sathi_crop_groups,
    get_scheme_info,
    gfr_get_crop_registries,
    gfr_get_recommendations,
    initiate_pmfby_grievance_otp,
    initiate_pmfby_status_check,
    initiate_pm_kisan_status_check,
    list_sathi_crops_in_group,
    pmfby_grievance_status,
    pmfby_submit_grievance,
    pmkisan_grievance_send_otp,
    pmkisan_grievance_status,
    pmkisan_submit_grievance,
    reverse_geocode,
    search_commodity,
    search_documents,
    search_pests_diseases,
    search_sathi_seed_availability,
    search_terms,
    search_videos,
    weather_forecast,
)

mcp = FastMCP("Bharat Vistaar MCP", host=os.getenv("MCP_HOST", "0.0.0.0"), port=int(os.getenv("MCP_PORT", "3001")))

_farmer_deps: contextvars.ContextVar[FarmerContext] = contextvars.ContextVar("farmer_deps")


class _RunCtx:
    """Minimal RunContext stand-in for tools that expect ctx.deps."""

    def __init__(self, deps: FarmerContext):
        self.deps = deps


def _farmer_from_meta(ctx: Context) -> FarmerContext:
    meta = getattr(ctx.request_context, "meta", None) if ctx.request_context else None
    raw: dict[str, Any] = {}
    if meta is not None:
        if isinstance(meta, dict):
            raw = meta.get("deps") or meta
        else:
            raw = getattr(meta, "deps", None) or {}
            if hasattr(raw, "model_dump"):
                raw = raw.model_dump()
            elif not isinstance(raw, dict):
                raw = dict(raw) if raw else {}
    session_id = raw.get("session_id") or "mcp-anonymous"
    return FarmerContext(
        query=raw.get("query", ""),
        lang_code=raw.get("lang_code", "hi"),
        session_id=session_id,
        moderation_str=raw.get("moderation_str"),
        latitude=raw.get("latitude"),
        longitude=raw.get("longitude"),
    )


def _set_farmer(ctx: Context) -> FarmerContext:
    deps = _farmer_from_meta(ctx)
    _farmer_deps.set(deps)
    return deps


async def _invoke(fn: Callable, ctx: Context, kwargs: dict[str, Any]) -> str:
    deps = _set_farmer(ctx)
    run_ctx = _RunCtx(deps)
    params = list(inspect.signature(fn).parameters.keys())
    if params and params[0] == "ctx":
        call_kwargs = kwargs
        if inspect.iscoroutinefunction(fn):
            result = await fn(run_ctx, **call_kwargs)
        else:
            result = fn(run_ctx, **call_kwargs)
    else:
        if inspect.iscoroutinefunction(fn):
            result = await fn(**kwargs)
        else:
            result = fn(**kwargs)
    if result is None:
        return ""
    return str(result)


def _register_ctx_tool(fn: Callable) -> None:
    @mcp.tool(name=fn.__name__, description=(fn.__doc__ or "").strip())
    async def _handler(ctx: Context, **kwargs: Any) -> str:
        return await _invoke(fn, ctx, kwargs)

    _handler.__name__ = fn.__name__


def _register_plain_tool(fn: Callable) -> None:
    @mcp.tool(name=fn.__name__, description=(fn.__doc__ or "").strip())
    async def _handler(ctx: Context, **kwargs: Any) -> str:
        return await _invoke(fn, ctx, kwargs)

    _handler.__name__ = fn.__name__


_CTX_TOOLS = (
    initiate_pm_kisan_status_check,
    check_pm_kisan_status_with_otp,
    initiate_pmfby_status_check,
    check_pmfby_status_with_otp,
    pmkisan_grievance_send_otp,
    pmkisan_submit_grievance,
    pmkisan_grievance_status,
    initiate_pmfby_grievance_otp,
    check_pmfby_grievance_otp,
    pmfby_grievance_status,
    pmfby_submit_grievance,
    analyze_crop_image,
)

_PLAIN_TOOLS = (
    get_scheme_info,
    check_shc_status,
    check_smam_scheme_status,
    search_terms,
    search_documents,
    search_videos,
    search_pests_diseases,
    weather_forecast,
    get_mandi_prices,
    search_commodity,
    forward_geocode,
    reverse_geocode,
    gfr_get_crop_registries,
    gfr_get_recommendations,
    get_sathi_crop_groups,
    list_sathi_crops_in_group,
    search_sathi_seed_availability,
)

for _tool in _CTX_TOOLS:
    _register_ctx_tool(_tool)
for _tool in _PLAIN_TOOLS:
    _register_plain_tool(_tool)


if __name__ == "__main__":
    transport = os.getenv("MCP_TRANSPORT", "streamable-http")
    mcp.run(transport=transport)