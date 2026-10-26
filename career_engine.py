"""
Smart Placement Prediction & Career Analytics System
Personalized Career Roadmap & Job Role Recommendation Engine
"""

from typing import Dict, Any, List, Optional

# ---------------------------------------------------------------------------
# Supported Career Roles & Curated Skill Taxonomies
# ---------------------------------------------------------------------------

JOB_ROLES: Dict[str, Dict[str, Any]] = {
    "Data Analyst": {
        "title": "Data Analyst",
        "description": "Translates business data into actionable visual insights, KPI dashboards, and statistical summaries.",
        "required_skills": [
            "SQL", "Python", "Excel", "Tableau", "Power BI", "Data Visualization", "Statistics", "EDA"
        ],
        "recommended_skills": [
            "Pandas", "NumPy", "Business Intelligence", "Reporting", "Communication", "Problem Solving"
        ],
        "benchmark_profile": {
            "min_cgpa": 7.2,
            "min_aptitude": 75.0,
            "min_projects": 2
        },
        "suggested_projects": [
            "Interactive Sales & Revenue Dashboard in Power BI or Tableau with drill-down filters",
            "Customer Churn & Retention Exploratory Data Analysis using Python, Pandas, and Seaborn",
            "Complex SQL Multi-Table Aggregation & Window Function Analytics on Retail Datasets"
        ],
        "learning_topics": [
            "Advanced SQL: Window Functions, CTEs, and Query Optimization",
            "Exploratory Data Analysis and Statistical Hypothesis Testing",
            "Data Storytelling, Dashboard Design, and Executive Metric Presentation"
        ]
    },
    "Data Scientist": {
        "title": "Data Scientist",
        "description": "Designs predictive algorithms, applies machine learning models, and discovers deep patterns in complex data.",
        "required_skills": [
            "Python", "Machine Learning", "Scikit-Learn", "Statistics", "Pandas", "NumPy", "SQL", "Data Modeling"
        ],
        "recommended_skills": [
            "Deep Learning", "TensorFlow", "PyTorch", "NLP", "Feature Engineering", "Mathematics", "Git"
        ],
        "benchmark_profile": {
            "min_cgpa": 7.8,
            "min_aptitude": 82.0,
            "min_projects": 3
        },
        "suggested_projects": [
            "End-to-End Placement or Credit Risk Classifier with Scikit-Learn, Cross-Validation & SHAP Explainability",
            "Natural Language Processing Sentiment Analyzer on Product Reviews using HuggingFace / Transformers",
            "Time-Series Demand Forecasting Pipeline with Automated Model Evaluation & Drift Detection"
        ],
        "learning_topics": [
            "Statistical Learning Theory, Regularization, and Supervised / Unsupervised ML",
            "Feature Engineering, Dimensionality Reduction, and Handling Imbalanced Datasets",
            "Model Interpretability (SHAP / LIME) and Production Model Packaging"
        ]
    },
    "Software Developer": {
        "title": "Software Developer",
        "description": "Engineers scalable backend APIs, responsive web applications, and robust software architectures.",
        "required_skills": [
            "Data Structures", "Algorithms", "Python", "Java", "JavaScript", "SQL", "OOP", "Git", "REST APIs"
        ],
        "recommended_skills": [
            "Flask", "Django", "React", "Node.js", "Docker", "Unit Testing", "System Design", "Linux"
        ],
        "benchmark_profile": {
            "min_cgpa": 7.5,
            "min_aptitude": 80.0,
            "min_projects": 2
        },
        "suggested_projects": [
            "Full-Stack Web Application with JWT/Session Authentication, Relational Database, and Responsive UI",
            "High-Throughput Microservice REST API with Dockerization, Input Validation, and Automated Unit Tests",
            "Collaborative Real-Time Task Management Tool with WebSockets and Role-Based Access Control"
        ],
        "learning_topics": [
            "Core Data Structures & Algorithmic Problem Solving (Trees, Graphs, Dynamic Programming)",
            "Object-Oriented Design Principles (SOLID) and Clean Code Practices",
            "RESTful API Architecture, Database Indexing, and Caching Strategies"
        ]
    },
    "Business Analyst": {
        "title": "Business Analyst",
        "description": "Bridges technical engineering teams with business stakeholders to translate domain requirements into solutions.",
        "required_skills": [
            "Business Analysis", "Requirements Gathering", "SQL", "Excel", "Data Visualization", "Communication", "Problem Solving"
        ],
        "recommended_skills": [
            "Power BI", "Tableau", "Agile", "Scrum", "Process Modeling", "Presentation", "Jira"
        ],
        "benchmark_profile": {
            "min_cgpa": 7.0,
            "min_aptitude": 72.0,
            "min_projects": 1
        },
        "suggested_projects": [
            "Comprehensive Business Process Re-engineering Case Study with BPMN Workflow Diagrams",
            "Market Opportunity & Competitive Gap Analysis Dashboard in Power BI with KPI Metrics",
            "Product Requirements Document (PRD) with User Stories, Acceptance Criteria, and Wireframes"
        ],
        "learning_topics": [
            "Agile & Scrum Methodologies, Sprint Planning, and User Story Mapping",
            "Stakeholder Management, Requirements Elicitation, and Gap Analysis",
            "Business Financial Metrics (ROI, CAC, LTV) and Quantitative Decision Support"
        ]
    },
    "QA Engineer": {
        "title": "QA Engineer",
        "description": "Ensures software stability, reliability, and security through manual test plans and automated test suites.",
        "required_skills": [
            "Software Testing", "Unit Testing", "Python", "Java", "Test Automation", "SQL", "Git", "Bug Tracking"
        ],
        "recommended_skills": [
            "Selenium", "PyTest", "Postman", "CI/CD", "Performance Testing", "API Testing", "Jira", "Linux"
        ],
        "benchmark_profile": {
            "min_cgpa": 7.0,
            "min_aptitude": 70.0,
            "min_projects": 1
        },
        "suggested_projects": [
            "Automated End-to-End Web Regression Test Suite using PyTest and Selenium WebDriver",
            "Automated REST API Test Harness in Postman / Python verifying Status Codes and Response Payloads",
            "Continuous Integration Testing Pipeline with Automated GitHub Actions and Test Coverage Reports"
        ],
        "learning_topics": [
            "Software Testing Methodologies: Black-Box, White-Box, Boundary Value Analysis, and Equivalence Partitioning",
            "API Testing and Automated Verification of Status Codes, Payloads, and Security Headers",
            "CI/CD Integration, Smoke Testing, and Test Automation Framework Architecture"
        ]
    }
}


# ---------------------------------------------------------------------------
# Job Role Evaluation
# ---------------------------------------------------------------------------

def evaluate_job_roles(profile_data: Dict[str, Any], resume_skills: Optional[List[str]] = None) -> List[Dict[str, Any]]:
    """
    Evaluates student profile and detected resume skills against all supported roles.
    Produces a transparent skill match percentage, matched skills, missing skills,
    and recommended next steps.
    """
    detected_skills_set = {s.lower() for s in (resume_skills or [])}

    # Extract student profile attributes
    cgpa = float(profile_data.get("CGPA", 0.0) or profile_data.get("cgpa", 0.0))
    aptitude = float(profile_data.get("AptitudeTestScore", 0.0) or profile_data.get("aptitude_score", 0.0))
    projects = int(profile_data.get("Projects", 0) or profile_data.get("projects", 0))

    results = []

    for role_name, role_meta in JOB_ROLES.items():
        req_skills = role_meta["required_skills"]
        rec_skills = role_meta["recommended_skills"]
        bench = role_meta["benchmark_profile"]

        matched_req = [s for s in req_skills if s.lower() in detected_skills_set]
        missing_req = [s for s in req_skills if s.lower() not in detected_skills_set]
        matched_rec = [s for s in rec_skills if s.lower() in detected_skills_set]

        # Calculate transparent match score
        # 70% weight on required skills, 15% on recommended skills, 15% on academic benchmarks
        req_score = (len(matched_req) / len(req_skills)) if req_skills else 1.0
        rec_score = (len(matched_rec) / len(rec_skills)) if rec_skills else 0.5

        # Benchmark score
        bench_score = 0.0
        if cgpa >= bench["min_cgpa"]:
            bench_score += 0.4
        else:
            bench_score += max(0.0, (cgpa / bench["min_cgpa"]) * 0.4)

        if aptitude >= bench["min_aptitude"]:
            bench_score += 0.4
        else:
            bench_score += max(0.0, (aptitude / bench["min_aptitude"]) * 0.4)

        if projects >= bench["min_projects"]:
            bench_score += 0.2
        else:
            bench_score += max(0.0, (projects / bench["min_projects"]) * 0.2)

        composite_match = round(((req_score * 0.70) + (rec_score * 0.15) + (bench_score * 0.15)) * 100, 1)
        composite_match = max(10.0, min(98.0, composite_match))  # Realistic bounds

        # Explanation formulation
        reasons = []
        if len(matched_req) >= len(req_skills) // 2:
            reasons.append(f"Demonstrates strong foundation in key competencies ({', '.join(matched_req[:3])}).")
        if aptitude >= bench["min_aptitude"]:
            reasons.append(f"Aptitude test score ({aptitude}) satisfies target role baseline ({bench['min_aptitude']}).")
        if projects >= bench["min_projects"]:
            reasons.append(f"Completed projects ({projects}) meet practical portfolio requirements.")
        if not reasons:
            reasons.append("Good entry-level alignment with high upside following targeted skill development.")

        results.append({
            "role": role_name,
            "title": role_meta["title"],
            "description": role_meta["description"],
            "match_percentage": composite_match,
            "matched_skills": matched_req + matched_rec,
            "missing_skills": missing_req,
            "all_required_skills": req_skills,
            "learning_topics": role_meta["learning_topics"],
            "suggested_projects": role_meta["suggested_projects"],
            "recommendation_reason": " ".join(reasons)
        })

    # Sort descending by match percentage
    results.sort(key=lambda x: x["match_percentage"], reverse=True)
    return results


# ---------------------------------------------------------------------------
# Roadmap Generation
# ---------------------------------------------------------------------------

def generate_roadmap(career_goal: str, profile_data: Dict[str, Any], resume_skills: Optional[List[str]] = None) -> Dict[str, Any]:
    """
    Builds a structured, prioritized career improvement roadmap tailored
    to the student's selected career goal and current gaps.
    """
    role_meta = JOB_ROLES.get(career_goal, JOB_ROLES["Software Developer"])
    detected_skills_set = {s.lower() for s in (resume_skills or [])}

    req_skills = role_meta["required_skills"]
    missing_skills = [s for s in req_skills if s.lower() not in detected_skills_set]

    milestones: List[Dict[str, Any]] = []

    # Category 1: Core Knowledge & Skill Gaps
    for i, skill in enumerate(missing_skills[:3]):
        milestones.append({
            "milestone_key": f"{career_goal.lower().replace(' ', '_')}_skill_{skill.lower().replace(' ', '_')}",
            "title": f"Master Core Competency: {skill}",
            "category": "Core Knowledge",
            "priority": "High" if i == 0 else "Medium",
            "description": f"Study syntax, foundational concepts, and standard design patterns for {skill} through structured tutorials and hands-on exercises."
        })

    # Category 2: Practical Projects
    for idx, proj in enumerate(role_meta["suggested_projects"]):
        milestones.append({
            "milestone_key": f"{career_goal.lower().replace(' ', '_')}_proj_{idx+1}",
            "title": f"Portfolio Project: {proj[:45]}...",
            "category": "Hands-On Projects",
            "priority": "High" if idx == 0 else "Medium",
            "description": proj
        })

    # Category 3: Learning Topics
    for idx, topic in enumerate(role_meta["learning_topics"]):
        milestones.append({
            "milestone_key": f"{career_goal.lower().replace(' ', '_')}_topic_{idx+1}",
            "title": f"Advanced Study: {topic[:45]}...",
            "category": "Theoretical & Architecture",
            "priority": "Medium",
            "description": topic
        })

    # Category 4: Placement Readiness
    aptitude = float(profile_data.get("AptitudeTestScore", 0.0) or profile_data.get("aptitude_score", 0.0))
    if aptitude < role_meta["benchmark_profile"]["min_aptitude"]:
        milestones.append({
            "milestone_key": f"{career_goal.lower().replace(' ', '_')}_aptitude_boost",
            "title": f"Elevate Aptitude Score to {role_meta['benchmark_profile']['min_aptitude']}+",
            "category": "Placement Readiness",
            "priority": "High",
            "description": f"Practice quantitative aptitude, logical reasoning, and data interpretation mock assessments daily."
        })

    return {
        "career_goal": career_goal,
        "role_details": role_meta,
        "missing_skills": missing_skills,
        "milestones": milestones,
        "disclaimer": "Career roadmaps and match percentages are prescriptive educational recommendations based on campus placement benchmarks and do not constitute job offers or employment guarantees."
    }
