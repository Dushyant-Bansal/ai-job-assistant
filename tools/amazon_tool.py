"""Amazon book search via Tavily site-scoped queries."""

from __future__ import annotations

import logging

from tavily import TavilyClient

from config.settings import TAVILY_API_KEY, MAX_RESOURCE_RESULTS_PER_SKILL
from models.state import LearningResource

logger = logging.getLogger(__name__)


class AmazonBookSearchTool:
    """Finds relevant books on Amazon using site-scoped Tavily search."""

    def __init__(self) -> None:
        self._client = TavilyClient(api_key=TAVILY_API_KEY)

    def search(
        self,
        skill_names: list[str],
        domain: str = "",
    ) -> tuple[list[LearningResource], str | None]:
        resources: list[LearningResource] = []
        first_error: str | None = None
        for skill in skill_names:
            query = f"site:amazon.com book {skill} software engineering"
            if domain:
                query += f" {domain}"
            try:
                raw = self._client.search(
                    query,
                    search_depth="basic",
                    max_results=MAX_RESOURCE_RESULTS_PER_SKILL,
                )
                items = raw.get("results", []) if isinstance(raw, dict) else getattr(raw, "results", [])
                for r in items:
                    resources.append(
                        LearningResource(
                            title=r.get("title", ""),
                            url=r.get("url", ""),
                            source="amazon",
                            description=(r.get("content", "") or "")[:300],
                        )
                    )
            except Exception as e:
                if first_error is None:
                    first_error = str(e)
                logger.warning("Tavily Amazon search failed for %r: %s", query, e)
        return resources, first_error
