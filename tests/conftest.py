"""Pytest fixtures and configuration."""

from __future__ import annotations

import pytest

from models.state import LearningResource, Skill, SkillGap, TrainingStep


@pytest.fixture
def sample_user_skills() -> list[Skill]:
    return [
        Skill(name="Python", category="technical", rating=70),
        Skill(name="Kubernetes", category="technical", rating=40),
        Skill(name="LLMs", category="technical", rating=50),
    ]


@pytest.fixture
def sample_required_skills() -> list[Skill]:
    return [
        Skill(name="Python", category="technical", rating=80),
        Skill(name="Kubernetes", category="technical", rating=70),
        Skill(name="Large Language Models (LLMs)", category="technical", rating=75),
    ]


@pytest.fixture
def sample_skill_gaps() -> list[SkillGap]:
    return [
        SkillGap(skill_name="Kubernetes", user_rating=40, required_rating=70, gap=30, priority="high"),
        SkillGap(skill_name="Large Language Models (LLMs)", user_rating=50, required_rating=75, gap=25, priority="medium"),
    ]


@pytest.fixture
def sample_training_plan() -> list[TrainingStep]:
    return [
        TrainingStep(
            skill="Kubernetes",
            priority=1,
            estimated_hours=20,
            description="Learn container orchestration.",
            resources=[
                LearningResource(title="K8s Docs", url="https://k8s.io", source="web", description=""),
            ],
        ),
    ]


@pytest.fixture
def sample_analysis_result(sample_user_skills, sample_required_skills, sample_skill_gaps, sample_training_plan) -> dict:
    return {
        "job_description": "We need a Python developer with Kubernetes experience.",
        "match_percentage": 65.0,
        "job_title": "Senior Software Engineer",
        "software_domain": "Cloud Infrastructure",
        "user_skills": sample_user_skills,
        "required_skills": sample_required_skills,
        "skill_gaps": sample_skill_gaps,
        "training_plan": sample_training_plan,
        "web_articles": [
            LearningResource(title="K8s Tutorial", url="https://example.com/k8s", source="web", description=""),
        ],
        "news_articles": [],
        "blog_posts": [],
        "youtube_videos": [],
        "amazon_books": [],
        "training_courses": [],
    }
