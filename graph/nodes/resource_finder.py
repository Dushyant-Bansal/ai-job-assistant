"""Agents that search for learning resources across different platforms.

Each agent class wraps one tool and writes results to a distinct state key
so they can run in parallel via LangGraph fan-out without conflicts.
"""

from __future__ import annotations

import logging

from config.settings import MAX_SKILLS_TO_SEARCH

logger = logging.getLogger(__name__)
from models.state import GraphState, LearningResource
from tools.amazon_tool import AmazonBookSearchTool
from tools.course_tools import CourseSearchTool
from tools.tavily_tools import TavilySearchTool
from tools.youtube_tool import YouTubeSearchTool


def _skill_name(s) -> str:
    """Extract skill name from Skill or dict."""
    return s.name if hasattr(s, "name") else s.get("name", "")


def _top_gap_skill_names(state: GraphState) -> list[str]:
    """Return the names of the top-N skills with the biggest gaps.

    Falls back to required_skills when there are no gaps (e.g. perfect match).
    Falls back to software_domain or generic query when both are empty.
    """
    gaps = state.get("skill_gaps", [])
    if gaps:
        return [
            g.skill_name if hasattr(g, "skill_name") else g.get("skill_name", "")
            for g in gaps[:MAX_SKILLS_TO_SEARCH]
        ]
    # No gaps — use top required skills so we still get resources
    required = state.get("required_skills", [])
    names = [_skill_name(s) for s in required[:MAX_SKILLS_TO_SEARCH]]
    if names:
        return names
    # required_skills may be empty when "ignore programming languages" filtered all
    required_for_resources = state.get("required_skills_for_resources", [])
    names = [_skill_name(s) for s in required_for_resources[:MAX_SKILLS_TO_SEARCH]]
    if names:
        return names
    # Both empty — use domain or generic so we still return resources
    domain = state.get("software_domain", "").strip()
    if domain:
        return [domain]
    return ["software engineering"]


class WebArticleSearchAgent:
    """Searches Tavily for tutorial / guide web articles."""

    def __init__(self) -> None:
        self._tool = TavilySearchTool()

    def run(self, state: GraphState) -> dict:
        skills = _top_gap_skill_names(state)
        domain = state.get("software_domain", "")
        if not skills:
            logger.warning(
                "WebArticleSearchAgent: no skills to search (skill_gaps and required_skills empty)"
            )
        articles, err = self._tool.search_web_articles(skills, domain)
        logger.info("WebArticleSearchAgent: found %d web articles for %d skills", len(articles), len(skills))
        out: dict = {"web_articles": articles, "search_skills_used": skills}
        if err:
            out["resource_search_warnings"] = [f"Tavily (web): {err}"]
        return out


class NewsSearchAgent:
    """Searches Tavily for recent news articles."""

    def __init__(self) -> None:
        self._tool = TavilySearchTool()

    def run(self, state: GraphState) -> dict:
        skills = _top_gap_skill_names(state)
        domain = state.get("software_domain", "")
        articles, err = self._tool.search_news(skills, domain)
        out: dict = {"news_articles": articles}
        if err:
            out["resource_search_warnings"] = [f"Tavily (news): {err}"]
        return out


class YouTubeSearchAgent:
    """Searches YouTube for learning videos."""

    def __init__(self) -> None:
        self._tool = YouTubeSearchTool()

    def run(self, state: GraphState) -> dict:
        skills = _top_gap_skill_names(state)
        domain = state.get("software_domain", "")
        videos = self._tool.search(skills, domain)
        return {"youtube_videos": videos}


class AmazonBookSearchAgent:
    """Searches Amazon for relevant books."""

    def __init__(self) -> None:
        self._tool = AmazonBookSearchTool()

    def run(self, state: GraphState) -> dict:
        skills = _top_gap_skill_names(state)
        domain = state.get("software_domain", "")
        books, err = self._tool.search(skills, domain)
        out: dict = {"amazon_books": books}
        if err:
            out["resource_search_warnings"] = [f"Tavily (Amazon): {err}"]
        return out


class CourseSearchAgent:
    """Searches O'Reilly, Pluralsight, Coursera, Udemy, DeepLearning.ai."""

    def __init__(self) -> None:
        self._tool = CourseSearchTool()

    def run(self, state: GraphState) -> dict:
        skills = _top_gap_skill_names(state)
        domain = state.get("software_domain", "")
        courses, err = self._tool.search(skills, domain)
        out: dict = {"training_courses": courses}
        if err:
            out["resource_search_warnings"] = [f"Tavily (courses): {err}"]
        return out


class BlogSearchAgent:
    """Searches for relevant blog posts on dev.to, Medium, Hashnode, etc."""

    def __init__(self) -> None:
        self._tool = TavilySearchTool()

    def run(self, state: GraphState) -> dict:
        skills = _top_gap_skill_names(state)
        domain = state.get("software_domain", "")
        posts, err = self._tool.search_blog_posts(skills, domain)
        out: dict = {"blog_posts": posts}
        if err:
            out["resource_search_warnings"] = [f"Tavily (blog): {err}"]
        return out
