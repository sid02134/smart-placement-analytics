# Smart Placement Prediction & Career Analytics System

> **College Data Science Capstone Project (Semester 5)**  
> An interpretable machine learning web application for student placement prediction, risk stratification, what-if scenario simulation, and prescriptive career recommendations.

---

## 1. Project Overview

The **Smart Placement Prediction & Career Analytics System** is an end-to-end data science and machine learning application designed to bridge the gap between academic preparation and campus recruitment outcomes. Built upon a dataset of **9,928 student records**, the system integrates a trained, tuned machine learning model with an interactive web dashboard. 

Beyond binary placement classification, the platform offers:
- **Calibrated Placement Forecasting**: Exact probability scoring for placement and non-placement.
- **Three-Tier Placement Risk Stratification**: Automated categorization into Low, Medium, and High risk.
- **Real-Time What-If Intervention Studio**: Simulation of isolated skill enhancements to quantify expected percentage-point gains ($\Delta$ pp).
- **Prescriptive Career Recommendations**: Actionable guidance prioritized by impact and benchmarked against placed alumni profiles.
- **Transparent Model & Exploratory Analytics**: Interactive visualizations of 10 candidate models, 5-fold cross-validation stability, global SHAP feature importance, and historical exploratory data analysis (EDA).

---

## 2. Problem Statement

In higher education institutions, campus placement preparation is frequently reactive. Students often discover gaps in their technical preparation, aptitude scores, or interpersonal capabilities only after failing competitive placement rounds. Career services departments face significant challenges in identifying at-risk students early enough to implement meaningful interventions.

Existing approaches typically rely on basic academic cutoffs (such as college CGPA) or manual counseling heuristics. These methods fail to:
1. Capture multi-dimensional interactions between aptitude, coursework, practical projects, certifications, and soft skills.
2. Provide probabilistic risk estimates before company recruitment drives commence.
3. Quantify the marginal return of specific interventions (e.g., *"How much will completing an additional project improve my placement probability?"*).
4. Offer transparent, personalized benchmarks based on successfully placed alumni.

---

## 3. Project Objectives

1. **Interpretability & Accuracy**: Train, benchmark, and tune multiple machine learning classifiers to achieve robust out-of-sample accuracy and high recall on placed students while preserving model interpretability.
2. **Early Risk Identification**: Formulate a validated risk classification threshold to segment students into Low ($\le 0.30$), Medium ($0.30 - 0.60$), and High ($> 0.60$) risk tiers.
3. **Actionable What-If Analysis**: Implement a dynamic simulation engine allowing students and mentors to evaluate the sensitivity of placement probability to incremental metric changes.
4. **Alumni-Benchmarked Guidance**: Compare individual profiles against placed alumni feature averages to generate prioritized upskilling roadmaps.
5. **Production-Grade Web Application**: Deploy a responsive, accessible, dark glassmorphic web dashboard powered by a Flask backend and clean vanilla frontend architecture.

---

## 4. Technologies Used

| Domain | Technology / Library | Version / Details | Purpose |
| :--- | :--- | :--- | :--- |
| **Backend Framework** | Flask | `>= 3.0.0` | REST API routing, template rendering, and error handling |
| **Language & Runtime** | Python | `3.13.7` (Windows x64) | Core application execution environment |
| **Machine Learning** | scikit-learn | `== 1.6.1` *(pinned)* | Pipeline preprocessing, ColumnTransformer, Logistic Regression |
| **Model Serialization** | Joblib | `>= 1.4.0` | Saving and loading trained pipeline artifacts |
| **Data Manipulation** | Pandas & NumPy | `>= 2.2.0`, `>= 2.0.0` | Dataset processing, matrix transformations, and metric calculations |
| **Frontend Structure** | HTML5 (Jinja2) | Native Flask Templates | Semantic structure, accessible forms, modal dialogs |
| **Frontend Styling** | Vanilla CSS3 | Custom Design System | Dark glassmorphism, responsive grid/flexbox, CSS variables |
| **Frontend Logic** | Vanilla JavaScript | ES6+ (Fetch API, DOM) | Async API calls, preset loaders, stale-state management |
| **Data Visualizations** | Chart.js | `4.4.7` (via CDN) | Dynamic What-If bar chart, model comparisons, CV error bars |
| **Model Explainability** | SHAP | Evaluated in Reports | Global feature importance and SHAP value extractions |

---

## 5. Dataset Overview

The project utilizes an institutionally prepared dataset of **9,928 student records** partitioned into three disjoint splits for training, validation, and testing.

### Dataset Partitioning

```
Total Records: 9,928
├── Training Set:   6,353 records (64.0%)  [41.1% Placed / 58.9% NotPlaced]
├── Validation Set: 1,591 records (16.0%)  [Model benchmarking & hyperparameter tuning]
└── Test Set:       1,984 records (20.0%)  [Out-of-sample risk stratification & test evaluation]
```

### Data Quality & Integrity
- **Missing Values**: 0 across all columns.
- **Duplicate Rows**: 0 exact duplicate records.
- **Target Distribution (Training Split)**: 
  - `NotPlaced`: 3,742 students (58.90%)
  - `Placed`: 2,611 students (41.10%)
- *Data Source Confirmation Note*: Datasets are provided as cleaned CSV files in `data/processed/`. Institutional/departmental origin details should be confirmed with the project supervisor if required for external archival.

---

## 6. The 10 Input Features & Target Variable

The model expects exactly 10 input features across four key developmental dimensions:

| # | Feature Name | Data Type | Domain / Range | SHAP Rank | Description |
| :-: | :--- | :---: | :---: | :-: | :--- |
| 1 | `AptitudeTestScore` | Numeric (Float) | 0.0 – 100.0 | **#1** | Standardized quantitative, logical, and verbal aptitude test score. |
| 2 | `HSC_Marks` | Numeric (Float) | 0.0 – 100.0 | **#2** | Higher Secondary Certificate (12th Grade) overall percentage. |
| 3 | `SSC_Marks` | Numeric (Float) | 0.0 – 100.0 | **#3** | Secondary School Certificate (10th Grade) overall percentage. |
| 4 | `Projects` | Numeric (Integer) | $\ge 0$ | **#4** | Number of completed technical or academic software projects. |
| 5 | `SoftSkillsRating` | Numeric (Float) | 1.0 – 5.0 | **#5** | Evaluated soft skills, presentation, and interview readiness rating. |
| 6 | `CGPA` | Numeric (Float) | 0.0 – 10.0 | **#6** | Cumulative Grade Point Average in the undergraduate degree. |
| 7 | `Workshops/Certifications` | Numeric (Integer) | $\ge 0$ | **#7** | Number of verified industry workshops and certifications. |
| 8 | `ExtracurricularActivities` | Categorical | `Yes` / `No` | **#8** | Active participation in college clubs, student governance, or sports. |
| 9 | `PlacementTraining` | Categorical | `Yes` / `No` | **#9** | Enrollment and attendance in campus placement preparation courses. |
| 10 | `Internships` | Numeric (Integer) | $\ge 0$ | **#10** | Number of completed corporate or industrial internships. |

### Target Variable: `PlacementStatus`
- Binary classification target:
  - `1` / `"Placed"`: Student successfully placed in campus recruitment.
  - `0` / `"NotPlaced"`: Student not placed during campus recruitment.

---

## 7. Machine Learning Model Architecture

### Pipeline Preprocessing
The production model (`models/placement_model.joblib`) is encapsulated within a Scikit-Learn `Pipeline` with a `ColumnTransformer`:
- **Numeric Features (8)**: Imputed with `SimpleImputer(strategy='median')` and scaled with `StandardScaler()`.
- **Categorical Features (2)**: Encoded with `OneHotEncoder(drop='if_binary', handle_unknown='ignore')`.

### Production Model: Tuned Logistic Regression
- **Algorithm**: `LogisticRegression(C=..., solver='lbfgs', max_iter=1000)`
- **Calibration**: Probability outputs derived via sigmoid logit transformation.
- **Selection Rationale**:
  1. **High Recall on Placed Candidates**: Outperformed more complex tree ensembles on placed recall (82.24% on validation set).
  2. **Monotonicity & Interpretability**: Guaranteed positive coefficient monotonicity for positive career interventions, eliminating non-linear counter-intuitive behaviors during What-If simulations.
  3. **High Discriminative Ability**: Achieved an ROC-AUC of **0.8800** and PR-AUC of **0.8428**, closely matching Gradient Boosting (0.8795) and Extra Trees (0.8792).
  4. **Low Latency**: Sub-millisecond inference time suitable for real-time frontend recalculations.

---

## 8. Model Evaluation Results

### A. 10-Model Validation Set Benchmark (1,591 Records)

All models were evaluated on the independent validation split using identical preprocessing:

| Model | Accuracy | Precision (Placed) | Recall (Placed) | F1-Score (Placed) | ROC-AUC | PR-AUC | Log-Loss |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Logistic Regression (Selected)** | **80.39%** | **74.06%** | **82.24%** | **77.93%** | **0.8800** | **0.8428** | **0.4376** |
| Gradient Boosting | 80.52% | 77.36% | 75.97% | 76.66% | 0.8795 | 0.8446 | 0.4305 |
| Extra Trees | 79.70% | 74.20% | 79.40% | 76.71% | 0.8792 | 0.8433 | 0.4348 |
| AdaBoost | 80.20% | 76.69% | 76.12% | 76.40% | 0.8786 | 0.8360 | 0.4706 |
| CatBoost | 80.26% | 77.55% | 74.78% | 76.14% | 0.8764 | 0.8436 | 0.4351 |
| Random Forest | 80.14% | 76.26% | 76.72% | 76.49% | 0.8753 | 0.8395 | 0.4367 |
| XGBoost | 79.89% | 76.92% | 74.63% | 75.76% | 0.8741 | 0.8405 | 0.4378 |
| LightGBM | 79.51% | 76.30% | 74.48% | 75.38% | 0.8721 | 0.8385 | 0.4423 |
| SVM (RBF Kernel) | 79.32% | 73.07% | 80.60% | 76.65% | 0.8579 | 0.7805 | 0.4607 |
| Decision Tree (Baseline) | 77.06% | 71.33% | 76.12% | 73.65% | 0.8333 | 0.7768 | 1.7745 |

### B. 5-Fold Stratified Cross-Validation (Training Split: 6,353 Records)

To confirm generalization stability and ensure no fold-specific bias:

| Candidate Model | Mean Accuracy | Accuracy Std | Mean Precision | Mean Recall | Mean F1-Score | F1 Std | Mean ROC-AUC |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Logistic Regression** | **0.7872** | **± 0.0068** | 0.7157 | **0.8005** | **0.7556** | **± 0.0069** | **0.8750** |
| Gradient Boosting | 0.7976 | ± 0.0072 | 0.7644 | 0.7342 | 0.7488 | ± 0.0078 | 0.8760 |
| Extra Trees | 0.7903 | ± 0.0109 | 0.7295 | 0.7798 | 0.7536 | ± 0.0107 | 0.8728 |

### C. Out-of-Sample Test Set Risk Stratification (1,984 Records)

On the unseen test cohort, student risk was classified according to metadata thresholds (`models/model_metadata.json`):

| Risk Tier | Risk Score Range | Placement Probability | Test Cohort Count | Percentage | Profile Characteristics |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **Low Risk** | $\text{Risk} \le 0.30$ | $P \ge 70.0\%$ | **661 students** | **33.32%** | High aptitude (> 80), consistent academic scores, active projects. |
| **Medium Risk** | $0.30 < \text{Risk} \le 0.60$ | $40.0\% \le P < 70.0\%$ | **407 students** | **20.51%** | Borderline candidates; single skill improvements shift them to Low Risk. |
| **High Risk** | $\text{Risk} > 0.60$ | $P < 40.0\%$ | **916 students** | **46.17%** | Significant deficits in aptitude (< 70) and academic/project foundations. |

---

## 9. Application Features & User Workflows

1. **Interactive Placement Forecaster**:
   - Accepts 10 feature inputs with real-time numeric and range validation.
   - Profile presets for rapid 1-click evaluation:
     - *High-Risk Profile (Test Row 1)*: $P = 9.05\%$, High Risk.
     - *Borderline Profile (Test Row 22)*: $P = 51.68\%$, Medium Risk.
     - *Placed Profile (Test Row 2)*: $P = 86.01\%$, Low Risk.
2. **What-If Intervention Studio**:
   - Calculates baseline probability and isolates percentage-point improvements ($\Delta$ pp) across 6 actionable pathways:
     - *Aptitude +10 points* ($+4.89\text{ pp}$)
     - *Projects +1 completed* ($+2.61\text{ pp}$)
     - *Soft Skills +0.5 rating* ($+2.44\text{ pp}$)
     - *Workshops/Certifications +1* ($+1.20\text{ pp}$)
     - *Enroll in Placement Training* ($+3.64\text{ pp}$, if not currently enrolled)
     - *Combined Growth Package* ($+22.93\text{ pp}$)
3. **Prescriptive Career Recommendations**:
   - Automatically identifies gaps between the candidate's metrics and placed alumni averages:
     - Placed Average Aptitude: `84.42`
     - Placed Average Projects: `2.50`
     - Placed Average Soft Skills: `4.52`
     - Placed Average Certifications: `1.39`
     - Placed Average Internships: `1.24`
   - Prioritizes top 5 interventions in descending order of probability gain.
4. **Stale-State Management**:
   - Automatic visual warning banner whenever inputs are altered.
   - Dynamic loading spinners overwrite old results immediately upon re-submission.
   - Reset button clears inputs, placeholders, scenario grids, and Chart.js instances.
5. **Interactive Model Benchmarking & EDA Gallery**:
   - Dynamic table of all 10 candidate models.
   - 4-metric cross-validation comparison chart.
   - Full-resolution modal viewer for Phase 1 EDA distributions and correlation heatmaps.

---

## 10. Project Folder Structure

```
SmartPlacementAnalytics/
├── .venv/                         # Dedicated Python 3.13 virtual environment
├── data/
│   └── processed/
│       ├── train_clean.csv        # 6,353 training student records
│       ├── validation_clean.csv   # 1,591 validation student records
│       └── test_clean.csv         # 1,984 test student records
├── models/
│   ├── model_metadata.json        # Feature schema, risk thresholds, target mapping
│   └── placement_model.joblib     # Pre-trained Scikit-Learn pipeline (scikit-learn 1.6.1)
├── reports/
│   ├── figures/                   # High-resolution Phase 1 EDA figures (01 to 05)
│   ├── additional_models_validation.csv
│   ├── all_models_validation.csv
│   ├── career_recommendations_demo.csv
│   ├── cross_validation_results.csv
│   ├── phase1_eda_summary.json
│   ├── placement_comparison.csv
│   ├── placement_risk_summary.csv
│   ├── shap_feature_importance.csv
│   ├── ten_model_comparison.png
│   ├── tuned_models_validation.csv
│   └── what_if_scenario_comparison.csv
├── static/
│   ├── css/
│   │   └── styles.css             # Glassmorphic responsive styling & UI tokens
│   └── js/
│       └── main.js                # Frontend controller, API calls, Chart.js integrations
├── templates/
│   └── index.html                 # Main dashboard single-page Jinja2 application
├── app.py                         # Flask web application and REST API controllers
├── predictor.py                   # Core ML inference engine, validation, and What-If logic
├── requirements.txt               # Pinned Python package dependencies
├── test_api.py                    # 57-test automated verification suite
└── README.md                      # Comprehensive project documentation
```

---

## 11. REST API Endpoint Reference

| HTTP Method | Endpoint URI | Request Payload | Response Summary |
| :--- | :--- | :--- | :--- |
| `GET` | `/api/health` | None | Service status, model architecture (`Tuned Logistic Regression`), and feature count (10). |
| `POST` | `/api/predict` | JSON with 10 features | Predicted label (`Placed`/`NotPlaced`), placement probability, non-placement probability, risk score, and risk level. |
| `POST` | `/api/what-if` | JSON with 10 features | Array of 7 simulated scenario objects with probability, non-placement prob, risk tier, and $\Delta\text{ pp}$ change. |
| `POST` | `/api/recommendations` | JSON with 10 features | Array of 5 prioritized recommendations with current values, simulated targets, alumni benchmarks, and $\Delta\text{ pp}$ gains. |
| `GET` | `/api/sample-profiles` | None | Dictionary of predefined profiles (`at_risk`, `placed`, `borderline`) matching test set records. |
| `GET` | `/api/analytics-data` | None | Consolidated JSON payload with 10-model comparison metrics, cross-validation stats, SHAP rankings, risk split, and EDA records. |
| `GET` | `/reports/figures/<file>` | None | Serves static PNG figure assets for exploratory data analysis charts. |

---

## 12. Windows Installation & Execution Guide

Follow these instructions to run the application locally on a Windows machine.

### Prerequisites
- Windows 10 or 11
- Python 3.13 installed and accessible in the system path or virtual environment

### Step 1: Open PowerShell in the Project Directory
```powershell
cd "D:\ds cp sem 5\SmartPlacementAnalytics"
```

### Step 2: Activate the Virtual Environment
```powershell
.\.venv\Scripts\activate
```
*(If execution policies prevent script execution, run: `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass`)*

### Step 3: Install Dependencies (If Setting Up Fresh)
```powershell
pip install -r requirements.txt
```

### Step 4: Run the Automated Verification Suite
To verify model integrity, probability calculations, boundary cases, and API routes:
```powershell
.venv\Scripts\python.exe test_api.py
```
*Expected Output:* `RESULTS: 57/57 TESTS PASSED [SUCCESS]`

### Step 5: Start the Web Application
```powershell
.venv\Scripts\python.exe app.py
```
*Console Output:*
```text
Starting SmartPlacementAnalytics API on http://127.0.0.1:5000
 * Serving Flask app 'app'
 * Running on http://127.0.0.1:5000
```

### Step 6: Access the Dashboard
Open your web browser (Chrome, Edge, Firefox) and navigate to:
```
http://127.0.0.1:5000/
```

---

## 13. Limitations & Responsible-Use Disclaimer

1. **Statistical Estimates, Not Absolute Guarantees**:
   The placement probabilities and risk categories generated by this system represent mathematical forecasts derived from historical student recruitment patterns. They do not constitute a guarantee of employment, nor do they guarantee rejection by any specific employer.
2. **Unmeasured Macroeconomic & Industry Factors**:
   The model does not account for macroeconomic fluctuations, company-specific hiring freezes, sector-specific downturns, or sudden changes in corporate recruitment policies.
3. **Qualitative & Subjective Factors**:
   Critical real-world hiring variables—such as candidate cultural fit, spontaneous problem-solving under pressure, coding test proctoring, communication nuances, and personal demeanor during live interviews—cannot be fully quantified by numerical ratings.
4. **Advisory Decision Support Only**:
   This platform is engineered strictly as an **educational decision support tool** for students, faculty mentors, and academic advisors. It must never be used as an automated filtering, gatekeeping, or disqualifying mechanism for student opportunities.

---

## 14. Academic Declaration

This project was developed for the **Semester 5 Data Science Capstone Project**:
- **Project Title**: Smart Placement Prediction & Career Analytics System
- **Location**: `D:\ds cp sem 5\SmartPlacementAnalytics`
- **Verification Status**: Fully tested, validated, and documented.
