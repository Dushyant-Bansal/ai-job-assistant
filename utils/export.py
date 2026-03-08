"""Export utilities for analysis results."""

from __future__ import annotations

import json


def _to_dict(obj):
    """Convert Pydantic model or dict to JSON-serializable dict."""
    if hasattr(obj, "model_dump"):
        return obj.model_dump()
    if isinstance(obj, dict):
        return {k: _to_dict(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_to_dict(v) for v in obj]
    return obj


def build_export_json(result: dict) -> str:
    """Build structured JSON for export."""
    export = {
        "job_description": result.get("job_description", ""),
        "match_score": result.get("match_percentage", 0),
        "job_title": result.get("job_title", ""),
        "domain": result.get("software_domain", ""),
        "skill_gaps": _to_dict(result.get("skill_gaps", [])),
        "training_plan": _to_dict(result.get("training_plan", [])),
        "learning_resources": {
            "web_articles": _to_dict(result.get("web_articles", [])),
            "news_articles": _to_dict(result.get("news_articles", [])),
            "blog_posts": _to_dict(result.get("blog_posts", [])),
            "youtube_videos": _to_dict(result.get("youtube_videos", [])),
            "amazon_books": _to_dict(result.get("amazon_books", [])),
            "training_courses": _to_dict(result.get("training_courses", [])),
        },
    }
    return json.dumps(export, indent=2)
