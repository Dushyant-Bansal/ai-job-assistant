"""Tavily-powered web and news search tools."""

from __future__ import annotations

from tavily import TavilyClient

from config.settings import TAVILY_API_KEY, MAX_RESOURCE_RESULTS_PER_SKILL
from models.state import LearningResource


class TavilySearchTool:
    """Wraps Tavily for general web and news article searches."""

    def __init__(self) -> None:
        self._client = TavilyClient(api_key=TAVILY_API_KEY)

    def search_web_articles(
        self,
        skill_names: list[str],
        domain: str = "",
    ) -> list[LearningResource]:
        resources: list[LearningResource] = []
        for skill in skill_names:
            query = f"{skill} tutorial guide software engineering"
            if domain:
                query += f" {domain}"
            try:
                results = self._client.search(
                    query,
                    search_depth="advanced",
                    max_results=MAX_RESOURCE_RESULTS_PER_SKILL,
                )
                for r in results.get("results", []):
                    resources.append(
                        LearningResource(
                            title=r.get("title", ""),
                            url=r.get("url", ""),
                            source="web",
                            description=(r.get("content", "") or "")[:300],
                        )
                    )
            except Exception:
                continue
        return resources

    def search_news(
        self,
        skill_names: list[str],
        domain: str = "",
    ) -> list[LearningResource]:
        resources: list[LearningResource] = []
        for skill in skill_names:
            query = f"{skill} software engineering news latest"
            if domain:
                query += f" {domain}"
            try:
                results = self._client.search(
                    query,
                    search_depth="basic",
                    topic="news",
                    max_results=MAX_RESOURCE_RESULTS_PER_SKILL,
                )
                for r in results.get("results", []):
                    resources.append(
                        LearningResource(
                            title=r.get("title", ""),
                            url=r.get("url", ""),
                            source="news",
                            description=(r.get("content", "") or "")[:300],
                        )
                    )
            except Exception:
                continue
        return resources

    def search_blog_posts(
        self,
        skill_names: list[str],
        domain: str = "",
    ) -> list[LearningResource]:
        """Search for relevant blog posts on dev.to, Medium, Hashnode, etc."""
        resources: list[LearningResource] = []
        for skill in skill_names:
            query = f"{skill} blog software engineering"
            if domain:
                query += f" {domain}"
            try:
                results = self._client.search(
                    query,
                    search_depth="advanced",
                    max_results=MAX_RESOURCE_RESULTS_PER_SKILL,
                )
                for r in results.get("results", []):
                    url = r.get("url", "")
                    source = "blog"
                    if "dev.to" in url:
                        source = "dev.to"
                    elif "medium.com" in url:
                        source = "Medium"
                    elif "hashnode" in url:
                        source = "Hashnode"
                    elif "substack.com" in url:
                        source = "Substack"
                    resources.append(
                        LearningResource(
                            title=r.get("title", ""),
                            url=url,
                            source=source,
                            description=(r.get("content", "") or "")[:300],
                        )
                    )
            except Exception:
                continue
        return resources
