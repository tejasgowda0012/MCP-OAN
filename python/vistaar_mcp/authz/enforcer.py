import os
import casbin
import logging

logger = logging.getLogger(__name__)

# Calculate absolute paths to the model and policy files
AUTHZ_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(AUTHZ_DIR, "model.conf")
POLICY_PATH = os.path.join(AUTHZ_DIR, "policy.csv")

# Singleton Enforcer instance
_enforcer = None

def get_enforcer() -> casbin.Enforcer:
    global _enforcer
    if _enforcer is None:
        try:
            _enforcer = casbin.Enforcer(MODEL_PATH, POLICY_PATH)
            logger.info("Casbin enforcer initialized successfully.")
        except Exception as e:
            logger.error(f"Failed to initialize Casbin enforcer: {e}")
            raise
    return _enforcer
