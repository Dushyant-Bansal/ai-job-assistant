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
    req_skills_list = [_to_skill(s) for s in required_skills] if required_skills else []
    for i, skill in enumerate(req_skills_list):
        key = f"include_req_{i}_{skill.name}"
        if st.session_state.get(key) is False:
            st.session_state["override_keep_expanded"] = True
            break
    expanded = st.session_state.get("override_keep_expanded", False)
    with st.expander("Override & Re-analyze", expanded=expanded):
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

        # Add new skills (in case LLM missed them)
        st.subheader("Add skill (if missed)")
        st.caption("Add a skill the resume analysis may have missed.")
        if "override_added_skills" not in st.session_state:
            st.session_state["override_added_skills"] = []
        added_skills: list[Skill] = st.session_state["override_added_skills"]

        add_col1, add_col2, add_col3 = st.columns([2, 1, 1])
        with add_col1:
            new_skill_name = st.text_input(
                "Skill name",
                placeholder="e.g. Kubernetes",
                key="add_skill_name",
            )
        with add_col2:
            new_skill_rating = st.number_input(
                "Rating",
                min_value=1,
                max_value=100,
                value=50,
                key="add_skill_rating",
            )
        with add_col3:
            add_clicked = st.button("Add", key="add_skill_btn")

        if add_clicked and new_skill_name and new_skill_name.strip():
            name = new_skill_name.strip()
            existing_names = {s.name for s in user_skills_list} | {s.name for s in added_skills}
            if name not in existing_names:
                added_skills.append(
                    Skill(
                        name=name,
                        category="technical",
                        rating=new_skill_rating,
                        years_experience=None,
                        depth_signal="",
                    )
                )
                st.session_state["override_added_skills"] = added_skills
                st.session_state["override_keep_expanded"] = True
                st.rerun()
            else:
                st.warning(f"Skill '{name}' already exists.")

        if added_skills:
            st.caption("Added skills (included in re-analysis):")
            for i, skill in enumerate(added_skills):
                col1, col2 = st.columns([4, 1])
                with col1:
                    st.markdown(f"- **{skill.name}** ({skill.rating})")
                with col2:
                    if st.button("Remove", key=f"remove_added_{i}_{skill.name}"):
                        added_skills.pop(i)
                        st.session_state["override_added_skills"] = added_skills
                        st.rerun()

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
    # Merge in user-added skills
    overridden_user.extend(added_skills)
    # Clear added skills after re-analyze (they're now in user_skills)
    if "override_added_skills" in st.session_state:
        del st.session_state["override_added_skills"]

    overridden_required = effective_required

    return (overridden_user, overridden_required, new_domain), effective_required
