import os
from supabase import create_client, Client

_supabase_client = None


def get_supabase_client() -> Client:
    """獲取 Supabase 客戶端實例 (Singleton)"""
    global _supabase_client

    if _supabase_client is None:
        url = os.environ.get("SUPABASE_URL")
        key = os.environ.get("SUPABASE_KEY")

        if not url or not key:
            raise ValueError(
                "Missing SUPABASE_URL or SUPABASE_KEY in environment variables"
            )

        _supabase_client = create_client(url, key)

    return _supabase_client
