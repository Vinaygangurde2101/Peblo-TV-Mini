import os
import json
from app.core.config import settings


def test_public_catalogue_read(client):
    # Ensure dummy catalogue file exists
    storage_dir = os.path.dirname(settings.CATALOGUE_PATH)
    os.makedirs(storage_dir, exist_ok=True)

    dummy_payload = {
        "version": "1.0.0",
        "generated_at": "2026-09-03T00:00:00Z",
        "total_shows": 1,
        "total_episodes": 1,
        "sections": [
          {
            "name": "Trending Now",
            "shows": []
          }
        ],
        "shows": [
            {
                "id": "show-1",
                "title": "Breaking Badlands",
                "synopsis": "Meth producer story",
                "category": "Crime",
                "section": "Trending Now",
                "poster_url": "/static/artwork/poster.jpg",
                "banner_url": "/static/artwork/banner.jpg",
                "seasons": [
                    {
                        "id": "s1",
                        "season_number": 1,
                        "title": "Season 1",
                        "episodes": [
                            {
                                "content_group": "bb-ep-101",
                                "episode_number": 1,
                                "title": "Pilot",
                                "languages": ["English", "Hindi"],
                                "variants": []
                            }
                        ]
                    }
                ],
                "trailers": []
            }
        ]
    }

    with open(settings.CATALOGUE_PATH, "w", encoding="utf-8") as f:
        json.dump(dummy_payload, f)

    # 1. Fetch public catalog
    res = client.get("/catalog")
    assert res.status_code == 200
    data = res.json()
    assert data["version"] == "1.0.0"
    assert len(data["shows"]) == 1

    # 2. Composed search query
    search_res = client.get("/catalog/search?q=Badlands&category=Crime&language=Hindi&section=Trending%20Now")
    assert search_res.status_code == 200
    results = search_res.json()
    assert len(results) == 1
    assert results[0]["id"] == "show-1"

    # 3. Mismatched query returns empty array
    no_res = client.get("/catalog/search?category=NonExistentCategory")
    assert no_res.status_code == 200
    assert len(no_res.json()) == 0
