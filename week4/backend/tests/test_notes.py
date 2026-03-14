def test_create_and_list_notes(client):
    payload = {"title": "Test", "content": "Hello world"}
    r = client.post("/notes/", json=payload)
    assert r.status_code == 201, r.text
    data = r.json()
    assert data["title"] == "Test"
    note_id = data["id"]

    # Convert the note into action items
    r = client.post(f"/notes/{note_id}/extract")
    assert r.status_code == 200
    extracted = r.json()
    assert isinstance(extracted, list)

    # Ensure action items were created in the system
    r = client.get("/action-items/")
    assert r.status_code == 200
    action_list = r.json()
    assert len(action_list) >= len(extracted)

    r = client.get("/notes/")
    assert r.status_code == 200
    items = r.json()
    assert len(items) >= 1

    r = client.get("/notes/search/")
    assert r.status_code == 200

    r = client.get("/notes/search/", params={"q": "Hello"})
    assert r.status_code == 200
    items = r.json()
    assert len(items) >= 1

    # Search should be case-insensitive
    payload2 = {"title": "MiXeD", "content": "Case Test"}
    r = client.post("/notes/", json=payload2)
    assert r.status_code == 201, r.text

    r = client.get("/notes/search/", params={"q": "mixed"})
    assert r.status_code == 200
    items = r.json()
    assert any(item["title"] == "MiXeD" for item in items)


def test_update_and_delete_note(client):
    payload = {"title": "Orig", "content": "Orig"}
    r = client.post("/notes/", json=payload)
    assert r.status_code == 201, r.text
    note_id = r.json()["id"]

    # Update
    updated = {"title": "Updated", "content": "Updated content"}
    r = client.put(f"/notes/{note_id}", json=updated)
    assert r.status_code == 200
    assert r.json()["title"] == "Updated"

    # Delete
    r = client.delete(f"/notes/{note_id}")
    assert r.status_code == 204

    # Ensure it no longer exists
    r = client.get(f"/notes/{note_id}")
    assert r.status_code == 404


def test_note_payload_validation(client):
    # empty title should be rejected as a bad request (400)
    r = client.post("/notes/", json={"title": "", "content": "okay"})
    assert r.status_code == 400

    r = client.post("/notes/", json={"title": "OK", "content": ""})
    assert r.status_code == 400


def test_note_not_found_errors(client):
    r = client.put("/notes/99999", json={"title": "foo", "content": "bar"})
    assert r.status_code == 404

    r = client.delete("/notes/99999")
    assert r.status_code == 404
