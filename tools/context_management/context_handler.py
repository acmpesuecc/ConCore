import json
import os
import time
from typing import Any, Dict, List

def read_context(path: str) -> Dict[str, Any]:
    if not os.path.exists(path):
        return {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

def write_context(path: str, data: Dict[str, Any]) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def update_context_from_llm(path: str, update_text: str, source: str = "user") -> None:
    context = read_context(path)
    
    if "history" not in context:
        context["history"] = []
    
    entry = {
        "content": update_text,
        "source": source,
        "timestamp": int(time.time())
    }
    
    context["history"].append(entry)
    
    context["latest_update"] = update_text
    context["last_updated"] = int(time.time())
    
    write_context(path, context)

def append_to_chat_history(path: str, message: Dict[str, Any]) -> None:
    chat_history = read_context(path)
    
    if "messages" not in chat_history:
        chat_history["messages"] = []
    
    chat_history["messages"].append(message)
    
    if len(chat_history["messages"]) > 100:
        chat_history["messages"] = chat_history["messages"][-100:]
    
    write_context(path, chat_history)

def append_dataset_metadata(path: str, metadata: Dict[str, Any]) -> None:
    all_metadata = read_context(path)
    
    if "datasets" not in all_metadata:
        all_metadata["datasets"] = []
    
    all_metadata["datasets"].append(metadata)
    all_metadata["last_updated"] = int(time.time())
    
    write_context(path, all_metadata)

def get_context_summary(path: str, max_entries: int = 5) -> str:
    context = read_context(path)
    history = context.get("history", [])
    
    if not history:
        return "No context available yet."
    
    recent = history[-max_entries:]
    summary_lines = []
    
    for entry in recent:
        content = entry.get("content", "")
        source = entry.get("source", "unknown")
        summary_lines.append(f"[{source}] {content}")
    
    return "\n".join(summary_lines)

def search_context(path: str, query: str, max_results: int = 5) -> List[Dict[str, Any]]:
    context = read_context(path)
    history = context.get("history", [])
    
    query_lower = query.lower()
    results = []
    
    for entry in history:
        content = entry.get("content", "").lower()
        if query_lower in content:
            results.append(entry)
    
    return results[-max_results:]