import json
import os
import time
from typing import Generator, Dict, Any
from dotenv import load_dotenv
import google.generativeai as genai

from tools.script_executor.sandbox import run_script_safely
from tools.context_management.context_handler import read_context, write_context, append_to_context

# =========================================================
# INITIAL SETUP
# =========================================================
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

SCRIPTS_DIR_NAME = "scripts"
COTAS_LOG = "cotas-log.json"
FINAL_INSIGHT = "final-insight.txt"
MAX_SCRIPT_SAVE_BYTES = 1_000_000

# =========================================================
# UTILS
# =========================================================
def _ensure_session_dirs(session_path: str):
    scripts_dir = os.path.join(session_path, SCRIPTS_DIR_NAME)
    os.makedirs(scripts_dir, exist_ok=True)
    return scripts_dir

def _read_json(path: str) -> Dict[str, Any]:
    if not os.path.exists(path):
        return {}
    with open(path, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except Exception:
            return {}

def _write_json(path: str, data: Dict[str, Any]):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def _append_log(log_path: str, entry: Dict[str, Any]):
    log = _read_json(log_path) or {"steps": []}
    log.setdefault("steps", []).append(entry)
    _write_json(log_path, log)

def _save_script(scripts_dir: str, step: int, content: str) -> str:
    filename = f"act_{step:03d}.py"
    path = os.path.join(scripts_dir, filename)
    if len(content.encode("utf-8")) > MAX_SCRIPT_SAVE_BYTES:
        content = content.encode("utf-8")[:MAX_SCRIPT_SAVE_BYTES].decode("utf-8", "ignore")
        content += "\n# Truncated due to size limit\n"
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    return path

def _summarize_with_model(model, context: Dict[str, Any], metadata: Dict[str, Any], last_output: str) -> str:
    prompt = f"""You are synthesizing the results of a complete data analysis session.

CONTEXT SUMMARY:
{json.dumps(context, indent=2)}

DATASET INFORMATION:
{json.dumps(metadata, indent=2)}

MOST RECENT OUTPUT:
{last_output}

TASK: Write a comprehensive final insight that:
1. Highlights the most important discoveries and patterns found
2. Connects findings across different analysis steps
3. Provides actionable conclusions
4. Is clear, concise, and professionally written

Respond with ONLY the final insight paragraph (no JSON, no formatting).
"""
    try:
        resp = model.generate_content(prompt)
        return getattr(resp, "text", str(resp)).strip()
    except Exception as e:
        return last_output or f"Summary generation failed: {str(e)}"

def _search_context(query: str, context: Dict[str, Any]) -> str:
    """
    SEARCH action: searches only session context (user input + previous steps)
    """
    history = context.get("history", [])
    results = []
    query_lower = query.lower()
    
    for entry in history:
        entry_text = entry.get("content", "") or entry.get("insight", "")
        if query_lower in entry_text.lower():
            results.append(f"[Step {entry.get('step', '?')}] {entry_text}")
    
    if not results:
        return f"No context entries found matching query: '{query}'"
    
    return "\n\n".join(results[:5])  # Return top 5 matches

# =========================================================
# COTAS ENGINE
# =========================================================
def cotas_stream(session_path: str, context_file: str, metadata_file: str, max_loops: int = 20) -> Generator[str, None, None]:
    """
    CoTAS loop: THINK → SEARCH → ACT → INSIGHT
    Fully stateful: all scripts, logs, and context updates persisted.
    """
    scripts_dir = _ensure_session_dirs(session_path)
    cotas_log_path = os.path.join(session_path, COTAS_LOG)
    final_insight_path = os.path.join(session_path, FINAL_INSIGHT)

    metadata = _read_json(metadata_file)
    context = read_context(context_file) or {}
    model = genai.GenerativeModel("gemini-1.5-flash")
    last_output = context.get("last_output") if isinstance(context, dict) else None

    for step in range(1, max_loops + 1):
        yield f"--- Step {step} ---"

        thought_prompt = f"""You are an autonomous data analysis agent following the CoTAS methodology.

CURRENT SESSION CONTEXT:
{json.dumps(context, indent=2)}

DATASET METADATA:
{json.dumps(metadata, indent=2)}

PREVIOUS OUTPUT:
{last_output or "No previous output"}

YOUR TASK:
Analyze the current state and decide the next action. Choose ONE of:

1. THINK - Reasoning and planning (use when you need to analyze what to do next)
2. SEARCH - Query the session context (use when you need to recall previous findings)
3. ACT - Execute Python code (use when you need to analyze data, create visualizations, or compute results)

CRITICAL: Respond with ONLY valid JSON in this EXACT format:
{{
  "action": "THINK",
  "content": "Your reasoning about what to do next and why"
}}

OR

{{
  "action": "SEARCH",
  "content": "search query keywords"
}}

OR

{{
  "action": "ACT",
  "content": "import pandas as pd\\n# Your complete Python code here"
}}

No additional text before or after the JSON. Ensure the JSON is properly formatted.
"""

        # ---------- MODEL DECISION ----------
        try:
            response = model.generate_content(thought_prompt)
            response_text = getattr(response, "text", str(response)).strip()
            
            # Try to extract JSON if wrapped in markdown
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0].strip()
            
            decision = json.loads(response_text)
            
            # Validate required fields
            if "action" not in decision or "content" not in decision:
                raise ValueError("Missing required fields 'action' or 'content'")
                
        except Exception as e:
            err_msg = f"Failed to parse model decision: {str(e)}\nResponse: {response_text[:500]}"
            entry = {"step": step, "action": "ERROR_PARSE", "error": err_msg, "timestamp": int(time.time())}
            _append_log(cotas_log_path, entry)
            append_to_context(context_file, entry)
            yield f"❌ ERROR: {err_msg}"
            break

        action = decision.get("action", "THINK").upper()
        content = decision.get("content", "")
        timestamp = int(time.time())

        # ---------- THINK ----------
        if action == "THINK":
            entry = {"step": step, "action": "THINK", "content": content, "timestamp": timestamp}
            _append_log(cotas_log_path, entry)
            append_to_context(context_file, entry)
            context["last_output"] = content
            write_context(context_file, context)
            last_output = content
            
            yield f"💭 THINK:"
            yield f"{content}"
            yield f"✓ Reasoning recorded"
            continue

        # ---------- SEARCH ----------
        elif action == "SEARCH":
            search_result = _search_context(content, context)
            entry = {
                "step": step, 
                "action": "SEARCH", 
                "query": content, 
                "result": search_result, 
                "timestamp": timestamp
            }
            _append_log(cotas_log_path, entry)
            append_to_context(context_file, entry)
            context["last_output"] = search_result
            write_context(context_file, context)
            last_output = search_result
            
            yield f"🔍 SEARCH: '{content}'"
            yield f"Results:\n{search_result}"
            yield f"✓ Search complete"
            continue

        # ---------- ACT ----------
        elif action == "ACT":
            yield f"⚙️ ACT: Executing generated code..."
            
            try:
                script_path = _save_script(scripts_dir, step, content)
                yield f"📝 Script saved: {os.path.basename(script_path)}"
            except Exception as e:
                entry = {"step": step, "action": "ACT_SAVE_ERROR", "error": str(e), "timestamp": timestamp}
                _append_log(cotas_log_path, entry)
                append_to_context(context_file, entry)
                yield f"❌ Error saving script: {str(e)}"
                break

            try:
                run_result = run_script_safely(content)
            except Exception as e:
                run_result = {"stdout": "", "stderr": f"Execution failed: {str(e)}"}

            stdout = run_result.get("stdout", "")
            stderr = run_result.get("stderr", "")
            
            act_entry = {
                "step": step,
                "action": "ACT",
                "script": os.path.relpath(script_path, session_path),
                "stdout": stdout,
                "stderr": stderr,
                "timestamp": timestamp
            }
            _append_log(cotas_log_path, act_entry)
            append_to_context(context_file, act_entry)

            if stderr:
                yield f"⚠️ Execution errors:\n{stderr}"
            if stdout:
                yield f"📊 Output:\n{stdout}"

            # Generate insight from execution results
            feedback_prompt = f"""Analyze the results of this code execution:

CODE EXECUTED:
{content}

STANDARD OUTPUT:
{stdout if stdout else "(empty)"}

ERROR OUTPUT:
{stderr if stderr else "(none)"}

TASK: Provide a structured insight with:
1. What was accomplished
2. Key findings or results
3. What should be done next

Respond with ONLY the insight text (no JSON, no extra formatting).
"""
            try:
                feedback = model.generate_content(feedback_prompt)
                insight = getattr(feedback, "text", "").strip()
            except Exception as e:
                insight = stdout or stderr or f"Insight generation failed: {str(e)}"

            context["last_output"] = insight
            context.setdefault("insight_history", []).append(insight)
            write_context(context_file, context)
            last_output = insight
            
            yield f"💡 INSIGHT:"
            yield f"{insight}"
            yield f"✓ Step {step} complete"

    # ---------- FINAL SUMMARY ----------
    yield "\n" + "="*60
    yield "GENERATING FINAL SUMMARY"
    yield "="*60
    
    final_summary = _summarize_with_model(model, read_context(context_file), metadata, last_output or "")
    
    try:
        with open(final_insight_path, "w", encoding="utf-8") as f:
            f.write(final_summary)
        yield f"📄 Final insight saved to: {FINAL_INSIGHT}"
    except Exception as e:
        yield f"⚠️ Could not save final insight: {str(e)}"
    
    final_entry = {
        "step": "final", 
        "action": "FINAL_SUMMARY", 
        "summary": final_summary,
        "timestamp": int(time.time())
    }
    _append_log(cotas_log_path, final_entry)
    append_to_context(context_file, final_entry)
    
    yield "\n" + "="*60
    yield "🎯 FINAL INSIGHT:"
    yield "="*60
    yield f"{final_summary}"
    yield "\n✅ Analysis complete"