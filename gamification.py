"""
Smart Placement Prediction & Career Analytics System
Gamification, Student Achievements & Milestone Badge Engine
"""

from typing import Dict, Any, List
import database

BADGE_DEFINITIONS: List[Dict[str, Any]] = [
    {
        "badge_key": "aptitude_master",
        "badge_title": "Aptitude Master",
        "description": "Achieve an Aptitude Test Score of 80.0 or higher.",
        "icon": "zap",
        "criteria": "AptitudeTestScore >= 80.0"
    },
    {
        "badge_key": "project_builder",
        "badge_title": "Project Builder",
        "description": "Complete and record 3 or more technical portfolio projects.",
        "icon": "folder-plus",
        "criteria": "Projects >= 3"
    },
    {
        "badge_key": "skill_improver",
        "badge_title": "Skill Improver",
        "description": "Demonstrate verified positive improvement between saved assessments in CGPA, Aptitude, or Placement Probability.",
        "icon": "trending-up",
        "criteria": "Assessment[n] > Assessment[n-1] in CGPA, Aptitude, or Probability"
    },
    {
        "badge_key": "placement_ready",
        "badge_title": "Placement Ready",
        "description": "Attain Low Placement Risk (Probability >= 70%) with Aptitude >= 75.0 and Projects >= 2.",
        "icon": "check-circle",
        "criteria": "PlacementProb >= 0.70 & Aptitude >= 75.0 & Projects >= 2"
    },
    {
        "badge_key": "resume_verified",
        "badge_title": "Resume Verified",
        "description": "Upload, parse, and benchmark your technical resume through the Resume Analyzer.",
        "icon": "file-text",
        "criteria": "Uploaded valid PDF resume"
    },
    {
        "badge_key": "career_architect",
        "badge_title": "Career Architect",
        "description": "Select a personalized career roadmap and mark at least one learning milestone completed.",
        "icon": "compass",
        "criteria": "Career Roadmap chosen & >= 1 milestone completed"
    },
    {
        "badge_key": "holistic_achiever",
        "badge_title": "Holistic Achiever",
        "description": "Maintain Soft Skills >= 4.0, active Extracurriculars, and enrolled in Campus Placement Training.",
        "icon": "award",
        "criteria": "SoftSkills >= 4.0 & Extracurriculars='Yes' & Training='Yes'"
    }
]


def evaluate_and_award_badges(student_id: int, db_path: str = None) -> List[Dict[str, Any]]:
    """
    Evaluates student records and awards newly eligible badges.
    Returns the comprehensive list of all badges with earned state and progress info.
    """
    profile = database.get_student_profile(student_id, db_path) or {}
    history = database.get_student_assessment_history(student_id, limit=50, db_path=db_path)
    milestones = database.get_student_milestones(student_id, db_path)
    resume = database.get_latest_resume(student_id, db_path)
    earned_records = {b["badge_key"]: b for b in database.get_student_badges(student_id, db_path)}

    cgpa = float(profile.get("cgpa", 0.0))
    aptitude = float(profile.get("aptitude_score", 0.0))
    projects = int(profile.get("projects", 0))
    soft_skills = float(profile.get("soft_skills", 1.0))
    extra = str(profile.get("extracurriculars", "No"))
    training = str(profile.get("placement_training", "No"))

    # Latest assessment probability
    latest_prob = 0.0
    if history:
        latest_prob = float(history[-1].get("placement_probability", 0.0))

    results: List[Dict[str, Any]] = []

    for badge in BADGE_DEFINITIONS:
        key = badge["badge_key"]
        is_earned = key in earned_records
        earned_at = earned_records[key]["earned_at"] if is_earned else None
        eligible_now = False
        progress_info = ""

        if key == "aptitude_master":
            eligible_now = aptitude >= 80.0
            progress_info = f"{aptitude:.1f} / 80.0 pts"
        elif key == "project_builder":
            eligible_now = projects >= 3
            progress_info = f"{projects} / 3 projects"
        elif key == "skill_improver":
            # Check if there are at least two assessments and the latest shows positive progress
            if len(history) >= 2:
                prev = history[-2]
                curr = history[-1]
                prob_up = curr.get("placement_probability", 0) > prev.get("placement_probability", 0)
                apt_up = curr.get("aptitude_score", 0) > prev.get("aptitude_score", 0)
                cgpa_up = curr.get("cgpa", 0) > prev.get("cgpa", 0)
                eligible_now = prob_up or apt_up or cgpa_up
                progress_info = "Progress verified across snapshots" if eligible_now else "Snapshot recorded; awaiting improvement"
            else:
                progress_info = f"{len(history)} / 2 snapshots recorded"
        elif key == "placement_ready":
            eligible_now = (latest_prob >= 0.70) and (aptitude >= 75.0) and (projects >= 2)
            progress_info = f"Prob: {latest_prob*100:.1f}%, Apt: {aptitude:.1f}, Proj: {projects}"
        elif key == "resume_verified":
            eligible_now = resume is not None
            progress_info = "Resume verified" if resume else "No resume uploaded yet"
        elif key == "career_architect":
            completed_milestones = sum(1 for m in milestones if m.get("is_completed"))
            eligible_now = completed_milestones >= 1
            progress_info = f"{completed_milestones} / 1 milestone completed"
        elif key == "holistic_achiever":
            eligible_now = (soft_skills >= 4.0) and (extra == "Yes") and (training == "Yes")
            progress_info = f"Soft: {soft_skills:.1f}/5.0 | Extra: {extra} | Training: {training}"

        # Award if newly eligible
        if eligible_now and not is_earned:
            database.award_badge(
                student_id=student_id,
                badge_key=key,
                badge_title=badge["badge_title"],
                description=badge["description"],
                icon=badge["icon"],
                db_path=db_path
            )
            is_earned = True
            # Re-fetch earned record for timestamp
            newly_earned = database.get_student_badges(student_id, db_path)
            for b in newly_earned:
                if b["badge_key"] == key:
                    earned_at = b["earned_at"]

        results.append({
            "badge_key": key,
            "badge_title": badge["badge_title"],
            "description": badge["description"],
            "icon": badge["icon"],
            "criteria": badge["criteria"],
            "is_earned": is_earned,
            "earned_at": earned_at,
            "progress_info": progress_info
        })

    return results
