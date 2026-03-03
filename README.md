# AI Job Training Assistant

An AI-powered tool that analyses your resume against a software engineering job
description, identifies skill gaps, and generates a personalised training plan
with curated learning resources.

## Features

- **Resume analysis** — extracts technical and soft skills from PDF / DOCX / TXT
  resumes and rates them 1–100.
- **Job description analysis** — identifies required skills, industry, and
  software engineering domain.
- **Skill matching** — computes a weighted match percentage and highlights gaps.
- **Resource discovery** — searches for web articles, news, YouTube videos,
  Amazon books, and courses on O'Reilly, Pluralsight, Coursera, Udemy, and
  DeepLearning.ai.
- **Training plan** — prioritised, actionable study plan based on skill gaps.

## Architecture

Built with:

| Component | Technology |
|-----------|------------|
| Orchestration | [LangGraph](https://github.com/langchain-ai/langgraph) |
| LLM | OpenAI GPT-4o (via LangChain) |
| UI | [Streamlit](https://streamlit.io) |
| Web search | [Tavily](https://tavily.com) |
| Video search | YouTube Data API v3 |
| Book search | Tavily (site-scoped to Amazon) |
| Course search | Tavily (site-scoped to each platform) |

### Graph flow

```
START → parse_resume → analyze_jd → validate_industry
          │ (if not software job → END with error)
          ▼
     match_skills
          │
    ┌─────┼─────┬────────┬─────────┐   (fan-out, parallel)
    ▼     ▼     ▼        ▼         ▼
  web   news  youtube  amazon   courses
    └─────┼─────┴────────┴─────────┘   (fan-in)
          ▼
  generate_training_plan → END
```

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

## Usage

1. Upload your resume (PDF, DOCX, or TXT) in the sidebar.
2. Paste the full job description into the text area.
3. Click **Analyze**.
4. Review your match score, skill comparison chart, identified gaps, and the
   generated training plan with curated resources across five tabs.

## Project structure

```
ai-job-assistant/
├── app.py                  # Streamlit entry point
├── config/
│   └── settings.py         # API keys, model config, canonical skills
├── models/
│   └── state.py            # Pydantic models & LangGraph state schema
├── parsers/
│   └── file_parser.py      # PDF / DOCX / TXT → plain text
├── graph/
│   ├── builder.py          # LangGraph construction & compilation
│   └── nodes/
│       ├── resume_analyzer.py
│       ├── jd_analyzer.py
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
│   └── tabs.py
├── requirements.txt
└── .env.example
```
