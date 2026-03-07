"""YouTube Data API v3 search tool."""

from __future__ import annotations

import logging

from googleapiclient.discovery import build

from config.settings import YOUTUBE_API_KEY, MAX_RESOURCE_RESULTS_PER_SKILL
from models.state import LearningResource

logger = logging.getLogger(__name__)


class YouTubeSearchTool:
    """Searches YouTube for learning videos related to given skills."""

    def __init__(self) -> None:
        if not YOUTUBE_API_KEY:
            logger.warning(
                "YOUTUBE_API_KEY is not set. YouTube search will return no results. "
                "Get a key at https://console.cloud.google.com (YouTube Data API v3)."
            )
        self._youtube = build(
            "youtube", "v3", developerKey=YOUTUBE_API_KEY
        )

    def search(
        self,
        skill_names: list[str],
        domain: str = "",
    ) -> list[LearningResource]:
        if not YOUTUBE_API_KEY:
            return []

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
                    item_id = item.get("id", {})
                    video_id = item_id.get("videoId")
                    if not video_id:
                        continue
                    snippet = item.get("snippet", {})
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
            except Exception as e:
                logger.exception(
                    "YouTube API error for query %r: %s",
                    query,
                    e,
                    exc_info=False,
                )
        return resources
