from sqlalchemy.orm import Session
from typing import List

from app.models.show import Show, ContentStatus
from app.models.season import Season
from app.models.episode import Episode
from app.schemas.validation import ValidationReportResponse, ShowValidationReport
from app.storage.factory import get_storage_service
from app.storage.base import BaseStorageService


def generate_validation_report(db: Session, storage: BaseStorageService = None) -> ValidationReportResponse:
    """
    Scans the editorial database for publish blockers prior to generating a live catalogue.
    Groups problems by Show and Episode so content editors can resolve missing metadata/artwork.
    """
    if storage is None:
        storage = get_storage_service()

    # Query all shows that are candidates for publishing
    shows = db.query(Show).filter(Show.status == ContentStatus.PUBLISHED).all()

    shows_with_issues: List[ShowValidationReport] = []
    total_blockers = 0
    total_episodes_count = 0

    for show in shows:
        problems: List[str] = []

        # 1. Show-level checks
        if not show.section or not show.section.strip():
            problems.append("Show is missing a section classification (e.g., 'Trending Now').")

        if not show.category or not show.category.strip():
            problems.append("Show is missing a category (e.g., 'Crime').")

        if not show.poster_url:
            problems.append("Show is missing a poster artwork URL.")
        elif not storage.exists(show.poster_url):
            problems.append(f"Show poster artwork file does not exist in storage: '{show.poster_url}'.")

        if show.banner_url and not storage.exists(show.banner_url):
            problems.append(f"Show banner artwork file does not exist in storage: '{show.banner_url}'.")

        # 2. Season & Episode checks
        seasons = db.query(Season).filter(
            Season.show_id == show.id,
            Season.status == ContentStatus.PUBLISHED
        ).order_by(Season.season_number.asc()).all()

        if not seasons:
            problems.append("Show has no published seasons.")

        for season in seasons:
            episodes = db.query(Episode).filter(
                Episode.season_id == season.id,
                Episode.status == ContentStatus.PUBLISHED
            ).all()

            total_episodes_count += len(episodes)

            if not episodes:
                problems.append(f"Season {season.season_number} '{season.title or ''}' has no published episodes.")

            for ep in episodes:
                ep_prefix = f"Season {season.season_number} Episode {ep.episode_number} '{ep.title}' ({ep.language or 'Unknown Language'})"

                if not ep.content_group or not ep.content_group.strip():
                    problems.append(f"{ep_prefix} is missing a content_group key.")

                if not ep.language or not ep.language.strip():
                    problems.append(f"{ep_prefix} is missing a language classification.")

                if ep.duration_seconds is None or ep.duration_seconds <= 0:
                    problems.append(f"{ep_prefix} has no duration specified.")

                if not ep.thumbnail_url:
                    problems.append(f"{ep_prefix} is missing a thumbnail artwork URL.")
                elif not storage.exists(ep.thumbnail_url):
                    problems.append(f"{ep_prefix} thumbnail artwork file does not exist in storage: '{ep.thumbnail_url}'.")

        if problems:
            total_blockers += len(problems)
            shows_with_issues.append(
                ShowValidationReport(
                    show_id=show.id,
                    show_title=show.title,
                    problems=problems
                )
            )

    is_publishable = total_blockers == 0 and len(shows) > 0

    return ValidationReportResponse(
        is_publishable=is_publishable,
        total_blockers=total_blockers,
        shows_count=len(shows),
        episodes_count=total_episodes_count,
        shows_with_issues=shows_with_issues
    )
