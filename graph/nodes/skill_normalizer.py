"""Agent that uses an LLM to normalize skill names and group synonyms."""

from __future__ import annotations

import json
from typing import Any

from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from config.settings import LLM_MODEL, LLM_TEMPERATURE, normalize_skill_name
from models.state import GraphState


def _skill_name(s: Any) -> str:
    return s.name if hasattr(s, "name") else s.get("name", "")


SYSTEM_PROMPT = """\
You are an expert at normalizing technical skill names for software engineering.

Given a list of skill names extracted from a resume and a job description, produce
a mapping where each skill name maps to its canonical form. Group synonyms together:
- "LLM", "LLMs", "Large Language Models (LLMs)", "Large Language Models" → same canonical
- "Python", "Python 3", "Python3" → same canonical
- "React", "React.js", "ReactJS" → same canonical
- "K8s", "Kubernetes" → same canonical
- "RAG", "Retrieval-Augmented Generation" → same canonical
- "Agentic AI", "AI Agentic Development" → same canonical

Use the most widely recognized, concise name as the canonical form (e.g. "LLMs" not
"Large Language Models (LLMs)", "Python" not "Python 3").

Return a JSON object: {{"original_skill_name": "canonical_name", ...}}
Include every skill in the input list. If a skill has no synonyms, map it to itself.
"""

USER_PROMPT = """\
Skill names from resume and job description:
{skill_names}

Return the mapping as JSON only, no markdown.
"""


class SkillNormalizerAgent:
    """LLM-backed agent that normalizes skill names and groups synonyms.

    Uses manual JSON parsing (not Pydantic structured output) because OpenAI
    structured output requires additionalProperties: false and does not support
    dynamic dict keys.
    """

    def __init__(self) -> None:
        self._llm = ChatOpenAI(
            model=LLM_MODEL,
            temperature=LLM_TEMPERATURE,
        )
        self._prompt = ChatPromptTemplate.from_messages(
            [("system", SYSTEM_PROMPT), ("human", USER_PROMPT)]
        )

    def run(self, state: GraphState) -> dict:
        user_skills = state.get("user_skills", [])
        required_skills = state.get("required_skills", [])
        all_names = list(
            {_skill_name(s) for s in user_skills + required_skills if _skill_name(s)}
        )
        if not all_names:
            return {"skill_canonical_map": {}}

        chain = self._prompt | self._llm
        result = chain.invoke({"skill_names": "\n".join(f"- {n}" for n in all_names)})
        raw = result.content if hasattr(result, "content") else str(result)
        raw = raw.strip()
        if raw.startswith("```"):
            raw = raw.split("\n", 1)[1] if "\n" in raw else raw[3:]
        if raw.endswith("```"):
            raw = raw.rsplit("```", 1)[0]
        raw = raw.strip()

        try:
            mapping = json.loads(raw)
        except json.JSONDecodeError:
            mapping = {n: n for n in all_names}

        mapping = {str(k).strip(): str(v).strip() for k, v in mapping.items()}
        for name in all_names:
            key = name.strip()
            if not key:
                continue
            if key not in mapping:
                mapping[key] = key
            if name != key:
                mapping[name] = mapping[key]

        # Normalize all canonical values through config (e.g. "Large Language Models (LLMs)" -> "LLMs")
        # so LLM output aligns with SKILL_SYNONYMS and resume/JD variants match.
        mapping = {k: normalize_skill_name(v) for k, v in mapping.items()}

        return {"skill_canonical_map": mapping}
