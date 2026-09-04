import os
import json
from app.auth.jwt import create_access_token
from app.models.user import UserRole
from app.models.show import Show, ContentStatus
from app.models.season import Season
from app.models.episode import Episode
from app.core.config import settings


def test_full_end_to_end_platform_workflow(client, admin_user, db):
    """
    Complete End-to-End Integration Test:
    CMS Login -> Show Creation -> Season/Episode Setup -> Artwork Setup ->
    Validation Report Audit -> Atomic Publish -> Public Catalogue Consumption.
    """
    # Isolate test environment by making existing seeded shows draft
    db.query(Show).update({"status": ContentStatus.DRAFT})
    db.commit()

    # 1. Admin Login
    login_res = client.post(
        "/auth/login",
        json={"email": admin_user.email, "password": "admin_pass"}
    )
    assert login_res.status_code == 200
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Create Artwork Files in Storage
    artwork_dir = os.path.join(settings.STORAGE_PATH, "artwork")
    os.makedirs(artwork_dir, exist_ok=True)
    poster_path = os.path.join(artwork_dir, "e2e_poster.jpg")
    thumb_path = os.path.join(artwork_dir, "e2e_thumb.jpg")
    with open(poster_path, "w") as f:
        f.write("e2e_img_data")
    with open(thumb_path, "w") as f:
        f.write("e2e_img_data")

    poster_url = "/static/artwork/e2e_poster.jpg"
    thumb_url = "/static/artwork/e2e_thumb.jpg"

    # 3. Create Published Show
    show_res = client.post(
        "/admin/shows",
        json={
            "title": "E2E Platform Masterpiece",
            "synopsis": "End to end integration test show.",
            "category": "Drama",
            "section": "Trending Now",
            "status": "published",
            "poster_url": poster_url
        },
        headers=headers
    )
    assert show_res.status_code == 201
    show_id = show_res.json()["id"]

    # 4. Create Season 0 (Trailer) and Season 1
    s0_res = client.post(
        "/admin/seasons",
        json={"show_id": show_id, "season_number": 0, "title": "Trailers", "status": "published"},
        headers=headers
    )
    s0_id = s0_res.json()["id"]

    s1_res = client.post(
        "/admin/seasons",
        json={"show_id": show_id, "season_number": 1, "title": "Season 1", "status": "published"},
        headers=headers
    )
    s1_id = s1_res.json()["id"]

    # 5. Create Episodes (Season 0 Trailer + Season 1 Multi-Language Variants)
    client.post(
        "/admin/episodes",
        json={
            "season_id": s0_id,
            "episode_number": 1,
            "title": "Official Teaser",
            "content_group": "e2e-trailer-1",
            "language": "English",
            "duration_seconds": 90,
            "thumbnail_url": thumb_url,
            "status": "published"
        },
        headers=headers
    )

    client.post(
        "/admin/episodes",
        json={
            "season_id": s1_id,
            "episode_number": 1,
            "title": "Pilot Episode",
            "content_group": "e2e-ep-101",
            "language": "English",
            "duration_seconds": 3200,
            "thumbnail_url": thumb_url,
            "status": "published"
        },
        headers=headers
    )

    client.post(
        "/admin/episodes",
        json={
            "season_id": s1_id,
            "episode_number": 1,
            "title": "Pilot Episode (Hindi Dub)",
            "content_group": "e2e-ep-101",
            "language": "Hindi",
            "duration_seconds": 3200,
            "thumbnail_url": thumb_url,
            "status": "published"
        },
        headers=headers
    )

    # 6. Run Validation Report Audit
    val_res = client.get("/admin/validation-report", headers=headers)
    assert val_res.status_code == 200
    val_data = val_res.json()
    assert val_data["is_publishable"] is True
    assert val_data["total_blockers"] == 0

    # 7. Execute Atomic Catalogue Publish
    pub_res = client.post("/admin/catalog/publish", headers=headers)
    assert pub_res.status_code == 200
    assert pub_res.json()["status"] == "success"

    # 8. Public Viewer API Catalogue Read (Unauthenticated)
    cat_res = client.get("/catalog")
    assert cat_res.status_code == 200
    cat_data = cat_res.json()

    published_show = next(s for s in cat_data["shows"] if s["id"] == show_id)
    assert published_show["title"] == "E2E Platform Masterpiece"

    # Season 0 Exclusion Check
    season_numbers = [s["season_number"] for s in published_show["seasons"]]
    assert 0 not in season_numbers
    assert 1 in season_numbers
    assert len(published_show["trailers"]) == 1

    # Multi-Language Variant Grouping Check
    ep_group = published_show["seasons"][0]["episodes"][0]
    assert ep_group["content_group"] == "e2e-ep-101"
    assert "English" in ep_group["languages"]
    assert "Hindi" in ep_group["languages"]

    # 9. Public Composed Search Check
    search_res = client.get("/catalog/search?q=Masterpiece&language=Hindi&category=Drama")
    assert search_res.status_code == 200
    assert len(search_res.json()) == 1
