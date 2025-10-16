import json
import os
import time
from typing import Any, Dict, List

def read_context(path: str) -> Dict[str, Any]:
    """Read JSON context file, return empty dict if not found"""
    if not os.path.exists(path):
        return {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

def write_context(path: str, data: Dict[str, Any]) -> None:
    """Write JSON context file"""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def update_context_from_llm(path: str, update_text: str, source: str = "user") -> None:
    """
    Update context based on LLM-extracted important information.
    Maintains a history of context updates.
    """
    context = read_context(path)
    
    # Ensure history exists
    if "history" not in context:
        context["history"] = []
    
    # Add new context entry
    entry = {
        "content": update_text,
        "source": source,
        "timestamp": int(time.time())
    }
    
    context["history"].append(entry)
    
    # Also maintain a "latest" field for quick access
    context["latest_update"] = update_text
    context["last_updated"] = int(time.time())
    
    write_context(path, context)

def append_to_chat_history(path: str, message: Dict[str, Any]) -> None:
    """
    Append a message to chat history.
    """
    chat_history = read_context(path)
    
    if "messages" not in chat_history:
        chat_history["messages"] = []
    
    chat_history["messages"].append(message)
    
    # Keep only last 100 messages to prevent file bloat
    if len(chat_history["messages"]) > 100:
        chat_history["messages"] = chat_history["messages"][-100:]
    
    write_context(path, chat_history)

def append_dataset_metadata(path: str, metadata: Dict[str, Any]) -> None:
    """
    Append new dataset metadata to the metadata file.
    """
    all_metadata = read_context(path)
    
    if "datasets" not in all_metadata:
        all_metadata["datasets"] = []
    
    all_metadata["datasets"].append(metadata)
    all_metadata["last_updated"] = int(time.time())
    
    write_context(path, all_metadata)

def get_context_summary(path: str, max_entries: int = 5) -> str:
    """
    Get a concise summary of recent context for prompts.
    """
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
    """
    Search through context history for relevant entries.
    Simple keyword-based search.
    """
    context = read_context(path)
    history = context.get("history", [])
    
    query_lower = query.lower()
    results = []
    
    for entry in history:
        content = entry.get("content", "").lower()
        if query_lower in content:
            results.append(entry)
    
    return results[-max_results:]  # Return most recent matches