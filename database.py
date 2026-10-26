"""
Smart Placement Prediction & Career Analytics System
SQLite Database Management & Privacy-Preserving Persistence Layer
"""

import os
import sqlite3
from datetime import datetime
from typing import Optional, Dict, Any, List

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INSTANCE_DIR = os.path.join(BASE_DIR, "instance")
DEFAULT_DB_PATH = os.path.join(INSTANCE_DIR, "smart_placement.db")


def get_db_path() -> str:
    """Returns database file path, honoring environment override if present."""
    return os.environ.get("DATABASE_PATH", DEFAULT_DB_PATH)


def get_db_connection(db_path: Optional[str] = None) -> sqlite3.Connection:
    """Creates a configured SQLite connection with foreign keys and row factory."""
    path = db_path or get_db_path()
    os.makedirs(os.path.dirname(path), exist_ok=True)
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def init_db(db_path: Optional[str] = None) -> None:
    """Initializes database schema safely without dropping existing tables."""
    path = db_path or get_db_path()
    os.makedirs(os.path.dirname(path), exist_ok=True)
    conn = get_db_connection(path)
    cursor = conn.cursor()

    # 1. Students Account Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL COLLATE NOCASE,
            password_hash TEXT NOT NULL,
            full_name TEXT NOT NULL,
            target_role TEXT DEFAULT 'Software Developer',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP
        );
    """)

    # 2. Student Profile Table (Academic Details & Current Baseline)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS student_profiles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER UNIQUE NOT NULL,
            cgpa REAL DEFAULT 0.0,
            ssc_marks REAL DEFAULT 0.0,
            hsc_marks REAL DEFAULT 0.0,
            aptitude_score REAL DEFAULT 0.0,
            soft_skills REAL DEFAULT 1.0,
            projects INTEGER DEFAULT 0,
            certifications INTEGER DEFAULT 0,
            internships INTEGER DEFAULT 0,
            extracurriculars TEXT DEFAULT 'No',
            placement_training TEXT DEFAULT 'No',
            target_role TEXT DEFAULT 'Software Developer',
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE
        );
    """)

    # 3. Assessment History (Progress Tracking with Timestamps)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS assessment_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            cgpa REAL NOT NULL,
            ssc_marks REAL NOT NULL,
            hsc_marks REAL NOT NULL,
            aptitude_score REAL NOT NULL,
            soft_skills REAL NOT NULL,
            projects INTEGER NOT NULL,
            certifications INTEGER NOT NULL,
            internships INTEGER NOT NULL,
            extracurriculars TEXT NOT NULL,
            placement_training TEXT NOT NULL,
            placement_probability REAL NOT NULL,
            risk_score REAL NOT NULL,
            risk_level TEXT NOT NULL,
            predicted_status TEXT NOT NULL,
            assessment_label TEXT DEFAULT 'Assessment Snapshot',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE
        );
    """)

    # 4. Career Roadmap Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS career_roadmaps (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER UNIQUE NOT NULL,
            career_goal TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE
        );
    """)

    # 5. Career Roadmap Milestones Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS roadmap_milestones (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            milestone_key TEXT NOT NULL,
            title TEXT NOT NULL,
            category TEXT NOT NULL,
            priority TEXT NOT NULL,
            description TEXT,
            is_completed INTEGER DEFAULT 0,
            completed_at TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(student_id, milestone_key),
            FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE
        );
    """)

    # 6. Resumes & Analysis Results Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS resumes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            original_filename TEXT NOT NULL,
            stored_filename TEXT NOT NULL,
            file_path TEXT NOT NULL,
            file_size_bytes INTEGER NOT NULL,
            uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            extracted_text_preview TEXT,
            detected_skills_json TEXT,
            target_role TEXT,
            match_percentage REAL DEFAULT 0.0,
            matched_skills_json TEXT,
            missing_skills_json TEXT,
            suggestions_json TEXT,
            custom_jd_compared INTEGER DEFAULT 0,
            FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE
        );
    """)

    # 7. Achievement Badges Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS achievement_badges (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            badge_key TEXT NOT NULL,
            badge_title TEXT NOT NULL,
            description TEXT NOT NULL,
            icon TEXT,
            earned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(student_id, badge_key),
            FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE
        );
    """)

    conn.commit()
    conn.close()


# ---------------------------------------------------------------------------
# Student CRUD Helper Functions
# ---------------------------------------------------------------------------

def create_student(email: str, password_hash: str, full_name: str, target_role: str = "Software Developer", db_path: Optional[str] = None) -> int:
    """Inserts a new student and creates their initial blank profile."""
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO students (email, password_hash, full_name, target_role) VALUES (?, ?, ?, ?)",
        (email.strip().lower(), password_hash, full_name.strip(), target_role)
    )
    student_id = cursor.lastrowid

    # Automatically create associated profile
    cursor.execute(
        "INSERT INTO student_profiles (student_id, target_role) VALUES (?, ?)",
        (student_id, target_role)
    )

    conn.commit()
    conn.close()
    return student_id


def get_student_by_email(email: str, db_path: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """Retrieves student record by case-insensitive email."""
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM students WHERE email = ? COLLATE NOCASE", (email.strip().lower(),))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def get_student_by_id(student_id: int, db_path: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """Retrieves student record by id."""
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM students WHERE id = ?", (student_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def update_student_last_login(student_id: int, db_path: Optional[str] = None) -> None:
    """Updates the last login timestamp for a student."""
    conn = get_db_connection(db_path)
    conn.execute("UPDATE students SET last_login = CURRENT_TIMESTAMP WHERE id = ?", (student_id,))
    conn.commit()
    conn.close()


# ---------------------------------------------------------------------------
# Profile CRUD Helper Functions
# ---------------------------------------------------------------------------

def get_student_profile(student_id: int, db_path: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """Retrieves full profile for a student."""
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM student_profiles WHERE student_id = ?", (student_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def upsert_student_profile(student_id: int, profile_data: Dict[str, Any], db_path: Optional[str] = None) -> None:
    """Updates or inserts student profile data."""
    conn = get_db_connection(db_path)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO student_profiles (
            student_id, cgpa, ssc_marks, hsc_marks, aptitude_score,
            soft_skills, projects, certifications, internships,
            extracurriculars, placement_training, target_role, updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        ON CONFLICT(student_id) DO UPDATE SET
            cgpa = excluded.cgpa,
            ssc_marks = excluded.ssc_marks,
            hsc_marks = excluded.hsc_marks,
            aptitude_score = excluded.aptitude_score,
            soft_skills = excluded.soft_skills,
            projects = excluded.projects,
            certifications = excluded.certifications,
            internships = excluded.internships,
            extracurriculars = excluded.extracurriculars,
            placement_training = excluded.placement_training,
            target_role = excluded.target_role,
            updated_at = CURRENT_TIMESTAMP;
    """, (
        student_id,
        float(profile_data.get("CGPA", 0.0)),
        float(profile_data.get("SSC_Marks", 0.0)),
        float(profile_data.get("HSC_Marks", 0.0)),
        float(profile_data.get("AptitudeTestScore", 0.0)),
        float(profile_data.get("SoftSkillsRating", 1.0)),
        int(profile_data.get("Projects", 0)),
        int(profile_data.get("Workshops/Certifications", profile_data.get("Certifications", 0))),
        int(profile_data.get("Internships", 0)),
        str(profile_data.get("ExtracurricularActivities", "No")),
        str(profile_data.get("PlacementTraining", "No")),
        str(profile_data.get("target_role", "Software Developer"))
    ))

    # Also sync target_role on student table
    if "target_role" in profile_data:
        cursor.execute("UPDATE students SET target_role = ? WHERE id = ?", (profile_data["target_role"], student_id))

    conn.commit()
    conn.close()


# ---------------------------------------------------------------------------
# Assessment History & Progress Tracking
# ---------------------------------------------------------------------------

def save_assessment_snapshot(student_id: int, features: Dict[str, Any], prediction: Dict[str, Any], label: str = "Assessment Snapshot", db_path: Optional[str] = None) -> int:
    """Saves a timestamped assessment record for a student."""
    conn = get_db_connection(db_path)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO assessment_history (
            student_id, cgpa, ssc_marks, hsc_marks, aptitude_score,
            soft_skills, projects, certifications, internships,
            extracurriculars, placement_training,
            placement_probability, risk_score, risk_level, predicted_status,
            assessment_label
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        student_id,
        float(features.get("CGPA", 0.0)),
        float(features.get("SSC_Marks", 0.0)),
        float(features.get("HSC_Marks", 0.0)),
        float(features.get("AptitudeTestScore", 0.0)),
        float(features.get("SoftSkillsRating", 1.0)),
        int(features.get("Projects", 0)),
        int(features.get("Workshops/Certifications", features.get("Certifications", 0))),
        int(features.get("Internships", 0)),
        str(features.get("ExtracurricularActivities", "No")),
        str(features.get("PlacementTraining", "No")),
        float(prediction.get("placement_probability", 0.0)),
        float(prediction.get("risk_score", 1.0)),
        str(prediction.get("risk_level", "High")),
        str(prediction.get("prediction", "NotPlaced")),
        label
    ))
    record_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return record_id


def get_student_assessment_history(student_id: int, limit: int = 50, db_path: Optional[str] = None) -> List[Dict[str, Any]]:
    """Returns chronological assessment records for a student."""
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM assessment_history
        WHERE student_id = ?
        ORDER BY created_at ASC
        LIMIT ?
    """, (student_id, limit))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]


# ---------------------------------------------------------------------------
# Career Roadmap & Milestones
# ---------------------------------------------------------------------------

def set_career_goal(student_id: int, career_goal: str, db_path: Optional[str] = None) -> None:
    """Sets or updates the student's primary career goal."""
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO career_roadmaps (student_id, career_goal, updated_at)
        VALUES (?, ?, CURRENT_TIMESTAMP)
        ON CONFLICT(student_id) DO UPDATE SET
            career_goal = excluded.career_goal,
            updated_at = CURRENT_TIMESTAMP;
    """, (student_id, career_goal))

    cursor.execute("UPDATE students SET target_role = ? WHERE id = ?", (career_goal, student_id))
    cursor.execute("UPDATE student_profiles SET target_role = ? WHERE student_id = ?", (career_goal, student_id))
    conn.commit()
    conn.close()


def get_career_goal(student_id: int, db_path: Optional[str] = None) -> Optional[str]:
    """Gets the student's selected career goal."""
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT career_goal FROM career_roadmaps WHERE student_id = ?", (student_id,))
    row = cursor.fetchone()
    conn.close()
    return row["career_goal"] if row else None


def save_roadmap_milestones(student_id: int, milestones: List[Dict[str, Any]], db_path: Optional[str] = None) -> None:
    """Inserts or updates roadmap milestones without losing completed status."""
    conn = get_db_connection(db_path)
    cursor = conn.cursor()

    for m in milestones:
        cursor.execute("""
            INSERT INTO roadmap_milestones (
                student_id, milestone_key, title, category, priority, description, is_completed
            ) VALUES (?, ?, ?, ?, ?, ?, 0)
            ON CONFLICT(student_id, milestone_key) DO UPDATE SET
                title = excluded.title,
                category = excluded.category,
                priority = excluded.priority,
                description = excluded.description;
        """, (
            student_id,
            m["milestone_key"],
            m["title"],
            m.get("category", "Learning Topic"),
            m.get("priority", "Medium"),
            m.get("description", "")
        ))

    conn.commit()
    conn.close()


def toggle_milestone_completion(student_id: int, milestone_key: str, completed: bool, db_path: Optional[str] = None) -> bool:
    """Toggles milestone completion status for the student."""
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    completed_val = 1 if completed else 0
    completed_at = datetime.utcnow().isoformat() if completed else None

    cursor.execute("""
        UPDATE roadmap_milestones
        SET is_completed = ?, completed_at = ?
        WHERE student_id = ? AND milestone_key = ?
    """, (completed_val, completed_at, student_id, milestone_key))

    affected = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return affected


def get_student_milestones(student_id: int, db_path: Optional[str] = None) -> List[Dict[str, Any]]:
    """Returns all roadmap milestones for the student."""
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM roadmap_milestones
        WHERE student_id = ?
        ORDER BY
            CASE priority WHEN 'High' THEN 1 WHEN 'Medium' THEN 2 ELSE 3 END,
            id ASC
    """, (student_id,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]


# ---------------------------------------------------------------------------
# Resumes & Analysis
# ---------------------------------------------------------------------------

def save_resume_record(student_id: int, resume_data: Dict[str, Any], db_path: Optional[str] = None) -> int:
    """Saves parsed resume metadata and match analysis results."""
    conn = get_db_connection(db_path)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO resumes (
            student_id, original_filename, stored_filename, file_path, file_size_bytes,
            extracted_text_preview, detected_skills_json, target_role,
            match_percentage, matched_skills_json, missing_skills_json, suggestions_json,
            custom_jd_compared
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        student_id,
        resume_data["original_filename"],
        resume_data["stored_filename"],
        resume_data["file_path"],
        int(resume_data.get("file_size_bytes", 0)),
        resume_data.get("extracted_text_preview", ""),
        resume_data.get("detected_skills_json", "[]"),
        resume_data.get("target_role", "Software Developer"),
        float(resume_data.get("match_percentage", 0.0)),
        resume_data.get("matched_skills_json", "[]"),
        resume_data.get("missing_skills_json", "[]"),
        resume_data.get("suggestions_json", "[]"),
        1 if resume_data.get("custom_jd_compared") else 0
    ))

    resume_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return resume_id


def get_latest_resume(student_id: int, db_path: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """Retrieves the student's latest uploaded resume and analysis."""
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM resumes
        WHERE student_id = ?
        ORDER BY uploaded_at DESC
        LIMIT 1
    """, (student_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def delete_resume_record(student_id: int, resume_id: int, db_path: Optional[str] = None) -> Optional[str]:
    """Deletes resume record and returns stored file path for physical cleanup."""
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT file_path FROM resumes WHERE id = ? AND student_id = ?", (resume_id, student_id))
    row = cursor.fetchone()
    if not row:
        conn.close()
        return None

    file_path = row["file_path"]
    cursor.execute("DELETE FROM resumes WHERE id = ? AND student_id = ?", (resume_id, student_id))
    conn.commit()
    conn.close()
    return file_path


# ---------------------------------------------------------------------------
# Achievement Badges
# ---------------------------------------------------------------------------

def award_badge(student_id: int, badge_key: str, badge_title: str, description: str, icon: str = "award", db_path: Optional[str] = None) -> bool:
    """Awards a badge if not already earned."""
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT OR IGNORE INTO achievement_badges (student_id, badge_key, badge_title, description, icon)
            VALUES (?, ?, ?, ?, ?)
        """, (student_id, badge_key, badge_title, description, icon))
        awarded = cursor.rowcount > 0
        conn.commit()
        return awarded
    finally:
        conn.close()


def get_student_badges(student_id: int, db_path: Optional[str] = None) -> List[Dict[str, Any]]:
    """Returns all badges earned by the student."""
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM achievement_badges
        WHERE student_id = ?
        ORDER BY earned_at ASC
    """, (student_id,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]
