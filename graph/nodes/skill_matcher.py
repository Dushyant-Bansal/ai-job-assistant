"""Agent that computes the match percentage between user skills and required skills."""

from __future__ import annotations

from typing import Any

from models.state import GraphState, Skill, SkillGap


def _skill_rating(s: Skill | dict[str, Any]) -> int:
    return s.rating if hasattr(s, "rating") else s.get("rating", 0)


def _skill_name(s: Skill | dict[str, Any]) -> str:
    return s.name if hasattr(s, "name") else s.get("name", "")


class SkillMatcherAgent:
    """Deterministic agent — no LLM call needed.

    Compares the user's skill ratings against the job's required ratings
    and computes a weighted match percentage.
    """

    def run(self, state: GraphState) -> dict:
        user_map: dict[str, int] = {
            _skill_name(s).lower(): _skill_rating(s)
            for s in state["user_skills"]
        }

        gaps: list[SkillGap] = []
        weighted_match = 0.0
        total_weight = 0.0

        for req in state["required_skills"]:
            req_rating = _skill_rating(req)
            req_name = _skill_name(req)
            user_rating = user_map.get(req_name.lower(), 0)
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

        return {
            "match_percentage": round(match_pct, 1),
            "skill_gaps": gaps,
        }
