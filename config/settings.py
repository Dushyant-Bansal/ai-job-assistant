import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY", "")
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY", "")

API_KEYS = {
    "OPENAI_API_KEY": (OPENAI_API_KEY, "LLM analysis (resume & job parsing)"),
    "TAVILY_API_KEY": (TAVILY_API_KEY, "Web articles, news, blog posts, books, courses"),
    "YOUTUBE_API_KEY": (YOUTUBE_API_KEY, "YouTube videos"),
}


def missing_api_keys() -> list[str]:
    """Return names of API keys that are missing or empty."""
    return [name for name, (value, _) in API_KEYS.items() if not (value or "").strip()]

LLM_MODEL = "gpt-4o"
LLM_TEMPERATURE = 0.2

MAX_RESOURCE_RESULTS_PER_SKILL = 3
MAX_SKILLS_TO_SEARCH = 5

SOFTWARE_DOMAINS = [
    "LLM Training / LLM Development",
    "RAG / Retrieval-Augmented Generation",
    "AI Agentic Development",
    "AI Agentic Infrastructure",
    "Machine Learning",
    "AI Infrastructure",
    "Data Engineering / ETL",
    "Distributed Systems",
    "Network Security",
    "Compute Infrastructure",
    "Storage Infrastructure",
    "Networking Infrastructure",
    "General Software Security",
    "Desktop Application Development",
    "Mobile Application Development",
    "Web Development (Frontend)",
    "Web Development (Backend)",
    "Web Development (Full-Stack)",
    "DevOps / SRE",
    "Embedded Systems",
    "Cloud Infrastructure",
    "Database Engineering",
    "Game Development",
    "Other",
]

CANONICAL_SKILLS = [
    "Python", "Java", "JavaScript", "TypeScript", "Go", "Rust", "C", "C++",
    "C#", "Ruby", "PHP", "Swift", "Kotlin", "Scala", "R", "MATLAB",
    "SQL", "NoSQL", "PostgreSQL", "MySQL", "MongoDB", "Redis", "Elasticsearch",
    "Cassandra", "DynamoDB",
    "React", "Angular", "Vue.js", "Next.js", "Svelte", "HTML", "CSS",
    "Tailwind CSS", "Bootstrap",
    "Node.js", "Express.js", "Django", "Flask", "FastAPI", "Spring Boot",
    "Ruby on Rails", "ASP.NET",
    "AWS", "Azure", "GCP", "Docker", "Kubernetes", "Terraform", "Ansible",
    "Jenkins", "GitHub Actions", "CI/CD",
    "Linux", "Git", "REST APIs", "GraphQL", "gRPC", "WebSockets",
    "Microservices", "Monolithic Architecture", "Event-Driven Architecture",
    "System Design", "Distributed Systems", "Load Balancing",
    "Message Queues", "Kafka", "RabbitMQ", "Celery",
    "Machine Learning", "Deep Learning", "NLP", "Computer Vision",
    "PyTorch", "TensorFlow", "Scikit-learn", "Pandas", "NumPy",
    "LLMs", "RAG", "LangChain", "Prompt Engineering", "MLOps",
    "Apache Spark", "Apache Airflow", "ETL Pipelines", "Data Warehousing",
    "dbt", "Snowflake", "BigQuery", "Databricks",
    "React Native", "Flutter", "SwiftUI", "Android SDK",
    "Networking", "TCP/IP", "DNS", "HTTP/HTTPS", "TLS/SSL",
    "Cryptography", "OAuth", "JWT", "SAML",
    "Unit Testing", "Integration Testing", "End-to-End Testing",
    "Test-Driven Development", "pytest", "JUnit", "Selenium",
    "Agile", "Scrum", "Kanban",
    "Leadership", "Communication", "Teamwork", "Problem Solving",
    "Mentoring", "Project Management", "Cross-functional Collaboration",
    "Technical Writing", "Presentation Skills", "Time Management",
    "Critical Thinking", "Adaptability", "Conflict Resolution",
]

# Skill synonyms: (canonical_name, [variants]) — used to match resume and JD skills
SKILL_SYNONYMS: list[tuple[str, list[str]]] = [
    ("LLMs", ["LLM", "LLMs", "Large Language Models", "Large Language Models (LLM)", "Large Language Models (LLMs)", "LLM Systems", "LLM Development"]),
    ("AI Agentic Development", ["Agentic AI", "AI Agentic Development", "Agentic Development", "Agentic Systems"]),
    ("RAG", ["RAG", "Retrieval-Augmented Generation", "Retrieval Augmented Generation", "RAG Systems"]),
    ("Machine Learning", ["ML", "Machine Learning", "Machine Learning (ML)", "ML Systems"]),
    ("Deep Learning", ["DL", "Deep Learning", "Deep Learning (DL)"]),
    ("Natural Language Processing", ["NLP", "Natural Language Processing", "Natural Language Processing (NLP)", "NLP Systems"]),
    ("Kubernetes", ["K8s", "Kubernetes", "K8s/Kubernetes", "Kubernetes Systems"]),
    ("JavaScript", ["JS", "JavaScript", "Javascript", "JavaScript Systems"]),
    ("Python", ["Python", "Python 3", "Python3", "Python Systems"]),
    ("React", ["React", "React.js", "ReactJS", "React Systems"]),
    ("Node.js", ["Node", "Node.js", "NodeJS", "Node Systems"]),
    ("Amazon Web Services", ["AWS", "Amazon Web Services", "Amazon AWS", "AWS Systems"]),
    ("CI/CD", ["CI/CD", "CI CD", "Continuous Integration", "Continuous Deployment"]),
    ("REST APIs", ["REST", "REST API", "REST APIs", "RESTful", "REST Systems"]),
    ("GraphQL", ["GraphQL", "GraphQL API", "GraphQL Systems"]),
    ("Docker", ["Docker", "Docker Containers", "Containerization"]),
    ("PostgreSQL", ["Postgres", "PostgreSQL", "PostgresQL"]),
    ("MongoDB", ["Mongo", "MongoDB"]),
    ("Redis", ["Redis", "Redis Cache"]),
    ("Apache Kafka", ["Kafka", "Apache Kafka"]),
    ("Apache Spark", ["Spark", "Apache Spark"]),
    ("TensorFlow", ["TensorFlow", "Tensor Flow", "TF"]),
    ("PyTorch", ["PyTorch", "Pytorch", "Torch"]),
]


def _build_variant_map() -> dict[str, str]:
    m: dict[str, str] = {}
    for canonical, variants in SKILL_SYNONYMS:
        for v in variants:
            m[v.strip().lower()] = canonical
    return m


_VARIANT_TO_CANONICAL = _build_variant_map()


def normalize_skill_name(name: str) -> str:
    """Return the canonical skill name for matching. Case-insensitive."""
    if not name or not name.strip():
        return name
    key = name.strip().lower()
    return _VARIANT_TO_CANONICAL.get(key, name.strip())

# Programming languages to exclude when "ignore programming languages" is enabled
PROGRAMMING_LANGUAGES = frozenset(
    s.lower()
    for s in [
        "Python", "Java", "JavaScript", "TypeScript", "Go", "Rust", "C", "C++",
        "C#", "Ruby", "PHP", "Swift", "Kotlin", "Scala", "R", "MATLAB",
    ]
)


def is_programming_language(skill_name: str) -> bool:
    """Return True if the skill is a programming language."""
    canonical = normalize_skill_name(skill_name)
    return canonical.strip().lower() in PROGRAMMING_LANGUAGES
