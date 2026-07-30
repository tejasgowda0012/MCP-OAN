"""
Role-Based Access Control (RBAC) for MCP tools.

Provides a `requires_role` decorator that can be applied to tool functions
to restrict access based on the user's role in FarmerContext.

Usage:
    from vistaar_mcp.rbac import requires_role

    @requires_role(["farmer", "staff"])
    async def some_restricted_tool(ctx, ...):
        ...

When a user with an unauthorized role calls the tool, it returns a
human-readable denial string instead of raising an exception, so the
LLM can relay the message to the user gracefully.
"""
from __future__ import annotations

import functools
import inspect
import logging
from typing import Any, Callable, Sequence

logger = logging.getLogger(__name__)


from vistaar_mcp.authz.enforcer import get_enforcer

def enforce_policy(action: str = "execute") -> Callable:
    """Decorator that enforces Casbin policies for tools.

    Args:
        action: The action to enforce (e.g., 'execute').

    Returns:
        Decorated function that checks `enforcer.enforce()` before execution.
    """
    def decorator(fn: Callable) -> Callable:
        @functools.wraps(fn)
        async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
            ctx = _extract_ctx(args, kwargs)
            if ctx is not None:
                harness = getattr(getattr(ctx, "deps", None), "harness", "unknown")
                enforcer = get_enforcer()
                
                # Check policy: enforce(sub, obj, act)
                # Note: fn.__name__ gives us the original tool function name (e.g., 'search_terms')
                tool_name = fn.__name__
                if not enforcer.enforce(harness, tool_name, action):
                    logger.warning(
                        "Casbin RBAC denied: harness=%s tool=%s action=%s",
                        harness, tool_name, action,
                    )
                    return (
                        f"Access Denied: You do not have permission to use the tool '{tool_name}' "
                        f"from your current interface."
                    )
            if inspect.iscoroutinefunction(fn):
                return await fn(*args, **kwargs)
            return fn(*args, **kwargs)

        @functools.wraps(fn)
        def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
            ctx = _extract_ctx(args, kwargs)
            if ctx is not None:
                harness = getattr(getattr(ctx, "deps", None), "harness", "unknown")
                enforcer = get_enforcer()
                
                tool_name = fn.__name__
                if not enforcer.enforce(harness, tool_name, action):
                    logger.warning(
                        "Casbin RBAC denied: harness=%s tool=%s action=%s",
                        harness, tool_name, action,
                    )
                    return (
                        f"Access Denied: You do not have permission to use the tool '{tool_name}' "
                        f"from your current interface."
                    )
            return fn(*args, **kwargs)

        if inspect.iscoroutinefunction(fn):
            return async_wrapper
        return sync_wrapper

    return decorator


def _extract_ctx(args: tuple, kwargs: dict) -> Any:
    """Try to find the RunContext/ctx object from tool function arguments."""
    if "ctx" in kwargs:
        return kwargs["ctx"]
    if args:
        return args[0]
    return None
