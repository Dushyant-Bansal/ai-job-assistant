"""Sidebar UI: resume upload and job-description input."""

from __future__ import annotations

import streamlit as st

from config.settings import API_KEYS, missing_api_keys


def render_sidebar() -> tuple:
    """Render the sidebar and return (uploaded_file, job_description, analyze_clicked)."""
    with st.sidebar:
        missing = missing_api_keys()
        if missing:
            st.warning(
                "**Missing API keys:** "
                + ", ".join(missing)
                + ". Add them to `.env` to enable all features. "
                "See README for setup."
            )

        st.header("Inputs")

        st.subheader("1. Upload your resume")
        uploaded_file = st.file_uploader(
            "Supported formats: PDF, DOCX, TXT",
            type=["pdf", "docx", "txt"],
            help="Upload your resume so we can extract your skills.",
        )

        st.subheader("2. Paste the job description")
        job_description = st.text_area(
            "Job description",
            height=300,
            placeholder="Paste the full job description here …",
        )

        st.subheader("3. Options")
        ignore_programming_languages = st.checkbox(
            "Ignore programming language requirements",
            value=False,
            help="Exclude programming languages (Python, Java, etc.) from the job's required skills when comparing.",
        )

        st.divider()
        analyze_clicked = st.button(
            "Analyze",
            type="primary",
            use_container_width=True,
            disabled=not (uploaded_file and job_description),
        )

    return uploaded_file, job_description, analyze_clicked, ignore_programming_languages
