import os
import sqlite3
import hashlib
import secrets
from datetime import datetime
from typing import Optional, List, Dict, Any
import contextlib

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "mcp_auth.db")

class ProviderRegistry:
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        self._init_db()

    @contextlib.contextmanager
    def _get_conn(self):
        # Using WAL mode for better concurrency between the API server and admin app
        conn = sqlite3.connect(self.db_path, timeout=10.0)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL")
        try:
            yield conn
        finally:
            conn.close()

    def _init_db(self):
        with self._get_conn() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS providers (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    api_key_hash TEXT NOT NULL,
                    role TEXT NOT NULL,
                    active BOOLEAN DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_key_rotation TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()

    def _hash_key(self, api_key: str) -> str:
        return hashlib.sha256(api_key.encode("utf-8")).hexdigest()

    def _generate_slug(self, name: str) -> str:
        base = name.lower().replace(" ", "-")
        import string
        safe = "".join(c for c in base if c in string.ascii_lowercase + string.digits + "-")
        return safe or "provider"

    def add_provider(self, name: str, role: str) -> tuple[Dict[str, Any], str]:
        """Creates a provider and returns (provider_dict, plaintext_api_key)."""
        provider_id = self._generate_slug(name)
        
        # Ensure ID uniqueness
        base_id = provider_id
        counter = 1
        with self._get_conn() as conn:
            while conn.execute("SELECT 1 FROM providers WHERE id = ?", (provider_id,)).fetchone():
                provider_id = f"{base_id}-{counter}"
                counter += 1

        raw_key = f"vistaar_{secrets.token_urlsafe(48)}"
        hashed_key = self._hash_key(raw_key)

        with self._get_conn() as conn:
            conn.execute(
                "INSERT INTO providers (id, name, api_key_hash, role) VALUES (?, ?, ?, ?)",
                (provider_id, name, hashed_key, role)
            )
            conn.commit()

        return self.get_provider(provider_id), raw_key

    def get_provider(self, provider_id: str) -> Optional[Dict[str, Any]]:
        with self._get_conn() as conn:
            row = conn.execute("SELECT * FROM providers WHERE id = ?", (provider_id,)).fetchone()
            return dict(row) if row else None

    def list_providers(self) -> List[Dict[str, Any]]:
        with self._get_conn() as conn:
            rows = conn.execute("SELECT * FROM providers ORDER BY created_at DESC").fetchall()
            return [dict(row) for row in rows]

    def update_provider(self, provider_id: str, active: Optional[bool] = None, role: Optional[str] = None):
        updates = []
        params = []
        if active is not None:
            updates.append("active = ?")
            params.append(1 if active else 0)
        if role is not None:
            updates.append("role = ?")
            params.append(role)
        
        if not updates:
            return

        params.append(provider_id)
        query = f"UPDATE providers SET {', '.join(updates)} WHERE id = ?"
        with self._get_conn() as conn:
            conn.execute(query, params)
            conn.commit()

    def delete_provider(self, provider_id: str):
        with self._get_conn() as conn:
            conn.execute("DELETE FROM providers WHERE id = ?", (provider_id,))
            conn.commit()

    def regenerate_key(self, provider_id: str) -> str:
        """Regenerates the API key, updates the DB, and returns the new plaintext key."""
        raw_key = f"vistaar_{secrets.token_urlsafe(48)}"
        hashed_key = self._hash_key(raw_key)
        now = datetime.utcnow().isoformat()
        
        with self._get_conn() as conn:
            conn.execute(
                "UPDATE providers SET api_key_hash = ?, last_key_rotation = ? WHERE id = ?",
                (hashed_key, now, provider_id)
            )
            conn.commit()
        return raw_key

    def lookup_by_api_key(self, api_key: str) -> Optional[Dict[str, Any]]:
        """Returns the provider if the key matches and is active."""
        if not api_key:
            return None
            
        hashed_key = self._hash_key(api_key)
        with self._get_conn() as conn:
            row = conn.execute(
                "SELECT * FROM providers WHERE api_key_hash = ? AND active = 1", 
                (hashed_key,)
            ).fetchone()
            return dict(row) if row else None

registry = ProviderRegistry()
