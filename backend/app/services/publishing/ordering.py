from typing import List, Dict, Any


def apply_deterministic_ordering(catalogue_shows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Sorts catalogue shows deterministically:
    1. Primary: section ASC (Unassigned placed last)
    2. Secondary: show title ASC
    Inside each show:
    3. seasons sorted by season_number ASC
    4. episodes sorted by episode_number ASC
    """
    def show_sort_key(show: Dict[str, Any]):
        section = show.get("section") or "ZZZZ_UNASSIGNED"
        title = show.get("title") or ""
        return (section.lower(), title.lower())

    sorted_shows = sorted(catalogue_shows, key=show_sort_key)

    for show in sorted_shows:
        if "seasons" in show:
            show["seasons"].sort(key=lambda s: s["season_number"])
            for season in show["seasons"]:
                if "episodes" in season:
                    season["episodes"].sort(key=lambda e: e["episode_number"])

    return sorted_shows
