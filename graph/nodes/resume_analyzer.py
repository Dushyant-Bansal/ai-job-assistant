"""Agent that parses the resume text and extracts rated skills."""

from __future__ import annotations

from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from config.settings import CANONICAL_SKILLS, LLM_MODEL, LLM_TEMPERATURE
from models.state import GraphState, ResumeAnalysis

SYSTEM_PROMPT = """\
You are an expert technical recruiter and resume analyst.

Given a candidate's resume, extract every identifiable skill — both technical
and soft.  For each skill:

1. **name** – Normalise to one of the canonical names below when possible.
   If the skill does not appear in the list, use its most widely-recognised
   name.
2. **category** – "technical" or "soft".
3. **rating** (1-100) – Estimate proficiency based on:
   - years of experience mentioned or inferable
   - depth signals (mentioned in passing ≈ 20-40, used professionally ≈ 40-60,
     led projects / deep expertise ≈ 60-80, published / industry-recognised
     expert ≈ 80-100)
4. **years_experience** – Approximate years if inferable, else null.
5. **depth_signal** – Verbatim snippet from the resume that supports the rating.

Canonical skill list (prefer these names):
{canonical_skills}

Be thorough — extract all skills you can find, including those implied by
project descriptions or job titles.
"""

USER_PROMPT = """\
Resume text:
{resume_text}
"""


class ResumeAnalyzerAgent:
    """LLM-backed agent that extracts and rates skills from a resume."""

    def __init__(self) -> None:
        self._llm = ChatOpenAI(
            model=LLM_MODEL,
            temperature=LLM_TEMPERATURE,
        ).with_structured_output(ResumeAnalysis)
        self._prompt = ChatPromptTemplate.from_messages(
            [("system", SYSTEM_PROMPT), ("human", USER_PROMPT)]
        )

    def run(self, state: GraphState) -> dict:
        chain = self._prompt | self._llm
        result: ResumeAnalysis = chain.invoke(
            {
                "resume_text": state["resume_text"],
                "canonical_skills": ", ".join(CANONICAL_SKILLS),
            }
        )
        return {"user_skills": result.skills}
