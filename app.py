"""AI Job Training Assistant — Streamlit entry point."""

from __future__ import annotations

import streamlit as st

from graph.builder import build_graph, build_recompute_graph
from parsers.file_parser import parse_resume
from ui.overrides import render_override_section
from ui.results import (
    render_match_score,
    render_skill_chart,
    render_skill_gaps,
    render_training_plan,
)
from ui.sidebar import render_sidebar
from ui.tabs import render_resource_tabs

# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="AI Job Training Assistant",
    page_icon="\U0001f3af",
    layout="wide",
)

st.title("\U0001f3af AI Job Training Assistant")
st.markdown(
    "Upload your resume and paste a software engineering job description to "
    "discover your skill gaps and get a personalised training plan."
)

# ---------------------------------------------------------------------------
# Sidebar inputs
# ---------------------------------------------------------------------------
uploaded_file, job_description, analyze_clicked = render_sidebar()

# ---------------------------------------------------------------------------
# Run the analysis pipeline (full or recompute with overrides)
# ---------------------------------------------------------------------------
result = None

if analyze_clicked:
    try:
        resume_bytes = uploaded_file.read()
        resume_text = parse_resume(uploaded_file.name, resume_bytes)
    except Exception as exc:
        st.error(f"Failed to parse resume: {exc}")
        st.stop()

    if not resume_text.strip():
        st.warning("The uploaded resume appears to be empty. Please try another file.")
        st.stop()

    graph = build_graph()
    status_container = st.status("Analyzing …", expanded=True)

    with status_container:
        final_state = {}
        for event in graph.stream(
            {"resume_text": resume_text, "job_description": job_description},
            stream_mode="updates",
        ):
            node_name = list(event.keys())[0]
            readable = node_name.replace("_", " ").title()
            st.write(f"Running: **{readable}** …")
            node_output = event[node_name]
            if node_output:
                final_state.update(node_output)

    status_container.update(label="Analysis complete", state="complete")

    if final_state.get("error_message"):
        st.error(final_state["error_message"])
        st.stop()

    result = final_state
    st.session_state["analysis_result"] = result

elif "analysis_result" in st.session_state:
    result = st.session_state["analysis_result"]

if result is None:
    st.info("Upload a resume and paste a job description to get started.")
    st.stop()

# ---------------------------------------------------------------------------
# Results
# ---------------------------------------------------------------------------
st.divider()
render_match_score(result)
st.divider()
render_skill_chart(result)
st.divider()
render_skill_gaps(result.get("skill_gaps", []))
st.divider()
render_training_plan(result.get("training_plan", []))
st.divider()
render_resource_tabs(result)

# ---------------------------------------------------------------------------
# Override & Re-analyze
# ---------------------------------------------------------------------------
user_skills = result.get("user_skills", [])
current_domain = result.get("software_domain", "")
override_result = render_override_section(user_skills, current_domain)

if override_result:
    overridden_skills, new_domain = override_result

    exclude_keys = {
        "match_percentage",
        "skill_gaps",
        "web_articles",
        "news_articles",
        "youtube_videos",
        "amazon_books",
        "training_courses",
        "blog_posts",
        "training_plan",
    }
    initial_state = {
        k: v for k, v in result.items()
        if k not in exclude_keys and v is not None
    }
    initial_state["user_skills"] = overridden_skills
    initial_state["software_domain"] = new_domain

    with st.status("Re-analyzing with overrides …", expanded=True) as status:
        recompute_graph = build_recompute_graph()
        new_state = {}
        for event in recompute_graph.stream(initial_state, stream_mode="updates"):
            node_name = list(event.keys())[0]
            readable = node_name.replace("_", " ").title()
            st.write(f"Running: **{readable}** …")
            node_output = event[node_name]
            if node_output:
                new_state.update(node_output)

    result = {**result, **new_state}
    st.session_state["analysis_result"] = result
    st.rerun()
