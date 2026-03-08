"""Agent that computes the match percentage between user skills and required skills."""

from __future__ import annotations

from typing import Any

from config.settings import is_programming_language, normalize_skill_name
from models.state import GraphState, Skill, SkillGap


def _skill_rating(s: Skill | dict[str, Any]) -> int:
    return s.rating if hasattr(s, "rating") else s.get("rating", 0)


def _skill_name(s: Skill | dict[str, Any]) -> str:
    return s.name if hasattr(s, "name") else s.get("name", "")


def _skill_canonical(name: str, canonical_map: dict[str, str] | None) -> str:
    """Return canonical skill name from LLM map or config fallback."""
    if canonical_map is None:
        return normalize_skill_name(name)
    n = name.strip()
    if n in canonical_map:
        return canonical_map[n]
    name_lower = n.lower()
    for k, v in canonical_map.items():
        if k.strip().lower() == name_lower:
            return v
    return normalize_skill_name(name)


class SkillMatcherAgent:
    """Compares the user's skill ratings against the job's required ratings.

    Uses LLM-generated skill_canonical_map when available for synonym matching,
    otherwise falls back to config-based normalize_skill_name.
    """

    def run(self, state: GraphState) -> dict:
        required_skills = list(state["required_skills"])
        if state.get("ignore_programming_languages"):
            required_skills = [
                s for s in required_skills
                if not is_programming_language(_skill_name(s))
            ]

        canonical_map = state.get("skill_canonical_map")

        user_map: dict[str, int] = {}
        for s in state["user_skills"]:
            name = _skill_name(s)
            canonical = _skill_canonical(name, canonical_map)
            rating = _skill_rating(s)
            key = canonical.lower()
            user_map[key] = max(user_map.get(key, 0), rating)

        gaps: list[SkillGap] = []
        weighted_match = 0.0
        total_weight = 0.0

        req_by_canonical: dict[str, tuple[str, int]] = {}
        for req in required_skills:
            req_rating = _skill_rating(req)
            req_name = _skill_name(req)
            req_canonical = _skill_canonical(req_name, canonical_map)
            key = req_canonical.lower()
            if key not in req_by_canonical or req_rating > req_by_canonical[key][1]:
                req_by_canonical[key] = (req_name, req_rating)

        for req_canonical_lower, (req_name, req_rating) in req_by_canonical.items():
            user_rating = user_map.get(req_canonical_lower, 0)
            total_weight += req_rating
            weighted_match += min(user_rating, req_rating)

            if user_rating < req_rating:
                gap = req_rating - user_rating
                if gap > 60:
                    priority = "critical"
                elif gap > 40:
                    priority = "high"
                elif gap > 20:
                    priority = "medium"
                else:
                    priority = "low"
                gaps.append(
                    SkillGap(
                        skill_name=req_name,
                        user_rating=user_rating,
                        required_rating=req_rating,
                        gap=gap,
                        priority=priority,
                    )
                )

        match_pct = (weighted_match / total_weight * 100) if total_weight else 0.0
        gaps.sort(key=lambda g: g.gap, reverse=True)

        out: dict = {
            "match_percentage": round(match_pct, 1),
            "skill_gaps": gaps,
        }
        if state.get("ignore_programming_languages"):
            out["required_skills"] = required_skills
        return out
