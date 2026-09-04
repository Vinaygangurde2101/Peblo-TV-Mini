from app.auth.jwt import create_access_token


def get_auth_headers(user):
    token = create_access_token(user_id=user.id, email=user.email, role=user.role)
    return {"Authorization": f"Bearer {token}"}


def test_show_crud_lifecycle(client, editor_user):
    headers = get_auth_headers(editor_user)

    # 1. Create Show
    create_res = client.post(
        "/admin/shows",
        json={
            "title": "Stranger Elements",
            "synopsis": "Sci-Fi mystery set in 1980s Indiana.",
            "category": "Sci-Fi",
            "section": "Trending Now",
            "status": "draft"
        },
        headers=headers
    )
    assert create_res.status_code == 201
    show_data = create_res.json()
    show_id = show_data["id"]
    assert show_data["title"] == "Stranger Elements"

    # 2. Get Show List with Search
    list_res = client.get(
        f"/admin/shows?q=Stranger&category=Sci-Fi",
        headers=headers
    )
    assert list_res.status_code == 200
    list_data = list_res.json()
    assert list_data["total"] == 1
    assert list_data["items"][0]["id"] == show_id

    # 3. Update Show
    update_res = client.put(
        f"/admin/shows/{show_id}",
        json={"title": "Stranger Elements S1", "status": "published"},
        headers=headers
    )
    assert update_res.status_code == 200
    assert update_res.json()["title"] == "Stranger Elements S1"
    assert update_res.json()["status"] == "published"

    # 4. Delete Show
    delete_res = client.delete(f"/admin/shows/{show_id}", headers=headers)
    assert delete_res.status_code == 204


def test_episode_duplicate_language_conflict(client, editor_user):
    headers = get_auth_headers(editor_user)

    # Create parent show and season
    show_res = client.post("/admin/shows", json={"title": "Conflict Show"}, headers=headers)
    show_id = show_res.json()["id"]

    season_res = client.post(
        "/admin/seasons",
        json={"show_id": show_id, "season_number": 1, "title": "Season 1"},
        headers=headers
    )
    season_id = season_res.json()["id"]

    # Create first episode variant (English)
    ep1_res = client.post(
        "/admin/episodes",
        json={
            "season_id": season_id,
            "episode_number": 1,
            "title": "Pilot",
            "content_group": "conflict-ep-1",
            "language": "English"
        },
        headers=headers
    )
    assert ep1_res.status_code == 201

    # Attempt duplicate (content_group="conflict-ep-1", language="English")
    ep2_res = client.post(
        "/admin/episodes",
        json={
            "season_id": season_id,
            "episode_number": 1,
            "title": "Pilot Duplicate",
            "content_group": "conflict-ep-1",
            "language": "English"
        },
        headers=headers
    )
    assert ep2_res.status_code == 409
    assert "already exists" in ep2_res.json()["detail"]
