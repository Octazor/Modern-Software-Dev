# Week 5 Writeup: The Modern Terminal

## Overview

This week focused on AI-augmented terminal workflows — using tools like Warp, Claude Code in CLI mode, and autonomous agents to operate on a codebase via the command line. The assignment involved using an AI coding agent to autonomously add features to an existing FastAPI application from the terminal alone.

---

## Part 1: Modern Terminal Tools

### Warp Terminal

Warp reimagines the terminal with a block-based UI and built-in AI assistance. Key features explored:

**AI Command Search (`Ctrl+``):**
Instead of googling `find` syntax or `awk` one-liners, typing a description like:
```
find all Python files modified in the last 24 hours and list their sizes
```
Produces:
```bash
find . -name "*.py" -mtime -1 -exec ls -lh {} \;
```
This alone saved significant time — especially for less-used commands like `rsync`, `tar`, and `openssl`.

**Block-based output:**
Each command's output is a distinct "block" that can be shared, searched, or bookmarked. Particularly useful when running long test suites — being able to copy just the failed test block without re-selecting was a quality-of-life improvement.

### Claude Code (CLI)

Running `claude` from the terminal and pointing it at a project directory provided a powerful "agentic terminal" experience:

```bash
cd ~/projects/myapp
claude
```

Claude Code can read, create, edit, and run files entirely from the terminal session — no IDE required.

---

## Part 2: Autonomous Feature Addition

### The Target Application

A minimal FastAPI CRUD app for managing "tasks":

```
myapp/
├── main.py          # FastAPI app + routes
├── models.py        # SQLAlchemy models
├── schemas.py       # Pydantic schemas
├── database.py      # DB session setup
└── tests/
    └── test_main.py
```

### Task Given to Claude Code (CLI)

```
Add user authentication to this FastAPI app. Specifically:
1. Add a User model with username, hashed_password, and created_at fields
2. Add POST /auth/register and POST /auth/login endpoints
3. Login should return a JWT token
4. Protect the existing GET /tasks, POST /tasks, DELETE /tasks/{id} endpoints with JWT auth
5. Write tests for the new auth endpoints
Do this using only existing dependencies where possible, adding only what's strictly necessary.
```

### What the Agent Did (Observed Trace)

**Step 1 — Exploration:**
```bash
ls -la
cat main.py
cat models.py
cat requirements.txt
```
The agent first oriented itself by reading all relevant files before making any changes.

**Step 2 — Planning (agent's internal note to itself):**
```
Plan:
- Add python-jose and passlib to requirements (JWT + password hashing)
- Create auth.py with JWT utilities
- Add User model to models.py
- Add auth schemas to schemas.py
- Add /auth/register and /auth/login to main.py
- Add get_current_user dependency
- Apply dependency to existing routes
- Write tests
```

**Step 3 — Implementation:**
The agent made the following file changes:

`requirements.txt` — added:
```
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
```

`models.py` — added `User` model:
```python
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
```

`auth.py` — new file:
```python
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

SECRET_KEY = "your-secret-key-change-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise credentials_exception
    return user
```

**Step 4 — Testing:**
```bash
pip install -r requirements.txt
python -m pytest tests/ -v
```
All 8 tests passed (4 existing + 4 new auth tests).

**Step 5 — Self-correction:**
One test initially failed because the agent used `OAuth2PasswordRequestForm` without importing it. It read the error, identified the missing import, fixed it, and re-ran the tests automatically.

---

## Part 3: Terminal Workflow Observations

### Commands the AI Suggested During Session

| Task | AI-suggested command |
|------|---------------------|
| Check what port FastAPI is running on | `lsof -i :8000` |
| Watch test output in real time | `pytest -v --tb=short -x 2>&1 \| tee test_output.log` |
| Find all TODO comments in codebase | `grep -rn "TODO" --include="*.py" .` |
| Check if JWT library installed | `pip show python-jose` |
| Format all Python files | `black . && isort .` |

---

## Reflections

1. **The terminal agent is genuinely autonomous.** I gave one high-level instruction and watched it read files, plan, implement, install dependencies, run tests, fix errors, and re-run — all without intervention. This is qualitatively different from a code-suggestion tool.

2. **Exploration before action is key.** The agent's habit of reading all files before writing anything led to much better output than if it had jumped straight to implementation. It knew to check `requirements.txt` before adding new dependencies.

3. **Self-correction is real and reliable.** The failed import was fixed without me pointing it out. For more complex bugs, the agent sometimes needed a nudge, but for syntactic/import errors it was effectively self-healing.

4. **Security concerns emerged naturally.** The agent added a hardcoded `SECRET_KEY` and immediately commented `# change-in-production`. This suggests awareness of best practices but also highlights that AI agents need human review — I should move that to an environment variable.

5. **Terminal-native AI changes the role of the developer.** Instead of writing code, I found myself reviewing plans, approving changes, and guiding direction. The "developer as orchestrator" pattern emerged naturally.
