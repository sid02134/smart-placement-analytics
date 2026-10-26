"""
Smart Placement Prediction & Career Analytics System
Flask Backend API & Web Application
"""

import os
import json
import functools
from typing import Dict, Any
from flask import Flask, request, jsonify, render_template, send_from_directory, session
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import pandas as pd

from predictor import PlacementPredictor
import database
import career_engine
import resume_engine
import gamification

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
REPORTS_DIR = os.path.join(BASE_DIR, "reports")
FIGURES_DIR = os.path.join(REPORTS_DIR, "figures")
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads", "resumes")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app = Flask(__name__, template_folder="templates", static_folder="static")

# Safe session & security configuration
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "smart-placement-analytics-secure-dev-key-change-in-prod")
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024  # 5MB upload limit
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Initialize SQLite database schema
database.init_db()

# Initialize Predictor instance reusing placement_model.joblib and model_metadata.json
try:
    predictor = PlacementPredictor()
    model_loaded = True
    init_error = None
except Exception as e:
    predictor = None
    model_loaded = False
    init_error = str(e)


# -------------------------------------------------------------------------
# Authentication Decorator & Helpers
# -------------------------------------------------------------------------

def login_required(view_func):
    """Decorator ensuring that only authenticated students access protected routes."""
    @functools.wraps(view_func)
    def wrapped_view(*args, **kwargs):
        if "student_id" not in session:
            return jsonify({
                "status": "fail",
                "error": "Authentication required. Please log in to access this resource.",
                "auth_required": True
            }), 401
        return view_func(*args, **kwargs)
    return wrapped_view


def get_current_student_id() -> int:
    return session.get("student_id")


# -------------------------------------------------------------------------
# Web Page Route
# -------------------------------------------------------------------------
@app.route("/", methods=["GET"])
def index():
    """Serves the main Smart Placement Analytics web dashboard."""
    return render_template("index.html")


# -------------------------------------------------------------------------
# Static File Routes for Analytical Reports & Figures
# -------------------------------------------------------------------------
@app.route("/reports/figures/<path:filename>")
def serve_figure(filename):
    """Serves pre-generated EDA figure images."""
    return send_from_directory(FIGURES_DIR, filename)


@app.route("/reports/<path:filename>")
def serve_report_file(filename):
    """Serves report images and artifacts."""
    return send_from_directory(REPORTS_DIR, filename)


# -------------------------------------------------------------------------
# REST API Endpoints: Health & Prediction Engine (Public)
# -------------------------------------------------------------------------
@app.route("/api/health", methods=["GET"])
def health_check():
    """Health check endpoint confirming API status and model load state."""
    if not model_loaded:
        return jsonify({
            "status": "unhealthy",
            "model_loaded": False,
            "error": init_error
        }), 500

    return jsonify({
        "status": "healthy",
        "model_loaded": True,
        "model_name": predictor.metadata.get("model_name"),
        "positive_class": predictor.metadata.get("positive_class_label", "Placed"),
        "expected_features_count": len(predictor.features),
        "expected_features": predictor.features,
        "risk_thresholds": predictor.risk_thresholds
    }), 200


@app.route("/api/predict", methods=["POST"])
def predict():
    """
    Accepts all 10 student features and returns:
    - predicted placement status ('Placed' or 'NotPlaced')
    - placement probability
    - non-placement probability
    - risk score and risk level ('Low', 'Medium', 'High')
    """
    if not model_loaded:
        return jsonify({"status": "error", "error": "Model is not loaded."}), 500

    data = request.get_json(silent=True)
    if data is None or not isinstance(data, dict):
        return jsonify({
            "status": "fail",
            "error": "Invalid request body. Expected a valid JSON object containing student features."
        }), 400

    try:
        result = predictor.predict(data)
        return jsonify({
            "status": "success",
            "prediction": result["prediction"],
            "predicted_class": result["predicted_class"],
            "placement_probability": result["placement_probability"],
            "non_placement_probability": result["non_placement_probability"],
            "placement_percentage": result["placement_percentage"],
            "risk_score": result["risk_score"],
            "risk_level": result["risk_level"],
            "features_used": result["features_used"]
        }), 200
    except ValueError as ve:
        return jsonify({
            "status": "fail",
            "error": str(ve)
        }), 400
    except Exception as e:
        return jsonify({
            "status": "error",
            "error": f"Prediction failed: {str(e)}"
        }), 500


@app.route("/api/what-if", methods=["POST"])
def what_if():
    """
    Accepts student features and returns what-if scenario simulations
    comparing baseline against incremental skill, aptitude, and experience improvements.
    """
    if not model_loaded:
        return jsonify({"status": "error", "error": "Model is not loaded."}), 500

    data = request.get_json(silent=True)
    if data is None or not isinstance(data, dict):
        return jsonify({
            "status": "fail",
            "error": "Invalid request body. Expected a valid JSON object containing student features."
        }), 400

    try:
        scenarios = predictor.simulate_what_if_scenarios(data)
        return jsonify({
            "status": "success",
            "total_scenarios": len(scenarios),
            "scenarios": scenarios
        }), 200
    except ValueError as ve:
        return jsonify({
            "status": "fail",
            "error": str(ve)
        }), 400
    except Exception as e:
        return jsonify({
            "status": "error",
            "error": f"What-if simulation failed: {str(e)}"
        }), 500


@app.route("/api/recommendations", methods=["POST"])
def recommendations():
    """
    Accepts student features and returns tailored, prioritized career improvement
    recommendations benchmarked against successfully placed students.
    """
    if not model_loaded:
        return jsonify({"status": "error", "error": "Model is not loaded."}), 500

    data = request.get_json(silent=True)
    if data is None or not isinstance(data, dict):
        return jsonify({
            "status": "fail",
            "error": "Invalid request body. Expected a valid JSON object containing student features."
        }), 400

    try:
        recs = predictor.generate_career_recommendations(data)
        return jsonify({
            "status": "success",
            "total_recommendations": len(recs),
            "recommendations": recs
        }), 200
    except ValueError as ve:
        return jsonify({
            "status": "fail",
            "error": str(ve)
        }), 400
    except Exception as e:
        return jsonify({
            "status": "error",
            "error": f"Recommendation generation failed: {str(e)}"
        }), 500


@app.route("/api/analytics-data", methods=["GET"])
def analytics_data():
    """Loads and serves analytical data directly from existing project reports."""
    try:
        data_payload = {}

        # 1. EDA Summary
        eda_path = os.path.join(REPORTS_DIR, "phase1_eda_summary.json")
        if os.path.exists(eda_path):
            with open(eda_path, "r", encoding="utf-8") as f:
                data_payload["eda_summary"] = json.load(f)

        # 2. All Models Validation
        all_models_path = os.path.join(REPORTS_DIR, "all_models_validation.csv")
        if os.path.exists(all_models_path):
            df_models = pd.read_csv(all_models_path)
            data_payload["model_comparisons"] = df_models.to_dict(orient="records")

        # 3. Tuned Models
        tuned_path = os.path.join(REPORTS_DIR, "tuned_models_validation.csv")
        if os.path.exists(tuned_path):
            df_tuned = pd.read_csv(tuned_path)
            data_payload["tuned_models"] = df_tuned.to_dict(orient="records")

        # 4. SHAP Feature Importance
        shap_path = os.path.join(REPORTS_DIR, "shap_feature_importance.csv")
        if os.path.exists(shap_path):
            df_shap = pd.read_csv(shap_path)
            data_payload["shap_importance"] = df_shap.to_dict(orient="records")

        # 5. Placement Feature Comparison
        comp_path = os.path.join(REPORTS_DIR, "placement_comparison.csv")
        if os.path.exists(comp_path):
            df_comp = pd.read_csv(comp_path)
            data_payload["placement_comparison"] = df_comp.to_dict(orient="records")

        # 6. Placement Risk Distribution
        risk_path = os.path.join(REPORTS_DIR, "placement_risk_summary.csv")
        if os.path.exists(risk_path):
            df_risk = pd.read_csv(risk_path)
            data_payload["risk_summary"] = df_risk.to_dict(orient="records")

        # 7. Cross Validation Results
        cv_path = os.path.join(REPORTS_DIR, "cross_validation_results.csv")
        if os.path.exists(cv_path):
            df_cv = pd.read_csv(cv_path)
            data_payload["cross_validation"] = df_cv.to_dict(orient="records")

        return jsonify({
            "status": "success",
            "data": data_payload
        }), 200
    except Exception as e:
        return jsonify({
            "status": "error",
            "error": f"Failed to load analytics data: {str(e)}"
        }), 500


@app.route("/api/sample-profiles", methods=["GET"])
def sample_profiles():
    """Returns verified student test profiles for 1-click loading."""
    profiles = {
        "at_risk": {
            "name": "High Risk Profile (Row 1 of Test Set)",
            "data": {
                "CGPA": 7.7,
                "Internships": 1,
                "Projects": 1,
                "Workshops/Certifications": 0,
                "AptitudeTestScore": 69.0,
                "SoftSkillsRating": 4.0,
                "ExtracurricularActivities": "No",
                "PlacementTraining": "No",
                "SSC_Marks": 55.0,
                "HSC_Marks": 69.0
            }
        },
        "placed": {
            "name": "Strong Placement Profile (Row 2 of Test Set)",
            "data": {
                "CGPA": 7.9,
                "Internships": 1,
                "Projects": 3,
                "Workshops/Certifications": 2,
                "AptitudeTestScore": 90.0,
                "SoftSkillsRating": 4.8,
                "ExtracurricularActivities": "Yes",
                "PlacementTraining": "Yes",
                "SSC_Marks": 82.0,
                "HSC_Marks": 80.0
            }
        },
        "borderline": {
            "name": "Moderate / Borderline Profile (Row 22 of Test Set)",
            "data": {
                "CGPA": 7.8,
                "Internships": 0,
                "Projects": 2,
                "Workshops/Certifications": 0,
                "AptitudeTestScore": 79.0,
                "SoftSkillsRating": 4.5,
                "ExtracurricularActivities": "Yes",
                "PlacementTraining": "No",
                "SSC_Marks": 80.0,
                "HSC_Marks": 81.0
            }
        }
    }
    return jsonify({"status": "success", "profiles": profiles}), 200


# -------------------------------------------------------------------------
# Authentication Routes (Registration, Login, Logout, Status)
# -------------------------------------------------------------------------

@app.route("/api/auth/register", methods=["POST"])
def register():
    """Registers a new student with unique email and securely hashed password."""
    data = request.get_json(silent=True) or {}
    email = str(data.get("email", "")).strip().lower()
    password = str(data.get("password", "")).strip()
    full_name = str(data.get("full_name", "")).strip()
    target_role = str(data.get("target_role", "Software Developer")).strip()

    if not full_name:
        return jsonify({"status": "fail", "error": "Full name is required."}), 400
    if not email or "@" not in email or "." not in email:
        return jsonify({"status": "fail", "error": "A valid email address is required."}), 400
    if len(password) < 6:
        return jsonify({"status": "fail", "error": "Password must be at least 6 characters long."}), 400

    existing = database.get_student_by_email(email)
    if existing:
        return jsonify({"status": "fail", "error": "An account with this email already exists."}), 409

    pwd_hash = generate_password_hash(password)
    student_id = database.create_student(email, pwd_hash, full_name, target_role)

    # Establish secure session
    session.clear()
    session["student_id"] = student_id
    session["student_name"] = full_name
    session["student_email"] = email

    return jsonify({
        "status": "success",
        "message": "Registration successful.",
        "student": {
            "id": student_id,
            "full_name": full_name,
            "email": email,
            "target_role": target_role
        }
    }), 201


@app.route("/api/auth/login", methods=["POST"])
def login():
    """Authenticates student credentials and establishes a session."""
    data = request.get_json(silent=True) or {}
    email = str(data.get("email", "")).strip().lower()
    password = str(data.get("password", "")).strip()

    if not email or not password:
        return jsonify({"status": "fail", "error": "Email and password are required."}), 400

    student = database.get_student_by_email(email)
    if not student or not check_password_hash(student["password_hash"], password):
        return jsonify({"status": "fail", "error": "Invalid email or password."}), 401

    database.update_student_last_login(student["id"])

    session.clear()
    session["student_id"] = student["id"]
    session["student_name"] = student["full_name"]
    session["student_email"] = student["email"]

    return jsonify({
        "status": "success",
        "message": "Login successful.",
        "student": {
            "id": student["id"],
            "full_name": student["full_name"],
            "email": student["email"],
            "target_role": student.get("target_role", "Software Developer")
        }
    }), 200


@app.route("/api/auth/logout", methods=["POST"])
def logout():
    """Clears authenticated session."""
    session.clear()
    return jsonify({"status": "success", "message": "Successfully logged out."}), 200


@app.route("/api/auth/me", methods=["GET"])
def get_current_user():
    """Returns current student authentication status and session details."""
    student_id = get_current_student_id()
    if not student_id:
        return jsonify({"status": "success", "logged_in": False, "student": None}), 200

    student = database.get_student_by_id(student_id)
    if not student:
        session.clear()
        return jsonify({"status": "success", "logged_in": False, "student": None}), 200

    return jsonify({
        "status": "success",
        "logged_in": True,
        "student": {
            "id": student["id"],
            "full_name": student["full_name"],
            "email": student["email"],
            "target_role": student.get("target_role", "Software Developer"),
            "created_at": student.get("created_at")
        }
    }), 200


# -------------------------------------------------------------------------
# Student Dashboard & Profile Routes (Authenticated)
# -------------------------------------------------------------------------

@app.route("/api/student/profile", methods=["GET"])
@login_required
def get_profile():
    """Returns the authenticated student's profile, academic stats, and prediction."""
    student_id = get_current_student_id()
    student = database.get_student_by_id(student_id)
    profile = database.get_student_profile(student_id) or {}
    history = database.get_student_assessment_history(student_id, limit=5)
    resume = database.get_latest_resume(student_id)

    # Format profile data into prediction format
    profile_inputs = {
        "CGPA": profile.get("cgpa", 0.0),
        "SSC_Marks": profile.get("ssc_marks", 0.0),
        "HSC_Marks": profile.get("hsc_marks", 0.0),
        "AptitudeTestScore": profile.get("aptitude_score", 0.0),
        "SoftSkillsRating": profile.get("soft_skills", 1.0),
        "Projects": profile.get("projects", 0),
        "Workshops/Certifications": profile.get("certifications", 0),
        "Internships": profile.get("internships", 0),
        "ExtracurricularActivities": profile.get("extracurriculars", "No"),
        "PlacementTraining": profile.get("placement_training", "No"),
        "target_role": profile.get("target_role", student.get("target_role", "Software Developer"))
    }

    # If profile has valid values, compute active prediction
    current_prediction = None
    if profile.get("cgpa", 0.0) > 0:
        try:
            current_prediction = predictor.predict(profile_inputs)
        except Exception:
            current_prediction = None

    return jsonify({
        "status": "success",
        "student": {
            "id": student["id"],
            "full_name": student["full_name"],
            "email": student["email"]
        },
        "profile": profile_inputs,
        "prediction": current_prediction,
        "has_history": len(history) > 0,
        "has_resume": resume is not None
    }), 200


@app.route("/api/student/profile", methods=["POST"])
@login_required
def save_profile():
    """Updates the student's profile and optionally records an assessment snapshot."""
    student_id = get_current_student_id()
    data = request.get_json(silent=True) or {}

    try:
        # Validate inputs via predictor validation logic
        prepared_df = predictor.validate_and_prepare_input(data)
        clean_inputs = prepared_df.iloc[0].to_dict()
        if "target_role" in data:
            clean_inputs["target_role"] = data["target_role"]

        # Run model prediction
        pred_result = predictor.predict(clean_inputs)

        # Update profile table
        database.upsert_student_profile(student_id, clean_inputs)

        # If user explicitly requested saving as a snapshot
        save_snapshot = data.get("save_snapshot", True)
        if save_snapshot:
            label = data.get("assessment_label", "Self Assessment")
            database.save_assessment_snapshot(student_id, clean_inputs, pred_result, label)

        # Trigger badge evaluation
        gamification.evaluate_and_award_badges(student_id)

        return jsonify({
            "status": "success",
            "message": "Student profile updated successfully.",
            "profile": clean_inputs,
            "prediction": pred_result
        }), 200
    except ValueError as ve:
        return jsonify({"status": "fail", "error": str(ve)}), 400
    except Exception as e:
        return jsonify({"status": "error", "error": f"Failed to save profile: {str(e)}"}), 500


# -------------------------------------------------------------------------
# Student Progress Tracker Routes (Authenticated)
# -------------------------------------------------------------------------

@app.route("/api/student/progress", methods=["GET"])
@login_required
def get_progress():
    """Returns the student's chronological assessment history for progress graphs."""
    student_id = get_current_student_id()
    history = database.get_student_assessment_history(student_id, limit=50)

    # Calculate metric changes if at least two assessments exist
    improvements = []
    needs_attention = []
    if len(history) >= 2:
        prev = history[-2]
        curr = history[-1]

        # Probability change
        prob_diff = round((curr["placement_probability"] - prev["placement_probability"]) * 100, 2)
        if prob_diff > 0:
            improvements.append(f"Placement Probability increased by +{prob_diff} pp (from {prev['placement_probability']*100:.1f}% to {curr['placement_probability']*100:.1f}%).")
        elif prob_diff < 0:
            needs_attention.append(f"Placement Probability dipped by {prob_diff} pp.")

        # Aptitude change
        apt_diff = round(curr["aptitude_score"] - prev["aptitude_score"], 1)
        if apt_diff > 0:
            improvements.append(f"Aptitude score improved by +{apt_diff} pts.")
        elif apt_diff < 0:
            needs_attention.append(f"Aptitude score decreased by {apt_diff} pts.")

        # Projects change
        proj_diff = curr["projects"] - prev["projects"]
        if proj_diff > 0:
            improvements.append(f"Added {proj_diff} new completed project(s).")

        # Soft skills change
        soft_diff = round(curr["soft_skills"] - prev["soft_skills"], 1)
        if soft_diff > 0:
            improvements.append(f"Soft skills rating elevated by +{soft_diff}.")

    return jsonify({
        "status": "success",
        "total_assessments": len(history),
        "history": history,
        "improvements": improvements,
        "needs_attention": needs_attention,
        "disclaimer": "Progress metrics and probability trends represent model simulations and do not guarantee actual placement offers."
    }), 200


@app.route("/api/student/assessment", methods=["POST"])
@login_required
def record_assessment():
    """Explicitly records an assessment point in the student's timeline."""
    student_id = get_current_student_id()
    data = request.get_json(silent=True) or {}

    try:
        prepared_df = predictor.validate_and_prepare_input(data)
        clean_inputs = prepared_df.iloc[0].to_dict()
        pred_result = predictor.predict(clean_inputs)
        label = data.get("assessment_label", "Timed Assessment")

        record_id = database.save_assessment_snapshot(student_id, clean_inputs, pred_result, label)
        gamification.evaluate_and_award_badges(student_id)

        return jsonify({
            "status": "success",
            "message": "Assessment snapshot recorded.",
            "record_id": record_id,
            "prediction": pred_result
        }), 201
    except ValueError as ve:
        return jsonify({"status": "fail", "error": str(ve)}), 400
    except Exception as e:
        return jsonify({"status": "error", "error": f"Failed to record assessment: {str(e)}"}), 500


# -------------------------------------------------------------------------
# Career Roadmap & Job Role Recommendation Routes
# -------------------------------------------------------------------------

@app.route("/api/career/roles", methods=["GET"])
def get_job_roles():
    """
    Evaluates student profile and detected resume skills against supported roles.
    Works for logged in students or provides transparent benchmarks for guests.
    """
    student_id = get_current_student_id()
    profile_data = {}
    resume_skills = []

    if student_id:
        profile = database.get_student_profile(student_id)
        if profile:
            profile_data = profile
        resume = database.get_latest_resume(student_id)
        if resume and resume.get("detected_skills_json"):
            try:
                resume_skills = json.loads(resume["detected_skills_json"])
            except Exception:
                resume_skills = []

    roles = career_engine.evaluate_job_roles(profile_data, resume_skills)
    return jsonify({
        "status": "success",
        "roles": roles,
        "disclaimer": "Job role recommendations and match percentages are educational heuristics and not actual job offers."
    }), 200


@app.route("/api/career/roadmap", methods=["GET"])
@login_required
def get_roadmap():
    """Retrieves student's active career roadmap and milestone checklist."""
    student_id = get_current_student_id()
    goal = database.get_career_goal(student_id) or "Software Developer"
    profile = database.get_student_profile(student_id) or {}

    resume = database.get_latest_resume(student_id)
    resume_skills = []
    if resume and resume.get("detected_skills_json"):
        try:
            resume_skills = json.loads(resume["detected_skills_json"])
        except Exception:
            resume_skills = []

    roadmap_data = career_engine.generate_roadmap(goal, profile, resume_skills)

    # Sync generated milestones to DB if not already present
    database.save_roadmap_milestones(student_id, roadmap_data["milestones"])

    # Load saved milestones from DB with completion state
    saved_milestones = database.get_student_milestones(student_id)

    completed_count = sum(1 for m in saved_milestones if m.get("is_completed"))
    total_count = len(saved_milestones)
    progress_pct = round((completed_count / total_count * 100), 1) if total_count > 0 else 0.0

    return jsonify({
        "status": "success",
        "career_goal": goal,
        "role_details": roadmap_data["role_details"],
        "milestones": saved_milestones,
        "completed_count": completed_count,
        "total_count": total_count,
        "progress_percentage": progress_pct,
        "disclaimer": roadmap_data["disclaimer"]
    }), 200


@app.route("/api/career/roadmap/select", methods=["POST"])
@login_required
def select_career_goal():
    """Selects target career goal and generates initial milestones."""
    student_id = get_current_student_id()
    data = request.get_json(silent=True) or {}
    goal = data.get("career_goal", "Software Developer")

    if goal not in career_engine.JOB_ROLES:
        return jsonify({
            "status": "fail",
            "error": f"Invalid career goal. Supported goals: {', '.join(career_engine.JOB_ROLES.keys())}"
        }), 400

    database.set_career_goal(student_id, goal)

    profile = database.get_student_profile(student_id) or {}
    resume = database.get_latest_resume(student_id)
    resume_skills = []
    if resume and resume.get("detected_skills_json"):
        try:
            resume_skills = json.loads(resume["detected_skills_json"])
        except Exception:
            resume_skills = []

    roadmap_data = career_engine.generate_roadmap(goal, profile, resume_skills)
    database.save_roadmap_milestones(student_id, roadmap_data["milestones"])

    return jsonify({
        "status": "success",
        "message": f"Career goal updated to {goal}.",
        "career_goal": goal
    }), 200


@app.route("/api/career/roadmap/milestone", methods=["POST"])
@login_required
def toggle_milestone():
    """Marks a milestone completed or incomplete."""
    student_id = get_current_student_id()
    data = request.get_json(silent=True) or {}
    milestone_key = data.get("milestone_key")
    completed = bool(data.get("is_completed", True))

    if not milestone_key:
        return jsonify({"status": "fail", "error": "milestone_key is required."}), 400

    success = database.toggle_milestone_completion(student_id, milestone_key, completed)
    if not success:
        return jsonify({"status": "fail", "error": "Milestone not found."}), 404

    # Award career architect badge if eligible
    gamification.evaluate_and_award_badges(student_id)

    return jsonify({
        "status": "success",
        "milestone_key": milestone_key,
        "is_completed": completed
    }), 200


# -------------------------------------------------------------------------
# Resume Analyzer Routes (Authenticated)
# -------------------------------------------------------------------------

@app.route("/api/resume/upload", methods=["POST"])
@login_required
def upload_resume():
    """
    Accepts PDF resume upload, validates format and size, extracts text,
    detects technical skills, and matches against target role / custom JD.
    """
    student_id = get_current_student_id()

    if "resume" not in request.files:
        return jsonify({"status": "fail", "error": "No resume file provided in form-data."}), 400

    file = request.files["resume"]
    if not file or file.filename == "":
        return jsonify({"status": "fail", "error": "No file selected."}), 400

    original_name = file.filename
    if not original_name.lower().endswith(".pdf"):
        return jsonify({"status": "fail", "error": "Only PDF files (.pdf) are supported."}), 400

    # Read content to check size safely
    file_bytes = file.read()
    if len(file_bytes) > 5 * 1024 * 1024:
        return jsonify({"status": "fail", "error": "File size exceeds 5MB limit."}), 400

    # Generate safe isolated filename
    safe_base = secure_filename(original_name)
    stored_name = f"student_{student_id}_{int(os.times()[4])}_{safe_base}"
    file_path = os.path.join(app.config["UPLOAD_FOLDER"], stored_name)

    with open(file_path, "wb") as f:
        f.write(file_bytes)

    # Extract text using pypdf
    extracted_text, extract_err = resume_engine.extract_text_from_pdf(file_path)
    if extract_err:
        # Clean up file on failure
        try:
            os.remove(file_path)
        except Exception:
            pass
        return jsonify({"status": "fail", "error": extract_err}), 400

    target_role = request.form.get("target_role", "Software Developer")
    custom_jd = request.form.get("job_description", "")

    analysis = resume_engine.analyze_resume_text(
        resume_text=extracted_text,
        target_role=target_role,
        custom_jd_text=custom_jd
    )

    resume_record = {
        "original_filename": original_name,
        "stored_filename": stored_name,
        "file_path": file_path,
        "file_size_bytes": len(file_bytes),
        "extracted_text_preview": extracted_text[:1000],
        "detected_skills_json": json.dumps(analysis["detected_skills"]),
        "target_role": target_role,
        "match_percentage": analysis["match_percentage"],
        "matched_skills_json": json.dumps(analysis["matched_skills"]),
        "missing_skills_json": json.dumps(analysis["missing_skills"]),
        "suggestions_json": json.dumps(analysis["suggestions"]),
        "custom_jd_compared": analysis["custom_jd_compared"]
    }

    resume_id = database.save_resume_record(student_id, resume_record)
    gamification.evaluate_and_award_badges(student_id)

    return jsonify({
        "status": "success",
        "message": "Resume uploaded and analyzed successfully.",
        "resume_id": resume_id,
        "analysis": analysis
    }), 201


@app.route("/api/resume/latest", methods=["GET"])
@login_required
def get_latest_resume_analysis():
    """Retrieves the student's most recently analyzed resume."""
    student_id = get_current_student_id()
    resume = database.get_latest_resume(student_id)
    if not resume:
        return jsonify({
            "status": "success",
            "has_resume": False,
            "message": "No resume uploaded yet."
        }), 200

    return jsonify({
        "status": "success",
        "has_resume": True,
        "resume": {
            "id": resume["id"],
            "original_filename": resume["original_filename"],
            "uploaded_at": resume["uploaded_at"],
            "target_role": resume["target_role"],
            "match_percentage": resume["match_percentage"],
            "detected_skills": json.loads(resume.get("detected_skills_json") or "[]"),
            "matched_skills": json.loads(resume.get("matched_skills_json") or "[]"),
            "missing_skills": json.loads(resume.get("missing_skills_json") or "[]"),
            "suggestions": json.loads(resume.get("suggestions_json") or "[]"),
            "custom_jd_compared": bool(resume.get("custom_jd_compared"))
        }
    }), 200


@app.route("/api/resume/<int:resume_id>", methods=["DELETE"])
@login_required
def delete_resume(resume_id: int):
    """Securely deletes an uploaded resume and removes its analysis."""
    student_id = get_current_student_id()
    file_path = database.delete_resume_record(student_id, resume_id)
    if not file_path:
        return jsonify({"status": "fail", "error": "Resume record not found."}), 404

    # Remove physical file if it exists
    if os.path.exists(file_path):
        try:
            os.remove(file_path)
        except Exception:
            pass

    return jsonify({"status": "success", "message": "Resume deleted successfully."}), 200


# -------------------------------------------------------------------------
# Achievement Badges Route (Authenticated)
# -------------------------------------------------------------------------

@app.route("/api/student/badges", methods=["GET"])
@login_required
def get_badges():
    """Returns all gamification achievement badges with earned status and progress."""
    student_id = get_current_student_id()
    badges = gamification.evaluate_and_award_badges(student_id)
    earned_count = sum(1 for b in badges if b.get("is_earned"))
    total_count = len(badges)

    return jsonify({
        "status": "success",
        "earned_count": earned_count,
        "total_count": total_count,
        "badges": badges,
        "disclaimer": "Achievement badges celebrate academic and preparation milestones and do not guarantee corporate recruitment outcomes."
    }), 200


# -------------------------------------------------------------------------
# Global Error Handlers
# -------------------------------------------------------------------------

@app.errorhandler(404)
def not_found(e):
    if request.path.startswith("/api/"):
        return jsonify({"status": "fail", "error": "Resource or endpoint not found."}), 404
    return render_template("index.html"), 200


@app.errorhandler(405)
def method_not_allowed(e):
    return jsonify({"status": "fail", "error": "HTTP method not allowed for this endpoint."}), 405


@app.errorhandler(500)
def server_error(e):
    return jsonify({"status": "error", "error": "Internal server error."}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"Starting SmartPlacementAnalytics API on http://127.0.0.1:{port}")
    app.run(host="127.0.0.1", port=port, debug=False)
