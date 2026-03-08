# AI Job Training Assistant

An AI-powered tool that analyzes your resume against a software engineering job description, identifies skill gaps, and generates a personalized training plan with curated learning resources.

---

## Problem Statement

- **Job seekers struggle** to identify skill gaps between their resume and job requirements.
- **Manually comparing** a resume to a job description is time-consuming and prone to oversight.
- **Finding relevant learning resources** for identified gaps is fragmented across many platforms (YouTube, courses, books, articles).
- **There is no unified tool** that automates gap analysis and curates learning resources in one place.

**Solution:** An AI-powered assistant that analyzes resume vs. job description, identifies gaps, and suggests personalized training resources across multiple platforms.

---

## Features

- **Resume analysis** — extracts technical and soft skills from PDF / DOCX / TXT resumes and rates them 1–100.
- **Job description analysis** — identifies required skills, industry, and software engineering domain.
- **Skill matching** — computes a weighted match percentage and highlights gaps.
- **Resource discovery** — searches for web articles, news, YouTube videos, Amazon books, blog posts, and courses on O'Reilly, Pluralsight, Coursera, Udemy, and DeepLearning.ai.
- **Training plan** — prioritised, actionable study plan based on skill gaps.
- **User overrides (human in the loop)** — add skills, adjust ratings, change domain; re-analyze without re-uploading.
- **Export** — download full analysis as JSON.

---

## Design Principles

| Principle | Description |
|-----------|-------------|
| **Modular orchestration** | LangGraph state machine with discrete nodes; each step is a separate agent. |
| **Structured outputs** | Pydantic models for resume, JD, training plan; typed contracts throughout. |
| **Canonical skill mapping** | Synonyms (LLMs, RAG, K8s, Python 3) normalized for matching. |
| **Graceful degradation** | Missing API keys disable features, not the app; warnings shown in UI. |
| **Privacy-first** | Resume and job description are not stored on any server. |
| **User overrides (human in the loop)** | Add skills, adjust ratings, change domain; re-analyze from `normalize_skills` onward. |

---

## Architecture

### Technology Stack

| Component | Technology |
|-----------|------------|
| Orchestration | [LangGraph](https://github.com/langchain-ai/langgraph) |
| LLM | OpenAI GPT-4o (via LangChain) |
| UI | [Streamlit](https://streamlit.io) |
| Web search | [Tavily](https://tavily.com) |
| Video search | YouTube Data API v3 |
| Book search | Tavily (site-scoped to Amazon) |
| Course search | Tavily (site-scoped to O'Reilly, Pluralsight, Coursera, Udemy, DeepLearning.ai) |
| Parsing | PyMuPDF (PDF), python-docx (DOCX), plain TXT |

### Graph Flow

```
START
  │
  ▼
parse_resume ──► analyze_jd ──► validate_industry
                                    │
                    (if not software job → END with error)
                                    │
                                    ▼
                            normalize_skills
                                    │
                                    ▼
                              match_skills
                                    │
        ┌───────┬───────┬───────┬───┴───┬───────┬───────┐
        ▼       ▼       ▼       ▼       ▼       ▼       ▼
     web    news   youtube amazon courses blog  (parallel)
        └───────┴───────┴───────┴───┬───┴───────┴───────┘
                                    ▼
                        generate_training_plan
                                    │
                                    ▼
                                  END
```

### State & Data Flow

`GraphState` (TypedDict) flows through every node:

| Stage | Fields |
|-------|--------|
| **Inputs** | `resume_text`, `job_description`, `ignore_programming_languages` |
| **Resume/JD** | `user_skills`, `required_skills`, `required_skills_for_resources`, `job_title`, `industry`, `is_software_job`, `software_domain` |
| **Matching** | `skill_canonical_map`, `match_percentage`, `skill_gaps` |
| **Resources** | `web_articles`, `news_articles`, `youtube_videos`, `amazon_books`, `training_courses`, `blog_posts` (merged via reducers) |
| **Output** | `training_plan`, `error_message`, `resource_search_warnings` |

---

## Setup

### 1. Clone and install

```bash
git clone <your-repo-url>
cd ai-job-assistant
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure API keys

Copy the example env file and fill in your keys:

```bash
cp .env.example .env
```

| Key | Where to get it |
|-----|-----------------|
| `OPENAI_API_KEY` | https://platform.openai.com/api-keys |
| `TAVILY_API_KEY` | https://app.tavily.com |
| `YOUTUBE_API_KEY` | https://console.cloud.google.com (YouTube Data API v3) |

### 3. Run

```bash
streamlit run app.py
```

The app opens at **http://localhost:8501**.

---

## Usage

1. Upload your resume (PDF, DOCX, or TXT) in the sidebar.
2. Paste the full job description into the text area.
3. Optionally enable **Ignore programming languages** to focus on non-PL gaps.
4. Click **Analyze**.
5. Review your match score, skill comparison chart, identified gaps, and the generated training plan with curated resources across six tabs (Web, News, YouTube, Books, Courses, Blog).
6. Use **Add skill** to include skills the analyzer may have missed, then **Re-analyze**.
7. Click **Export as JSON** to download the full analysis.

**Privacy:** Your resume and job description are not stored on any server.

---

## Testing

### Unit tests (28 tests)

```bash
pytest tests/ -v
```

| Test file | Coverage |
|-----------|----------|
| `test_parsers.py` | `parse_txt`, `parse_resume` (TXT, PDF, unsupported extensions) |
| `test_config.py` | `normalize_skill_name`, `is_programming_language`, `missing_api_keys` |
| `test_skill_matcher.py` | Perfect match, gap detection, synonym matching |
| `test_resource_finder.py` | `_top_gap_skill_names` fallbacks |
| `test_export.py` | `build_export_json` structure |

### LLM-as-a-judge eval tests (3 tests)

Eval tests use GPT-4o-mini to judge whether analysis outputs (skill gaps, training plan) are reasonable given the job description. Requires `OPENAI_API_KEY`.

```bash
# Run all tests including evals
pytest tests/ -v

# Skip eval tests (no API key needed)
SKIP_EVALS=1 pytest tests/ -v

# On Windows PowerShell:
# $env:SKIP_EVALS=1; pytest tests/ -v
```

| Eval | What it checks |
|------|----------------|
| Skill gaps | Are gaps plausible for the job description? |
| Training plan | Does the plan prioritize critical gaps appropriately? |
| Synonym matching | Are LLMs vs. Large Language Models matched correctly? |

---

## Project Structure

```
ai-job-assistant/
├── app.py                  # Streamlit entry point
├── config/
│   └── settings.py         # API keys, model config, canonical skills, synonyms
├── models/
│   └── state.py            # Pydantic models & LangGraph state schema
├── parsers/
│   └── file_parser.py      # PDF / DOCX / TXT → plain text
├── graph/
│   ├── builder.py         # LangGraph construction & compilation
│   └── nodes/
│       ├── resume_analyzer.py
│       ├── jd_analyzer.py
│       ├── skill_normalizer.py
│       ├── skill_matcher.py
│       ├── resource_finder.py
│       └── training_planner.py
├── tools/
│   ├── tavily_tools.py
│   ├── youtube_tool.py
│   ├── amazon_tool.py
│   └── course_tools.py
├── ui/
│   ├── sidebar.py
│   ├── results.py
│   ├── tabs.py
│   └── overrides.py
├── tests/
│   ├── conftest.py
│   ├── test_parsers.py
│   ├── test_config.py
│   ├── test_skill_matcher.py
│   ├── test_resource_finder.py
│   ├── test_export.py
│   └── test_evals.py
├── utils/
│   └── export.py           # Export JSON builder
├── scripts/
│   └── generate_deck.py   # Generate PowerPoint design deck
├── pytest.ini
├── requirements.txt
└── .env.example
```

---

## Future Directions

- **Login with credentials** — e.g. Google auth for authenticated sessions
- **Save projects on server** — store job description, skills analysis, training plan, and learning resources as a project with a unique name per user
- **Load previous project** — restore a saved project from JSON
- **Google Calendar integration** — add the training plan to the user's Google Calendar based on user-defined days and times

---

## Generate Design Deck

A PowerPoint deck describing the design, architecture, and testing can be generated:

```bash
python scripts/generate_deck.py
```

Output: `AI_Job_Assistant_Design_Deck.pptx`
