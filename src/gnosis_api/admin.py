"""Admin CLI for managing API keys."""

from __future__ import annotations

import argparse
import secrets
import sqlite3
from datetime import UTC, datetime

from gnosis_api.config import settings
from gnosis_api.keys import hash_key


def _get_db() -> sqlite3.Connection:
    con = sqlite3.connect(str(settings.keys_db_path))
    con.row_factory = sqlite3.Row
    con.executescript("""
        CREATE TABLE IF NOT EXISTS api_key (
            id INTEGER PRIMARY KEY,
            key_hash TEXT NOT NULL UNIQUE,
            email TEXT NOT NULL,
            tier TEXT NOT NULL DEFAULT 'free',
            created_at TEXT NOT NULL,
            enabled INTEGER NOT NULL DEFAULT 1
        );
        CREATE TABLE IF NOT EXISTS request_log (
            id INTEGER PRIMARY KEY,
            key_hash TEXT NOT NULL,
            timestamp REAL NOT NULL
        );
        CREATE INDEX IF NOT EXISTS idx_request_log_key_ts ON request_log(key_hash, timestamp);
    """)
    return con


def create_key(email: str, tier: str = "free") -> str:
    raw_key = f"gn_{secrets.token_urlsafe(32)}"
    key_hash = hash_key(raw_key)

    db = _get_db()
    db.execute(
        "INSERT INTO api_key (key_hash, email, tier, created_at) VALUES (?, ?, ?, ?)",
        (key_hash, email, tier, datetime.now(UTC).isoformat()),
    )
    db.commit()
    db.close()
    return raw_key


def revoke_key(email: str) -> bool:
    db = _get_db()
    cursor = db.execute("UPDATE api_key SET enabled = 0 WHERE email = ?", (email,))
    db.commit()
    db.close()
    return cursor.rowcount > 0


def list_keys() -> list[dict]:
    db = _get_db()
    rows = db.execute("SELECT email, tier, created_at, enabled FROM api_key").fetchall()
    db.close()
    return [dict(r) for r in rows]


def main():
    parser = argparse.ArgumentParser(description="Gnosis API key management")
    sub = parser.add_subparsers(dest="command")

    create = sub.add_parser("create", help="Create a new API key")
    create.add_argument("email")
    create.add_argument("--tier", default="free", choices=["free", "paid"])

    revoke = sub.add_parser("revoke", help="Revoke keys for an email")
    revoke.add_argument("email")

    sub.add_parser("list", help="List all API keys")

    args = parser.parse_args()

    if args.command == "create":
        key = create_key(args.email, args.tier)
        print(f"API key created: {key}")
        print("Save this key — it cannot be retrieved later.")
    elif args.command == "revoke":
        if revoke_key(args.email):
            print(f"Keys revoked for {args.email}")
        else:
            print(f"No keys found for {args.email}")
    elif args.command == "list":
        keys = list_keys()
        if not keys:
            print("No API keys found")
        for k in keys:
            status = "active" if k["enabled"] else "revoked"
            print(f"  {k['email']} ({k['tier']}) — {status} — {k['created_at']}")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
