"""Tests for resource finder _top_gap_skill_names logic."""

from __future__ import annotations

import pytest

from graph.nodes.resource_finder import _top_gap_skill_names
from models.state import SkillGap


def _make_state(**kwargs):
    return kwargs


class TestTopGapSkillNames:
    def test_uses_skill_gaps_first(self):
        state = _make_state(
            skill_gaps=[
                SkillGap(skill_name="Kubernetes", user_rating=0, required_rating=70, gap=70, priority="critical"),
                SkillGap(skill_name="Python", user_rating=50, required_rating=80, gap=30, priority="medium"),
            ],
        )
        names = _top_gap_skill_names(state)
        assert "Kubernetes" in names
        assert "Python" in names

    def test_falls_back_to_required_skills_when_no_gaps(self):
        state = _make_state(
            skill_gaps=[],
            required_skills=[
                {"name": "Python"},
                {"name": "AWS"},
            ],
        )
        names = _top_gap_skill_names(state)
        assert "Python" in names
        assert "AWS" in names

    def test_falls_back_to_required_skills_for_resources(self):
        state = _make_state(
            skill_gaps=[],
            required_skills=[],
            required_skills_for_resources=[{"name": "Kubernetes"}, {"name": "Docker"}],
        )
        names = _top_gap_skill_names(state)
        assert "Kubernetes" in names
        assert "Docker" in names

    def test_falls_back_to_domain(self):
        state = _make_state(
            skill_gaps=[],
            required_skills=[],
            required_skills_for_resources=[],
            software_domain="Machine Learning",
        )
        names = _top_gap_skill_names(state)
        assert names == ["Machine Learning"]

    def test_falls_back_to_generic(self):
        state = _make_state(
            skill_gaps=[],
            required_skills=[],
            required_skills_for_resources=[],
            software_domain="",
        )
        names = _top_gap_skill_names(state)
        assert names == ["software engineering"]
