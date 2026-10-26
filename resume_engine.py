"""
Smart Placement Prediction & Career Analytics System
Resume Parser, Transparent Skill Extractor & Role Alignment Engine
"""

import os
import re
from typing import Dict, Any, List, Set, Tuple, Optional
from pypdf import PdfReader
from career_engine import JOB_ROLES

# ---------------------------------------------------------------------------
# Transparent, Curated Technical Skill Dictionary
# ---------------------------------------------------------------------------

SKILL_TAXONOMY: Dict[str, List[str]] = {
    "Programming Languages": [
        "Python", "Java", "C++", "C#", "C", "JavaScript", "TypeScript",
        "Go", "Rust", "R", "PHP", "Ruby", "Swift", "Kotlin", "SQL", "HTML", "CSS"
    ],
    "Frameworks & Libraries": [
        "Flask", "Django", "FastAPI", "React", "Node.js", "Express",
        "Spring Boot", "Angular", "Vue", "Next.js", "Bootstrap", "Tailwind",
        "Pandas", "NumPy", "Scikit-Learn", "TensorFlow", "PyTorch", "Keras",
        "Matplotlib", "Seaborn", "OpenCV", "NLTK"
    ],
    "Databases & Cloud": [
        "MySQL", "PostgreSQL", "SQLite", "MongoDB", "Redis", "Oracle",
        "Firebase", "AWS", "Azure", "GCP", "Docker", "Kubernetes", "Linux"
    ],
    "Developer Tools & Methods": [
        "Git", "GitHub", "GitLab", "CI/CD", "Postman", "Jira", "Selenium",
        "PyTest", "JUnit", "Agile", "Scrum", "REST APIs", "GraphQL"
    ],
    "Core CS & Data Competencies": [
        "Data Structures", "Algorithms", "Object-Oriented Programming", "OOP",
        "System Design", "Database Management", "DBMS", "Operating Systems",
        "Computer Networks", "Machine Learning", "Deep Learning", "Data Analysis",
        "Data Visualization", "Tableau", "Power BI", "Statistics", "EDA"
    ],
    "Interpersonal & Soft Skills": [
        "Communication", "Leadership", "Teamwork", "Problem Solving",
        "Critical Thinking", "Time Management", "Adaptability", "Presentation"
    ]
}

# Flattened list with regex boundaries for accurate extraction
FLAT_SKILLS: List[str] = []
for category_skills in SKILL_TAXONOMY.values():
    FLAT_SKILLS.extend(category_skills)
# Remove duplicates while preserving order
FLAT_SKILLS = list(dict.fromkeys(FLAT_SKILLS))


def extract_text_from_pdf(pdf_path: str) -> Tuple[str, Optional[str]]:
    """
    Extracts plain text from a PDF file using pypdf.
    Returns: (extracted_text, error_message)
    """
    if not os.path.exists(pdf_path):
        return "", "File not found on server."

    try:
        reader = PdfReader(pdf_path)
        if len(reader.pages) == 0:
            return "", "PDF file contains 0 pages."

        full_text = []
        for idx, page in enumerate(reader.pages):
            page_text = page.extract_text() or ""
            full_text.append(page_text)

        extracted = "\n".join(full_text).strip()
        if not extracted:
            return "", "No readable text found. The document may be a scanned image without optical character recognition."

        return extracted, None
    except Exception as e:
        return "", f"Failed to extract text from PDF: {str(e)}"


def detect_skills_in_text(text: str) -> List[str]:
    """
    Identifies technical and soft skills in extracted text using case-insensitive
    boundary patterns to avoid false substring matches.
    """
    detected: List[str] = []
    text_lower = text.lower()

    for skill in FLAT_SKILLS:
        skill_lower = skill.lower()

        # Special short terms requiring careful regex boundaries
        if skill_lower in ["c", "r", "go", "oop"]:
            pattern = rf"(?:\b|\s){re.escape(skill_lower)}(?:\b|[,\.\s;:])"
        elif skill_lower == "c++":
            pattern = r"(?:c\+\+|cpp)"
        elif skill_lower == "c#":
            pattern = r"(?:c#|csharp)"
        else:
            pattern = rf"\b{re.escape(skill_lower)}\b"

        if re.search(pattern, text_lower, re.IGNORECASE):
            detected.append(skill)

    return detected


def analyze_resume_text(
    resume_text: str,
    target_role: str = "Software Developer",
    custom_jd_text: Optional[str] = None
) -> Dict[str, Any]:
    """
    Analyzes resume text against the target role and optional Job Description.
    Calculates transparent match scores, lists matched/missing competencies,
    and returns actionable resume improvement suggestions.
    """
    detected_skills = detect_skills_in_text(resume_text)
    detected_lower = {s.lower() for s in detected_skills}

    role_info = JOB_ROLES.get(target_role, JOB_ROLES["Software Developer"])
    role_req_skills = role_info["required_skills"]
    role_rec_skills = role_info["recommended_skills"]

    # If user provided a custom Job Description, also extract skills from JD
    jd_skills = []
    if custom_jd_text and custom_jd_text.strip():
        jd_skills = detect_skills_in_text(custom_jd_text)

    # Effective target skills to benchmark against
    if jd_skills:
        benchmark_skills = list(dict.fromkeys(role_req_skills + jd_skills))
    else:
        benchmark_skills = role_req_skills

    matched = [s for s in benchmark_skills if s.lower() in detected_lower]
    missing = [s for s in benchmark_skills if s.lower() not in detected_lower]

    # Calculate match percentage
    if benchmark_skills:
        match_pct = round((len(matched) / len(benchmark_skills)) * 100, 1)
    else:
        match_pct = 50.0

    match_pct = max(10.0, min(95.0, match_pct))

    # Improvement suggestions
    suggestions: List[str] = []
    if missing:
        top_missing = missing[:4]
        suggestions.append(f"Consider acquiring and showcasing projects in: {', '.join(top_missing)}.")

    # Project & metric action suggestions
    has_metrics = bool(re.search(r"\b(?:\d+[%kK]|\d+\+?\s*(?:users|clients|accuracy|requests|ms))\b", resume_text))
    if not has_metrics:
        suggestions.append("Quantify your project outcomes with concrete numbers (e.g., 'improved accuracy by 12%', 'served 500+ requests').")

    has_git = "Git" in detected_skills or "GitHub" in detected_skills
    if not has_git:
        suggestions.append("Include active GitHub links to demonstrate source code quality, commits, and collaborative version control.")

    suggestions.append(f"Align resume terminology with standard {target_role} expectations and review your summary bullet points.")

    return {
        "target_role": target_role,
        "total_skills_detected": len(detected_skills),
        "detected_skills": detected_skills,
        "matched_skills": matched,
        "missing_skills": missing,
        "match_percentage": match_pct,
        "suggestions": suggestions,
        "custom_jd_compared": bool(custom_jd_text and custom_jd_text.strip()),
        "disclaimer": "This analysis is an educational estimate using transparent keyword identification. It may not capture synonyms, complex phrasing, or portfolio nuances, and does not replicate proprietary commercial ATS ranking engines."
    }
