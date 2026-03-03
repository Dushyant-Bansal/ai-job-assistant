"""YouTube Data API v3 search tool."""

from __future__ import annotations

from googleapiclient.discovery import build

from config.settings import YOUTUBE_API_KEY, MAX_RESOURCE_RESULTS_PER_SKILL
from models.state import LearningResource


class YouTubeSearchTool:
    """Searches YouTube for learning videos related to given skills."""

    def __init__(self) -> None:
        self._youtube = build(
            "youtube", "v3", developerKey=YOUTUBE_API_KEY
        )

    def search(
        self,
        skill_names: list[str],
        domain: str = "",
    ) -> list[LearningResource]:
        resources: list[LearningResource] = []
        for skill in skill_names:
            query = f"{skill} tutorial software engineering"
            if domain:
                query += f" {domain}"
            try:
                response = (
                    self._youtube.search()
                    .list(
                        q=query,
                        part="snippet",
                        type="video",
                        maxResults=MAX_RESOURCE_RESULTS_PER_SKILL,
                        order="relevance",
                    )
                    .execute()
                )
                for item in response.get("items", []):
                    video_id = item["id"]["videoId"]
                    snippet = item["snippet"]
                    resources.append(
                        LearningResource(
                            title=snippet.get("title", ""),
                            url=f"https://www.youtube.com/watch?v={video_id}",
                            source="youtube",
                            description=(
                                snippet.get("description", "") or ""
                            )[:300],
                        )
                    )
            except Exception:
                continue
        return resources
