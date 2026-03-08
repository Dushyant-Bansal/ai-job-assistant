"""Agent that analyses a job description for required skills, industry, and domain."""

from __future__ import annotations

from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from config.settings import (
    CANONICAL_SKILLS,
    LLM_MODEL,
    LLM_TEMPERATURE,
    SOFTWARE_DOMAINS,
)
from models.state import GraphState, JDAnalysis

SYSTEM_PROMPT = """\
You are an expert technical recruiter who analyses job descriptions.

Given a job description, extract:

1. **job_title** – The role title.
2. **experience_years** – Desired years of experience (null if not stated).
3. **industry** – The primary industry (e.g. "software engineering",
   "finance", "healthcare").
4. **is_software_job** – true if this is a software engineering role, false
   otherwise.
5. **software_domain** – Classify into exactly ONE of these domains:
   {software_domains}
   Choose "Other" only if none fit.
6. **required_skills** – List of skills with:
   - **name** – Normalised (prefer canonical list below).
   - **category** – "technical" or "soft".
   - **rating** (1-100) based on language intensity:
     "familiar with" / "nice to have" ≈ 30-50,
     "experience with" ≈ 50-70,
     "strong experience" / "proficient" ≈ 70-85,
     "expert" / "deep expertise" / "mastery" ≈ 85-100.
     Also factor in the seniority of the job title and years of experience
     requested to adjust ratings upward for senior roles.
   - **years_experience** – If explicitly stated for that skill.
   - **depth_signal** – Verbatim JD text justifying the rating.

Canonical skill list (prefer these names):
{canonical_skills}
"""

USER_PROMPT = """\
Job description:
{job_description}
"""


class JDAnalyzerAgent:
    """LLM-backed agent that analyses a job description."""

    def __init__(self) -> None:
        self._llm = ChatOpenAI(
            model=LLM_MODEL,
            temperature=LLM_TEMPERATURE,
        ).with_structured_output(JDAnalysis)
        self._prompt = ChatPromptTemplate.from_messages(
            [("system", SYSTEM_PROMPT), ("human", USER_PROMPT)]
        )

    def run(self, state: GraphState) -> dict:
        chain = self._prompt | self._llm
        result: JDAnalysis = chain.invoke(
            {
                "job_description": state["job_description"],
                "canonical_skills": ", ".join(CANONICAL_SKILLS),
                "software_domains": ", ".join(SOFTWARE_DOMAINS),
            }
        )
        skills = result.required_skills
        return {
            "job_title": result.job_title,
            "experience_years": result.experience_years,
            "industry": result.industry,
            "is_software_job": result.is_software_job,
            "software_domain": result.software_domain,
            "required_skills": skills,
            "required_skills_for_resources": skills,
        }
