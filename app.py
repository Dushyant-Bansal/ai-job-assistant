"""AI Job Training Assistant — Streamlit entry point."""

from __future__ import annotations

import logging
import streamlit as st

from config.settings import API_KEYS, missing_api_keys

logging.basicConfig(level=logging.INFO, format="%(name)s: %(message)s")
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
    "discover your skill gaps and get a personalized training plan."
)

missing_keys = missing_api_keys()
if missing_keys:
    with st.expander("⚠️ Missing API keys — some features disabled", expanded=True):
        for name in missing_keys:
            _, description = API_KEYS[name]
            st.markdown(f"- **{name}** — {description}")
        st.caption("Add keys to `.env` and restart. See README for setup.")

# ---------------------------------------------------------------------------
# Sidebar inputs
# ---------------------------------------------------------------------------
uploaded_file, job_description, analyze_clicked, ignore_programming_languages = render_sidebar()

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
            {
                "resume_text": resume_text,
                "job_description": job_description,
                "ignore_programming_languages": ignore_programming_languages,
            },
            stream_mode="updates",
        ):
            for node_name, node_output in event.items():
                readable = node_name.replace("_", " ").title()
                st.write(f"Running: **{readable}** …")
                if node_output:
                    final_state.update(node_output)

    status_container.update(label="Analysis complete", state="complete")

    if final_state.get("error_message"):
        st.error(final_state["error_message"])
        st.stop()

    result = final_state
    st.session_state["analysis_result"] = result
    if "override_keep_expanded" in st.session_state:
        del st.session_state["override_keep_expanded"]

elif "analysis_result" in st.session_state:
    result = st.session_state["analysis_result"]

if result is None:
    st.info("Upload a resume and paste a job description to get started.")
    st.stop()

# ---------------------------------------------------------------------------
# Override & Re-analyze — check first so we replace the page when clicked
# ---------------------------------------------------------------------------
user_skills = result.get("user_skills", [])
required_skills = result.get("required_skills", [])
current_domain = result.get("software_domain", "")
override_result, effective_required_skills = render_override_section(
    user_skills, required_skills, current_domain
)

if override_result:
    overridden_user_skills, overridden_required_skills, new_domain = override_result

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
        "resource_search_warnings",
    }
    initial_state = {
        k: v for k, v in result.items()
        if k not in exclude_keys and v is not None
    }
    initial_state["user_skills"] = overridden_user_skills
    initial_state["required_skills"] = overridden_required_skills
    initial_state["required_skills_for_resources"] = overridden_required_skills
    initial_state["software_domain"] = new_domain
    initial_state["ignore_programming_languages"] = ignore_programming_languages

    st.divider()
    with st.status("Re-analyzing with overrides …", expanded=True):
        recompute_graph = build_recompute_graph()
        new_state = {}
        for event in recompute_graph.stream(initial_state, stream_mode="updates"):
            for node_name, node_output in event.items():
                readable = node_name.replace("_", " ").title()
                st.write(f"Running: **{readable}** …")
                if node_output:
                    new_state.update(node_output)

    result = {**result, **new_state}
    st.session_state["analysis_result"] = result
    st.rerun()

# ---------------------------------------------------------------------------
# Results — only rendered when not re-analyzing (page replaced after rerun)
# ---------------------------------------------------------------------------
st.divider()
render_match_score(result)
st.divider()
render_skill_chart(result, required_skills_override=effective_required_skills)
st.divider()
render_skill_gaps(result.get("skill_gaps", []))
st.divider()
render_training_plan(result.get("training_plan", []))
st.divider()
warnings = result.get("resource_search_warnings", [])
if warnings:
    for w in warnings:
        st.warning(w)
st.divider()
render_resource_tabs(result)

with st.expander("Debug: resource counts & search inputs", expanded=False):
    def _skill_name(s):
        return s.name if hasattr(s, "name") else s.get("name", "")
    gaps = result.get("skill_gaps", [])
    req = result.get("required_skills", [])
    req_for_res = result.get("required_skills_for_resources", [])
    if gaps:
        skills_used = [g.skill_name if hasattr(g, "skill_name") else g.get("skill_name", "") for g in gaps[:5]]
    elif req:
        skills_used = [_skill_name(s) for s in req[:5]]
    elif req_for_res:
        skills_used = [_skill_name(s) for s in req_for_res[:5]]
    else:
        skills_used = []
    domain = result.get("software_domain", "")
    st.write("**skill_gaps:**", len(gaps), "| **required_skills:**", len(req), "| **required_skills_for_resources:**", len(req_for_res))
    st.write("**Skills sent to search:**", skills_used if skills_used else "_none (fallback: domain or 'software engineering')_")
    if skills_used:
        sample_query = f"{skills_used[0]} tutorial guide software engineering"
        if domain:
            sample_query += f" {domain}"
        st.write("**Sample web query:**", f"`{sample_query}`")
    st.write("---")
    resource_keys = [
        "web_articles",
        "news_articles",
        "blog_posts",
        "youtube_videos",
        "amazon_books",
        "training_courses",
    ]
    for key in resource_keys:
        val = result.get(key, [])
        count = len(val) if isinstance(val, list) else "?"
        st.write(f"**{key}**: {count} items")
    st.caption(
        "If counts are 0: check API keys (Tavily, YouTube) in .env, terminal for API errors, "
        "and that skill_gaps/required_skills are populated."
    )
