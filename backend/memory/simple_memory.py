"""
Simple text-based persistent memory using Supabase.
Table: user_memories (id, user_id, content, created_at). No embeddings, no vectors.
"""

import logging
from typing import Dict, List

from db import supabase

logger = logging.getLogger(__name__)

# Max memories to fetch for aggregation (oldest first; later override same keys)
RETRIEVE_ALL_LIMIT = 500


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


def retrieve_memories(user_id: str, limit: int = 1) -> List[str]:
    """Return last N memories for user (by created_at desc). Reserved for future use / external callers."""
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


def retrieve_all_memories_asc(user_id: str) -> List[str]:
    """Return ALL memories for user ordered by created_at ASC (oldest first). Used for aggregation; later memories override same attributes."""
    try:
        res = supabase.table("user_memories").select("content").eq(
            "user_id", user_id
        ).order("created_at", desc=False).limit(RETRIEVE_ALL_LIMIT).execute()
        if not res.data:
            return []
        return [row.get("content", "") for row in res.data if row.get("content")]
    except Exception as e:
        logger.warning(f"retrieve_all_memories_asc failed: {e}")
        return []


def _extract_preferences_from_memory(text: str) -> Dict[str, str]:
    """Simple keyword extraction from one memory string. Returns dict of attribute -> value (only keys that matched)."""
    out: Dict[str, str] = {}
    lower = text.lower().strip()
    if not lower:
        return out
    # Diet
    if "vegetarian" in lower:
        out["diet"] = "vegetarian"
    # Eggs (avoid takes precedence if both appear in same message; order of checks matters across memories)
    if "avoid eggs" in lower:
        out["eggs"] = "avoid"
    if "okay with eggs" in lower or "eggs allowed" in lower or "allow eggs" in lower:
        out["eggs"] = "allowed"
    # Breakfast style
    if "south indian" in lower:
        out["breakfast_style"] = "South Indian"
    # Protein
    if "high protein" in lower:
        out["protein"] = "high"
    # Beverage
    if "coffee" in lower:
        if "black coffee" in lower and "without sugar" in lower:
            out["beverage"] = "black coffee without sugar"
        elif "black coffee" in lower:
            out["beverage"] = "black coffee"
        else:
            out["beverage"] = "coffee"
    # Commute
    if "bus" in lower:
        out["commute"] = "bus"
    if "train" in lower:
        out["commute"] = "train"
    if "walk" in lower or "walking" in lower:
        out["commute"] = "walk"
    # Location
    if "chennai" in lower:
        out["location"] = "Chennai"
    if "mumbai" in lower:
        out["location"] = "Mumbai"
    if "delhi" in lower:
        out["location"] = "Delhi"
    return out


def consolidate_memories_to_preferences(memories: List[str]) -> Dict[str, str]:
    """Merge all memories into one preference dict. Process in created_at ASC order; later entries override only same attribute keys."""
    prefs: Dict[str, str] = {}
    for content in memories:
        if not (content and content.strip()):
            continue
        extracted = _extract_preferences_from_memory(content)
        for key, value in extracted.items():
            prefs[key] = value
    return prefs


def format_personal_memory_block(memories: List[str]) -> str:
    """Format raw personal memory list for injection into agent prompts. Preserves full free text."""
    if not memories:
        return ""
    lines = [m.strip() for m in memories if m and str(m).strip()]
    if not lines:
        return ""
    return "\n".join(f"- {line}" for line in lines)


def format_preferences_block(prefs: Dict[str, str]) -> str:
    """Format preference dict as a single consolidated block for agent context."""
    if not prefs:
        return ""
    label_map = {
        "diet": "Diet",
        "eggs": "Eggs",
        "breakfast_style": "Breakfast style",
        "protein": "Protein preference",
        "beverage": "Beverage",
        "commute": "Commute",
        "location": "Location",
    }
    lines = []
    for key, value in prefs.items():
        label = label_map.get(key, key.replace("_", " ").title())
        lines.append(f"- {label}: {value}")
    return "\n".join(lines)
