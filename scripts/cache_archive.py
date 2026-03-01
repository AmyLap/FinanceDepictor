"""Simple JSON-backed cache manager for parsed statement files.

Stores a mapping of filename -> list-of-transaction-rows (as lists).
Used by the upload flow to avoid re-parsing the same file.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

CACHE_PATH = Path("logs") / "cache.json"


def _ensure_cache_file() -> None:
    CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
    if not CACHE_PATH.exists():
        CACHE_PATH.write_text(json.dumps({}))


def load_cache() -> Dict[str, List[List[Any]]]:
    _ensure_cache_file()
    try:
        with open(CACHE_PATH, "r", encoding="utf-8") as fh:
            return json.load(fh)
    except Exception:
        return {}


def save_cache(cache: Dict[str, List[List[Any]]]) -> None:
    _ensure_cache_file()
    with open(CACHE_PATH, "w", encoding="utf-8") as fh:
        json.dump(cache, fh, ensure_ascii=False, indent=4)


def get_cached_transactions(filename: str) -> Optional[List[List[Any]]]:
    cache = load_cache()
    return cache.get(filename)


def add_cache_entries(filename: str, transactions: List[List[Any]]) -> None:
    cache = load_cache()
    if filename not in cache:
        cache[filename] = []
    cache[filename] += transactions
    save_cache(cache)
