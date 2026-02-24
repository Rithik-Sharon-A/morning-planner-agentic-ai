"""
Simple text-based persistent memory using Supabase.
Table: user_memories (id, user_id, content, created_at). No embeddings, no vectors.
"""

import logging
from typing import List

from db import supabase

logger = logging.getLogger(__name__)


def add_memory(user_id: str, content: str) -> bool:
    """Insert a memory row. Returns True on success."""
    try:
        if not content or not content.strip():
            logger.warning("add_memory: empty content")
            return False
        supabase.table("user_memories").insert({
            "user_id": user_id,
            "content": content.strip(),
        }).execute()
        logger.info(f"add_memory: stored for user_id={user_id}")
        return True
    except Exception as e:
        logger.error(f"add_memory failed: {e}")
        return False


def retrieve_memories(user_id: str, limit: int = 5) -> List[str]:
    """Return last N memories for user (by created_at desc). If Supabase unavailable, return []."""
    try:
        res = supabase.table("user_memories").select("content").eq(
            "user_id", user_id
        ).order("created_at", desc=True).limit(limit).execute()
        if not res.data:
            return []
        return [row.get("content", "") for row in res.data if row.get("content")]
    except Exception as e:
        logger.warning(f"retrieve_memories failed: {e}")
        return []
