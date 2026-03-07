from __future__ import annotations

from typing import Annotated, TypedDict

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Pydantic models used for LLM structured output
# ---------------------------------------------------------------------------

class Skill(BaseModel):
    """A single skill extracted from a resume or job description."""

    name: str = Field(description="Canonical skill name")
    category: str = Field(description="'technical' or 'soft'")
    rating: int = Field(
        ge=1,
        le=100,
        description="Proficiency rating 1-100",
    )
    years_experience: float | None = Field(
        default=None,
        description="Estimated years of experience, if inferable",
    )
    depth_signal: str = Field(
        default="",
        description="Verbatim text evidence justifying the rating",
    )


class ResumeAnalysis(BaseModel):
    """Structured output from resume analysis."""

    skills: list[Skill] = Field(default_factory=list)


class JDAnalysis(BaseModel):
    """Structured output from job-description analysis."""

    job_title: str = ""
    experience_years: int | None = None
    industry: str = ""
    is_software_job: bool = True
    software_domain: str = ""
    required_skills: list[Skill] = Field(default_factory=list)


class SkillGap(BaseModel):
    """Represents a gap between a user's skill level and the required level."""

    skill_name: str
    user_rating: int = 0
    required_rating: int = 0
    gap: int = 0
    priority: str = "medium"


class LearningResource(BaseModel):
    """A single learning resource (article, video, book, course …)."""

    title: str
    url: str
    source: str = ""
    description: str = ""


class TrainingStep(BaseModel):
    """One step in the generated training plan."""

    skill: str
    priority: int = 1
    estimated_hours: int = 0
    description: str = ""
    resources: list[LearningResource] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# LangGraph state – the central data contract flowing through every node
# ---------------------------------------------------------------------------

def _merge_resources(
    existing: list[LearningResource],
    new: list[LearningResource],
) -> list[LearningResource]:
    """Reducer that merges resource lists without duplicates."""
    seen_urls = {r.url for r in existing}
    merged = list(existing)
    for r in new:
        if r.url not in seen_urls:
            merged.append(r)
            seen_urls.add(r.url)
    return merged


class GraphState(TypedDict, total=False):
    # Inputs
    resume_text: str
    job_description: str

    # Resume analysis
    user_skills: list[Skill]

    # JD analysis
    required_skills: list[Skill]
    job_title: str
    experience_years: int | None
    industry: str
    is_software_job: bool
    software_domain: str

    # Matching
    match_percentage: float
    skill_gaps: list[SkillGap]

    # Resources
    web_articles: Annotated[list[LearningResource], _merge_resources]
    news_articles: Annotated[list[LearningResource], _merge_resources]
    youtube_videos: Annotated[list[LearningResource], _merge_resources]
    amazon_books: Annotated[list[LearningResource], _merge_resources]
    training_courses: Annotated[list[LearningResource], _merge_resources]
    blog_posts: Annotated[list[LearningResource], _merge_resources]

    # Output
    training_plan: list[TrainingStep]
    error_message: str | None
