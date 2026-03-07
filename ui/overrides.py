"""Override UI: editable skill ratings and domain for re-analysis."""

from __future__ import annotations

from typing import Any

import streamlit as st

from config.settings import SOFTWARE_DOMAINS
from models.state import Skill


def _to_skill(item: Skill | dict[str, Any]) -> Skill:
    """Normalise dict or Skill to Skill."""
    if isinstance(item, Skill):
        return item
    return Skill(**item)


def render_override_section(
    user_skills: list[Skill] | list[dict[str, Any]],
    current_domain: str,
) -> tuple[list[Skill], str] | None:
    """Render the override controls and return (overridden_skills, domain) if re-analyze clicked.

    Returns None if the user has not clicked Re-analyze.
    """
    with st.expander("Override & Re-analyze", expanded=False):
        st.caption(
            "Adjust your skill ratings or the job domain, then re-run the analysis "
            "to see updated match scores and training recommendations."
        )

        overrides: dict[str, int] = {}
        skills = [_to_skill(s) for s in user_skills] if user_skills else []

        if skills:
            st.subheader("Skill rating overrides")
            st.caption("Change any rating (1–100) to reflect your actual proficiency.")
            cols = st.columns(3)
        for i, skill in enumerate(skills):
            with cols[i % 3]:
                val = st.number_input(
                    f"{skill.name}",
                    min_value=1,
                    max_value=100,
                    value=skill.rating,
                    key=f"override_skill_{i}_{skill.name}",
                )
                overrides[skill.name] = val

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

    if not reanalyze_clicked:
        return None

    skills = [_to_skill(s) for s in user_skills]
    overridden_skills = [
        Skill(
            name=s.name,
            category=s.category,
            rating=overrides.get(s.name, s.rating),
            years_experience=s.years_experience,
            depth_signal=s.depth_signal,
        )
        for s in skills
    ]
    return overridden_skills, new_domain
