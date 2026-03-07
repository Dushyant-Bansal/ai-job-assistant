"""Agents that search for learning resources across different platforms.

Each agent class wraps one tool and writes results to a distinct state key
so they can run in parallel via LangGraph fan-out without conflicts.
"""

from __future__ import annotations

from config.settings import MAX_SKILLS_TO_SEARCH
from models.state import GraphState, LearningResource
from tools.amazon_tool import AmazonBookSearchTool
from tools.course_tools import CourseSearchTool
from tools.tavily_tools import TavilySearchTool
from tools.youtube_tool import YouTubeSearchTool


def _top_gap_skill_names(state: GraphState) -> list[str]:
    """Return the names of the top-N skills with the biggest gaps."""
    gaps = state.get("skill_gaps", [])
    return [g.skill_name for g in gaps[:MAX_SKILLS_TO_SEARCH]]


class WebArticleSearchAgent:
    """Searches Tavily for tutorial / guide web articles."""

    def __init__(self) -> None:
        self._tool = TavilySearchTool()

    def run(self, state: GraphState) -> dict:
        skills = _top_gap_skill_names(state)
        domain = state.get("software_domain", "")
        articles = self._tool.search_web_articles(skills, domain)
        return {"web_articles": articles}


class NewsSearchAgent:
    """Searches Tavily for recent news articles."""

    def __init__(self) -> None:
        self._tool = TavilySearchTool()

    def run(self, state: GraphState) -> dict:
        skills = _top_gap_skill_names(state)
        domain = state.get("software_domain", "")
        articles = self._tool.search_news(skills, domain)
        return {"news_articles": articles}


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
        books = self._tool.search(skills, domain)
        return {"amazon_books": books}


class CourseSearchAgent:
    """Searches O'Reilly, Pluralsight, Coursera, Udemy, DeepLearning.ai."""

    def __init__(self) -> None:
        self._tool = CourseSearchTool()

    def run(self, state: GraphState) -> dict:
        skills = _top_gap_skill_names(state)
        domain = state.get("software_domain", "")
        courses = self._tool.search(skills, domain)
        return {"training_courses": courses}


class BlogSearchAgent:
    """Searches for relevant blog posts on dev.to, Medium, Hashnode, etc."""

    def __init__(self) -> None:
        self._tool = TavilySearchTool()

    def run(self, state: GraphState) -> dict:
        skills = _top_gap_skill_names(state)
        domain = state.get("software_domain", "")
        posts = self._tool.search_blog_posts(skills, domain)
        return {"blog_posts": posts}
