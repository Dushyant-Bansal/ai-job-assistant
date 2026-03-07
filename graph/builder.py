"""Constructs and compiles the LangGraph that orchestrates the full pipeline."""

from __future__ import annotations

from langgraph.graph import END, StateGraph

from models.state import GraphState
from graph.nodes.jd_analyzer import JDAnalyzerAgent
from graph.nodes.resource_finder import (
    AmazonBookSearchAgent,
    BlogSearchAgent,
    CourseSearchAgent,
    NewsSearchAgent,
    WebArticleSearchAgent,
    YouTubeSearchAgent,
)
from graph.nodes.resume_analyzer import ResumeAnalyzerAgent
from graph.nodes.skill_matcher import SkillMatcherAgent
from graph.nodes.training_planner import TrainingPlannerAgent

# ---------------------------------------------------------------------------
# Instantiate agents (singletons — created once, reused per invocation)
# ---------------------------------------------------------------------------
_resume_agent = ResumeAnalyzerAgent()
_jd_agent = JDAnalyzerAgent()
_matcher_agent = SkillMatcherAgent()
_web_agent = WebArticleSearchAgent()
_news_agent = NewsSearchAgent()
_youtube_agent = YouTubeSearchAgent()
_amazon_agent = AmazonBookSearchAgent()
_course_agent = CourseSearchAgent()
_blog_agent = BlogSearchAgent()
_planner_agent = TrainingPlannerAgent()


# ---------------------------------------------------------------------------
# Thin wrappers that satisfy the LangGraph node signature (state → dict)
# ---------------------------------------------------------------------------
def parse_resume(state: GraphState) -> dict:
    return _resume_agent.run(state)


def analyze_jd(state: GraphState) -> dict:
    return _jd_agent.run(state)


def validate_industry(state: GraphState) -> dict:
    if not state.get("is_software_job", True):
        return {
            "error_message": (
                "This does not appear to be a software engineering job. "
                "We only support software engineering roles at this time."
            )
        }
    return {}


def match_skills(state: GraphState) -> dict:
    return _matcher_agent.run(state)


def search_web_articles(state: GraphState) -> dict:
    return _web_agent.run(state)


def search_news(state: GraphState) -> dict:
    return _news_agent.run(state)


def search_youtube(state: GraphState) -> dict:
    return _youtube_agent.run(state)


def search_amazon(state: GraphState) -> dict:
    return _amazon_agent.run(state)


def search_courses(state: GraphState) -> dict:
    return _course_agent.run(state)


def search_blog_posts(state: GraphState) -> dict:
    return _blog_agent.run(state)


def generate_training_plan(state: GraphState) -> dict:
    return _planner_agent.run(state)


# ---------------------------------------------------------------------------
# Routing function for the conditional edge after industry validation
# ---------------------------------------------------------------------------
def _route_after_validation(state: GraphState) -> str:
    if state.get("error_message"):
        return "stop"
    return "continue"


# ---------------------------------------------------------------------------
# Build and compile the graph
# ---------------------------------------------------------------------------
def build_graph():
    graph = StateGraph(GraphState)

    graph.add_node("parse_resume", parse_resume)
    graph.add_node("analyze_jd", analyze_jd)
    graph.add_node("validate_industry", validate_industry)
    graph.add_node("match_skills", match_skills)
    graph.add_node("search_web_articles", search_web_articles)
    graph.add_node("search_news", search_news)
    graph.add_node("search_youtube", search_youtube)
    graph.add_node("search_amazon", search_amazon)
    graph.add_node("search_courses", search_courses)
    graph.add_node("search_blog_posts", search_blog_posts)
    graph.add_node("generate_training_plan", generate_training_plan)

    # --- Edges ---
    graph.set_entry_point("parse_resume")
    graph.add_edge("parse_resume", "analyze_jd")
    graph.add_edge("analyze_jd", "validate_industry")

    graph.add_conditional_edges(
        "validate_industry",
        _route_after_validation,
        {"continue": "match_skills", "stop": END},
    )

    # Fan-out: after matching, search all resource types in parallel
    graph.add_edge("match_skills", "search_web_articles")
    graph.add_edge("match_skills", "search_news")
    graph.add_edge("match_skills", "search_youtube")
    graph.add_edge("match_skills", "search_amazon")
    graph.add_edge("match_skills", "search_courses")
    graph.add_edge("match_skills", "search_blog_posts")

    # Fan-in: all searches feed into the training planner
    graph.add_edge("search_web_articles", "generate_training_plan")
    graph.add_edge("search_news", "generate_training_plan")
    graph.add_edge("search_youtube", "generate_training_plan")
    graph.add_edge("search_amazon", "generate_training_plan")
    graph.add_edge("search_courses", "generate_training_plan")
    graph.add_edge("search_blog_posts", "generate_training_plan")

    graph.add_edge("generate_training_plan", END)

    return graph.compile()


def build_recompute_graph():
    """Builds a graph that runs from match_skills onward.

    Used when the user provides overrides (skill ratings, domain). Expects
    initial state to already contain user_skills, required_skills, job_title,
    industry, is_software_job, software_domain — with overrides applied.
    """
    graph = StateGraph(GraphState)

    graph.add_node("match_skills", match_skills)
    graph.add_node("search_web_articles", search_web_articles)
    graph.add_node("search_news", search_news)
    graph.add_node("search_youtube", search_youtube)
    graph.add_node("search_amazon", search_amazon)
    graph.add_node("search_courses", search_courses)
    graph.add_node("search_blog_posts", search_blog_posts)
    graph.add_node("generate_training_plan", generate_training_plan)

    graph.set_entry_point("match_skills")
    graph.add_edge("match_skills", "search_web_articles")
    graph.add_edge("match_skills", "search_news")
    graph.add_edge("match_skills", "search_youtube")
    graph.add_edge("match_skills", "search_amazon")
    graph.add_edge("match_skills", "search_courses")
    graph.add_edge("match_skills", "search_blog_posts")

    graph.add_edge("search_web_articles", "generate_training_plan")
    graph.add_edge("search_news", "generate_training_plan")
    graph.add_edge("search_youtube", "generate_training_plan")
    graph.add_edge("search_amazon", "generate_training_plan")
    graph.add_edge("search_courses", "generate_training_plan")
    graph.add_edge("search_blog_posts", "generate_training_plan")

    graph.add_edge("generate_training_plan", END)

    return graph.compile()
