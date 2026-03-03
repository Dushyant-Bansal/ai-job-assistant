"""Agent that computes the match percentage between user skills and required skills."""

from __future__ import annotations

from models.state import GraphState, SkillGap


class SkillMatcherAgent:
    """Deterministic agent — no LLM call needed.

    Compares the user's skill ratings against the job's required ratings
    and computes a weighted match percentage.
    """

    def run(self, state: GraphState) -> dict:
        user_map: dict[str, int] = {
            s.name.lower(): s.rating for s in state["user_skills"]
        }

        gaps: list[SkillGap] = []
        weighted_match = 0.0
        total_weight = 0.0

        for req in state["required_skills"]:
            req_rating = req.rating
            user_rating = user_map.get(req.name.lower(), 0)
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
                        skill_name=req.name,
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
