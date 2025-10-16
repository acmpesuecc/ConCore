# Contributing to Data Copilot

Thank you for your interest in contributing to Data Copilot! This document provides guidelines and structure information to help you contribute effectively.

## Project Structure

### High-Level Architecture

```
┌─────────────────┐
│   Frontend UI   │  (templates/index.html)
│  (HTML/JS/CSS)  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   Flask API     │  (app.py)
│   - Routes      │
│   - Session Mgmt│
└────────┬────────┘
         │
         ▼
┌─────────────────────────────────┐
│        Tools Layer              │
├─────────────────────────────────┤
│ • Context Management            │
│   - Read/write context          │
│   - Chat history tracking       │
│                                 │
│ • Data Ingestion                │
│   - File parsing (CSV/Excel/DB) │
│   - LLM metadata extraction     │
│                                 │
│ • LLM Orchestrator              │
│   - Chat message processing     │
│   - CoTAS autonomous analysis   │
│                                 │
│ • Script Executor               │
│   - Sandboxed Python execution  │
└─────────────────────────────────┘
         │
         ▼
┌─────────────────┐
│  Storage Layer  │
│  (session dirs) │
│  - datasets     │
│  - scripts      │
│  - results      │
│  - context JSON │
└─────────────────┘
```

### Component Breakdown

#### 1. **app.py** - Main Flask Application
- Defines API routes (`/create-session`, `/chat`, `/upload-file`, `/generate-insights`)
- Manages session directory structure
- Handles file uploads and streaming responses

#### 2. **tools/context_management/context_handler.py**
- `read_context()` - Loads JSON context files
- `write_context()` - Saves JSON context files
- `update_context_from_llm()` - Appends timestamped context entries
- `append_to_chat_history()` - Maintains conversation history
- `append_dataset_metadata()` - Stores dataset information

#### 3. **tools/data_ingestion/parser.py**
- `handle_file_upload()` - Main entry point for file processing
- `extract_metadata_with_llm()` - Uses Gemini to analyze dataset structure
- Supports CSV, Excel, SQLite, JSON formats
- Extracts columns, row counts, data types, and sample data

#### 4. **tools/llm/orchestrator.py**
- `process_user_message()` - Handles chat interactions
- `cotas_generate_insights()` - Autonomous analysis loop
  - **THINK**: Agent reasons about next steps
  - **ACT**: Agent writes and executes Python code
  - **DONE**: Agent provides final insights
- Uses Google Gemini API for decision-making

#### 5. **tools/script_executor/sandbox.py**
- `run_script_safely()` - Executes Python in subprocess
- Timeout protection (default 30s)
- Output truncation (50,000 chars max)
- Error handling and cleanup

#### 6. **templates/index.html**
- Single-page application UI
- Real-time chat interface
- File upload handling
- Server-Sent Events (SSE) for streaming insights
- Session management UI

### Data Flow Example

**User uploads CSV → Analysis**
```
1. User selects file in UI
2. Frontend sends POST to /upload-file
3. parser.py saves file and extracts metadata
4. Gemini analyzes structure and generates insights
5. Metadata saved to dataset_metadata.json
6. Context updated with dataset description
7. Response returned to frontend

User clicks "Generate Insights"
8. Frontend opens SSE connection to /generate-insights
9. orchestrator.py starts CoTAS loop
10. For each step:
    - Gemini decides: THINK, ACT, or DONE
    - If ACT: code written and executed by sandbox.py
    - Results streamed back to frontend in real-time
11. Loop continues until DONE or max_loops reached
12. Final insights saved and displayed
```

## Pull Request Guidelines

### Before Submitting

1. **Fork the repository** and create your branch from `main`
2. **Test your changes** locally with the setup instructions
3. **Follow existing code style** (PEP 8 for Python)
4. **Update documentation** if you're changing functionality

### PR Requirements

Every pull request **MUST** include a clear 5-line explanation addressing:

#### For Bug Fixes:
```
1. What was the problem? (describe the bug/issue)
2. What caused it? (root cause analysis)
3. What solution did you use? (approach/library/technique)
4. How did you implement it? (specific changes made)
5. How was it tested? (verification steps)
```

#### For Features:
```
1. What does this feature do? (functionality description)
2. Why is it needed? (problem it solves)
3. What technologies/approaches were used? (implementation details)
4. How does it integrate? (architecture changes)
5. How was it tested? (test cases/scenarios)
```

### Example PR Description

```markdown
## Bug Fix: File Upload Fails for Large CSV Files

**Problem:** Uploading CSV files larger than 50MB resulted in timeout errors.

**Root Cause:** Flask's default timeout (30s) was insufficient for processing 
large files during pandas read_csv() operations.

**Solution Used:** Implemented chunked file reading with pandas' `chunksize` 
parameter and increased Flask's request timeout to 120 seconds.

**Implementation:** Modified parser.py line 85 to use 
`pd.read_csv(file_path, chunksize=10000)` and updated app.py config with 
`app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 120`.

**Testing:** Tested with 100MB CSV (1M rows). Upload completes in 45s. 
Verified metadata extraction accuracy matches smaller files.
```

## Project-Specific Rules

### 1. **Context Management**
- Always use `read_context()` and `write_context()` for JSON operations
- Never directly manipulate storage files
- Include timestamps in all context updates

### 2. **LLM Integration**
- All LLM calls must have error handling
- Parse JSON responses defensively (handle missing fields)
- Strip markdown code blocks before JSON parsing
- Use `gemini-2.5-flash` for consistency

### 3. **Code Execution Safety**
- Never execute user code directly
- Always use `run_script_safely()` with timeout
- Validate file paths before script execution
- Sanitize error messages before returning to UI

### 4. **Session Isolation**
- Each session has its own directory under `storage/`
- Never access files outside session directory
- Clean up temporary files after processing

### 5. **API Response Format**
- Always return JSON from Flask routes
- Include appropriate HTTP status codes
- Use streaming (SSE) for long-running operations
- Handle exceptions with proper error messages

### 6. **Frontend Requirements**
- Keep UI simple and functional
- Show loading states for async operations
- Display errors clearly to users
- Maintain accessibility standards

## Testing Requirements

### Manual Testing Checklist

Before submitting PR, verify:
- Session creation works
- File upload succeeds (test with CSV, Excel)
- Chat messages are processed
- Context updates are saved
- CoTAS analysis runs without errors
- Streaming updates display correctly
- Error handling shows user-friendly messages

### Code Quality

- Follow PEP 8 Python style guidelines
- Add docstrings to new functions
- Keep functions focused and under 50 lines

## 📝 Commit Message Format

Use clear, descriptive commit messages:

```
feat: add Excel sheet selection support
fix: resolve timeout issue in large file uploads
docs: update API endpoint documentation
```

## Getting Help

- Review closed PRs for examples
- Ask questions in issue comments before starting work
- Tag maintainers for guidance on complex changes

## Code of Conduct

- Be **RESPECTFUL** and **CONSTRUCTIVE**
- Accept feedback gracefully
- Help others learn and grow