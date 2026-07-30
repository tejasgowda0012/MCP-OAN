import asyncio
import uuid
import os
from typing import Any

# Ensure we can import from the app
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from vistaar_mcp.authz.provider_registry import registry
from vistaar_mcp.authz.enforcer import get_enforcer
from vistaar_mcp.rbac import enforce_policy
from vistaar_mcp.deps import FarmerContext

class MockRunContext:
    """Mocks the pydantic-ai RunContext which wraps FarmerContext"""
    def __init__(self, deps: FarmerContext):
        self.deps = deps

@enforce_policy(action="execute")
async def dummy_protected_tool(ctx: Any, some_arg: str) -> str:
    """A dummy tool to test RBAC without hitting external APIs."""
    return f"Tool executed successfully with arg: {some_arg}"

async def run_genuine_tests():
    print("=== Running Genuine Auth & RBAC Tests ===")
    
    test_role = f"test_role_{uuid.uuid4().hex[:6]}"
    test_provider = f"test_provider_{uuid.uuid4().hex[:6]}"
    
    print("\n1. Testing Provider Registry (SQLite)")
    provider, api_key = registry.add_provider(test_provider, test_role)
    provider_id = provider["id"]
    print(f"  [SUCCESS] Created provider '{provider_id}' with role '{test_role}'")
    
    # Test lookup
    lookup = registry.lookup_by_api_key(api_key)
    assert lookup is not None, "Failed to lookup valid API key"
    assert lookup["role"] == test_role, "Role mismatch in DB"
    print("  [SUCCESS] API Key hashed and verified correctly in SQLite")
    
    # Test invalid key
    assert registry.lookup_by_api_key("wrong_key") is None
    print("  [SUCCESS] Invalid keys correctly rejected")
    
    print("\n2. Testing Casbin RBAC Enforcement")
    enforcer = get_enforcer()
    
    # Create context with our test role (simulating what ProviderAuthMiddleware does)
    deps = FarmerContext(
        query="test",
        lang_code="en",
        session_id="session1",
        harness=test_role,
        user_id="user1"
    )
    mock_ctx = MockRunContext(deps)
    
    # Scenario A: Tool is NOT allowed (no policy exists yet)
    result = await dummy_protected_tool(mock_ctx, "hello")
    assert "Access Denied" in result, f"Expected Access Denied, got: {result}"
    print("  [SUCCESS] Tool correctly DENIED when policy doesn't exist")
    
    # Scenario B: Tool IS allowed (we add policy)
    enforcer.add_policy(test_role, "dummy_protected_tool", "execute")
    result = await dummy_protected_tool(mock_ctx, "hello")
    assert "Tool executed successfully" in result, f"Expected success, got: {result}"
    print("  [SUCCESS] Tool correctly ALLOWED after policy added")
    
    print("\n3. Cleaning up...")
    registry.delete_provider(provider_id)
    enforcer.remove_policy(test_role, "dummy_protected_tool", "execute")
    print("  [SUCCESS] Test data removed")
    
    print("\n[DONE] All Genuine Tests Passed!")

if __name__ == "__main__":
    asyncio.run(run_genuine_tests())
