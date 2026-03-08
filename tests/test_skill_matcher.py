"""Tests for skill matcher agent."""

from __future__ import annotations

import pytest

from graph.nodes.skill_matcher import SkillMatcherAgent
from models.state import Skill


class TestSkillMatcherAgent:
    def test_perfect_match_no_gaps(self):
        agent = SkillMatcherAgent()
        state = {
            "user_skills": [Skill(name="Python", category="technical", rating=80)],
            "required_skills": [Skill(name="Python", category="technical", rating=80)],
        }
        out = agent.run(state)
        assert out["match_percentage"] == 100.0
        assert out["skill_gaps"] == []

    def test_gap_detected(self):
        agent = SkillMatcherAgent()
        state = {
            "user_skills": [Skill(name="Python", category="technical", rating=40)],
            "required_skills": [Skill(name="Python", category="technical", rating=80)],
        }
        out = agent.run(state)
        assert out["match_percentage"] < 100
        assert len(out["skill_gaps"]) == 1
        assert out["skill_gaps"][0].skill_name == "Python"
        assert out["skill_gaps"][0].gap == 40

    def test_synonym_match_with_canonical_map(self):
        """LLMs and Large Language Models (LLMs) should match via canonical map."""
        agent = SkillMatcherAgent()
        state = {
            "user_skills": [Skill(name="LLMs", category="technical", rating=70)],
            "required_skills": [Skill(name="Large Language Models (LLMs)", category="technical", rating=75)],
            "skill_canonical_map": {"LLMs": "LLMs", "Large Language Models (LLMs)": "LLMs"},
        }
        out = agent.run(state)
        # User has 70, required 75 -> small gap
        assert len(out["skill_gaps"]) == 1
        assert out["skill_gaps"][0].skill_name == "Large Language Models (LLMs)"
        assert out["skill_gaps"][0].gap == 5
