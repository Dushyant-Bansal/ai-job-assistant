"""Tests for export utilities."""

from __future__ import annotations

import json
import pytest

from models.state import LearningResource, SkillGap, TrainingStep
from utils.export import build_export_json


class TestBuildExportJson:
    def test_produces_valid_json(self, sample_analysis_result):
        output = build_export_json(sample_analysis_result)
        data = json.loads(output)
        assert isinstance(data, dict)

    def test_includes_all_required_keys(self, sample_analysis_result):
        output = build_export_json(sample_analysis_result)
        data = json.loads(output)
        assert "job_description" in data
        assert "match_score" in data
        assert "job_title" in data
        assert "domain" in data
        assert "skill_gaps" in data
        assert "training_plan" in data
        assert "learning_resources" in data

    def test_learning_resources_structure(self, sample_analysis_result):
        output = build_export_json(sample_analysis_result)
        data = json.loads(output)
        resources = data["learning_resources"]
        assert "web_articles" in resources
        assert "news_articles" in resources
        assert "blog_posts" in resources
        assert "youtube_videos" in resources
        assert "amazon_books" in resources
        assert "training_courses" in resources

    def test_handles_empty_result(self):
        output = build_export_json({})
        data = json.loads(output)
        assert data["job_description"] == ""
        assert data["match_score"] == 0
        assert data["skill_gaps"] == []
        assert data["training_plan"] == []
