# Week 2 Writeup: The Anatomy of Coding Agents

## Overview

This week explored how coding agents work under the hood — the agentic loop, tool use, and how LLMs chain reasoning with actions. The assignment involved building a simple agent with tool-calling capabilities and observing how it navigates multi-step tasks.

---

## Part 1: Understanding the Agentic Loop

The core pattern of any coding agent:

```
User Input → LLM Reasoning → Tool Call → Tool Result → LLM Reasoning → ... → Final Answer
```

Each iteration through this loop is one "step" of the agent. The model decides at each step whether to:
- Call a tool (e.g., read a file, run code, search the web)
- Respond to the user directly

Key insight: the model doesn't "run" the tools itself — it outputs a *structured request* (usually JSON), and the host application executes the tool and feeds the result back.

---

## Part 2: Building a Simple Tool-Calling Agent

### Tools Implemented

**Tool 1: `read_file`**
```python
def read_file(path: str) -> str:
    """Read the contents of a file at the given path."""
    with open(path, "r") as f:
        return f.read()
```

**Tool 2: `run_python`**
```python
import subprocess

def run_python(code: str) -> str:
    """Execute a Python snippet and return stdout + stderr."""
    result = subprocess.run(
        ["python3", "-c", code],
        capture_output=True,
        text=True,
        timeout=10
    )
    return result.stdout + result.stderr
```

**Tool 3: `list_directory`**
```python
import os

def list_directory(path: str) -> list[str]:
    """List files and folders in a directory."""
    return os.listdir(path)
```

### Agent Loop Implementation

```python
import anthropic
import json

client = anthropic.Anthropic()

tools = [
    {
        "name": "read_file",
        "description": "Read the contents of a file at the given path.",
        "input_schema": {
            "type": "object",
            "properties": {"path": {"type": "string"}},
            "required": ["path"]
        }
    },
    {
        "name": "run_python",
        "description": "Execute a Python snippet and return stdout + stderr.",
        "input_schema": {
            "type": "object",
            "properties": {"code": {"type": "string"}},
            "required": ["code"]
        }
    },
    {
        "name": "list_directory",
        "description": "List files and folders in a directory.",
        "input_schema": {
            "type": "object",
            "properties": {"path": {"type": "string"}},
            "required": ["path"]
        }
    }
]

def run_tool(name, inputs):
    if name == "read_file":
        return read_file(**inputs)
    elif name == "run_python":
        return run_python(**inputs)
    elif name == "list_directory":
        return str(list_directory(**inputs))

def agent_loop(user_message):
    messages = [{"role": "user", "content": user_message}]

    while True:
        response = client.messages.create(
            model="claude-opus-4-5",
            max_tokens=4096,
            tools=tools,
            messages=messages
        )

        # Append assistant response
        messages.append({"role": "assistant", "content": response.content})

        if response.stop_reason == "end_turn":
            # Extract final text response
            for block in response.content:
                if hasattr(block, "text"):
                    return block.text
            return ""

        # Process tool calls
        tool_results = []
        for block in response.content:
            if block.type == "tool_use":
                result = run_tool(block.name, block.input)
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": result
                })

        messages.append({"role": "user", "content": tool_results})
```

---

## Part 3: Agent in Action

**Task given to agent:**
```
Look at the files in ./data/, read the contents of any .txt file you find, 
then run a Python snippet to count how many words are in each file and report back.
```

**Agent trace:**

1. **Step 1 – Tool call:** `list_directory(path="./data/")`
   - Result: `['notes.txt', 'readme.txt', 'config.json']`

2. **Step 2 – Tool call:** `read_file(path="./data/notes.txt")`
   - Result: (file contents)

3. **Step 3 – Tool call:** `read_file(path="./data/readme.txt")`
   - Result: (file contents)

4. **Step 4 – Tool call:** `run_python(code="...")`
   - The model wrote a small Python snippet to count words across both files
   - Result: `notes.txt: 142 words\nreadme.txt: 89 words`

5. **Step 5 – Final answer:**
   ```
   Here are the word counts:
   - notes.txt: 142 words
   - readme.txt: 89 words
   (config.json was skipped as it's not a text file)
   ```

**Observation:** The agent correctly identified only `.txt` files, used the directory listing to plan its approach, and self-generated the word-counting code without being told how to implement it. It completed the task in 4 tool calls.

---

## Reflections

1. **The agentic loop is surprisingly simple in structure** — the complexity comes from the model's ability to choose the right tool and pass the right arguments, not from complex orchestration code.

2. **Tool descriptions matter enormously.** When I wrote vague descriptions like "runs code," the model sometimes passed multi-line scripts where a single expression was expected. Specific descriptions with examples dramatically improved reliability.

3. **Observing the trace is essential for debugging.** Printing each step of the agent loop revealed that the model sometimes made redundant tool calls (e.g., listing the directory twice). This points to the importance of providing the model with sufficient context upfront.

4. **Error handling in tools is critical.** When `run_python` returned a traceback, the model actually read the error, diagnosed the issue, and corrected its code in the next step — a genuinely impressive self-correction behavior.

5. **Stop conditions matter.** Without checking `stop_reason == "end_turn"`, the loop can run indefinitely if the model keeps finding new things to investigate.
