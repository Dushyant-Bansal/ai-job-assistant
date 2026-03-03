"""Training course search across multiple platforms via Tavily site-scoped queries."""

from __future__ import annotations

from tavily import TavilyClient

from config.settings import TAVILY_API_KEY, MAX_RESOURCE_RESULTS_PER_SKILL
from models.state import LearningResource

COURSE_PLATFORMS = [
    ("oreilly", "site:oreilly.com"),
    ("pluralsight", "site:pluralsight.com"),
    ("coursera", "site:coursera.org"),
    ("udemy", "site:udemy.com"),
    ("deeplearning.ai", "site:deeplearning.ai"),
]


class CourseSearchTool:
    """Searches multiple online-learning platforms for courses on given skills."""

    def __init__(self) -> None:
        self._client = TavilyClient(api_key=TAVILY_API_KEY)

    def search(
        self,
        skill_names: list[str],
        domain: str = "",
    ) -> list[LearningResource]:
        resources: list[LearningResource] = []
        for skill in skill_names:
            for platform_name, site_filter in COURSE_PLATFORMS:
                query = f"{site_filter} course {skill}"
                if domain:
                    query += f" {domain}"
                try:
                    results = self._client.search(
                        query,
                        search_depth="basic",
                        max_results=MAX_RESOURCE_RESULTS_PER_SKILL,
                    )
                    for r in results.get("results", []):
                        resources.append(
                            LearningResource(
                                title=r.get("title", ""),
                                url=r.get("url", ""),
                                source=platform_name,
                                description=(r.get("content", "") or "")[:300],
                            )
                        )
                except Exception:
                    continue
        return resources
