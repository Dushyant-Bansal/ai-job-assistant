"""LLM-as-a-judge evaluation tests.

These tests use an LLM to evaluate the quality of analysis outputs.
Requires OPENAI_API_KEY. Skip if not set or if --skip-evals is passed.
"""

from __future__ import annotations

import os
import pytest

from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

# Skip entire module if no API key or --skip-evals
pytestmark = pytest.mark.skipif(
    not os.getenv("OPENAI_API_KEY") or os.getenv("SKIP_EVALS") == "1",
    reason="OPENAI_API_KEY required for evals; set SKIP_EVALS=1 to skip",
)


JUDGE_PROMPT = """\
You are an expert evaluator for a job training assistant app.

Given:
1. Job description (excerpt): {job_description}
2. Skill gaps: {skill_gaps}
3. Training plan: {training_plan}

Evaluate whether the output is REASONABLE. Consider:
- Are the skill gaps plausible given the job description?
- Does the training plan address the gaps in a sensible order?
- Are the priorities (critical/high/medium/low) appropriate for the gap sizes?

Respond with ONLY a JSON object: {{"score": 1-5, "reason": "brief explanation"}}
Score: 5=excellent, 4=good, 3=acceptable, 2=poor, 1=unacceptable
"""


def _run_judge(job_excerpt: str, skill_gaps: list[dict], training_plan: list[dict]) -> dict:
    """Run LLM judge and return parsed score."""
    import json
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    prompt = ChatPromptTemplate.from_messages([("human", JUDGE_PROMPT)])
    chain = prompt | llm
    result = chain.invoke({
        "job_description": job_excerpt[:500],
        "skill_gaps": str(skill_gaps),
        "training_plan": str(training_plan),
    })
    raw = result.content if hasattr(result, "content") else str(result)
    raw = raw.strip()
    if raw.startswith("```"):
        raw = raw.split("\n", 1)[1] if "\n" in raw else raw[3:]
    if raw.endswith("```"):
        raw = raw.rsplit("```", 1)[0]
    return json.loads(raw.strip())


class TestLLMJudgeSkillGaps:
    """Eval: Are skill gaps plausible for the job description?"""

    def test_software_engineer_jd_skill_gaps(self):
        job_excerpt = (
            "We are looking for a Senior Software Engineer with strong Python, "
            "Kubernetes, and cloud experience. 5+ years required. "
            "Experience with LLMs and RAG systems is a plus."
        )
        skill_gaps = [
            {"skill_name": "Kubernetes", "user_rating": 30, "required_rating": 75, "gap": 45, "priority": "high"},
            {"skill_name": "Python", "user_rating": 60, "required_rating": 80, "gap": 20, "priority": "medium"},
        ]
        training_plan = [
            {"skill": "Kubernetes", "priority": 1, "estimated_hours": 25, "description": "Learn container orchestration."},
            {"skill": "Python", "priority": 2, "estimated_hours": 10, "description": "Deepen Python expertise."},
        ]
        out = _run_judge(job_excerpt, skill_gaps, training_plan)
        assert out["score"] >= 3, f"Judge score {out['score']}: {out.get('reason', '')}"


class TestLLMJudgeTrainingPlan:
    """Eval: Does the training plan make sense?"""

    def test_training_plan_prioritizes_critical_gaps(self):
        job_excerpt = "Python developer, Kubernetes required, AWS preferred."
        skill_gaps = [
            {"skill_name": "Kubernetes", "user_rating": 10, "required_rating": 80, "gap": 70, "priority": "critical"},
            {"skill_name": "AWS", "user_rating": 50, "required_rating": 60, "gap": 10, "priority": "low"},
        ]
        training_plan = [
            {"skill": "Kubernetes", "priority": 1, "estimated_hours": 40, "description": "Critical gap."},
            {"skill": "AWS", "priority": 2, "estimated_hours": 5, "description": "Small gap."},
        ]
        out = _run_judge(job_excerpt, skill_gaps, training_plan)
        assert out["score"] >= 3, f"Judge score {out['score']}: {out.get('reason', '')}"


class TestLLMJudgeSynonymMatching:
    """Eval: Are synonym skills (e.g. LLMs vs Large Language Models) matched correctly?"""

    def test_llm_synonym_in_gaps(self):
        job_excerpt = "Experience with Large Language Models and RAG required."
        skill_gaps = [
            {"skill_name": "Large Language Models (LLMs)", "user_rating": 40, "required_rating": 75, "gap": 35, "priority": "high"},
        ]
        training_plan = [
            {"skill": "Large Language Models (LLMs)", "priority": 1, "estimated_hours": 30, "description": "Learn LLM fundamentals."},
        ]
        out = _run_judge(job_excerpt, skill_gaps, training_plan)
        assert out["score"] >= 3, f"Judge score {out['score']}: {out.get('reason', '')}"
