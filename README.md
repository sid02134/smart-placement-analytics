# Smart Placement Prediction & Career Analytics System

> **College Data Science Capstone Project (Semester 5)**  
> An interpretable machine learning, student progress tracking, and career analytics platform for placement forecasting, risk stratification, what-if scenario simulation, resume benchmarking, and personalized career roadmaps.

---

## 1. Project Overview

The **Smart Placement Prediction & Career Analytics System** is an end-to-end data science and full-stack machine learning web application built upon historical student performance data (**9,928 student records**).

Beyond standalone binary placement prediction, the system provides:
1. **Calibrated Placement Forecasting**: Exact probability scoring for placement and non-placement using a tuned Logistic Regression pipeline.
2. **Three-Tier Placement Risk Stratification**: Automated risk assignment into Low ($\le 0.30$), Medium ($0.30 - 0.60$), and High ($> 0.60$) risk tiers.
3. **Real-Time What-If Intervention Studio**: Interactive simulation of isolated skill, experience, and training improvements to quantify expected percentage-point gains ($\Delta$ pp).
4. **Prescriptive Career Recommendations**: Actionable guidance prioritized by impact and benchmarked against placed alumni profiles.
5. **Personalized Student Dashboard & Profile**: Secure student accounts, academic records, and recent predictions with full data isolation.
6. **Student Progress Tracker**: Persistent timeline of assessments with Chart.js visualization, tracking changes in CGPA, Aptitude, Projects, and predicted probability.
7. **Personalized Career Roadmap**: Structured milestones for 5 tech career tracks with interactive progress tracking.
8. **Job Role Recommendation Engine**: Multi-role alignment matching student competencies against Data Analyst, Data Scientist, Software Developer, Business Analyst, and QA Engineer profiles.
9. **Resume Analyzer**: PDF text extraction, transparent skill dictionary detection, target role / custom JD gap analysis, and ATS estimate disclaimer.
10. **Gamification & Achievement Badges**: 7 achievement badges celebrating academic rigor, portfolio building, and placement readiness.
11. **Modern Dark Theme Single-Page Navigation**: Polished top navigation bar with clean section switching without long vertical scrolling.

---

## 2. Technology Stack

| Domain | Technology / Library | Version / Details | Purpose |
| :--- | :--- | :--- | :--- |
| **Backend Framework** | Flask | `>= 3.0.0` | REST API routing, session management, template rendering |
| **Language & Runtime** | Python | `3.13` (Windows x64) | Core application execution environment |
| **Machine Learning** | scikit-learn | `== 1.6.1` *(strictly preserved)* | Pipeline preprocessing, ColumnTransformer, Logistic Regression |
| **Model Serialization** | Joblib | `>= 1.4.0` | Loading trained pipeline artifact (`models/placement_model.joblib`) |
| **Data Manipulation** | Pandas & NumPy | `>= 2.2.0`, `>= 2.0.0` | Dataset processing, matrix transformations, benchmarks |
| **Database & Persistence** | SQLite | Python `sqlite3` | Relational persistence, foreign keys, student data isolation |
| **Security & Passwords** | Werkzeug | Built-in | Password hashing (`generate_password_hash` / `check_password_hash`) |
| **PDF Extraction** | pypdf | `>= 5.0.0` | Safe PDF text extraction for resume parsing |
| **Frontend Structure** | HTML5 & Jinja2 | Native Flask Templates | Semantic structure, accessible forms, modal dialogs |
| **Frontend Styling** | Vanilla CSS3 | Custom Design System | Dark glassmorphism, responsive grid/flexbox, CSS variables |
| **Frontend Logic** | Vanilla JavaScript | ES6+ (Fetch API, DOM) | Section routing, asynchronous API calls, stale-state management |
| **Data Visualizations** | Chart.js | `4.4.7` (via CDN) | What-If bar chart, Progress timeline, Model benchmarks, SHAP |

---

## 3. Navigation & Section Structure

The web dashboard implements a modern top navigation bar with single-section switching:

```
[Overview]  [Predictor]  [What-If Lab]  [Career Guidance]  [My Progress]  [Resume Analyzer]  ---  [Login / Sign Up]
```

- **Overview**: Project introduction, statistics, dataset summary, 4 alumni KPI benchmark cards, and exploration links.
- **Predictor**: 10-feature input form, profile presets (*High-Risk*, *Placed*, *Borderline*, *Clear*), probability gauge, and risk card.
- **What-If Lab**: Actionable intervention studio with scenario cards and probability comparison bar chart.
- **Career Guidance**: Tabbed hub containing:
  - *Prescriptive Actions*: Alumni-benchmarked prioritized recommendations.
  - *Job Role Recommendations*: Skill alignment scores across 5 industry roles.
  - *Personalized Roadmap*: Goal selection and milestone checklist with completion toggles.
- **My Progress**: Authenticated student dashboard, academic profile, progress charts over time, diagnostic velocity, and achievement badges.
- **Resume Analyzer**: Drag-and-drop PDF resume upload, skill cloud, role/JD gap analysis, and recommendations.
- **Login / Sign Up**: Secure modal dialog for student registration and login. Updates navbar with student name and logout button.

*Note:* Model Benchmarks, SHAP & Risk, and EDA Gallery have been removed from the primary top navigation as requested, but are preserved in the codebase and can be explored from the Overview section.

---

## 4. Enhanced Features

### Feature 1: Student Dashboard & Profile
- Student registration and login with unique email validation.
- Passwords securely hashed using standard scrypt key derivation.
- Student profile stores CGPA, SSC/HSC marks, Aptitude, Soft Skills, Projects, Certifications, Internships, Extracurriculars, and Training.
- Strict multi-student data isolation: Student A cannot view or modify Student B's private profile or records.

### Feature 2: Student Progress Tracker
- Chronological snapshots saved in SQLite with timestamps.
- Interactive Chart.js timeline showing trajectory of Placement Probability and Aptitude test score across time.
- Automated progress diagnostics highlighting verified improvements and focus priorities.

### Feature 3: Personalized Career Roadmap
- Tailored roadmaps for:
  - **Data Analyst**
  - **Data Scientist**
  - **Software Developer**
  - **Business Analyst**
  - **QA Engineer**
- Generates structured milestones across Core Knowledge, Hands-On Projects, Architecture, and Placement Readiness.
- Students can check off completed milestones with persistent progress saving.

### Feature 4: Resume Analyzer
- Accepts PDF resumes (up to 5MB) with server-side validation.
- Extracts plain text using `pypdf` with graceful error handling for scanned/blank PDFs.
- Matches keywords against a transparent 70+ technical skill dictionary.
- Compares resume competencies against selected target role and optional custom Job Description.
- Provides matched skills, missing skills, and improvement suggestions.
- Secure deletion endpoint for uploaded files and records.
- *Transparent Disclaimer*: Clarifies that keyword analysis is an educational estimate, not an industry ATS score.

### Feature 5: Job Role Recommendation
- Evaluates student academic metrics, aptitude, and resume competencies across 5 target roles.
- Calculates transparent match percentages (weighted 70% required skills, 15% recommended skills, 15% academic benchmarks).
- Displays matched competencies, potential skill gaps, recommended projects, and study topics.

### Feature 6: Gamification & Achievement Badges
Evaluates student records against clear criteria and awards badges:
1. **Aptitude Master**: Aptitude score $\ge 80.0$.
2. **Project Builder**: $\ge 3$ completed technical projects.
3. **Skill Improver**: Verified positive improvement in CGPA, Aptitude, or Probability across snapshots.
4. **Placement Ready**: Low Risk ($P \ge 70.0\%$) with Aptitude $\ge 75.0$ and Projects $\ge 2$.
5. **Resume Verified**: Uploaded and analyzed a valid technical resume.
6. **Career Architect**: Selected a roadmap track and completed at least 1 milestone.
7. **Holistic Achiever**: Soft Skills $\ge 4.0$, active Extracurriculars, and campus Placement Training enrolled.

---

## 5. Machine Learning System (Preserved)

The original machine learning pipeline and metadata have been preserved completely intact:
- Artifact: `models/placement_model.joblib`
- Metadata: `models/model_metadata.json`
- Engine: `predictor.py`
- Version: `scikit-learn==1.6.1`

### Input Features (10)
1. `CGPA` (0.0 – 10.0)
2. `Internships` ($\ge 0$)
3. `Projects` ($\ge 0$)
4. `Workshops/Certifications` ($\ge 0$)
5. `AptitudeTestScore` (0.0 – 100.0)
6. `SoftSkillsRating` (1.0 – 5.0)
7. `ExtracurricularActivities` (`Yes` / `No`)
8. `PlacementTraining` (`Yes` / `No`)
9. `SSC_Marks` (0.0 – 100.0)
10. `HSC_Marks` (0.0 – 100.0)

### Risk Classification Thresholds
- **Low Risk**: Risk score $\le 0.30$ (Placement Probability $\ge 70.0\%$)
- **Medium Risk**: $0.30 < \text{Risk score} \le 0.60$ (Placement Probability $40.0\% - 70.0\%$)
- **High Risk**: Risk score $> 0.60$ (Placement Probability $< 40.0\%$)

---

## 6. Database Schema & Privacy

SQLite database is located at `instance/smart_placement.db` (or configurable via `DATABASE_PATH` environment variable).

### Tables
1. `students`: `id`, `email`, `password_hash`, `full_name`, `target_role`, `created_at`, `last_login`
2. `student_profiles`: `id`, `student_id`, `cgpa`, `ssc_marks`, `hsc_marks`, `aptitude_score`, `soft_skills`, `projects`, `certifications`, `internships`, `extracurriculars`, `placement_training`, `target_role`, `updated_at`
3. `assessment_history`: `id`, `student_id`, `cgpa`, `aptitude_score`, ..., `placement_probability`, `risk_score`, `risk_level`, `predicted_status`, `assessment_label`, `created_at`
4. `career_roadmaps`: `id`, `student_id`, `career_goal`, `updated_at`
5. `roadmap_milestones`: `id`, `student_id`, `milestone_key`, `title`, `category`, `priority`, `is_completed`, `completed_at`
6. `resumes`: `id`, `student_id`, `original_filename`, `stored_filename`, `file_path`, `detected_skills_json`, `match_percentage`, `matched_skills_json`, `missing_skills_json`, `suggestions_json`
7. `achievement_badges`: `id`, `student_id`, `badge_key`, `badge_title`, `description`, `icon`, `earned_at`

### Privacy & Data Isolation
- Foreign keys with `ON DELETE CASCADE` enabled.
- All student-specific endpoints require authentication and scope queries strictly to `session["student_id"]`.
- Passwords are never stored in plaintext.
- Uploaded resumes are isolated in `uploads/resumes/` and excluded from git tracking.
- `.gitignore` excludes `*.db`, `instance/`, `uploads/`, and `.env`.

---

## 7. Windows Setup & Execution Guide

### Step 1: Open PowerShell in Project Directory
```powershell
cd "D:\ds cp sem 5\SmartPlacementAnalytics"
```

### Step 2: Activate the Virtual Environment
```powershell
.\.venv\Scripts\activate
```

### Step 3: Install Required Dependencies
```powershell
pip install -r requirements.txt
```

### Step 4: Run the Complete Test Suites
Run both the original regression test suite and the new enhancement test suite:

```powershell
# 1. Run original 57-test regression suite
.venv\Scripts\python.exe test_api.py

# 2. Run 27-test enhancement integration suite
.venv\Scripts\python.exe test_enhancements.py
```
*Expected Result:*
- `test_api.py`: **57/57 TESTS PASSED**
- `test_enhancements.py`: **27/27 TESTS PASSED**
- Total: **84/84 tests passing (100%)**

### Step 5: Start the Web Application
```powershell
.venv\Scripts\python.exe app.py
```

### Step 6: Access Dashboard
Open your browser and navigate to:
```
http://127.0.0.1:5000/
```

---

## 8. REST API Endpoint Reference

| Method | Endpoint | Auth Required | Description |
| :--- | :--- | :---: | :--- |
| `GET` | `/api/health` | No | System health check and model metadata |
| `POST` | `/api/predict` | No | Placement prediction and risk stratification |
| `POST` | `/api/what-if` | No | 7-scenario What-If simulation |
| `POST` | `/api/recommendations` | No | Alumni-benchmarked prioritized recommendations |
| `GET` | `/api/analytics-data` | No | Model comparisons, CV stability, SHAP, and EDA data |
| `GET` | `/api/sample-profiles` | No | 1-click verified student presets |
| `POST` | `/api/auth/register` | No | Student account registration |
| `POST` | `/api/auth/login` | No | Student authentication and session creation |
| `POST` | `/api/auth/logout` | No | Session clearance |
| `GET` | `/api/auth/me` | No | Returns current session authentication state |
| `GET` | `/api/student/profile` | **Yes** | Retrieves authenticated student profile and prediction |
| `POST` | `/api/student/profile` | **Yes** | Updates student profile and saves assessment snapshot |
| `GET` | `/api/student/progress` | **Yes** | Chronological progress snapshots and diagnostic velocity |
| `POST` | `/api/student/assessment` | **Yes** | Explicitly records an assessment snapshot |
| `GET` | `/api/career/roles` | No | Transparent job role alignment across 5 roles |
| `GET` | `/api/career/roadmap` | **Yes** | Personalized learning milestones and checklist |
| `POST` | `/api/career/roadmap/select` | **Yes** | Updates career goal and generates milestones |
| `POST` | `/api/career/roadmap/milestone` | **Yes** | Toggles milestone completion state |
| `POST` | `/api/resume/upload` | **Yes** | Uploads and analyzes PDF resume |
| `GET` | `/api/resume/latest` | **Yes** | Retrieves latest resume analysis |
| `DELETE` | `/api/resume/<id>` | **Yes** | Securely deletes uploaded resume file and record |
| `GET` | `/api/student/badges` | **Yes** | Retrieves all 7 gamification achievement badges |

---

## 9. Limitations & Disclaimers

1. **Educational Decision Support**:
   Placement probabilities, risk categories, and career suggestions are statistical estimates derived from historical campus recruitment patterns. They do not constitute guarantees of employment, salary, or recruitment offers.
2. **Resume Keyword Matching**:
   The Resume Analyzer evaluates presence of technical skills using a curated dictionary and regular expressions. It is designed as an educational feedback tool and does not replicate commercial ATS ranking algorithms or assess qualitative portfolio code quality.
3. **Macroeconomic & Qualitative Factors**:
   The model does not capture spontaneous interview performance, coding test proctoring, corporate hiring freezes, or sector-specific market conditions.
