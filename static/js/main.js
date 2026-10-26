/**
 * Smart Placement Prediction & Career Analytics System
 * Frontend Application Logic & Chart.js Visualizations
 */

document.addEventListener('DOMContentLoaded', () => {
    initApp();
});

// Global state for charts
let whatIfChartInstance = null;
let modelsChartInstance = null;
let cvChartInstance = null;
let shapChartInstance = null;
let riskPieChartInstance = null;
let benchmarksChartInstance = null;

// Verified student presets
const PRESETS = {
    at_risk: {
        CGPA: 7.7,
        Internships: 1,
        Projects: 1,
        "Workshops/Certifications": 0,
        AptitudeTestScore: 69.0,
        SoftSkillsRating: 4.0,
        ExtracurricularActivities: "No",
        PlacementTraining: "No",
        SSC_Marks: 55.0,
        HSC_Marks: 69.0
    },
    placed: {
        CGPA: 7.9,
        Internships: 1,
        Projects: 3,
        "Workshops/Certifications": 2,
        AptitudeTestScore: 90.0,
        SoftSkillsRating: 4.8,
        ExtracurricularActivities: "Yes",
        PlacementTraining: "Yes",
        SSC_Marks: 82.0,
        HSC_Marks: 80.0
    },
    borderline: {
        CGPA: 7.8,
        Internships: 0,
        Projects: 2,
        "Workshops/Certifications": 0,
        AptitudeTestScore: 79.0,
        SoftSkillsRating: 4.5,
        ExtracurricularActivities: "Yes",
        PlacementTraining: "No",
        SSC_Marks: 80.0,
        HSC_Marks: 81.0
    }
};

/**
 * Initializes listeners, loads default analytical reports, and sets up preset buttons.
 */
function initApp() {
    setupFormListeners();
    setupPresetButtons();
    setupNavScroll();
    loadAnalyticsData();

    // Auto-load the high-risk preset initially to showcase prediction and recommendations right away
    applyPreset('at_risk', false);
}

/**
 * Sets up form submission and input validation.
 */
function setupFormListeners() {
    const form = document.getElementById('prediction-form');
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        await runPredictionFlow();
    });

    // Stale inputs warning: notify user if inputs are modified
    form.addEventListener('input', () => {
        const stale = document.getElementById('stale-warning');
        if (stale) stale.classList.remove('hidden');
    });

    const btnRecalcWhatif = document.getElementById('btn-recalc-whatif');
    if (btnRecalcWhatif) {
        btnRecalcWhatif.addEventListener('click', async () => {
            await runPredictionFlow();
        });
    }

    const btnRecalcRecs = document.getElementById('btn-recalc-recs');
    if (btnRecalcRecs) {
        btnRecalcRecs.addEventListener('click', async () => {
            await runPredictionFlow();
        });
    }
}

/**
 * Connects preset buttons for quick 1-click test evaluations.
 */
function setupPresetButtons() {
    document.getElementById('btn-preset-at-risk').addEventListener('click', () => applyPreset('at_risk', true));
    document.getElementById('btn-preset-placed').addEventListener('click', () => applyPreset('placed', true));
    document.getElementById('btn-preset-borderline').addEventListener('click', () => applyPreset('borderline', true));

    document.getElementById('btn-reset-form').addEventListener('click', () => {
        document.getElementById('prediction-form').reset();
        document.getElementById('form-error-alert').classList.add('hidden');
        const stale = document.getElementById('stale-warning');
        if (stale) stale.classList.add('hidden');
        document.getElementById('result-placeholder').classList.remove('hidden');
        document.getElementById('result-content').classList.add('hidden');

        // Clear scenarios and recommendations to prevent stale results
        const scenariosGrid = document.getElementById('scenarios-cards-grid');
        if (scenariosGrid) {
            scenariosGrid.innerHTML = `
                <div class="result-placeholder">
                    <p>No active student profile selected. Run a placement prediction above to simulate scenarios.</p>
                </div>
            `;
        }
        if (whatIfChartInstance) {
            whatIfChartInstance.destroy();
            whatIfChartInstance = null;
        }

        const recsContainer = document.getElementById('recommendations-container');
        if (recsContainer) {
            recsContainer.innerHTML = `
                <div class="result-placeholder">
                    <p>No active student profile selected. Run a placement prediction above to generate career recommendations.</p>
                </div>
            `;
        }
    });
}

/**
 * Smooth navigation scroll & active link tracking.
 */
function setupNavScroll() {
    const navItems = document.querySelectorAll('.nav-links .nav-item');
    window.addEventListener('scroll', () => {
        let current = '';
        const sections = document.querySelectorAll('section');
        sections.forEach(section => {
            const sectionTop = section.offsetTop - 120;
            if (window.scrollY >= sectionTop) {
                current = section.getAttribute('id');
            }
        });

        navItems.forEach(item => {
            item.classList.remove('active');
            if (item.getAttribute('href') === `#${current}`) {
                item.classList.add('active');
            }
        });
    });
}

/**
 * Fills input fields with a selected preset and optionally executes the prediction.
 */
function applyPreset(presetKey, runPredict = true) {
    const data = PRESETS[presetKey];
    if (!data) return;

    document.getElementById('input-cgpa').value = data.CGPA;
    document.getElementById('input-ssc').value = data.SSC_Marks;
    document.getElementById('input-hsc').value = data.HSC_Marks;
    document.getElementById('input-aptitude').value = data.AptitudeTestScore;
    document.getElementById('input-soft-skills').value = data.SoftSkillsRating;
    document.getElementById('input-projects').value = data.Projects;
    document.getElementById('input-certifications').value = data["Workshops/Certifications"];
    document.getElementById('input-internships').value = data.Internships;
    document.getElementById('input-extra').value = data.ExtracurricularActivities;
    document.getElementById('input-training').value = data.PlacementTraining;

    document.getElementById('form-error-alert').classList.add('hidden');
    const stale = document.getElementById('stale-warning');
    if (stale) stale.classList.add('hidden');

    if (runPredict) {
        runPredictionFlow();
    }
}

/**
 * Extracts and validates inputs from the DOM form.
 */
function getFormPayload() {
    const cgpa = parseFloat(document.getElementById('input-cgpa').value);
    const ssc = parseFloat(document.getElementById('input-ssc').value);
    const hsc = parseFloat(document.getElementById('input-hsc').value);
    const aptitude = parseFloat(document.getElementById('input-aptitude').value);
    const soft = parseFloat(document.getElementById('input-soft-skills').value);
    const projects = parseInt(document.getElementById('input-projects').value, 10);
    const certs = parseInt(document.getElementById('input-certifications').value, 10);
    const internships = parseInt(document.getElementById('input-internships').value, 10);
    const extra = document.getElementById('input-extra').value;
    const training = document.getElementById('input-training').value;

    // Client-side range validation
    if (isNaN(cgpa) || cgpa < 0 || cgpa > 10) throw new Error('CGPA must be a valid number between 0.0 and 10.0');
    if (isNaN(ssc) || ssc < 0 || ssc > 100) throw new Error('SSC Marks must be a valid percentage between 0 and 100');
    if (isNaN(hsc) || hsc < 0 || hsc > 100) throw new Error('HSC Marks must be a valid percentage between 0 and 100');
    if (isNaN(aptitude) || aptitude < 0 || aptitude > 100) throw new Error('Aptitude Test Score must be between 0 and 100');
    if (isNaN(soft) || soft < 1.0 || soft > 5.0) throw new Error('Soft Skills Rating must be between 1.0 and 5.0');
    if (isNaN(projects) || projects < 0) throw new Error('Projects count cannot be negative');
    if (isNaN(certs) || certs < 0) throw new Error('Workshops/Certifications count cannot be negative');
    if (isNaN(internships) || internships < 0) throw new Error('Internships count cannot be negative');

    return {
        CGPA: cgpa,
        Internships: internships,
        Projects: projects,
        "Workshops/Certifications": certs,
        AptitudeTestScore: aptitude,
        SoftSkillsRating: soft,
        ExtracurricularActivities: extra,
        PlacementTraining: training,
        SSC_Marks: ssc,
        HSC_Marks: hsc
    };
}

/**
 * Main prediction runner: triggers /api/predict, /api/what-if, and /api/recommendations.
 */
async function runPredictionFlow() {
    const errorAlert = document.getElementById('form-error-alert');
    const errorMsg = document.getElementById('form-error-msg');
    const submitBtn = document.getElementById('btn-submit-predict');
    const staleWarning = document.getElementById('stale-warning');

    try {
        errorAlert.classList.add('hidden');
        if (staleWarning) staleWarning.classList.add('hidden');
        submitBtn.disabled = true;
        submitBtn.innerHTML = `Running ML Forecast...`;

        // Put What-If and Recommendations in clear loading states immediately to prevent stale results
        const scenariosGrid = document.getElementById('scenarios-cards-grid');
        if (scenariosGrid) {
            scenariosGrid.innerHTML = `
                <div class="loading-state">
                    <div class="spinner"></div>
                    <p>Simulating What-If intervention pathways for this student profile...</p>
                </div>
            `;
        }

        const recsContainer = document.getElementById('recommendations-container');
        if (recsContainer) {
            recsContainer.innerHTML = `
                <div class="loading-state">
                    <div class="spinner"></div>
                    <p>Analyzing gap against placed alumni and prioritizing recommendations...</p>
                </div>
            `;
        }

        const payload = getFormPayload();

        // 1. Fetch Prediction
        const predRes = await fetch('/api/predict', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        const predData = await predRes.json();

        if (!predRes.ok || predData.status !== 'success') {
            throw new Error(predData.error || 'Failed to compute placement prediction.');
        }

        renderPredictionResult(predData);

        // 2. Fetch What-If Simulations
        await fetchWhatIf(payload);

        // 3. Fetch Prescriptive Recommendations
        await fetchRecommendations(payload);

    } catch (err) {
        errorMsg.textContent = err.message;
        errorAlert.classList.remove('hidden');
    } finally {
        submitBtn.disabled = false;
        submitBtn.innerHTML = `
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="20 6 9 17 4 12"></polyline></svg>
            Run Placement Prediction
        `;
    }
}

/**
 * Renders the prediction outcome card.
 */
function renderPredictionResult(data) {
    document.getElementById('result-placeholder').classList.add('hidden');
    const resultContent = document.getElementById('result-content');
    resultContent.classList.remove('hidden');

    const badgePred = document.getElementById('badge-prediction');
    const isPlaced = data.prediction === 'Placed';
    badgePred.textContent = data.prediction === 'Placed' ? 'Placed' : 'Not Placed';
    badgePred.className = `prediction-badge ${isPlaced ? 'placed' : 'not-placed'}`;

    // Probabilities
    const probPct = data.placement_percentage;
    document.getElementById('val-placement-prob').textContent = `${probPct.toFixed(1)}%`;
    document.getElementById('val-non-prob').textContent = `${(data.non_placement_probability * 100).toFixed(1)}%`;
    document.getElementById('val-status-flag').textContent = `Class ${data.predicted_class} (${data.prediction})`;

    // Progress Bar Fill
    const fillBar = document.getElementById('prob-fill-bar');
    fillBar.style.width = `${Math.min(100, Math.max(0, probPct))}%`;
    fillBar.className = 'probability-fill';
    if (data.risk_level === 'Low') fillBar.classList.add('low-risk');
    else if (data.risk_level === 'Medium') fillBar.classList.add('med-risk');
    else fillBar.classList.add('high-risk');

    // Risk Card
    const riskCard = document.getElementById('risk-card-container');
    const badgeRisk = document.getElementById('badge-risk-level');
    const riskScore = document.getElementById('val-risk-score');
    const riskDesc = document.getElementById('risk-explanation-text');

    riskCard.className = `risk-card ${data.risk_level.toLowerCase()}`;
    badgeRisk.textContent = `${data.risk_level} Risk`;
    riskScore.textContent = `Risk Score: ${data.risk_score.toFixed(4)}`;

    if (data.risk_level === 'Low') {
        riskDesc.textContent = 'Low Placement Risk (Risk Score ≤ 0.30, Placement Probability ≥ 70%). The student profile matches competitive hiring requirements.';
    } else if (data.risk_level === 'Medium') {
        riskDesc.textContent = 'Moderate Placement Risk (0.30 < Risk Score ≤ 0.60, Placement Probability 40% - 70%). Targeted improvements in aptitude or interview skills can transition this candidate to Low Risk.';
    } else {
        riskDesc.textContent = 'Elevated Non-Placement Risk (Risk Score > 0.60, Placement Probability < 40%). Immediate focus on quantitative aptitude, structured mock interviews, and technical projects recommended.';
    }
}

/**
 * Fetches and renders what-if scenarios from /api/what-if.
 */
async function fetchWhatIf(payload) {
    try {
        const res = await fetch('/api/what-if', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        const data = await res.json();
        if (data.status === 'success') {
            renderWhatIf(data.scenarios);
        } else {
            throw new Error(data.error || 'Failed to simulate what-if scenarios.');
        }
    } catch (err) {
        console.error('Error fetching what-if:', err);
        const container = document.getElementById('scenarios-cards-grid');
        if (container) {
            container.innerHTML = `<div class="alert-box error"><span>Simulation unavailable: ${err.message}</span></div>`;
        }
    }
}

/**
 * Renders What-If scenario cards and interactive Chart.js bar chart.
 */
function renderWhatIf(scenarios) {
    const container = document.getElementById('scenarios-cards-grid');
    container.innerHTML = '';

    const labels = [];
    const probabilities = [];
    const backgroundColors = [];

    scenarios.forEach((s) => {
        const isBase = s.Scenario === 'Baseline';
        const isHighlight = s.Scenario.includes('Combined');
        const probPct = (s.PlacementProbability * 100).toFixed(1);
        const delta = s.Change_vs_Baseline_pp;
        const deltaStr = delta > 0 ? `+${delta.toFixed(2)} pp` : `${delta.toFixed(2)} pp`;

        labels.push(s.Scenario);
        probabilities.push(probPct);

        if (isBase) backgroundColors.push('rgba(148, 163, 184, 0.7)');
        else if (isHighlight) backgroundColors.push('rgba(6, 182, 212, 0.85)');
        else backgroundColors.push('rgba(99, 102, 241, 0.8)');

        const card = document.createElement('div');
        card.className = `scenario-card ${isBase ? 'baseline' : ''} ${isHighlight ? 'highlight' : ''}`;
        card.innerHTML = `
            <div>
                <div class="scenario-header">
                    <span class="scenario-name">${s.Scenario}</span>
                    <span class="scenario-delta ${delta > 0 ? 'positive' : 'zero'}">${deltaStr}</span>
                </div>
                <div class="scenario-metrics">
                    <span class="scenario-prob">${probPct}%</span>
                    <span class="scenario-risk ${s.RiskLevel.toLowerCase()}">${s.RiskLevel} Risk</span>
                </div>
            </div>
            <p class="scenario-desc">${s.Description}</p>
        `;
        container.appendChild(card);
    });

    // Render What-If Chart
    const ctx = document.getElementById('chart-whatif').getContext('2d');
    if (whatIfChartInstance) whatIfChartInstance.destroy();

    whatIfChartInstance = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Placement Probability (%)',
                data: probabilities,
                backgroundColor: backgroundColors,
                borderRadius: 6,
                borderWidth: 1,
                borderColor: 'rgba(255, 255, 255, 0.1)'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false },
                tooltip: {
                    callbacks: {
                        label: (ctx) => `Probability: ${ctx.raw}%`
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    max: 100,
                    grid: { color: 'rgba(255, 255, 255, 0.06)' },
                    ticks: { color: '#94a3b8', font: { family: 'JetBrains Mono' } }
                },
                x: {
                    grid: { display: false },
                    ticks: { color: '#cbd5e1', font: { size: 11, weight: '600' } }
                }
            }
        }
    });
}

/**
 * Fetches and renders prescriptive career recommendations from /api/recommendations.
 */
async function fetchRecommendations(payload) {
    try {
        const res = await fetch('/api/recommendations', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        const data = await res.json();
        if (data.status === 'success') {
            renderRecommendations(data.recommendations);
        } else {
            throw new Error(data.error || 'Failed to generate recommendations.');
        }
    } catch (err) {
        console.error('Error fetching recommendations:', err);
        const container = document.getElementById('recommendations-container');
        if (container) {
            container.innerHTML = `<div class="alert-box error"><span>Guidance unavailable: ${err.message}</span></div>`;
        }
    }
}

/**
 * Renders recommendations cards with priority order.
 */
function renderRecommendations(recs) {
    const container = document.getElementById('recommendations-container');
    container.innerHTML = '';

    recs.forEach((r, idx) => {
        const card = document.createElement('div');
        card.className = 'rec-card';
        card.innerHTML = `
            <div>
                <div class="rec-top">
                    <span class="rec-feature-tag">Priority #${idx + 1} • ${r.Feature}</span>
                    <span class="rec-boost-badge">+${r.Placement_Probability_Change_pp.toFixed(2)} pp boost</span>
                </div>
                <h4 class="rec-title">${r.Recommendation}</h4>
                <p class="rec-action">${r.Suggested_Action}</p>
            </div>
            <div class="rec-stats-row">
                <div class="rec-stat-col">
                    <span class="label">Current</span>
                    <span class="val">${r.Current_Value}</span>
                </div>
                <div class="rec-stat-col">
                    <span class="label">Simulated</span>
                    <span class="val">${r.Simulated_Value}</span>
                </div>
                <div class="rec-stat-col">
                    <span class="label">Placed Benchmark</span>
                    <span class="val">${r.Benchmark_Placed_Avg.toFixed(2)}</span>
                </div>
                <div class="rec-stat-col">
                    <span class="label">Sim. Risk</span>
                    <span class="val">${r.Simulated_Risk}</span>
                </div>
            </div>
        `;
        container.appendChild(card);
    });
}

/**
 * Loads authentic analytics data from CSV reports via /api/analytics-data and builds charts.
 */
async function loadAnalyticsData() {
    try {
        const res = await fetch('/api/analytics-data');
        const resJson = await res.json();
        if (resJson.status !== 'success') return;

        const data = resJson.data;

        // 1. Populate Model Benchmarks Table
        if (data.model_comparisons) {
            renderModelsTable(data.model_comparisons);
            renderModelsChart(data.model_comparisons);
        }

        // 2. Populate Cross Validation Chart
        if (data.cross_validation) {
            renderCrossValidationChart(data.cross_validation);
        }

        // 3. Populate SHAP Feature Importance Chart
        if (data.shap_importance) {
            renderShapChart(data.shap_importance);
        }

        // 4. Populate Risk Distribution Doughnut Chart
        if (data.risk_summary) {
            renderRiskPieChart(data.risk_summary);
        }

        // 5. Populate Feature Benchmarks Chart (Placed vs NotPlaced)
        if (data.placement_comparison) {
            renderBenchmarksChart(data.placement_comparison);
        }

        // 6. Update EDA Header Metric Counters
        if (data.eda_summary) {
            const eda = data.eda_summary;
            const total = (eda.training_records || 6353) + (eda.validation_records || 1591) + (eda.test_records || 1984);
            document.getElementById('stat-total-records').textContent = total.toLocaleString();
        }

    } catch (err) {
        console.error('Error loading analytics data:', err);
    }
}

/**
 * Renders the 10-model comparison table.
 */
function renderModelsTable(models) {
    const tbody = document.getElementById('models-table-body');
    tbody.innerHTML = '';

    models.forEach(m => {
        const isTunedLogReg = m.Model === 'Logistic Regression';
        const tr = document.createElement('tr');
        if (isTunedLogReg) tr.className = 'selected-row';

        tr.innerHTML = `
            <td><strong>${m.Model}</strong> ${isTunedLogReg ? '<span class="tag-selected">Selected Model</span>' : ''}</td>
            <td>${(m.Accuracy * 100).toFixed(2)}%</td>
            <td>${(m.Precision_Placed * 100).toFixed(2)}%</td>
            <td>${(m.Recall_Placed * 100).toFixed(2)}%</td>
            <td>${(m.F1_Placed * 100).toFixed(2)}%</td>
            <td>${(m.ROC_AUC).toFixed(4)}</td>
            <td>${(m.PR_AUC).toFixed(4)}</td>
            <td>${isTunedLogReg ? 'High recall & calibrated probabilities' : 'Candidate baseline'}</td>
        `;
        tbody.appendChild(tr);
    });
}

/**
 * Renders 10-model comparative bar chart.
 */
function renderModelsChart(models) {
    const ctx = document.getElementById('chart-models-comparison').getContext('2d');
    if (modelsChartInstance) modelsChartInstance.destroy();

    const labels = models.map(m => m.Model);
    const accData = models.map(m => (m.Accuracy * 100).toFixed(1));
    const f1Data = models.map(m => (m.F1_Placed * 100).toFixed(1));
    const rocAucData = models.map(m => (m.ROC_AUC * 100).toFixed(1));

    modelsChartInstance = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [
                {
                    label: 'Accuracy (%)',
                    data: accData,
                    backgroundColor: 'rgba(56, 189, 248, 0.75)',
                    borderRadius: 4
                },
                {
                    label: 'F1-Score (%)',
                    data: f1Data,
                    backgroundColor: 'rgba(99, 102, 241, 0.75)',
                    borderRadius: 4
                },
                {
                    label: 'ROC-AUC (%)',
                    data: rocAucData,
                    backgroundColor: 'rgba(16, 185, 129, 0.75)',
                    borderRadius: 4
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    labels: { color: '#cbd5e1', font: { family: 'Plus Jakarta Sans', weight: '600' } }
                }
            },
            scales: {
                y: {
                    min: 65,
                    max: 100,
                    grid: { color: 'rgba(255, 255, 255, 0.06)' },
                    ticks: { color: '#94a3b8' }
                },
                x: {
                    grid: { display: false },
                    ticks: { color: '#cbd5e1', font: { size: 10, weight: '600' } }
                }
            }
        }
    });
}

/**
/**
 * Renders 5-fold cross validation stability chart.
 */
function renderCrossValidationChart(cvList) {
    const canvas = document.getElementById('chart-cv-stability');
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (cvChartInstance) {
        cvChartInstance.destroy();
        cvChartInstance = null;
    }

    const labels = cvList.map(item => item.Model);
    const accuracyMeans = cvList.map(item => (item.Accuracy_Mean * 100).toFixed(2));
    const recallMeans = cvList.map(item => (item.Recall_Mean * 100).toFixed(2));
    const f1Means = cvList.map(item => (item.F1_Mean * 100).toFixed(2));
    const rocAucMeans = cvList.map(item => (item.ROC_AUC_Mean * 100).toFixed(2));

    cvChartInstance = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [
                {
                    label: 'Mean CV Accuracy (%)',
                    data: accuracyMeans,
                    backgroundColor: 'rgba(56, 189, 248, 0.8)',
                    borderRadius: 4
                },
                {
                    label: 'Mean Recall (Placed) (%)',
                    data: recallMeans,
                    backgroundColor: 'rgba(16, 185, 129, 0.8)',
                    borderRadius: 4
                },
                {
                    label: 'Mean F1-Score (%)',
                    data: f1Means,
                    backgroundColor: 'rgba(99, 102, 241, 0.8)',
                    borderRadius: 4
                },
                {
                    label: 'Mean ROC-AUC (%)',
                    data: rocAucMeans,
                    backgroundColor: 'rgba(192, 132, 252, 0.8)',
                    borderRadius: 4
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'top',
                    labels: { color: '#cbd5e1', font: { family: 'Plus Jakarta Sans', weight: '600', size: 10 } }
                },
                tooltip: {
                    callbacks: {
                        label: function(ctx) {
                            const item = cvList[ctx.dataIndex];
                            if (ctx.datasetIndex === 0) {
                                return `Mean Accuracy: ${ctx.raw}% (SD: ±${(item.Accuracy_SD * 100).toFixed(2)}%)`;
                            } else if (ctx.datasetIndex === 1) {
                                return `Mean Recall (Placed): ${ctx.raw}%`;
                            } else if (ctx.datasetIndex === 2) {
                                return `Mean F1-Score: ${ctx.raw}% (SD: ±${(item.F1_SD * 100).toFixed(2)}%)`;
                            } else {
                                return `Mean ROC-AUC: ${ctx.raw}%`;
                            }
                        }
                    }
                }
            },
            scales: {
                y: {
                    min: 65,
                    max: 100,
                    grid: { color: 'rgba(255, 255, 255, 0.06)' },
                    ticks: { color: '#94a3b8' }
                },
                x: {
                    grid: { display: false },
                    ticks: { color: '#cbd5e1', font: { size: 11, weight: '600' } }
                }
            }
        }
    });
}

/**
 * Renders SHAP feature importance horizontal bar chart.
 */
function renderShapChart(shapList) {
    const canvas = document.getElementById('chart-shap');
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (shapChartInstance) {
        shapChartInstance.destroy();
        shapChartInstance = null;
    }

    const featureLabelsMap = {
        'numeric__AptitudeTestScore': 'Aptitude Test Score',
        'numeric__HSC_Marks': 'HSC (12th) Marks %',
        'numeric__SSC_Marks': 'SSC (10th) Marks %',
        'numeric__Projects': 'Projects Completed',
        'numeric__SoftSkillsRating': 'Soft Skills Rating',
        'numeric__CGPA': 'College CGPA',
        'numeric__Workshops/Certifications': 'Workshops / Certifications',
        'categorical__ExtracurricularActivities_No': 'Extracurriculars: No',
        'categorical__ExtracurricularActivities_Yes': 'Extracurriculars: Yes',
        'categorical__PlacementTraining_No': 'Placement Training: No',
        'categorical__PlacementTraining_Yes': 'Placement Training: Yes',
        'numeric__Internships': 'Internships'
    };

    const cleaned = shapList.map(item => {
        const rawName = item.Feature;
        const displayName = featureLabelsMap[rawName] || rawName.replace('numeric__', '').replace('categorical__', '').replace('_', ' ');
        return {
            name: displayName,
            val: parseFloat(item.Mean_Absolute_SHAP)
        };
    }).sort((a, b) => b.val - a.val);

    const labels = cleaned.map(c => c.name);
    const values = cleaned.map(c => c.val.toFixed(4));

    shapChartInstance = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Mean Absolute SHAP Value',
                data: values,
                backgroundColor: 'rgba(6, 182, 212, 0.85)',
                hoverBackgroundColor: 'rgba(56, 189, 248, 1)',
                borderRadius: 4
            }]
        },
        options: {
            indexAxis: 'y',
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false },
                tooltip: {
                    callbacks: {
                        label: (ctx) => `Mean |SHAP| Impact: ${ctx.raw} (Rank #${ctx.dataIndex + 1})`
                    }
                }
            },
            scales: {
                x: {
                    grid: { color: 'rgba(255, 255, 255, 0.06)' },
                    ticks: { color: '#94a3b8' }
                },
                y: {
                    grid: { display: false },
                    ticks: { color: '#cbd5e1', font: { size: 10, weight: '600' } }
                }
            }
        }
    });
}

/**
 * Renders Test Cohort Placement Risk Doughnut chart.
 */
function renderRiskPieChart(riskList) {
    const canvas = document.getElementById('chart-risk-pie');
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (riskPieChartInstance) {
        riskPieChartInstance.destroy();
        riskPieChartInstance = null;
    }

    const labels = riskList.map(r => `${r.RiskLevel} Risk (${r.Students} • ${parseFloat(r.Percentage).toFixed(1)}%)`);
    const counts = riskList.map(r => r.Students);

    riskPieChartInstance = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: labels,
            datasets: [{
                data: counts,
                backgroundColor: [
                    'rgba(16, 185, 129, 0.85)', // Low
                    'rgba(245, 158, 11, 0.85)', // Med
                    'rgba(244, 63, 94, 0.85)'   // High
                ],
                borderColor: '#0f172a',
                borderWidth: 3
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: { color: '#cbd5e1', font: { size: 11, weight: '600' }, padding: 15 }
                },
                tooltip: {
                    callbacks: {
                        label: function(ctx) {
                            const r = riskList[ctx.dataIndex];
                            return ` ${r.RiskLevel} Risk: ${r.Students} students (${parseFloat(r.Percentage).toFixed(2)}% of Test Cohort)`;
                        }
                    }
                }
            },
            cutout: '65%'
        }
    });
}

/**
 * Renders Placed vs Non-Placed feature benchmarks comparison chart.
 */
function renderBenchmarksChart(compList) {
    const canvas = document.getElementById('chart-benchmarks');
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (benchmarksChartInstance) {
        benchmarksChartInstance.destroy();
        benchmarksChartInstance = null;
    }

    const placed = compList.find(c => c.PlacementStatus === 'Placed') || {};
    const notPlaced = compList.find(c => c.PlacementStatus === 'NotPlaced') || {};

    const metrics = [
        { label: 'CGPA', placedRaw: Number(placed.mean_cgpa), notPlacedRaw: Number(notPlaced.mean_cgpa), unit: '/ 10', placedScaled: Number(placed.mean_cgpa) * 10, notPlacedScaled: Number(notPlaced.mean_cgpa) * 10 },
        { label: 'Aptitude Test Score', placedRaw: Number(placed.mean_aptitude), notPlacedRaw: Number(notPlaced.mean_aptitude), unit: '/ 100', placedScaled: Number(placed.mean_aptitude), notPlacedScaled: Number(notPlaced.mean_aptitude) },
        { label: 'SSC Marks %', placedRaw: Number(placed.mean_ssc), notPlacedRaw: Number(notPlaced.mean_ssc), unit: '%', placedScaled: Number(placed.mean_ssc), notPlacedScaled: Number(notPlaced.mean_ssc) },
        { label: 'HSC Marks %', placedRaw: Number(placed.mean_hsc), notPlacedRaw: Number(notPlaced.mean_hsc), unit: '%', placedScaled: Number(placed.mean_hsc), notPlacedScaled: Number(notPlaced.mean_hsc) },
        { label: 'Soft Skills Rating', placedRaw: Number(placed.mean_soft_skills), notPlacedRaw: Number(notPlaced.mean_soft_skills), unit: '/ 5.0', placedScaled: Number(placed.mean_soft_skills) * 20, notPlacedScaled: Number(notPlaced.mean_soft_skills) * 20 },
        { label: 'Projects Completed', placedRaw: Number(placed.mean_projects), notPlacedRaw: Number(notPlaced.mean_projects), unit: 'projects', placedScaled: Number(placed.mean_projects) * 20, notPlacedScaled: Number(notPlaced.mean_projects) * 20 },
        { label: 'Certifications', placedRaw: Number(placed.mean_certifications), notPlacedRaw: Number(notPlaced.mean_certifications), unit: 'certs', placedScaled: Number(placed.mean_certifications) * 20, notPlacedScaled: Number(notPlaced.mean_certifications) * 20 },
        { label: 'Internships', placedRaw: Number(placed.mean_internships), notPlacedRaw: Number(notPlaced.mean_internships), unit: 'internships', placedScaled: Number(placed.mean_internships) * 20, notPlacedScaled: Number(notPlaced.mean_internships) * 20 }
    ];

    benchmarksChartInstance = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: metrics.map(m => m.label),
            datasets: [
                {
                    label: 'Placed Students Mean (2,611)',
                    data: metrics.map(m => m.placedScaled.toFixed(1)),
                    backgroundColor: 'rgba(16, 185, 129, 0.85)',
                    borderRadius: 4
                },
                {
                    label: 'Not Placed Students Mean (3,742)',
                    data: metrics.map(m => m.notPlacedScaled.toFixed(1)),
                    backgroundColor: 'rgba(244, 63, 94, 0.8)',
                    borderRadius: 4
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'top',
                    labels: { color: '#cbd5e1', font: { family: 'Plus Jakarta Sans', weight: '600' } }
                },
                tooltip: {
                    callbacks: {
                        label: function(ctx) {
                            const m = metrics[ctx.dataIndex];
                            const rawVal = ctx.datasetIndex === 0 ? m.placedRaw : m.notPlacedRaw;
                            const diff = (m.placedRaw - m.notPlacedRaw).toFixed(2);
                            const sign = diff > 0 ? `+${diff}` : diff;
                            return `${ctx.dataset.label}: ${rawVal.toFixed(2)} ${m.unit} (Delta: ${sign})`;
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    max: 100,
                    grid: { color: 'rgba(255, 255, 255, 0.06)' },
                    ticks: { color: '#94a3b8' }
                },
                x: {
                    grid: { display: false },
                    ticks: { color: '#cbd5e1', font: { size: 10, weight: '600' } }
                }
            }
        }
    });
}


/**
 * Lightbox modal control for EDA figure inspection.
 */
window.openLightbox = function(imageSrc, caption) {
    const modal = document.getElementById('image-modal');
    const modalImg = document.getElementById('modal-image');
    const modalCap = document.getElementById('modal-caption');

    modalImg.src = imageSrc;
    modalCap.textContent = caption;
    modal.classList.remove('hidden');
};

window.closeLightbox = function() {
    const modal = document.getElementById('image-modal');
    modal.classList.add('hidden');
};
