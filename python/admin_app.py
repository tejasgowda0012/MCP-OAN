import os
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import secrets
from pydantic import BaseModel
from typing import List, Optional

# Database and Casbin
from vistaar_mcp.authz.provider_registry import registry
from vistaar_mcp.authz.enforcer import get_enforcer
from server import ALL_TOOLS

app = FastAPI(title="Vistaar MCP Admin Dashboard")
app.mount("/static", StaticFiles(directory="static"), name="static")
security = HTTPBasic()

# Setup Admin Credentials from Env
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "changeme")

def verify_admin(credentials: HTTPBasicCredentials = Depends(security)):
    correct_username = secrets.compare_digest(credentials.username, ADMIN_USERNAME)
    correct_password = secrets.compare_digest(credentials.password, ADMIN_PASSWORD)
    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username

# --- Models ---
class ProviderCreate(BaseModel):
    name: str
    role: str

class ProviderUpdate(BaseModel):
    active: Optional[bool] = None
    role: Optional[str] = None

class RoleCreate(BaseModel):
    name: str
    tools: List[str]

# --- Static UI ---
# We will create a templates dir shortly
templates_dir = os.path.join(os.path.dirname(__file__), "templates")
os.makedirs(templates_dir, exist_ok=True)

@app.get("/", response_class=HTMLResponse)
async def serve_admin_ui(admin: str = Depends(verify_admin)):
    with open(os.path.join(templates_dir, "admin.html"), "r") as f:
        return f.read()

# --- API Endpoints ---

@app.get("/api/tools", dependencies=[Depends(verify_admin)])
async def list_tools():
    return [{"name": fn.__name__, "description": (fn.__doc__ or "").strip()} for fn in ALL_TOOLS]

@app.get("/api/roles", dependencies=[Depends(verify_admin)])
async def list_roles():
    enforcer = get_enforcer()
    # policies are [ptype, role, tool, action]
    policies = enforcer.get_policy()
    roles = {}
    for policy in policies:
        if len(policy) >= 3:
            role_name = policy[0]
            tool_name = policy[1]
            if role_name not in roles:
                roles[role_name] = []
            roles[role_name].append(tool_name)
    return [{"name": name, "tools": tools} for name, tools in roles.items()]

@app.post("/api/roles", dependencies=[Depends(verify_admin)])
async def create_role(role_data: RoleCreate):
    enforcer = get_enforcer()
    for tool in role_data.tools:
        enforcer.add_policy(role_data.name, tool, "execute")
    return {"message": "Role created successfully"}

@app.delete("/api/roles/{role_name}", dependencies=[Depends(verify_admin)])
async def delete_role(role_name: str):
    enforcer = get_enforcer()
    # Check if providers are using this role
    providers = registry.list_providers()
    for p in providers:
        if p["role"] == role_name:
            raise HTTPException(status_code=400, detail=f"Cannot delete role. Provider '{p['name']}' is using it.")
            
    policies = enforcer.get_filtered_policy(0, role_name)
    for p in policies:
        enforcer.remove_policy(*p)
    return {"message": "Role deleted successfully"}

@app.put("/api/roles/{role_name}", dependencies=[Depends(verify_admin)])
async def update_role(role_name: str, role_data: RoleCreate):
    enforcer = get_enforcer()
    # Delete old policies
    policies = enforcer.get_filtered_policy(0, role_name)
    for p in policies:
        enforcer.remove_policy(*p)
    # Add new policies
    for tool in role_data.tools:
        enforcer.add_policy(role_name, tool, "execute")
    return {"message": "Role updated successfully"}

@app.get("/api/providers", dependencies=[Depends(verify_admin)])
async def list_providers():
    providers = registry.list_providers()
    # Remove api_key_hash before sending to frontend
    for p in providers:
        p.pop("api_key_hash", None)
    return providers

@app.post("/api/providers", dependencies=[Depends(verify_admin)])
async def create_provider(data: ProviderCreate):
    try:
        provider, api_key = registry.add_provider(data.name, data.role)
        provider.pop("api_key_hash", None)
        return {"provider": provider, "api_key": api_key}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.patch("/api/providers/{provider_id}", dependencies=[Depends(verify_admin)])
async def update_provider(provider_id: str, data: ProviderUpdate):
    registry.update_provider(provider_id, active=data.active, role=data.role)
    return {"message": "Provider updated successfully"}

@app.delete("/api/providers/{provider_id}", dependencies=[Depends(verify_admin)])
async def delete_provider(provider_id: str):
    registry.delete_provider(provider_id)
    return {"message": "Provider deleted successfully"}

@app.post("/api/providers/{provider_id}/regenerate", dependencies=[Depends(verify_admin)])
async def regenerate_provider_key(provider_id: str):
    try:
        new_key = registry.regenerate_key(provider_id)
        return {"api_key": new_key}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("ADMIN_PORT", 3002))
    uvicorn.run(app, host="0.0.0.0", port=port)
