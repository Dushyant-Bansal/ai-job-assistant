"""Override UI: editable skill ratings and domain for re-analysis."""

from __future__ import annotations

from typing import Any

import streamlit as st

from config.settings import SOFTWARE_DOMAINS
from models.state import Skill


def _to_skill(item: Skill | dict[str, Any] | Any) -> Skill:
    """Normalise dict, Skill, or object-like to Skill."""
    if isinstance(item, Skill):
        return item
    if isinstance(item, dict):
        return Skill(**item)
    # Object with attributes (e.g. Skill from different import/session)
    return Skill(
        name=getattr(item, "name", ""),
        category=getattr(item, "category", "technical"),
        rating=getattr(item, "rating", 50),
        years_experience=getattr(item, "years_experience", None),
        depth_signal=getattr(item, "depth_signal", ""),
    )


def render_override_section(
    user_skills: list[Skill] | list[dict[str, Any]],
    required_skills: list[Skill] | list[dict[str, Any]],
    current_domain: str,
) -> tuple[tuple[list[Skill], list[Skill], str] | None, list[Skill]]:
    """Render the override controls.

    Returns (override_result, effective_required_skills).
    - override_result: (user_skills, required_skills, domain) if Re-analyze clicked, else None.
    - effective_required_skills: required skills currently included (for chart display).
    """
    with st.expander("Override & Re-analyze", expanded=True):
        st.caption(
            "Adjust your skill ratings, the job's required skills, or remove skills that "
            "don't seem necessary. Then re-run the analysis."
        )

        user_overrides: dict[str, int] = {}
        user_skills_list = [_to_skill(s) for s in user_skills] if user_skills else []

        if user_skills_list:
            st.subheader("Your skills (from resume)")
            st.caption("Change any rating (1–100) to reflect your actual proficiency.")
            cols = st.columns(3)
            for i, skill in enumerate(user_skills_list):
                with cols[i % 3]:
                    val = st.number_input(
                        f"{skill.name}",
                        min_value=1,
                        max_value=100,
                        value=skill.rating,
                        key=f"override_user_{i}_{skill.name}",
                    )
                    user_overrides[skill.name] = val

        req_skills_list = [_to_skill(s) for s in required_skills] if required_skills else []
        req_overrides: dict[str, int] = {}
        req_included: dict[str, bool] = {}

        if req_skills_list:
            st.subheader("Job required skills")
            st.caption(
                "Adjust required ratings or uncheck skills to exclude from analysis."
            )
            for i, skill in enumerate(req_skills_list):
                col1, col2, col3 = st.columns([2, 1, 2])
                with col1:
                    st.markdown(f"**{skill.name}**")
                with col2:
                    included = st.checkbox(
                        "Include",
                        value=True,
                        key=f"include_req_{i}_{skill.name}",
                    )
                    req_included[skill.name] = included
                with col3:
                    val = st.number_input(
                        "Rating (1–100)",
                        min_value=1,
                        max_value=100,
                        value=skill.rating,
                        key=f"override_req_{i}_{skill.name}",
                        disabled=not included,
                    )
                    req_overrides[skill.name] = val

        st.subheader("Job domain override")
        domain_idx = (
            SOFTWARE_DOMAINS.index(current_domain)
            if current_domain in SOFTWARE_DOMAINS
            else 0
        )
        new_domain = st.selectbox(
            "Software domain",
            options=SOFTWARE_DOMAINS,
            index=domain_idx,
            key="override_domain",
        )

        st.divider()
        reanalyze_clicked = st.button(
            "Re-analyze with overrides",
            type="primary",
            use_container_width=True,
            key="reanalyze_btn",
        )

    effective_required = [
        Skill(
            name=s.name,
            category=s.category,
            rating=req_overrides.get(s.name, s.rating),
            years_experience=s.years_experience,
            depth_signal=s.depth_signal,
        )
        for s in req_skills_list
        if req_included.get(s.name, True)
    ]

    if not reanalyze_clicked:
        return None, effective_required

    overridden_user = [
        Skill(
            name=s.name,
            category=s.category,
            rating=user_overrides.get(s.name, s.rating),
            years_experience=s.years_experience,
            depth_signal=s.depth_signal,
        )
        for s in user_skills_list
    ]

    overridden_required = effective_required

    return (overridden_user, overridden_required, new_domain), effective_required
