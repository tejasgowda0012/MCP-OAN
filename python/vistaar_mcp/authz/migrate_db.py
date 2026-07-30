import os
import sys

# Add python dir to path so we can import vistaar_mcp
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import casbin
from casbin_sqlalchemy_adapter import Adapter
from vistaar_mcp.authz.provider_registry import registry, DB_PATH
import csv

def migrate():
    print(f"Migrating to SQLite DB at: {DB_PATH}")
    
    # 1. Initialize provider registry (this creates the providers table)
    print("Initializing providers table...")
    registry._init_db()
    
    # 2. Migrate Casbin policies
    print("Migrating Casbin policies...")
    adapter = Adapter(f'sqlite:///{DB_PATH}')
    model_path = os.path.join(os.path.dirname(__file__), "model.conf")
    csv_path = os.path.join(os.path.dirname(__file__), "policy.csv")
    
    # Initialize enforcer with the SQLite adapter
    e = casbin.Enforcer(model_path, adapter)
    
    # Read the existing CSV and add the internal role mappings instead
    if os.path.exists(csv_path):
        with open(csv_path, 'r') as f:
            reader = csv.reader(f)
            # Find all unique tools assigned to 'chat'
            tools = []
            for row in reader:
                row = [x.strip() for x in row]
                if len(row) >= 4 and row[1] == 'chat':
                    tools.append(row[2])
                    
        print(f"Found {len(tools)} tools. Assigning to 'internal' role...")
        for tool in tools:
            # Add policy: p, internal, tool, execute
            e.add_policy("internal", tool, "execute")
        
        print("Policies migrated to SQLite.")
    else:
        print("policy.csv not found, skipping Casbin migration.")

    # 3. Create the internal provider for bharat-oan-api
    existing = registry.get_provider("bharat-oan-api-internal")
    if not existing:
        print("Creating internal provider...")
        provider, api_key = registry.add_provider("Bharat OAN API (Internal)", "internal")
        
        # We need to manually set the ID to be exactly 'bharat-oan-api-internal' 
        # instead of the auto-generated slug to ensure consistency
        with registry._get_conn() as conn:
            conn.execute("UPDATE providers SET id = 'bharat-oan-api-internal' WHERE id = ?", (provider['id'],))
            conn.commit()
            
        print(f"\nSUCCESS! Generated internal API key: {api_key}")
        print("SAVE THIS KEY. You need to put this in your .env file as MCP_API_KEY")
    else:
        print("Internal provider already exists.")

if __name__ == "__main__":
    migrate()
