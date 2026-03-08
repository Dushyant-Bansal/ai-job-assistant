"""Agent that generates a prioritised training plan using an LLM."""

from __future__ import annotations

import json
from typing import Any

from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from config.settings import LLM_MODEL, LLM_TEMPERATURE
from models.state import (
    GraphState,
    TrainingPlan,
    TrainingStep,
)

SYSTEM_PROMPT = """\
You are a career coach who creates actionable training plans for software
engineers preparing for a specific job.

You will receive:
- The target job title and software domain.
- A list of skill gaps (skill name, user rating, required rating, gap size,
  priority).
- Available learning resources grouped by type.

Produce a list of training steps.  Each step:
- **skill** – The skill to improve.
- **priority** – Integer starting from 1 (most important first).  Order by
  gap priority (critical > high > medium > low) then gap size descending.
- **estimated_hours** – Rough estimate of study hours needed.
- **description** – 2-3 sentence actionable guidance on *how* to close the gap.
- **resources** – Pick the 3-5 most relevant resources from the provided lists
  for this skill.  Each resource needs: title, url, source, description.
"""

USER_PROMPT = """\
Job title: {job_title}
Domain: {software_domain}

Skill gaps (sorted by importance):
{gaps_json}

Available resources:
{resources_json}
"""


def _resources_payload(state: GraphState) -> str:
    """Serialise all resource lists into a compact JSON block."""
    all_resources: list[dict[str, Any]] = []
    for key in (
        "web_articles",
        "news_articles",
        "youtube_videos",
        "amazon_books",
        "training_courses",
        "blog_posts",
    ):
        for r in state.get(key, []):
            item = r if isinstance(r, dict) else r.model_dump()
            all_resources.append(item)
    return json.dumps(all_resources, indent=1)


class TrainingPlannerAgent:
    """LLM-backed agent that synthesises gaps and resources into a training plan."""

    def __init__(self) -> None:
        self._llm = ChatOpenAI(
            model=LLM_MODEL,
            temperature=LLM_TEMPERATURE,
        ).with_structured_output(TrainingPlan)
        self._prompt = ChatPromptTemplate.from_messages(
            [("system", SYSTEM_PROMPT), ("human", USER_PROMPT)]
        )

    def run(self, state: GraphState) -> dict:
        gaps = state.get("skill_gaps", [])
        gaps_json = json.dumps(
            [g.model_dump() if hasattr(g, "model_dump") else g for g in gaps],
            indent=1,
        )

        chain = self._prompt | self._llm
        result: TrainingPlan = chain.invoke(
            {
                "job_title": state.get("job_title", ""),
                "software_domain": state.get("software_domain", ""),
                "gaps_json": gaps_json,
                "resources_json": _resources_payload(state),
            }
        )

        training_plan = sorted(result.steps, key=lambda t: t.priority)
        return {"training_plan": training_plan}
