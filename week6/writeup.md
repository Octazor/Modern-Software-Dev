# Week 6 Writeup: AI Testing and Security

## Overview

This week covered AI-assisted testing and security analysis — using tools like Semgrep for static analysis and LLMs to find and fix vulnerabilities in code. The assignment required running Semgrep on a codebase, identifying at least 3 issues, and using an AI agent to fix them with explanations.

---

## Part 1: Static Analysis with Semgrep

### Setup

```bash
pip install semgrep
semgrep --config=auto ./myapp
```

### Findings

Running Semgrep on the FastAPI application from week 5 produced the following findings:

---

**Finding 1: Hardcoded Secret Key**

```
myapp/auth.py:12
  rule: python.lang.security.audit.hardcoded-secret.hardcoded-secret
  severity: ERROR

  SECRET_KEY = "your-secret-key-change-in-production"
```

**Risk:** Hardcoded secrets in source code get committed to version control and exposed to anyone with repo access, including CI/CD logs.

---

**Finding 2: SQL Injection via String Formatting**

```
myapp/routes/search.py:34
  rule: python.sqlalchemy.security.sqlalchemy-execute-raw-query.sqlalchemy-execute-raw-query
  severity: WARNING

  results = db.execute(f"SELECT * FROM tasks WHERE title LIKE '%{query}%'")
```

**Risk:** User-supplied `query` input is directly interpolated into a raw SQL string. An attacker can inject SQL to dump the database, bypass filters, or delete records.

---

**Finding 3: No Rate Limiting on Auth Endpoints**

```
myapp/main.py:45
  rule: python.flask.security.audit.missing-rate-limiting.missing-rate-limiting
  (adapted for FastAPI context)
```

The `/auth/login` endpoint had no rate limiting, making it vulnerable to brute-force credential stuffing attacks.

---

**Finding 4: Insecure JWT Algorithm Acceptance**

```
myapp/auth.py:58
  rule: python.jwt.security.jwt-python-hardcoded-secret
  
  payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
```

**Risk:** Accepting only `HS256` is fine, but the original code had `algorithms=None` which would allow an attacker to send a token with `alg: none` header and bypass verification entirely.

---

## Part 2: AI-Assisted Fixes

I used Claude to analyze each finding and produce fixes with explanations.

### Fix 1: Hardcoded Secret Key

**Prompt to Claude:**
```
This Semgrep rule flagged a hardcoded SECRET_KEY in my auth.py. 
How should I fix this properly for a FastAPI application?
Show me the corrected code.
```

**Fix applied:**
```python
# auth.py - before
SECRET_KEY = "your-secret-key-change-in-production"

# auth.py - after
import os
from functools import lru_cache
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    class Config:
        env_file = ".env"

@lru_cache()
def get_settings():
    return Settings()
```

`.env` file (not committed to git, added to `.gitignore`):
```
SECRET_KEY=your-actual-random-secret-key-here
```

Generate a secure key:
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

**Explanation from Claude:**
Moving the secret to environment variables ensures it's never in source code. Using `pydantic_settings` provides type validation and makes it clear what configuration the app requires. The `lru_cache` avoids reading from disk on every request.

---

### Fix 2: SQL Injection

**Prompt to Claude:**
```
Semgrep flagged this line in my FastAPI app as a SQL injection vulnerability:
results = db.execute(f"SELECT * FROM tasks WHERE title LIKE '%{query}%'")
Fix it using SQLAlchemy properly.
```

**Fix applied:**
```python
# Before (vulnerable)
results = db.execute(f"SELECT * FROM tasks WHERE title LIKE '%{query}%'")

# After (safe — parameterized query via SQLAlchemy ORM)
from sqlalchemy import or_
results = db.query(Task).filter(Task.title.ilike(f"%{query}%")).all()

# Alternative if raw SQL is truly needed:
from sqlalchemy import text
results = db.execute(
    text("SELECT * FROM tasks WHERE title LIKE :pattern"),
    {"pattern": f"%{query}%"}
).fetchall()
```

**Explanation from Claude:**
SQLAlchemy's ORM methods (`.filter()`, `.ilike()`) automatically parameterize queries — the query and data are sent separately to the database driver, making injection impossible. If raw SQL is necessary, `text()` with bound parameters achieves the same safety guarantee.

---

### Fix 3: Rate Limiting on Auth Endpoints

**Fix applied using `slowapi`:**

```python
# requirements.txt - add:
slowapi==0.1.9

# main.py
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
app = FastAPI()
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.post("/auth/login")
@limiter.limit("5/minute")
async def login(request: Request, form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    # ... existing login logic
```

**Explanation:**
Rate limiting to 5 attempts/minute per IP makes brute-force attacks impractical. For production, this should be combined with account lockout after N failed attempts and CAPTCHA for repeated failures.

---

### Fix 4: JWT Algorithm Validation

**Fix applied:**
```python
# Before (vulnerable if original code had algorithms=None)
payload = jwt.decode(token, SECRET_KEY, algorithms=None)  # DANGEROUS

# After
payload = jwt.decode(
    token,
    settings.secret_key,
    algorithms=["HS256"],  # Explicit allowlist
    options={"verify_exp": True}  # Ensure expiry is always checked
)
```

**Explanation:**
The `alg: none` attack allows an attacker to craft a token with no signature that passes validation. Explicitly allowlisting `["HS256"]` prevents this. The `verify_exp` option ensures tokens can't be used after expiry even if a library version has a bug.

---

## Part 3: AI-Generated Test Suite

I asked Claude to generate security-focused tests:

```python
# tests/test_security.py

import pytest
from fastapi.testclient import TestClient
from myapp.main import app

client = TestClient(app)

def test_login_rate_limit():
    """Verify that login is rate limited after 5 attempts."""
    for i in range(5):
        client.post("/auth/login", data={"username": "test", "password": "wrong"})
    response = client.post("/auth/login", data={"username": "test", "password": "wrong"})
    assert response.status_code == 429

def test_sql_injection_in_search():
    """Verify that SQL injection in search query doesn't cause an error or leak data."""
    malicious_query = "'; DROP TABLE tasks; --"
    response = client.get(f"/tasks/search?q={malicious_query}", headers=auth_headers)
    assert response.status_code == 200
    assert response.json() == []  # Should return empty, not an error

def test_jwt_none_algorithm_rejected():
    """Verify that tokens with alg=none are rejected."""
    import base64, json
    header = base64.b64encode(json.dumps({"alg": "none", "typ": "JWT"}).encode()).decode()
    payload = base64.b64encode(json.dumps({"sub": "admin"}).encode()).decode()
    fake_token = f"{header}.{payload}."
    response = client.get("/tasks", headers={"Authorization": f"Bearer {fake_token}"})
    assert response.status_code == 401

def test_protected_routes_require_auth():
    """Verify all protected routes return 401 without a token."""
    for endpoint in ["/tasks", "/tasks/1"]:
        response = client.get(endpoint)
        assert response.status_code == 401
```

---

## Reflections

1. **Semgrep found real bugs.** The raw SQL string interpolation was an actual vulnerability I had introduced in week 5 without realizing it. Static analysis as a CI gate would have caught this before it merged.

2. **AI explains vulnerabilities better than documentation.** Claude didn't just fix the code — it explained *why* each issue is dangerous with concrete attack scenarios. This is more actionable than a Semgrep rule ID.

3. **Security is a layered problem.** Fixing the four issues still leaves the app vulnerable to other attacks (e.g., insufficient input length limits, missing HTTPS enforcement). Security requires defense-in-depth, not a checklist.

4. **AI-generated security tests are a force multiplier.** Writing the JWT `alg: none` test myself would have required me to know that attack exists. Having Claude generate tests based on the vulnerabilities it identified means the test suite captures expert-level knowledge.

5. **False positives exist.** Semgrep flagged one line as a potential hardcoded password that was actually a default placeholder in a config comment. Reviewing findings critically is still necessary.
