from typing import List, Dict, Any
from app.models.episode import Episode


def aggregate_episodes_by_group(episodes: List[Episode]) -> List[Dict[str, Any]]:
    """
    Groups raw episode records sharing the same content_group into a single logical catalogue episode item.
    Aggregates available language variants into a sorted list: ["English", "Hindi", "Spanish"].
    """
    grouped_map: Dict[str, Dict[str, Any]] = {}

    for ep in episodes:
        group_key = ep.content_group
        if group_key not in grouped_map:
            grouped_map[group_key] = {
                "content_group": ep.content_group,
                "episode_number": ep.episode_number,
                "title": ep.title,
                "synopsis": ep.synopsis,
                "duration_seconds": ep.duration_seconds,
                "poster_url": ep.poster_url,
                "banner_url": ep.banner_url,
                "thumbnail_url": ep.thumbnail_url,
                "languages": [ep.language],
                "variants": [
                    {
                        "language": ep.language,
                        "title": ep.title,
                        "duration_seconds": ep.duration_seconds,
                        "thumbnail_url": ep.thumbnail_url
                    }
                ]
            }
        else:
            entry = grouped_map[group_key]
            if ep.language not in entry["languages"]:
                entry["languages"].append(ep.language)
                entry["languages"].sort()
            entry["variants"].append({
                "language": ep.language,
                "title": ep.title,
                "duration_seconds": ep.duration_seconds,
                "thumbnail_url": ep.thumbnail_url
            })

    # Convert to list and sort by episode_number
    result = list(grouped_map.values())
    result.sort(key=lambda x: x["episode_number"])
    return result
