"""Tests for config/settings."""

from __future__ import annotations

import pytest

from config.settings import (
    normalize_skill_name,
    is_programming_language,
    missing_api_keys,
)


class TestNormalizeSkillName:
    def test_llm_variants_to_canonical(self):
        assert normalize_skill_name("Large Language Models (LLMs)") == "LLMs"
        assert normalize_skill_name("LLM") == "LLMs"

    def test_kubernetes_variants(self):
        assert normalize_skill_name("K8s") == "Kubernetes"
        assert normalize_skill_name("K8s/Kubernetes") == "Kubernetes"

    def test_unknown_skill_unchanged(self):
        assert normalize_skill_name("Some Random Skill") == "Some Random Skill"

    def test_case_insensitive(self):
        assert normalize_skill_name("python") == "Python"
        assert normalize_skill_name("PYTHON") == "Python"

    def test_empty_returns_empty(self):
        assert normalize_skill_name("") == ""
        assert normalize_skill_name("   ") == "   "


class TestIsProgrammingLanguage:
    def test_python_is_pl(self):
        assert is_programming_language("Python") is True
        assert is_programming_language("python") is True

    def test_kubernetes_not_pl(self):
        assert is_programming_language("Kubernetes") is False

    def test_llms_not_pl(self):
        assert is_programming_language("LLMs") is False


class TestMissingApiKeys:
    def test_returns_list(self):
        result = missing_api_keys()
        assert isinstance(result, list)
