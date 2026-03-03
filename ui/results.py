"""Main results panel: match score, skill comparison chart, and training plan."""

from __future__ import annotations

import plotly.graph_objects as go
import streamlit as st

from models.state import GraphState, SkillGap, TrainingStep


def _priority_emoji(priority: str) -> str:
    return {
        "critical": "\U0001f534",  # red circle
        "high": "\U0001f7e0",      # orange circle
        "medium": "\U0001f7e1",    # yellow circle
        "low": "\U0001f7e2",       # green circle
    }.get(priority, "\u26aa")


def render_match_score(state: GraphState) -> None:
    match_pct = state.get("match_percentage", 0)
    col1, col2, col3 = st.columns(3)
    col1.metric("Match Score", f"{match_pct:.0f}%")
    col2.metric("Job Title", state.get("job_title", "N/A"))
    col3.metric("Domain", state.get("software_domain", "N/A"))


def render_skill_chart(state: GraphState) -> None:
    """Horizontal bar chart comparing user skills vs required skills."""
    required = state.get("required_skills", [])
    if not required:
        return

    user_map = {s.name.lower(): s.rating for s in state.get("user_skills", [])}

    skill_names = [s.name for s in required]
    req_ratings = [s.rating for s in required]
    user_ratings = [user_map.get(s.name.lower(), 0) for s in required]

    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            y=skill_names,
            x=req_ratings,
            name="Required",
            orientation="h",
            marker_color="#ef4444",
            opacity=0.7,
        )
    )
    fig.add_trace(
        go.Bar(
            y=skill_names,
            x=user_ratings,
            name="Your Level",
            orientation="h",
            marker_color="#3b82f6",
            opacity=0.7,
        )
    )
    fig.update_layout(
        barmode="overlay",
        title="Skill Comparison",
        xaxis_title="Rating (1–100)",
        yaxis=dict(autorange="reversed"),
        height=max(350, len(skill_names) * 32),
        margin=dict(l=10, r=10, t=40, b=30),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )
    st.plotly_chart(fig, use_container_width=True)


def render_skill_gaps(gaps: list[SkillGap]) -> None:
    if not gaps:
        st.success("No skill gaps detected — you're a strong match!")
        return

    st.subheader("Skill Gaps")
    for g in gaps:
        emoji = _priority_emoji(g.priority)
        st.markdown(
            f"{emoji} **{g.skill_name}** — gap of {g.gap} "
            f"(you: {g.user_rating}, needed: {g.required_rating}, "
            f"priority: {g.priority})"
        )


def render_training_plan(plan: list[TrainingStep]) -> None:
    if not plan:
        return

    st.subheader("Training Plan")
    for step in plan:
        with st.expander(
            f"**{step.priority}. {step.skill}** — ~{step.estimated_hours}h"
        ):
            st.write(step.description)
            if step.resources:
                st.markdown("**Recommended resources:**")
                for r in step.resources:
                    st.markdown(f"- [{r.title}]({r.url}) _({r.source})_")
