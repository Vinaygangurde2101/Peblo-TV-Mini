import os
import json
from fastapi import APIRouter, HTTPException, Query, status
from typing import Optional, List, Dict, Any

from app.core.config import settings
from app.schemas.catalogue import CatalogueResponse, CatalogueShow

router = APIRouter(prefix="/catalog", tags=["Public Catalogue"])


def _load_published_catalogue() -> Dict[str, Any]:
    """Helper loading live catalogue.json from disk storage with 404 fallback."""
    if not os.path.exists(settings.CATALOGUE_PATH):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No catalogue has been published yet. Please run administrative publish."
        )

    try:
        with open(settings.CATALOGUE_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error reading published catalogue file."
        )


@router.get("", response_model=CatalogueResponse)
def get_published_catalogue():
    """
    Returns the live published catalogue.
    PUBLIC CONSUMPTION ENDPOINT. Does not query administrative database.
    """
    return _load_published_catalogue()


@router.get("/search", response_model=List[CatalogueShow])
def search_catalogue(
    q: Optional[str] = Query(None, description="Search term matching show or episode title"),
    category: Optional[str] = Query(None, description="Filter by category"),
    language: Optional[str] = Query(None, description="Filter by available language variant"),
    section: Optional[str] = Query(None, description="Filter by section")
):
    """
    Performs composed search and filtering across published catalogue shows and episodes.
    Filters compose: q, category, language, and section all apply simultaneously.
    """
    catalogue = _load_published_catalogue()
    shows = catalogue.get("shows", [])

    results = []

    for show in shows:
        # Category filter
        if category and (not show.get("category") or show["category"].lower() != category.lower()):
            continue

        # Section filter
        if section and (not show.get("section") or show["section"].lower() != section.lower()):
            continue

        # Search term filter (q)
        if q:
            term = q.lower()
            show_title_match = term in (show.get("title") or "").lower()
            show_synopsis_match = term in (show.get("synopsis") or "").lower()
            
            # Check episode titles inside seasons
            ep_match = False
            for season in show.get("seasons", []):
                for ep in season.get("episodes", []):
                    if term in (ep.get("title") or "").lower():
                        ep_match = True
                        break
                if ep_match:
                    break

            if not (show_title_match or show_synopsis_match or ep_match):
                continue

        # Language variant filter
        if language:
            lang_term = language.lower()
            has_language = False
            for season in show.get("seasons", []):
                for ep in season.get("episodes", []):
                    ep_langs = [l.lower() for l in ep.get("languages", [])]
                    if lang_term in ep_langs:
                        has_language = True
                        break
                if has_language:
                    break

            if not has_language:
                continue

        results.append(show)

    return results
