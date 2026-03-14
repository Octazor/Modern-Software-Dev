# Week 4 Writeup: Coding Agent Patterns

## Overview

This week examined advanced patterns for building and orchestrating coding agents — specifically sub-agent delegation, parallel execution, and Claude Code's slash command system. The assignment involved creating a custom slash command and a multi-agent pipeline that delegates subtasks.

---

## Part 1: Agent Patterns Overview

### Pattern 1: Sequential Chaining
The simplest pattern — one agent calls another in a pipeline, passing output forward.

```
User → Agent A → Agent B → Agent C → Final Output
```

Use case: Generate code (A) → Review code (B) → Write tests (C)

### Pattern 2: Parallel Fan-Out
A coordinator dispatches multiple sub-agents simultaneously and aggregates results.

```
        ┌─ Sub-Agent A ─┐
User → Coordinator    Aggregator → Output
        └─ Sub-Agent B ─┘
```

Use case: Research 3 competing libraries simultaneously, then compare.

### Pattern 3: Hierarchical Delegation
A top-level "manager" agent breaks a complex task into subtasks and assigns them to specialized workers.

Use case: Full-stack feature implementation — manager delegates API design, DB migration, frontend component, and test suite to separate specialized agents.

---

## Part 2: Custom Claude Code Slash Command

### Command: `/refactor-module`

This slash command analyzes a Python module and produces a refactored version with improved structure, type annotations, and docstrings.

**Location:** `.claude/commands/refactor-module.md`

```markdown
# /refactor-module

Refactor the specified Python module for improved quality.

## Instructions

1. Read the file at the path provided by the user.
2. Analyze it for:
   - Missing type annotations
   - Functions longer than 30 lines (candidate for extraction)
   - Missing or incomplete docstrings
   - Duplicate logic
   - Poorly named variables (single letters, ambiguous names)
3. Produce a fully refactored version of the file.
4. Output a diff summary explaining every change made.
5. Do NOT change the public API — all public function signatures must remain compatible.

## Output Format

First, print a numbered list of issues found.
Then, output the refactored file in a code block.
Finally, print a brief diff summary.

## Example Usage

User: /refactor-module utils/data_processor.py
```

**Demo run:**
```
User: /refactor-module src/parser.py

Issues found:
1. Function `parse_data` is 78 lines — extracted into 3 sub-functions
2. 4 variables named `x`, `d`, `t`, `r` — renamed to descriptive names
3. No docstrings on 6/8 functions — added Google-style docstrings
4. `load_config()` called 3 times in same scope — hoisted to single call

[refactored file output...]

Diff summary:
- Extracted: parse_header(), parse_body(), parse_footer() from parse_data()
- Renamed: x→index, d→document, t→timestamp, r→result
- Added: docstrings to all 8 functions
- Optimized: config loading reduced from 3 calls to 1
```

---

## Part 3: Multi-Agent Pipeline

### Task: "Full Feature Implementation Pipeline"

**Goal:** Given a feature request, automatically implement an API endpoint with validation, database model, and unit tests.

### Architecture

```
Feature Request
      │
      ▼
┌──────────────┐
│   Manager    │  Breaks task into 3 subtasks
│   Agent      │
└──────────────┘
      │
   ┌──┴──┐
   │     │
   ▼     ▼     ▼
[API] [Model] [Tests]
Agent  Agent   Agent
   │     │       │
   └──┬──┘       │
      │           │
      ▼           ▼
   Integrator ◄──┘
      │
      ▼
  Final PR
```

### Implementation

```python
import anthropic

client = anthropic.Anthropic()

def run_subagent(system_prompt: str, task: str) -> str:
    """Run a specialized sub-agent with a given task."""
    response = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=4096,
        system=system_prompt,
        messages=[{"role": "user", "content": task}]
    )
    return response.content[0].text

def manager_agent(feature_request: str) -> dict:
    """Break a feature request into subtasks."""
    response = run_subagent(
        system_prompt="""You are a tech lead. Break the given feature request into exactly 3 subtasks:
        1. API endpoint implementation (FastAPI)
        2. Database model (SQLAlchemy)
        3. Unit tests (pytest)
        
        Return as JSON with keys: api_task, model_task, test_task""",
        task=feature_request
    )
    import json
    return json.loads(response)

def api_agent(task: str) -> str:
    return run_subagent(
        system_prompt="You are a FastAPI expert. Write clean, production-ready API endpoint code.",
        task=task
    )

def model_agent(task: str) -> str:
    return run_subagent(
        system_prompt="You are a database engineer. Write SQLAlchemy ORM models with proper relationships and constraints.",
        task=task
    )

def test_agent(task: str, api_code: str, model_code: str) -> str:
    return run_subagent(
        system_prompt="You are a QA engineer. Write comprehensive pytest unit tests.",
        task=f"{task}\n\nAPI code:\n{api_code}\n\nModel code:\n{model_code}"
    )

def run_pipeline(feature_request: str):
    print("Manager: Breaking down task...")
    subtasks = manager_agent(feature_request)

    print("Running sub-agents in parallel logic...")
    api_code = api_agent(subtasks["api_task"])
    model_code = model_agent(subtasks["model_task"])
    test_code = test_agent(subtasks["test_task"], api_code, model_code)

    return {
        "api": api_code,
        "model": model_code,
        "tests": test_code
    }

# Example
result = run_pipeline("Add a /users/{user_id}/posts endpoint that returns paginated posts for a user")
```

### Output

The pipeline produced:
- A FastAPI route handler with pagination (`skip`/`limit` query params), proper 404 handling, and Pydantic response model
- A SQLAlchemy `Post` model with `user_id` foreign key, timestamps, and an index on `user_id`
- 6 pytest test cases covering: happy path, empty results, invalid user ID, boundary pagination values, and response schema validation

Total generation time: ~25 seconds for all three outputs.

---

## Reflections

1. **Specialization improves quality.** Each sub-agent received a focused system prompt for its domain (API, DB, tests). The API agent's output was noticeably better than what a single general-purpose agent produced — it used FastAPI idioms more consistently.

2. **Manager agent reliability is critical.** The pipeline broke when the manager returned malformed JSON. Adding a retry loop with explicit JSON schema instructions fixed this.

3. **Context passing between agents is a design challenge.** The test agent needed both the API code and model code as context. Deciding what to pass (and in what format) required thought — too little context and tests were generic; too much context and the prompt became bloated.

4. **Slash commands are underrated.** The `/refactor-module` command saved significant time on a real project — running it on a legacy `utils.py` found 11 issues I would have missed. The persistent, versioned command means the team can maintain a shared library of workflows.

5. **Parallelism is worth it for longer tasks.** For quick tasks, sequential is fine. For tasks where each subtask takes 10+ seconds, running them in parallel (using `asyncio.gather`) would cut total time by ~60%.
