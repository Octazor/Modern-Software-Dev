# Week 7 Writeup: Modern Software Support

## Overview

This week focused on using AI for software support workflows — debugging, log analysis, incident triage, and documentation generation. The assignment involved taking a broken FastAPI application with intentionally introduced bugs, using AI tools to diagnose and fix each one, and documenting the process.

---

## Part 1: The Broken Application

The target app was a FastAPI task management service with the following known (but undisclosed) bugs introduced:

1. A performance bug (N+1 query pattern)
2. A logic bug in pagination
3. A memory leak in background task handling
4. Incorrect HTTP status codes on certain error paths

---

## Part 2: AI-Assisted Debugging Sessions

### Bug 1: N+1 Query Performance Issue

**Symptom observed:**
Response times for `GET /users/{user_id}/tasks` degraded from ~20ms to ~2000ms as the database grew.

**Debugging approach:**
I pasted the route handler and models into Claude with the prompt:

```
This endpoint is getting progressively slower as data grows. 
Can you identify any database query performance issues?

[code pasted]
```

**Claude's diagnosis:**
```
I can see an N+1 query problem. The route fetches a User object, then 
for each task in user.tasks, it accesses task.tags — which triggers a 
separate SELECT for each task's tags. For a user with 100 tasks, 
this results in 101 database queries.

Fix: Use SQLAlchemy's joinedload or selectinload to eager-load the 
tags relationship in the initial query.
```

**Fix applied:**
```python
# Before
user = db.query(User).filter(User.id == user_id).first()
tasks = user.tasks  # Each task.tags access triggers a new query

# After
from sqlalchemy.orm import selectinload

user = db.query(User)\
    .options(selectinload(User.tasks).selectinload(Task.tags))\
    .filter(User.id == user_id)\
    .first()
```

**Result:** Response time dropped from ~2000ms back to ~18ms. Query count reduced from 101 to 2.

---

### Bug 2: Pagination Logic Error

**Symptom observed:**
`GET /tasks?page=1&per_page=10` returned items 0–9. `page=2` returned items 10–19. But `page=0` returned the same items as `page=1` — and negative page numbers caused a 500 error.

**Debugging approach:**
```
This pagination function returns wrong results for page=0 and crashes on negative page values.
Find the bug and fix it.

def get_tasks_paginated(db, page: int, per_page: int):
    offset = page * per_page
    return db.query(Task).offset(offset).limit(per_page).all()
```

**Claude's diagnosis:**
```
Two issues:

1. Page 0 and page 1 both produce offset=0 (page 0 → 0*10=0, page 1 → 1*10=10 only if 
   page is 1-indexed). The current formula assumes 0-indexed pages but the API docs 
   likely describe 1-indexed pages. Use offset = (page - 1) * per_page for 1-indexed.

2. Negative page values produce a negative offset, which SQLAlchemy silently converts 
   to 0 in some drivers, or raises an error in others. Add input validation.
```

**Fix applied:**
```python
from fastapi import Query, HTTPException

@app.get("/tasks")
def get_tasks(
    page: int = Query(default=1, ge=1, description="Page number (1-indexed)"),
    per_page: int = Query(default=10, ge=1, le=100)
):
    offset = (page - 1) * per_page
    tasks = db.query(Task).offset(offset).limit(per_page).all()
    return tasks
```

Using FastAPI's `Query(ge=1)` constraint means invalid values are rejected with a 422 before reaching the handler.

---

### Bug 3: Memory Leak in Background Tasks

**Symptom observed:**
Memory usage grew steadily over time when the background email notification task was enabled. After ~1 hour, the process was using 800MB+ of RAM.

**Debugging approach:**
I used `tracemalloc` to capture a memory snapshot and pasted the output to Claude:

```
Here's a tracemalloc snapshot showing memory growth. 
Can you identify what's accumulating?

Top 10 memory consumers:
/myapp/notifications.py:45: size=340 MiB, count=89432, average=4.0 KiB
/myapp/notifications.py:62: size=12 MiB, count=3240, average=3.8 KiB
...
```

**Claude's diagnosis:**
```
The tracemalloc output points to notifications.py:45. Looking at your code, 
the issue is that completed_notifications list is never cleared:

completed_notifications = []  # module-level list

async def send_notification(task_id: int):
    # ... send email
    completed_notifications.append({"task_id": task_id, "sent_at": datetime.now(), "details": full_task_object})

This list grows unboundedly. Storing the full task object (with all relationships) 
for each notification is particularly expensive — 89,432 objects at 4KB each explains your 340MB.
```

**Fix applied:**
```python
from collections import deque

# Use a bounded deque to keep only recent history
completed_notifications: deque = deque(maxlen=1000)

async def send_notification(task_id: int):
    # ... send email
    # Store only what's needed for logging, not the full object
    completed_notifications.append({
        "task_id": task_id,
        "sent_at": datetime.now().isoformat()
    })
```

**Result:** Memory stabilized at ~45MB and no longer grew over time.

---

### Bug 4: Incorrect HTTP Status Codes

**Symptom observed:**
- `DELETE /tasks/999` (non-existent ID) returned `200 OK` with `{"deleted": false}` instead of `404`
- `POST /tasks` with duplicate title returned `200 OK` instead of `409 Conflict`

**Debugging with Claude:**
```
Review these route handlers and tell me if the HTTP status codes are semantically correct.
[handlers pasted]
```

**Claude's response:**
```
Two issues:

1. DELETE returning 200 with {"deleted": false} is misleading. A 200 response 
   tells the client "everything is fine" — the client has no reason to check 
   the body. Proper behavior: return 404 if the resource doesn't exist, 
   204 No Content on successful deletion.

2. POST with duplicate returning 200 violates REST semantics. The correct 
   status for a conflict (e.g., unique constraint violation) is 409 Conflict, 
   which lets API clients handle it programmatically.
```

**Fix applied:**
```python
@app.delete("/tasks/{task_id}", status_code=204)
def delete_task(task_id: int, db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    db.delete(task)
    db.commit()

@app.post("/tasks", status_code=201)
def create_task(task: TaskCreate, db: Session = Depends(get_db)):
    existing = db.query(Task).filter(Task.title == task.title).first()
    if existing:
        raise HTTPException(status_code=409, detail="A task with this title already exists")
    # ... create task
```

---

## Part 3: AI-Generated Documentation

After fixing all bugs, I used Claude to auto-generate updated API documentation:

**Prompt:**
```
Generate comprehensive API documentation in Markdown for these FastAPI routes. 
Include: endpoint, method, description, parameters, request body, response codes, and examples.
[routes pasted]
```

**Output (excerpt):**

```markdown
## GET /tasks

Returns a paginated list of tasks.

**Parameters:**
| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| page | integer | No | 1 | Page number (1-indexed, min: 1) |
| per_page | integer | No | 10 | Items per page (min: 1, max: 100) |

**Response: 200 OK**
```json
{
  "tasks": [...],
  "total": 42,
  "page": 1,
  "per_page": 10
}
```

**Response: 422 Unprocessable Entity** — Invalid page or per_page value
```

---

## Part 4: Log Analysis

I fed a production error log to Claude and asked it to triage:

```
Here are the last 200 lines of our app logs during an incident. 
Identify the root cause and timeline.
[logs pasted]
```

Claude correctly identified:
1. A database connection pool exhaustion at 14:32 (all 20 connections consumed)
2. Requests then started queuing, causing timeouts at 14:33
3. Root cause: a long-running analytics query had been introduced in a deploy at 14:25 that held connections open for 45+ seconds
4. Recommendation: set `pool_timeout`, use `pool_recycle`, and move analytics to a read replica

---

## Reflections

1. **AI debugging requires the right context.** Pasting just the buggy function wasn't enough for the N+1 issue — I also needed to paste the model relationships. "More context" consistently improved diagnosis quality.

2. **tracemalloc + Claude is a powerful combo.** I never would have found the memory leak manually in reasonable time. The AI's ability to connect the tracemalloc output to a specific code pattern was genuinely impressive.

3. **Documentation generation is a practical win.** Generating API docs from code took 30 seconds and produced better-formatted docs than I would have written manually. The main value isn't replacing the need for documentation — it's removing the friction.

4. **Log analysis is a killer use case.** Reading 200 lines of logs and building a coherent incident timeline is tedious for humans and fast for LLMs. This alone could significantly reduce mean time to resolution (MTTR) during incidents.

5. **The AI suggested fixes I wouldn't have thought of.** The bounded `deque` suggestion for the memory leak was cleaner than my instinct to add a manual "clear every N items" timer. Expert-level suggestions emerging from pattern recognition across many codebases is a genuine advantage.
