"""
Bharat Vistaar MCP server (Python / FastMCP).

Exposes all Vistaar agent tools over streamable HTTP for the bharat-oan-api Pydantic AI client.
Run: python server.py
"""
from __future__ import annotations

import contextvars
import inspect
import os
from pathlib import Path
from typing import Any, Callable, get_args, get_origin

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


async def _invoke(fn: Callable, ctx: Context, kwargs: dict[str, Any]) -> str:
    deps = _farmer_from_meta(ctx)
    run_ctx = _RunCtx(deps)
    params = list(inspect.signature(fn).parameters.keys())
    if params and params[0] == "ctx":
        if inspect.iscoroutinefunction(fn):
            result = await fn(run_ctx, **kwargs)
        else:
            result = fn(run_ctx, **kwargs)
    else:
        if inspect.iscoroutinefunction(fn):
            result = await fn(**kwargs)
        else:
            result = fn(**kwargs)
    if result is None:
        return ""
    return str(result)


def _schema_annotation(annotation: Any) -> Any:
    """Types safe for FastMCP inspect.eval_str (avoid bare Literal)."""
    if annotation is inspect.Parameter.empty:
        return Any
    origin = get_origin(annotation)
    if origin is not None:
        return str
    if isinstance(annotation, type):
        return annotation
    return str


def _format_exec_param(param: inspect.Parameter) -> str:
    if param.default is inspect.Parameter.empty:
        return param.name
    return f"{param.name}={param.default!r}"


def register_vistaar_tool(fn: Callable) -> None:
    """Register tool with explicit parameters (no **kwargs) for valid OpenAI schemas."""
    sig = inspect.signature(fn)
    tool_params = [p for name, p in sig.parameters.items() if name != "ctx"]
    if not tool_params:
        args_code = ""
        kwargs_map = ""
    else:
        args_code = ", ".join(_format_exec_param(p) for p in tool_params)
        kwargs_map = ", ".join(f"{p.name!r}: {p.name}" for p in tool_params)

    namespace: dict[str, Any] = {
        "Context": Context,
        "_invoke": _invoke,
        "_target": fn,
    }
    if args_code:
        src = (
            f"async def __handler(ctx: Context, {args_code}):\n"
            f"    return await _invoke(_target, ctx, {{{kwargs_map}}})\n"
        )
    else:
        src = (
            "async def __handler(ctx: Context):\n"
            "    return await _invoke(_target, ctx, {})\n"
        )
    exec(src, namespace)
    handler = namespace["__handler"]
    handler.__name__ = fn.__name__
    handler.__doc__ = (fn.__doc__ or "").strip()
    handler.__annotations__ = {"ctx": Context, "return": str}
    for name, ann in getattr(fn, "__annotations__", {}).items():
        if name not in ("ctx", "return"):
            handler.__annotations__[name] = _schema_annotation(ann)

    mcp.tool(name=fn.__name__, description=handler.__doc__)(handler)


ALL_TOOLS = (
    get_scheme_info,
    initiate_pm_kisan_status_check,
    check_pm_kisan_status_with_otp,
    initiate_pmfby_status_check,
    check_pmfby_status_with_otp,
    check_shc_status,
    pmkisan_grievance_send_otp,
    check_smam_scheme_status,
    pmkisan_submit_grievance,
    pmkisan_grievance_status,
    initiate_pmfby_grievance_otp,
    check_pmfby_grievance_otp,
    pmfby_grievance_status,
    pmfby_submit_grievance,
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
    analyze_crop_image,
)

for _tool in ALL_TOOLS:
    register_vistaar_tool(_tool)


if __name__ == "__main__":
    transport = os.getenv("MCP_TRANSPORT", "streamable-http")
    mcp.run(transport=transport)