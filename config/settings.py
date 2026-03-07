import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY", "")
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY", "")

LLM_MODEL = "gpt-4o"
LLM_TEMPERATURE = 0.2

MAX_RESOURCE_RESULTS_PER_SKILL = 3
MAX_SKILLS_TO_SEARCH = 5

SOFTWARE_DOMAINS = [
    "LLM Training / LLM Development",
    "RAG / Retrieval-Augmented Generation",
    "AI Agentic Development",
    "AI Agentic Infrastructure",
    "AI Agentic Development",
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
