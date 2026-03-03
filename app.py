"""AI Job Training Assistant — Streamlit entry point."""

from __future__ import annotations

import streamlit as st

from graph.builder import build_graph
from parsers.file_parser import parse_resume
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
# Run the analysis pipeline
# ---------------------------------------------------------------------------
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

    progress = st.empty()
    status_container = st.status("Analysing …", expanded=True)

    with status_container:
        final_state = {}
        for event in graph.stream(
            {"resume_text": resume_text, "job_description": job_description},
            stream_mode="updates",
        ):
            node_name = list(event.keys())[0]
            readable = node_name.replace("_", " ").title()
            st.write(f"Running: **{readable}** …")
            final_state.update(event[node_name])

    status_container.update(label="Analysis complete", state="complete")

    # --- Handle non-software-job early exit ---
    if final_state.get("error_message"):
        st.error(final_state["error_message"])
        st.stop()

    # --- Results ---
    st.divider()
    render_match_score(final_state)
    st.divider()
    render_skill_chart(final_state)
    st.divider()
    render_skill_gaps(final_state.get("skill_gaps", []))
    st.divider()
    render_training_plan(final_state.get("training_plan", []))
    st.divider()
    render_resource_tabs(final_state)
