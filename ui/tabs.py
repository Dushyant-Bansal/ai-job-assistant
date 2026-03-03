"""Tabbed display for learning resources grouped by type."""

from __future__ import annotations

import streamlit as st

from models.state import GraphState, LearningResource


def _render_resource_list(resources: list[LearningResource]) -> None:
    if not resources:
        st.info("No resources found for this category.")
        return
    for r in resources:
        st.markdown(f"**[{r.title}]({r.url})**")
        if r.description:
            st.caption(r.description)


def render_resource_tabs(state: GraphState) -> None:
    st.subheader("Learning Resources")

    tab_labels = [
        "Web Articles",
        "News",
        "YouTube Videos",
        "Amazon Books",
        "Training Courses",
    ]
    tabs = st.tabs(tab_labels)

    with tabs[0]:
        _render_resource_list(state.get("web_articles", []))

    with tabs[1]:
        _render_resource_list(state.get("news_articles", []))

    with tabs[2]:
        videos = state.get("youtube_videos", [])
        if not videos:
            st.info("No videos found.")
        else:
            for v in videos:
                col1, col2 = st.columns([1, 3])
                with col1:
                    video_id = v.url.split("v=")[-1] if "v=" in v.url else ""
                    if video_id:
                        st.image(
                            f"https://img.youtube.com/vi/{video_id}/mqdefault.jpg",
                            use_container_width=True,
                        )
                with col2:
                    st.markdown(f"**[{v.title}]({v.url})**")
                    if v.description:
                        st.caption(v.description)

    with tabs[3]:
        _render_resource_list(state.get("amazon_books", []))

    with tabs[4]:
        courses = state.get("training_courses", [])
        if not courses:
            st.info("No courses found.")
        else:
            platforms = sorted({c.source for c in courses})
            for platform in platforms:
                st.markdown(f"#### {platform.title()}")
                for c in courses:
                    if c.source == platform:
                        st.markdown(f"- [{c.title}]({c.url})")
                        if c.description:
                            st.caption(c.description)
