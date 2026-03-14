# API Documentation (Week 4)

This document describes the available FastAPI endpoints for the Week 4 backend.

---

## Notes

### GET /notes/

List all notes.

**Response (200)**
```json
[
  {"id": 1, "title": "Example", "content": "..."},
  {"id": 2, "title": "Another", "content": "..."}
]
```

---

### POST /notes/

Create a new note.

**Request body** (JSON)
```json
{
  "title": "My note",
  "content": "Some content"
}
```

**Success response (201)**
```json
{
  "id": 5,
  "title": "My note",
  "content": "Some content"
}
```

**Validation error (400)**
- Returned if `title` or `content` are empty.

---

### GET /notes/search/?q=...

Search notes by title or content (case-insensitive).

**Example**
`GET /notes/search/?q=hello`

**Response (200)**
```json
[
  {"id": 3, "title": "Hello world", "content": "..."}
]
```

---

### POST /notes/{id}/extract

Extract action items from a note's content.

**Example**
`POST /notes/3/extract`

**Response (200)**
```json
[
  {"id": 10, "description": "Do something!", "completed": false},
  {"id": 11, "description": "TODO: another task", "completed": false}
]
```

**Errors**
- `404 Not Found` if the note `id` does not exist.

---

### PUT /notes/{id}

Update an existing note.

**Request body** (JSON)
```json
{
  "title": "Updated title",
  "content": "Updated content"
}
```

**Success response (200)**
```json
{
  "id": 3,
  "title": "Updated title",
  "content": "Updated content"
}
```

**Errors**
- `400 Bad Request` when the request body fails validation (e.g., empty title/content).
- `404 Not Found` when the note does not exist.

---

### DELETE /notes/{id}

Delete a note.

**Success response (204)**
No body.

**Errors**
- `404 Not Found` when the note does not exist.

---

## Action Items

### GET /action-items/

List all action items.

**Response (200)**
```json
[
  {"id": 1, "description": "Do the thing", "completed": false},
  {"id": 2, "description": "Done already", "completed": true}
]
```

---

### POST /action-items/

Create a new action item.

**Request body**
```json
{
  "description": "Work on task"
}
```

**Success response (201)**
```json
{
  "id": 5,
  "description": "Work on task",
  "completed": false
}
```

---

### PUT /action-items/{id}/complete

Mark an action item as completed.

**Example**
`PUT /action-items/5/complete`

**Success response (200)**
```json
{
  "id": 5,
  "description": "Work on task",
  "completed": true
}
```

**Errors**
- `404 Not Found` if the action item does not exist.
