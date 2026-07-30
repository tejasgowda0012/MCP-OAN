import os
import casbin
from casbin_sqlalchemy_adapter import Adapter
import logging

logger = logging.getLogger(__name__)

# Calculate absolute paths to the model and policy files
AUTHZ_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(AUTHZ_DIR, "model.conf")
DB_PATH = os.path.join(AUTHZ_DIR, "mcp_auth.db")

# Singleton Enforcer instance
_enforcer = None

def get_enforcer() -> casbin.Enforcer:
    global _enforcer
    if _enforcer is None:
        try:
            adapter = Adapter(f'sqlite:///{DB_PATH}')
            _enforcer = casbin.Enforcer(MODEL_PATH, adapter)
            logger.info("Casbin enforcer initialized successfully with SQLite adapter.")
        except Exception as e:
            logger.error(f"Failed to initialize Casbin enforcer: {e}")
            raise
    return _enforcer
