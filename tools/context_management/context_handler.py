import json
import os
from typing import Any, Dict

def read_context(path: str) -> Dict[str, Any]:
    if not os.path.exists(path):
        return {}
    with open(path, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except Exception:
            return {}

def write_context(path: str, new_data: Dict[str, Any]) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(new_data, f, indent=4, ensure_ascii=False)

def append_to_context(path: str, entry: Dict[str, Any]) -> None:
    """
    Append a history entry to the context file. Creates file/structure if missing.
    """
    context = read_context(path)
    if not isinstance(context, dict):
        context = {}
    history = context.get("history", [])
    if not isinstance(history, list):
        history = []
    history.append(entry)
    context["history"] = history
    write_context(path, context)
