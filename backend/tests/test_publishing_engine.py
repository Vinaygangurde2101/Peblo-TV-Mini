import os
import json
import pytest
from app.auth.jwt import create_access_token
from app.models.show import Show, ContentStatus
from app.models.season import Season
from app.models.episode import Episode
from app.core.config import settings


def get_headers(user):
    token = create_access_token(user_id=user.id, email=user.email, role=user.role)
    return {"Authorization": f"Bearer {token}"}


def test_editor_cannot_publish_catalog(client, editor_user):
    headers = get_headers(editor_user)
    response = client.post("/admin/catalog/publish", headers=headers)
    assert response.status_code == 403
    assert "Permission denied" in response.json()["detail"]


def test_successful_atomic_publishing_flow(client, admin_user, db):
    headers = get_headers(admin_user)

    # Isolate test environment by making existing seeded shows draft
    db.query(Show).update({"status": ContentStatus.DRAFT})
    db.commit()

    # 1. Create artwork file placeholders to pass validation
    artwork_dir = os.path.join(settings.STORAGE_PATH, "artwork")
    os.makedirs(artwork_dir, exist_ok=True)
    poster_file = os.path.join(artwork_dir, "test_poster.jpg")
    thumb_file = os.path.join(artwork_dir, "test_thumb.jpg")
    with open(poster_file, "w") as f:
        f.write("fake_img_data")
    with open(thumb_file, "w") as f:
        f.write("fake_img_data")

    poster_url = "/static/artwork/test_poster.jpg"
    thumb_url = "/static/artwork/test_thumb.jpg"

    # 2. Populate Valid Published Show, Seasons (S0 + S1), and Multi-Language Episodes
    show = Show(
        title="Breaking Badlands Test",
        synopsis="Testing synopsis",
        category="Crime",
        section="Trending Now",
        status=ContentStatus.PUBLISHED,
        poster_url=poster_url
    )
    db.add(show)
    db.commit()

    # Season 0 (Trailer)
    s0 = Season(show_id=show.id, season_number=0, title="Trailers", status=ContentStatus.PUBLISHED)
    # Season 1 (Normal Season)
    s1 = Season(show_id=show.id, season_number=1, title="Season 1", status=ContentStatus.PUBLISHED)
    db.add_all([s0, s1])
    db.commit()

    # Episode 0 (Trailer in S0)
    ep_trailer = Episode(
        season_id=s0.id,
        episode_number=1,
        title="Official Teaser",
        content_group="test-trailer-01",
        language="English",
        duration_seconds=60,
        thumbnail_url=thumb_url,
        status=ContentStatus.PUBLISHED
    )

    # Episode 1 Variant English
    ep1_en = Episode(
        season_id=s1.id,
        episode_number=1,
        title="Pilot",
        content_group="test-ep-101",
        language="English",
        duration_seconds=3000,
        thumbnail_url=thumb_url,
        status=ContentStatus.PUBLISHED
    )

    # Episode 1 Variant Hindi
    ep1_hi = Episode(
        season_id=s1.id,
        episode_number=1,
        title="Pilot (Hindi)",
        content_group="test-ep-101",
        language="Hindi",
        duration_seconds=3000,
        thumbnail_url=thumb_url,
        status=ContentStatus.PUBLISHED
    )

    db.add_all([ep_trailer, ep1_en, ep1_hi])
    db.commit()

    # 3. Trigger Admin Publish
    response = client.post("/admin/catalog/publish", headers=headers)
    if response.status_code != 200:
        print("PUBLISH ERROR DETAIL:", response.json())
    assert response.status_code == 200
    res_data = response.json()
    assert res_data["status"] == "success"
    assert res_data["show_count"] >= 1

    # 4. Verify output file on disk
    assert os.path.exists(settings.CATALOGUE_PATH)
    with open(settings.CATALOGUE_PATH, "r", encoding="utf-8") as f:
        catalog_payload = json.load(f)

    assert catalog_payload["version"] == "1.0.0"
    target_show = next(s for s in catalog_payload["shows"] if s["id"] == show.id)

    # Check Season 0 handling: S0 must be in trailers, not seasons list
    season_numbers = [s["season_number"] for s in target_show["seasons"]]
    assert 0 not in season_numbers
    assert 1 in season_numbers
    assert len(target_show["trailers"]) == 1

    # Check Language Variant Grouping
    s1_data = next(s for s in target_show["seasons"] if s["season_number"] == 1)
    grouped_ep = s1_data["episodes"][0]
    assert grouped_ep["content_group"] == "test-ep-101"
    assert "English" in grouped_ep["languages"]
    assert "Hindi" in grouped_ep["languages"]
    assert len(grouped_ep["variants"]) == 2
