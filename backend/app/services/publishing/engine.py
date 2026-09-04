import os
import json
import uuid
from datetime import datetime, timezone
from typing import Dict, Any, Tuple
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.show import Show, ContentStatus
from app.models.season import Season
from app.models.episode import Episode
from app.models.publish_run import PublishRun, PublishStatus
from app.services.validation.report import generate_validation_report
from app.services.publishing.aggregator import aggregate_episodes_by_group
from app.services.publishing.ordering import apply_deterministic_ordering
from app.storage.factory import get_storage_service


class PublishValidationError(Exception):
    def __init__(self, validation_report):
        self.validation_report = validation_report
        super().__init__("Publish operation blocked by validation errors.")


def execute_catalogue_publish(db: Session, user_id: str) -> PublishRun:
    """
    Executes the 8-step atomic publishing flow:
    1. Validation check -> abort if blockers exist and log FAILED PublishRun
    2. Query published content
    3. Aggregate language variants per content_group
    4. Exclude Season 0 from normal season listings (nest under trailers)
    5. Apply deterministic sorting
    6. Generate catalogue JSON structure
    7. Write to temp file & perform atomic OS replace
    8. Record SUCCESS PublishRun in DB
    """
    storage = get_storage_service()

    # STEP 1: Validation Audit
    validation_report = generate_validation_report(db, storage)
    if not validation_report.is_publishable:
        failed_run = PublishRun(
            published_by_user_id=user_id,
            status=PublishStatus.FAILED,
            show_count=validation_report.shows_count,
            episode_count=validation_report.episodes_count,
            validation_errors=validation_report.model_dump(),
            error_message="Catalogue publish blocked by validation failures."
        )
        db.add(failed_run)
        db.commit()
        db.refresh(failed_run)
        raise PublishValidationError(validation_report)

    # STEP 2 & 3 & 4: Fetch Published Content & Group Variants
    shows = db.query(Show).filter(Show.status == ContentStatus.PUBLISHED).all()

    catalogue_shows = []
    total_episodes_published = 0
    section_set = set()

    for show in shows:
        if show.section:
            section_set.add(show.section)

        show_data: Dict[str, Any] = {
            "id": show.id,
            "title": show.title,
            "synopsis": show.synopsis,
            "category": show.category,
            "section": show.section,
            "poster_url": show.poster_url,
            "banner_url": show.banner_url,
            "seasons": [],
            "trailers": []
        }

        seasons = db.query(Season).filter(
            Season.show_id == show.id,
            Season.status == ContentStatus.PUBLISHED
        ).order_by(Season.season_number.asc()).all()

        for season in seasons:
            episodes = db.query(Episode).filter(
                Episode.season_id == season.id,
                Episode.status == ContentStatus.PUBLISHED
            ).order_by(Episode.episode_number.asc()).all()

            grouped_episodes = aggregate_episodes_by_group(episodes)
            total_episodes_published += len(episodes)

            # STEP 4: Exclude Season 0 from normal viewer season listings
            if season.season_number == 0:
                show_data["trailers"].extend(grouped_episodes)
            else:
                show_data["seasons"].append({
                    "id": season.id,
                    "season_number": season.season_number,
                    "title": season.title or f"Season {season.season_number}",
                    "episodes": grouped_episodes
                })

        catalogue_shows.append(show_data)

    # STEP 5: Deterministic Ordering
    sorted_shows = apply_deterministic_ordering(catalogue_shows)

    # Build grouped sections array for viewer UI
    sections_map: Dict[str, list] = {}
    for show_item in sorted_shows:
        sec_name = show_item.get("section") or "Featured"
        if sec_name not in sections_map:
            sections_map[sec_name] = []
        sections_map[sec_name].append(show_item)

    sections_list = [
        {"name": sec_name, "shows": show_list}
        for sec_name, show_list in sections_map.items()
    ]

    # STEP 6: Generate Catalogue JSON Payload
    now_utc = datetime.now(timezone.utc).isoformat()
    catalogue_payload = {
        "version": "1.0.0",
        "generated_at": now_utc,
        "total_shows": len(sorted_shows),
        "total_episodes": total_episodes_published,
        "sections": sections_list,
        "shows": sorted_shows
    }

    # STEP 7: Temp File Generation & Atomic OS Replace
    storage_dir = os.path.dirname(settings.CATALOGUE_PATH)
    os.makedirs(storage_dir, exist_ok=True)

    temp_catalogue_path = f"{settings.CATALOGUE_PATH}.tmp.{uuid.uuid4().hex}"
    
    with open(temp_catalogue_path, "w", encoding="utf-8") as f:
        json.dump(catalogue_payload, f, indent=2, ensure_ascii=False)

    # Atomic swap: OS-level atomic replace guarantees readers never see partial content
    os.replace(temp_catalogue_path, settings.CATALOGUE_PATH)

    # STEP 8: Record SUCCESS PublishRun in DB
    success_run = PublishRun(
        published_by_user_id=user_id,
        status=PublishStatus.SUCCESS,
        show_count=len(sorted_shows),
        episode_count=total_episodes_published,
        snapshot_path=settings.CATALOGUE_PATH,
        validation_errors=None
    )
    db.add(success_run)
    db.commit()
    db.refresh(success_run)

    return success_run
