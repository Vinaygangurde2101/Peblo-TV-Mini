from app.auth.jwt import create_access_token
from app.models.show import Show, ContentStatus
from app.models.season import Season
from app.models.episode import Episode


def test_validation_report_detects_missing_metadata(client, editor_user, db):
    token = create_access_token(user_id=editor_user.id, email=editor_user.email, role=editor_user.role)
    headers = {"Authorization": f"Bearer {token}"}

    # Create published show missing section and poster
    show = Show(
        title="Imperfect Show",
        status=ContentStatus.PUBLISHED,
        category="Drama",
        section=None,
        poster_url=None
    )
    db.add(show)
    db.commit()

    season = Season(
        show_id=show.id,
        season_number=1,
        title="Season 1",
        status=ContentStatus.PUBLISHED
    )
    db.add(season)
    db.commit()

    # Episode missing duration_seconds and thumbnail_url
    ep = Episode(
        season_id=season.id,
        episode_number=1,
        title="Episode 1",
        content_group="imp-ep-1",
        language="English",
        duration_seconds=None,
        thumbnail_url=None,
        status=ContentStatus.PUBLISHED
    )
    db.add(ep)
    db.commit()

    response = client.get("/admin/validation-report", headers=headers)
    assert response.status_code == 200
    data = response.json()

    assert data["is_publishable"] is False
    assert data["total_blockers"] >= 3
    assert len(data["shows_with_issues"]) > 0

    imperfect_report = next(s for s in data["shows_with_issues"] if s["show_id"] == show.id)
    assert any("section" in p for p in imperfect_report["problems"])
    assert any("poster" in p for p in imperfect_report["problems"])
    assert any("duration" in p for p in imperfect_report["problems"])
