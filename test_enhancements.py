"""
Smart Placement Prediction & Career Analytics System
Integration Test Suite for Enhanced Features:
- Student Registration, Login & Logout
- Password Hashing & Security
- Student Profile Storage & Prediction History
- Progress Tracking & Timestamps
- Student Data Isolation (Student A cannot access Student B)
- Career Roadmap & Milestones
- Job Role Recommendations
- Resume Analysis & Text Extraction
- Gamification & Achievement Badges
"""

import os
import json
import tempfile
import io
from app import app
import database
import career_engine
import resume_engine
import gamification
from pypdf import PdfWriter


def run_enhancement_tests():
    print("=" * 78)
    print("RUNNING ENHANCED FEATURES INTEGRATION TEST SUITE")
    print("=" * 78)

    # Use a temporary SQLite database for clean test isolation
    temp_db_fd, temp_db_path = tempfile.mkstemp(suffix=".db")
    os.close(temp_db_fd)
    os.environ["DATABASE_PATH"] = temp_db_path
    database.init_db(temp_db_path)

    app.config["TESTING"] = True
    app.config["SECRET_KEY"] = "test-secret-key-123"
    client = app.test_client()

    passed = 0
    total = 0

    def assert_t(name, condition, details=""):
        nonlocal passed, total
        total += 1
        if condition:
            passed += 1
            print(f"  [PASS] Test {total:02d}: {name}")
        else:
            print(f"  [FAIL] Test {total:02d}: {name} -> {details}")

    try:
        # ----------------------------------------------------
        # 1. Authentication Tests
        # ----------------------------------------------------
        print("\n1. Testing Student Registration, Password Hashing & Login...")

        # Initially unauthenticated
        me_resp = client.get("/api/auth/me")
        assert_t("Unauthenticated /api/auth/me returns logged_in: False",
                 me_resp.status_code == 200 and me_resp.get_json()["logged_in"] is False)

        # Register Student 1
        reg_payload1 = {
            "full_name": "Aarav Sharma",
            "email": "aarav@college.edu",
            "password": "securepassword123",
            "target_role": "Data Scientist"
        }
        reg_res1 = client.post("/api/auth/register", json=reg_payload1)
        assert_t("Student 1 registration returns HTTP 201",
                 reg_res1.status_code == 201 and reg_res1.get_json()["status"] == "success")

        # Verify password is not stored plaintext
        st1 = database.get_student_by_email("aarav@college.edu", temp_db_path)
        assert_t("Password is not stored plaintext (hashed using Werkzeug)",
                 st1 and st1["password_hash"] != "securepassword123" and st1["password_hash"].startswith("scrypt:"))

        # Duplicate registration fails
        reg_dup = client.post("/api/auth/register", json=reg_payload1)
        assert_t("Duplicate email registration returns HTTP 409 Conflict",
                 reg_dup.status_code == 409 and reg_dup.get_json()["status"] == "fail")

        # Login with invalid password fails
        bad_login = client.post("/api/auth/login", json={"email": "aarav@college.edu", "password": "wrongpassword"})
        assert_t("Invalid credentials login returns HTTP 401",
                 bad_login.status_code == 401 and bad_login.get_json()["status"] == "fail")

        # Login with valid password succeeds
        good_login = client.post("/api/auth/login", json={"email": "aarav@college.edu", "password": "securepassword123"})
        assert_t("Valid credentials login returns HTTP 200 and student details",
                 good_login.status_code == 200 and good_login.get_json()["student"]["email"] == "aarav@college.edu")

        # Session verified
        me_auth = client.get("/api/auth/me")
        assert_t("Authenticated session returns student profile",
                 me_auth.status_code == 200 and me_auth.get_json()["logged_in"] is True)

        # Logout
        logout_res = client.post("/api/auth/logout")
        assert_t("Logout clears student session",
                 logout_res.status_code == 200 and client.get("/api/auth/me").get_json()["logged_in"] is False)

        # ----------------------------------------------------
        # 2. Authorization & Data Isolation Tests
        # ----------------------------------------------------
        print("\n2. Testing Protected Endpoints & Multi-Student Data Isolation...")

        # Accessing protected endpoint without login fails
        unauth_prof = client.get("/api/student/profile")
        assert_t("Accessing protected profile without login returns HTTP 401",
                 unauth_prof.status_code == 401)

        # Log in as Student 1
        client.post("/api/auth/login", json={"email": "aarav@college.edu", "password": "securepassword123"})

        # Save profile for Student 1
        st1_profile_data = {
            "CGPA": 8.5,
            "Internships": 2,
            "Projects": 3,
            "Workshops/Certifications": 2,
            "AptitudeTestScore": 88.0,
            "SoftSkillsRating": 4.5,
            "ExtracurricularActivities": "Yes",
            "PlacementTraining": "Yes",
            "SSC_Marks": 85.0,
            "HSC_Marks": 86.0,
            "target_role": "Data Scientist"
        }
        prof_res1 = client.post("/api/student/profile", json=st1_profile_data)
        assert_t("Student 1 can update profile and get calculated prediction",
                 prof_res1.status_code == 200 and prof_res1.get_json()["prediction"]["risk_level"] == "Low")

        # Register Student 2 with their own client
        client2 = app.test_client()
        client2.post("/api/auth/register", json={
            "full_name": "Diya Patel",
            "email": "diya@college.edu",
            "password": "password456",
            "target_role": "QA Engineer"
        })

        # Check Student 2 profile is blank / default and does not expose Student 1
        st2_prof = client2.get("/api/student/profile").get_json()
        assert_t("Data Isolation: Student 2 cannot see Student 1's private CGPA or email",
                 st2_prof["student"]["email"] == "diya@college.edu" and st2_prof["profile"]["CGPA"] == 0.0)

        # ----------------------------------------------------
        # 3. Student Progress Tracker Tests
        # ----------------------------------------------------
        print("\n3. Testing Student Progress Tracker & History...")

        # Student 1 adds assessment snapshots
        client.post("/api/student/assessment", json={
            "CGPA": 8.5,
            "Internships": 2,
            "Projects": 3,
            "Workshops/Certifications": 2,
            "AptitudeTestScore": 88.0,
            "SoftSkillsRating": 4.5,
            "ExtracurricularActivities": "Yes",
            "PlacementTraining": "Yes",
            "SSC_Marks": 85.0,
            "HSC_Marks": 86.0,
            "assessment_label": "Midterm Check"
        })

        client.post("/api/student/assessment", json={
            "CGPA": 8.7,
            "Internships": 2,
            "Projects": 4,
            "Workshops/Certifications": 3,
            "AptitudeTestScore": 92.0,
            "SoftSkillsRating": 4.8,
            "ExtracurricularActivities": "Yes",
            "PlacementTraining": "Yes",
            "SSC_Marks": 85.0,
            "HSC_Marks": 86.0,
            "assessment_label": "Pre-Placement Final"
        })

        prog_res = client.get("/api/student/progress")
        prog_data = prog_res.get_json()
        assert_t("Progress tracker returns all recorded assessment snapshots",
                 prog_res.status_code == 200 and prog_data["total_assessments"] >= 2)
        assert_t("Progress tracker identifies verified improvements between assessments",
                 len(prog_data["improvements"]) > 0)

        # ----------------------------------------------------
        # 4. Career Roadmap & Milestones Tests
        # ----------------------------------------------------
        print("\n4. Testing Career Roadmap & Milestones...")

        roadmap_res = client.get("/api/career/roadmap")
        roadmap_data = roadmap_res.get_json()
        assert_t("Roadmap returns student career goal and milestones",
                 roadmap_res.status_code == 200 and len(roadmap_data["milestones"]) > 0)

        first_milestone = roadmap_data["milestones"][0]
        m_key = first_milestone["milestone_key"]

        # Toggle milestone completion
        toggle_res = client.post("/api/career/roadmap/milestone", json={
            "milestone_key": m_key,
            "is_completed": True
        })
        assert_t("Student can mark roadmap milestone as completed",
                 toggle_res.status_code == 200 and toggle_res.get_json()["is_completed"] is True)

        updated_roadmap = client.get("/api/career/roadmap").get_json()
        assert_t("Updated roadmap reflects completion progress percentage",
                 updated_roadmap["completed_count"] >= 1 and updated_roadmap["progress_percentage"] > 0)

        # ----------------------------------------------------
        # 5. Job Role Recommendations Tests
        # ----------------------------------------------------
        print("\n5. Testing Job Role Recommendations...")

        roles_res = client.get("/api/career/roles")
        roles_data = roles_res.get_json()
        assert_t("Returns all 5 supported career roles ranked by match score",
                 roles_res.status_code == 200 and len(roles_data["roles"]) == 5)
        top_role = roles_data["roles"][0]
        assert_t("Job role recommendation includes matched, missing skills and learning topics",
                 "matched_skills" in top_role and "missing_skills" in top_role and "learning_topics" in top_role)

        # ----------------------------------------------------
        # 6. Resume Analyzer Tests
        # ----------------------------------------------------
        print("\n6. Testing Resume Analyzer & PDF Text Extraction...")

        # Create a synthetic in-memory PDF resume for testing
        writer = PdfWriter()
        page = writer.add_blank_page(width=612, height=792)
        # Note: blank PDF has 0 extracted text, let's test extraction error handling first
        pdf_bytes_empty = io.BytesIO()
        writer.write(pdf_bytes_empty)
        pdf_bytes_empty.seek(0)

        res_upload_empty = client.post(
            "/api/resume/upload",
            data={"resume": (pdf_bytes_empty, "empty_resume.pdf")},
            content_type="multipart/form-data"
        )
        assert_t("Scanned or blank PDF without text returns graceful error",
                 res_upload_empty.status_code == 400 and "No readable text" in res_upload_empty.get_json()["error"])

        # Non-pdf upload rejected
        bad_file = io.BytesIO(b"Hello world")
        res_bad_ext = client.post(
            "/api/resume/upload",
            data={"resume": (bad_file, "resume.docx")},
            content_type="multipart/form-data"
        )
        assert_t("Non-PDF file upload rejected with HTTP 400",
                 res_bad_ext.status_code == 400)

        # Direct test of skill detection engine
        sample_resume_text = """
        Aarav Sharma - Data Scientist & Software Developer
        Technical Skills: Python, Scikit-Learn, Pandas, NumPy, SQL, Flask, Git, Docker, Machine Learning, Tableau.
        Projects: Built an end-to-end placement prediction classifier with 80% accuracy and Docker containerization.
        Education: B.Tech Computer Science, CGPA 8.5.
        """
        detected = resume_engine.detect_skills_in_text(sample_resume_text)
        assert_t("Skill detector extracts genuine skills from text",
                 all(s in detected for s in ["Python", "SQL", "Pandas", "Scikit-Learn", "Git", "Docker"]))

        analysis = resume_engine.analyze_resume_text(sample_resume_text, target_role="Data Scientist")
        assert_t("Resume analysis produces match percentage and suggestions",
                 analysis["match_percentage"] > 50.0 and len(analysis["matched_skills"]) >= 5)

        # ----------------------------------------------------
        # 7. Gamification & Achievement Badges Tests
        # ----------------------------------------------------
        print("\n7. Testing Gamification & Achievement Badges...")

        badges_res = client.get("/api/student/badges")
        badges_data = badges_res.get_json()
        assert_t("Badges endpoint returns all 7 standard badges",
                 badges_res.status_code == 200 and badges_data["total_count"] == 7)

        earned_keys = [b["badge_key"] for b in badges_data["badges"] if b["is_earned"]]
        assert_t("Student 1 earned 'Aptitude Master' (Aptitude 92 >= 80)",
                 "aptitude_master" in earned_keys)
        assert_t("Student 1 earned 'Project Builder' (Projects 4 >= 3)",
                 "project_builder" in earned_keys)
        assert_t("Student 1 earned 'Skill Improver' (verified progress between snapshots)",
                 "skill_improver" in earned_keys)
        assert_t("Student 1 earned 'Placement Ready' (Prob >= 70% & Aptitude >= 75 & Projects >= 2)",
                 "placement_ready" in earned_keys)

        print("\n" + "=" * 78)
        print(f"ENHANCEMENT SUITE RESULTS: {passed}/{total} TESTS PASSED")
        print("=" * 78)

        if passed == total:
            print("[SUCCESS] All Enhanced Integration Tests Passed Perfectly!")
            return 0
        else:
            print("[FAILURE] Some enhancement tests failed.")
            return 1

    finally:
        # Clean up temporary database
        if os.path.exists(temp_db_path):
            try:
                os.remove(temp_db_path)
            except Exception:
                pass


if __name__ == "__main__":
    import sys
    sys.exit(run_enhancement_tests())
