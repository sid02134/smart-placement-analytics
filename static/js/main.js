/**
 * Smart Placement Prediction & Career Analytics System
 * Frontend Application Logic, Navigation Controller & Visualizations
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
let studentProgressChartInstance = null;

// Authenticated session state
let currentUser = null;
let latestResumeRecordId = null;

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
 * Main application initialization.
 */
function initApp() {
    setupNavigation();
    setupGuidanceSubtabs();
    setupFormListeners();
    setupPresetButtons();
    setupAuthListeners();
    setupResumeDropzone();
    setupProfileModal();
    loadAnalyticsData();
    checkAuthStatus();

    // Auto-load the high-risk preset initially to showcase prediction and recommendations
    applyPreset('at_risk', false);

    // Check URL hash for initial section routing
    if (window.location.hash) {
        const hashSection = window.location.hash.replace('#', '');
        if (document.getElementById(hashSection)) {
            switchSection(hashSection);
        }
    }
}

// ==========================================================================
// NAVIGATION & SECTION SWITCHING CONTROLLER (PHASE 2)
// ==========================================================================

function setupNavigation() {
    const navButtons = document.querySelectorAll('#main-nav .nav-item');
    navButtons.forEach(btn => {
        btn.addEventListener('click', (e) => {
            const sectionId = btn.getAttribute('data-section');
            if (sectionId) {
                switchSection(sectionId);
            }
        });
    });

    // Mobile Hamburger Toggle
    const mobileBtn = document.getElementById('mobile-menu-toggle');
    const mainNav = document.getElementById('main-nav');
    if (mobileBtn && mainNav) {
        mobileBtn.addEventListener('click', () => {
            mainNav.classList.toggle('mobile-open');
        });
    }

    // Brand click returns to overview
    const brandBtn = document.getElementById('brand-home-btn');
    if (brandBtn) {
        brandBtn.addEventListener('click', () => switchSection('overview'));
        brandBtn.style.cursor = 'pointer';
    }

    // Handle browser back/forward buttons
    window.addEventListener('popstate', () => {
        if (window.location.hash) {
            const sec = window.location.hash.replace('#', '');
            if (document.getElementById(sec)) switchSection(sec, false);
        }
    });
}

/**
 * Switches the displayed section, hiding all others and updating the navigation highlight.
 */
window.switchSection = function(sectionId, updateHash = true) {
    // Hide all main and secondary sections
    const allSections = document.querySelectorAll('.section');
    allSections.forEach(sec => {
        sec.classList.remove('active');
        if (sec.classList.contains('secondary-section')) {
            sec.classList.add('hidden');
        }
    });

    // Activate selected section
    const targetSection = document.getElementById(sectionId);
    if (targetSection) {
        targetSection.classList.add('active');
        targetSection.classList.remove('hidden');
    }

    // Update active class on top navigation buttons
    const navButtons = document.querySelectorAll('#main-nav .nav-item');
    navButtons.forEach(btn => {
        if (btn.getAttribute('data-section') === sectionId) {
            btn.classList.add('active');
        } else {
            btn.classList.remove('active');
        }
    });

    // Close mobile navigation drawer if open
    const mainNav = document.getElementById('main-nav');
    if (mainNav) mainNav.classList.remove('mobile-open');

    // Update URL hash
    if (updateHash) {
        window.history.pushState(null, '', `#${sectionId}`);
    }

    // Scroll to top of viewport
    window.scrollTo({ top: 0, behavior: 'smooth' });

    // Trigger lazy loading of section data
    if (sectionId === 'my-progress') {
        refreshStudentDashboard();
    } else if (sectionId === 'recommendations') {
        loadJobRoles();
        loadRoadmap();
    } else if (sectionId === 'resume-analyzer') {
        loadLatestResume();
    }
};

/**
 * Opens a secondary section (such as Model Benchmarks or EDA Gallery) from overview links.
 */
window.showSecondaryView = function(secondarySectionId) {
    const allSections = document.querySelectorAll('.section');
    allSections.forEach(sec => sec.classList.remove('active'));

    const target = document.getElementById(secondarySectionId);
    if (target) {
        target.classList.remove('hidden');
        target.classList.add('active');
        window.scrollTo({ top: 0, behavior: 'smooth' });
    }
};

// ==========================================================================
// GUIDANCE SUBTABS CONTROLLER
// ==========================================================================

function setupGuidanceSubtabs() {
    const subtabButtons = document.querySelectorAll('#guidance-subtabs .subtab-btn');
    subtabButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            subtabButtons.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');

            const targetPaneId = btn.getAttribute('data-subtab');
            const panes = document.querySelectorAll('.guidance-tab-pane');
            panes.forEach(p => {
                if (p.id === targetPaneId) {
                    p.classList.remove('hidden');
                    p.classList.add('active');
                } else {
                    p.classList.add('hidden');
                    p.classList.remove('active');
                }
            });

            if (targetPaneId === 'tab-roles') loadJobRoles();
            if (targetPaneId === 'tab-roadmap') loadRoadmap();
        });
    });

    // Roadmap update goal button
    const btnUpdateGoal = document.getElementById('btn-update-career-goal');
    if (btnUpdateGoal) {
        btnUpdateGoal.addEventListener('click', async () => {
            const select = document.getElementById('roadmap-goal-select');
            const goal = select.value;
            try {
                const res = await fetch('/api/career/roadmap/select', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ career_goal: goal })
                });
                const data = await res.json();
                if (res.ok) {
                    await loadRoadmap();
                } else if (data.auth_required) {
                    openAuthModal('login');
                }
            } catch (err) {
                console.error('Failed to update goal:', err);
            }
        });
    }
}

// ==========================================================================
// PREDICTOR FORM & WHAT-IF ENGINE CONTROLLER
// ==========================================================================

function setupFormListeners() {
    const form = document.getElementById('prediction-form');
    if (form) {
        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            await runPredictionFlow();
        });

        // Stale inputs warning: notify user if inputs are modified
        form.addEventListener('input', () => {
            const stale = document.getElementById('stale-warning');
            if (stale) stale.classList.remove('hidden');
        });
    }

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

    const btnSaveProfile = document.getElementById('btn-save-to-profile');
    if (btnSaveProfile) {
        btnSaveProfile.addEventListener('click', async () => {
            await savePredictorToProfile();
        });
    }
}

function setupPresetButtons() {
    const btnAtRisk = document.getElementById('btn-preset-at-risk');
    const btnPlaced = document.getElementById('btn-preset-placed');
    const btnBorderline = document.getElementById('btn-preset-borderline');
    const btnReset = document.getElementById('btn-reset-form');

    if (btnAtRisk) btnAtRisk.addEventListener('click', () => applyPreset('at_risk', true));
    if (btnPlaced) btnPlaced.addEventListener('click', () => applyPreset('placed', true));
    if (btnBorderline) btnBorderline.addEventListener('click', () => applyPreset('borderline', true));

    if (btnReset) {
        btnReset.addEventListener('click', () => {
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
}

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

function renderPredictionResult(data) {
    document.getElementById('result-placeholder').classList.add('hidden');
    const resultContent = document.getElementById('result-content');
    resultContent.classList.remove('hidden');

    const badgePred = document.getElementById('badge-prediction');
    const isPlaced = data.prediction === 'Placed';
    badgePred.textContent = data.prediction === 'Placed' ? 'Placed' : 'Not Placed';
    badgePred.className = `prediction-badge ${isPlaced ? 'placed' : 'not-placed'}`;

    const probPct = data.placement_percentage;
    document.getElementById('val-placement-prob').textContent = `${probPct.toFixed(1)}%`;
    document.getElementById('val-non-prob').textContent = `${(data.non_placement_probability * 100).toFixed(1)}%`;
    document.getElementById('val-status-flag').textContent = `Class ${data.predicted_class} (${data.prediction})`;

    const fillBar = document.getElementById('prob-fill-bar');
    fillBar.style.width = `${Math.min(100, Math.max(0, probPct))}%`;
    fillBar.className = 'probability-fill';
    if (data.risk_level === 'Low') fillBar.classList.add('low-risk');
    else if (data.risk_level === 'Medium') fillBar.classList.add('med-risk');
    else fillBar.classList.add('high-risk');

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

// ==========================================================================
// AUTHENTICATION & STUDENT SESSION (PHASE 3)
// ==========================================================================

async function checkAuthStatus() {
    try {
        const res = await fetch('/api/auth/me');
        const data = await res.json();
        const unauthBtn = document.getElementById('nav-btn-auth');
        const userProfile = document.getElementById('nav-user-profile');
        const btnSaveProfile = document.getElementById('btn-save-to-profile');

        if (data.logged_in && data.student) {
            currentUser = data.student;
            if (unauthBtn) unauthBtn.classList.add('hidden');
            if (userProfile) {
                userProfile.classList.remove('hidden');
                document.getElementById('nav-user-name').textContent = currentUser.full_name.split(' ')[0];
                document.getElementById('nav-user-role').textContent = currentUser.target_role || 'Student';
                document.getElementById('nav-avatar-initial').textContent = currentUser.full_name.charAt(0).toUpperCase();
            }
            if (btnSaveProfile) btnSaveProfile.classList.remove('hidden');
        } else {
            currentUser = null;
            if (unauthBtn) unauthBtn.classList.remove('hidden');
            if (userProfile) userProfile.classList.add('hidden');
            if (btnSaveProfile) btnSaveProfile.classList.add('hidden');
        }
    } catch (err) {
        console.error('Error checking auth status:', err);
    }
}

function setupAuthListeners() {
    const navAuthBtn = document.getElementById('nav-btn-auth');
    if (navAuthBtn) {
        navAuthBtn.addEventListener('click', () => openAuthModal('login'));
    }

    const logoutBtn = document.getElementById('nav-btn-logout');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', async () => {
            try {
                await fetch('/api/auth/logout', { method: 'POST' });
                currentUser = null;
                await checkAuthStatus();
                switchSection('overview');
            } catch (err) {
                console.error('Logout error:', err);
            }
        });
    }

    // Login Form Submit
    const loginForm = document.getElementById('login-form');
    if (loginForm) {
        loginForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const email = document.getElementById('login-email').value;
            const password = document.getElementById('login-password').value;
            const errAlert = document.getElementById('login-error-alert');
            const errMsg = document.getElementById('login-error-msg');
            const submitBtn = document.getElementById('btn-submit-login');

            try {
                errAlert.classList.add('hidden');
                submitBtn.disabled = true;
                submitBtn.textContent = 'Signing in...';

                const res = await fetch('/api/auth/login', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ email, password })
                });
                const data = await res.json();

                if (!res.ok || data.status !== 'success') {
                    throw new Error(data.error || 'Invalid email or password.');
                }

                currentUser = data.student;
                closeAuthModal();
                await checkAuthStatus();
                switchSection('my-progress');
            } catch (err) {
                errMsg.textContent = err.message;
                errAlert.classList.remove('hidden');
            } finally {
                submitBtn.disabled = false;
                submitBtn.textContent = 'Sign In';
            }
        });
    }

    // Register Form Submit
    const regForm = document.getElementById('register-form');
    if (regForm) {
        regForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const fullName = document.getElementById('reg-name').value;
            const email = document.getElementById('reg-email').value;
            const password = document.getElementById('reg-password').value;
            const targetRole = document.getElementById('reg-role').value;
            const errAlert = document.getElementById('reg-error-alert');
            const errMsg = document.getElementById('reg-error-msg');
            const submitBtn = document.getElementById('btn-submit-register');

            try {
                errAlert.classList.add('hidden');
                submitBtn.disabled = true;
                submitBtn.textContent = 'Creating account...';

                const res = await fetch('/api/auth/register', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ full_name: fullName, email, password, target_role: targetRole })
                });
                const data = await res.json();

                if (!res.ok || data.status !== 'success') {
                    throw new Error(data.error || 'Registration failed.');
                }

                currentUser = data.student;
                closeAuthModal();
                await checkAuthStatus();
                switchSection('my-progress');
            } catch (err) {
                errMsg.textContent = err.message;
                errAlert.classList.remove('hidden');
            } finally {
                submitBtn.disabled = false;
                submitBtn.textContent = 'Create Account';
            }
        });
    }
}

window.openAuthModal = function(tab = 'login') {
    const modal = document.getElementById('auth-modal');
    modal.classList.remove('hidden');
    setAuthTab(tab);
};

window.closeAuthModal = function() {
    const modal = document.getElementById('auth-modal');
    modal.classList.add('hidden');
};

window.setAuthTab = function(tab) {
    const loginBtn = document.getElementById('tab-btn-login');
    const regBtn = document.getElementById('tab-btn-register');
    const loginForm = document.getElementById('login-form');
    const regForm = document.getElementById('register-form');

    if (tab === 'login') {
        loginBtn.classList.add('active');
        regBtn.classList.remove('active');
        loginForm.classList.remove('hidden');
        regForm.classList.add('hidden');
    } else {
        loginBtn.classList.remove('active');
        regBtn.classList.add('active');
        loginForm.classList.add('hidden');
        regForm.classList.remove('hidden');
    }
};

async function savePredictorToProfile() {
    try {
        const payload = getFormPayload();
        payload.save_snapshot = true;
        payload.assessment_label = "Predictor Manual Save";

        const res = await fetch('/api/student/profile', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        const data = await res.json();
        if (res.ok) {
            alert('Saved current metrics to your Student Profile & Progress History!');
        } else if (data.auth_required) {
            openAuthModal('login');
        } else {
            alert('Error: ' + data.error);
        }
    } catch (err) {
        alert('Failed to save to profile: ' + err.message);
    }
}

// ==========================================================================
// STUDENT DASHBOARD & PROGRESS TRACKER (PHASE 4 & 5)
// ==========================================================================

async function refreshStudentDashboard() {
    const guestCallout = document.getElementById('progress-guest-callout');
    const dashContent = document.getElementById('student-dashboard-content');

    if (!currentUser) {
        guestCallout.classList.remove('hidden');
        dashContent.classList.add('hidden');
        return;
    }

    guestCallout.classList.add('hidden');
    dashContent.classList.remove('hidden');

    try {
        // 1. Fetch Profile
        const profRes = await fetch('/api/student/profile');
        if (profRes.status === 401) {
            currentUser = null;
            refreshStudentDashboard();
            return;
        }
        const profData = await profRes.json();
        const p = profData.profile || {};
        const pred = profData.prediction;

        document.getElementById('dash-student-name').textContent = profData.student.full_name;
        document.getElementById('dash-student-email').textContent = profData.student.email;
        document.getElementById('dash-target-role').textContent = p.target_role || 'Software Developer';
        document.getElementById('dash-avatar-lg').textContent = profData.student.full_name.charAt(0).toUpperCase();

        document.getElementById('dash-metric-cgpa').textContent = (p.CGPA || 0.0).toFixed(2);
        document.getElementById('dash-metric-aptitude').textContent = (p.AptitudeTestScore || 0.0).toFixed(1);
        document.getElementById('dash-metric-projects').textContent = p.Projects || 0;

        if (pred) {
            document.getElementById('dash-metric-prob').textContent = `${pred.placement_percentage}%`;
            document.getElementById('dash-metric-risk').textContent = `${pred.risk_level} Risk`;
        } else {
            document.getElementById('dash-metric-prob').textContent = '--%';
            document.getElementById('dash-metric-risk').textContent = 'Pending';
        }

        // 2. Fetch Progress History
        const progRes = await fetch('/api/student/progress');
        const progData = await progRes.json();
        renderProgressTimeline(progData.history || []);
        renderDiagnostics(progData.improvements || [], progData.needs_attention || []);

        // 3. Fetch Badges
        await loadStudentBadges();

    } catch (err) {
        console.error('Error refreshing student dashboard:', err);
    }
}

function renderProgressTimeline(history) {
    const tbody = document.getElementById('progress-history-tbody');
    tbody.innerHTML = '';

    if (!history || history.length === 0) {
        tbody.innerHTML = `<tr><td colspan="8" class="text-center text-muted" style="padding: 2rem;">No saved assessments yet. Click "Take Assessment Snapshot" or use the Predictor to record your first baseline.</td></tr>`;
    } else {
        history.slice().reverse().forEach(h => {
            const tr = document.createElement('tr');
            const dateStr = h.created_at ? new Date(h.created_at).toLocaleDateString() : 'Recent';
            tr.innerHTML = `
                <td>${dateStr}</td>
                <td><strong>${h.assessment_label || 'Snapshot'}</strong></td>
                <td>${h.cgpa.toFixed(2)}</td>
                <td>${h.aptitude_score.toFixed(1)}</td>
                <td>${h.projects}</td>
                <td><strong>${(h.placement_probability * 100).toFixed(1)}%</strong></td>
                <td><span class="risk-badge ${h.risk_level.toLowerCase()}">${h.risk_level}</span></td>
                <td>${h.predicted_status}</td>
            `;
            tbody.appendChild(tr);
        });
    }

    // Chart.js Progress Timeline
    const canvas = document.getElementById('chart-student-progress');
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (studentProgressChartInstance) {
        studentProgressChartInstance.destroy();
        studentProgressChartInstance = null;
    }

    const labels = history.map((h, i) => `${h.assessment_label || 'S' + (i+1)}`);
    const probData = history.map(h => (h.placement_probability * 100).toFixed(1));
    const aptData = history.map(h => h.aptitude_score.toFixed(1));

    studentProgressChartInstance = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels.length > 0 ? labels : ['Baseline'],
            datasets: [
                {
                    label: 'Placement Probability (%)',
                    data: probData.length > 0 ? probData : [0],
                    borderColor: '#38bdf8',
                    backgroundColor: 'rgba(56, 189, 248, 0.1)',
                    tension: 0.3,
                    fill: true,
                    pointRadius: 5
                },
                {
                    label: 'Aptitude Test Score',
                    data: aptData.length > 0 ? aptData : [0],
                    borderColor: '#a855f7',
                    borderDash: [5, 5],
                    tension: 0.3,
                    fill: false,
                    pointRadius: 4
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { labels: { color: '#cbd5e1' } }
            },
            scales: {
                y: {
                    min: 0,
                    max: 100,
                    grid: { color: 'rgba(255, 255, 255, 0.06)' },
                    ticks: { color: '#94a3b8' }
                },
                x: {
                    grid: { display: false },
                    ticks: { color: '#cbd5e1' }
                }
            }
        }
    });
}

function renderDiagnostics(improvements, attention) {
    const listImp = document.getElementById('list-progress-improvements');
    const listAtt = document.getElementById('list-progress-attention');

    if (improvements.length > 0) {
        listImp.innerHTML = improvements.map(item => `<li>${item}</li>`).join('');
    } else {
        listImp.innerHTML = `<li class="text-muted">Record subsequent snapshots to detect positive trajectory velocity.</li>`;
    }

    if (attention.length > 0) {
        listAtt.innerHTML = attention.map(item => `<li>${item}</li>`).join('');
    } else {
        listAtt.innerHTML = `<li class="text-muted">Maintain current academic standards and build practical portfolio projects.</li>`;
    }
}

function setupProfileModal() {
    const btnEdit = document.getElementById('btn-edit-student-profile');
    if (btnEdit) {
        btnEdit.addEventListener('click', async () => {
            await openProfileEditModal();
        });
    }

    const btnSnapshot = document.getElementById('btn-record-new-snapshot');
    if (btnSnapshot) {
        btnSnapshot.addEventListener('click', async () => {
            await openProfileEditModal();
        });
    }

    const editForm = document.getElementById('edit-profile-form');
    if (editForm) {
        editForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const payload = {
                CGPA: parseFloat(document.getElementById('edit-cgpa').value),
                SSC_Marks: parseFloat(document.getElementById('edit-ssc').value),
                HSC_Marks: parseFloat(document.getElementById('edit-hsc').value),
                AptitudeTestScore: parseFloat(document.getElementById('edit-aptitude').value),
                SoftSkillsRating: parseFloat(document.getElementById('edit-soft').value),
                Projects: parseInt(document.getElementById('edit-projects').value, 10),
                "Workshops/Certifications": parseInt(document.getElementById('edit-certs').value, 10),
                Internships: parseInt(document.getElementById('edit-internships').value, 10),
                ExtracurricularActivities: document.getElementById('edit-extra').value,
                PlacementTraining: document.getElementById('edit-training').value,
                target_role: document.getElementById('edit-role').value,
                save_snapshot: document.getElementById('edit-save-snapshot').checked,
                assessment_label: "Profile Update Snapshot"
            };

            const errAlert = document.getElementById('edit-profile-error');
            const errMsg = document.getElementById('edit-profile-error-msg');
            const submitBtn = document.getElementById('btn-submit-edit-profile');

            try {
                errAlert.classList.add('hidden');
                submitBtn.disabled = true;

                const res = await fetch('/api/student/profile', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                });
                const data = await res.json();

                if (!res.ok || data.status !== 'success') {
                    throw new Error(data.error || 'Failed to update profile.');
                }

                closeProfileEditModal();
                await refreshStudentDashboard();
            } catch (err) {
                errMsg.textContent = err.message;
                errAlert.classList.remove('hidden');
            } finally {
                submitBtn.disabled = false;
            }
        });
    }
}

async function openProfileEditModal() {
    try {
        const res = await fetch('/api/student/profile');
        if (!res.ok) {
            openAuthModal('login');
            return;
        }
        const data = await res.json();
        const p = data.profile || {};

        document.getElementById('edit-cgpa').value = p.CGPA || '';
        document.getElementById('edit-ssc').value = p.SSC_Marks || '';
        document.getElementById('edit-hsc').value = p.HSC_Marks || '';
        document.getElementById('edit-aptitude').value = p.AptitudeTestScore || '';
        document.getElementById('edit-soft').value = p.SoftSkillsRating || 4.0;
        document.getElementById('edit-projects').value = p.Projects !== undefined ? p.Projects : 1;
        document.getElementById('edit-certs').value = p["Workshops/Certifications"] || 0;
        document.getElementById('edit-internships').value = p.Internships || 0;
        document.getElementById('edit-extra').value = p.ExtracurricularActivities || 'No';
        document.getElementById('edit-training').value = p.PlacementTraining || 'No';
        document.getElementById('edit-role').value = p.target_role || 'Software Developer';

        document.getElementById('profile-edit-modal').classList.remove('hidden');
    } catch (err) {
        console.error('Error opening edit modal:', err);
    }
}

window.closeProfileEditModal = function() {
    document.getElementById('profile-edit-modal').classList.add('hidden');
};

// ==========================================================================
// GAMIFICATION & ACHIEVEMENT BADGES (PHASE 9)
// ==========================================================================

async function loadStudentBadges() {
    try {
        const res = await fetch('/api/student/badges');
        if (!res.ok) return;
        const data = await res.json();
        const container = document.getElementById('badges-container');
        const pill = document.getElementById('badge-count-pill');
        if (!container) return;

        pill.innerHTML = `Earned: <strong>${data.earned_count} / ${data.total_count}</strong>`;
        container.innerHTML = '';

        data.badges.forEach(b => {
            const card = document.createElement('div');
            card.className = `badge-card ${b.is_earned ? 'earned' : 'unearned'}`;
            const dateStr = b.earned_at ? `Earned: ${new Date(b.earned_at).toLocaleDateString()}` : 'In Progress';

            card.innerHTML = `
                <div class="badge-top-row">
                    <div class="badge-icon-wrap">
                        <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"></polygon>
                        </svg>
                    </div>
                    <span class="badge-status-tag ${b.is_earned ? 'earned' : 'in-progress'}">${b.is_earned ? '✓ Unlocked' : 'Locked'}</span>
                </div>
                <h4 class="badge-title">${b.badge_title}</h4>
                <p class="badge-desc">${b.description}</p>
                <div class="badge-criteria-box">
                    <span>Criteria: ${b.criteria}</span>
                </div>
                <div class="badge-progress-info">
                    ${b.is_earned ? dateStr : 'Progress: ' + (b.progress_info || 'Evaluating')}
                </div>
            `;
            container.appendChild(card);
        });
    } catch (err) {
        console.error('Failed to load badges:', err);
    }
}

// ==========================================================================
// CAREER ROADMAP & JOB ROLE RECOMMENDATIONS (PHASE 6 & 8)
// ==========================================================================

async function loadJobRoles() {
    const container = document.getElementById('job-roles-container');
    if (!container) return;

    try {
        container.innerHTML = `
            <div class="loading-state">
                <div class="spinner"></div>
                <p>Computing transparent skill alignment across 5 technology roles...</p>
            </div>
        `;

        const res = await fetch('/api/career/roles');
        const data = await res.json();
        container.innerHTML = '';

        data.roles.forEach(role => {
            const card = document.createElement('div');
            card.className = 'glass-card job-role-card';
            const badgeClass = role.match_percentage >= 70 ? '' : 'medium';

            const matchedTags = role.matched_skills.map(s => `<span class="skill-tag matched">${s}</span>`).join('');
            const missingTags = role.missing_skills.map(s => `<span class="skill-tag missing">${s}</span>`).join('');
            const projectsList = role.suggested_projects.map(p => `<li>${p}</li>`).join('');
            const topicsList = role.learning_topics.map(t => `<li>${t}</li>`).join('');

            card.innerHTML = `
                <div class="role-card-header">
                    <div>
                        <h3 class="role-title">${role.title}</h3>
                    </div>
                    <div class="role-match-badge ${badgeClass}">${role.match_percentage}% Match</div>
                </div>
                <p class="role-desc">${role.description}</p>

                <div class="role-skills-section">
                    <span class="role-skills-title">Matched Competencies</span>
                    <div>${matchedTags || '<span class="text-muted" style="font-size:0.8rem;">None detected yet</span>'}</div>
                </div>

                <div class="role-skills-section">
                    <span class="role-skills-title">Potential Skill Gaps</span>
                    <div>${missingTags || '<span class="text-muted" style="font-size:0.8rem;">All core skills matched!</span>'}</div>
                </div>

                <div class="role-reason-box">
                    <strong>Why Recommended:</strong> ${role.recommendation_reason}
                </div>

                <div class="role-skills-section" style="margin-top: 1rem;">
                    <span class="role-skills-title">Recommended Practical Projects</span>
                    <ul class="role-projects-list">${projectsList}</ul>
                </div>

                <div class="role-skills-section">
                    <span class="role-skills-title">Key Learning Topics</span>
                    <ul class="role-topics-list">${topicsList}</ul>
                </div>
            `;
            container.appendChild(card);
        });
    } catch (err) {
        container.innerHTML = `<div class="alert-box error"><span>Failed to load job roles: ${err.message}</span></div>`;
    }
}

async function loadRoadmap() {
    const container = document.getElementById('roadmap-milestones-container');
    if (!container) return;

    try {
        const res = await fetch('/api/career/roadmap');
        if (res.status === 401) {
            container.innerHTML = `
                <div class="glass-card guest-callout-card">
                    <div class="callout-content">
                        <h3>Personalized Roadmap Requires Student Login</h3>
                        <p>Sign in to configure your personalized career milestones, track completed projects, and save your progress.</p>
                    </div>
                    <button type="button" class="btn btn-primary" onclick="openAuthModal('login')">Sign In</button>
                </div>
            `;
            return;
        }

        const data = await res.json();
        const select = document.getElementById('roadmap-goal-select');
        if (select && data.career_goal) select.value = data.career_goal;

        const fill = document.getElementById('roadmap-progress-fill');
        const pctLabel = document.getElementById('val-roadmap-progress-pct');
        if (fill && pctLabel) {
            fill.style.width = `${data.progress_percentage}%`;
            pctLabel.textContent = `${data.progress_percentage}% (${data.completed_count}/${data.total_count} done)`;
        }

        container.innerHTML = '';
        data.milestones.forEach(m => {
            const item = document.createElement('div');
            item.className = `milestone-item ${m.is_completed ? 'completed' : ''}`;
            const prioClass = (m.priority || 'medium').toLowerCase();

            item.innerHTML = `
                <div class="milestone-checkbox-wrap">
                    <input type="checkbox" class="milestone-checkbox" data-key="${m.milestone_key}" ${m.is_completed ? 'checked' : ''}>
                </div>
                <div class="milestone-details">
                    <div class="milestone-meta-row">
                        <span class="milestone-category-pill">${m.category}</span>
                        <span class="milestone-priority-pill ${prioClass}">${m.priority} Priority</span>
                    </div>
                    <h4 class="milestone-title">${m.title}</h4>
                    <p class="milestone-desc">${m.description}</p>
                </div>
            `;
            container.appendChild(item);
        });

        // Attach milestone toggling event
        container.querySelectorAll('.milestone-checkbox').forEach(box => {
            box.addEventListener('change', async (e) => {
                const key = box.getAttribute('data-key');
                const isChecked = box.checked;
                await toggleMilestone(key, isChecked);
            });
        });

    } catch (err) {
        container.innerHTML = `<div class="alert-box error"><span>Failed to load roadmap: ${err.message}</span></div>`;
    }
}

async function toggleMilestone(key, completed) {
    try {
        const res = await fetch('/api/career/roadmap/milestone', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ milestone_key: key, is_completed: completed })
        });
        if (res.ok) {
            await loadRoadmap();
        }
    } catch (err) {
        console.error('Failed to toggle milestone:', err);
    }
}

// ==========================================================================
// RESUME ANALYZER (PHASE 7)
// ==========================================================================

function setupResumeDropzone() {
    const dropzone = document.getElementById('resume-dropzone');
    const fileInput = document.getElementById('resume-file-input');
    const selectedInfo = document.getElementById('file-selected-info');
    const dropText = document.getElementById('dropzone-text');
    const filenameLabel = document.getElementById('selected-filename');
    const clearBtn = document.getElementById('btn-clear-file');
    const form = document.getElementById('resume-upload-form');

    if (!dropzone || !fileInput) return;

    ['dragenter', 'dragover'].forEach(eventName => {
        dropzone.addEventListener(eventName, (e) => {
            e.preventDefault();
            dropzone.classList.add('dragover');
        });
    });

    ['dragleave', 'drop'].forEach(eventName => {
        dropzone.addEventListener(eventName, (e) => {
            e.preventDefault();
            dropzone.classList.remove('dragover');
        });
    });

    dropzone.addEventListener('drop', (e) => {
        const files = e.dataTransfer.files;
        if (files && files.length > 0) {
            fileInput.files = files;
            showFileSelected(files[0].name);
        }
    });

    fileInput.addEventListener('change', () => {
        if (fileInput.files && fileInput.files.length > 0) {
            showFileSelected(fileInput.files[0].name);
        }
    });

    if (clearBtn) {
        clearBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            fileInput.value = '';
            selectedInfo.classList.add('hidden');
            dropText.classList.remove('hidden');
        });
    }

    function showFileSelected(name) {
        filenameLabel.textContent = name;
        dropText.classList.add('hidden');
        selectedInfo.classList.remove('hidden');
    }

    // Submit Resume Form
    if (form) {
        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            const submitBtn = document.getElementById('btn-submit-resume');
            const errAlert = document.getElementById('resume-error-alert');
            const errMsg = document.getElementById('resume-error-msg');

            if (!fileInput.files || fileInput.files.length === 0) {
                errMsg.textContent = 'Please choose a PDF resume to upload.';
                errAlert.classList.remove('hidden');
                return;
            }

            const formData = new FormData(form);

            try {
                errAlert.classList.add('hidden');
                submitBtn.disabled = true;
                submitBtn.innerHTML = `Extracting & Analyzing...`;

                const res = await fetch('/api/resume/upload', {
                    method: 'POST',
                    body: formData
                });
                const data = await res.json();

                if (!res.ok || data.status !== 'success') {
                    if (data.auth_required) {
                        openAuthModal('login');
                        return;
                    }
                    throw new Error(data.error || 'Failed to analyze resume.');
                }

                latestResumeRecordId = data.resume_id;
                renderResumeReport(data.analysis);

            } catch (err) {
                errMsg.textContent = err.message;
                errAlert.classList.remove('hidden');
            } finally {
                submitBtn.disabled = false;
                submitBtn.innerHTML = `
                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="20 6 9 17 4 12"></polyline></svg>
                    Parse & Benchmark Resume
                `;
            }
        });
    }

    // Delete Resume Button
    const deleteBtn = document.getElementById('btn-delete-resume');
    if (deleteBtn) {
        deleteBtn.addEventListener('click', async () => {
            if (!latestResumeRecordId) return;
            if (!confirm('Are you sure you want to permanently delete your resume and analysis?')) return;

            try {
                const res = await fetch(`/api/resume/${latestResumeRecordId}`, { method: 'DELETE' });
                if (res.ok) {
                    latestResumeRecordId = null;
                    document.getElementById('resume-placeholder').classList.remove('hidden');
                    document.getElementById('resume-report-content').classList.add('hidden');
                    fileInput.value = '';
                    selectedInfo.classList.add('hidden');
                    dropText.classList.remove('hidden');
                }
            } catch (err) {
                console.error('Delete error:', err);
            }
        });
    }
}

async function loadLatestResume() {
    try {
        const res = await fetch('/api/resume/latest');
        if (!res.ok) return;
        const data = await res.json();
        if (data.has_resume && data.resume) {
            latestResumeRecordId = data.resume.id;
            renderResumeReport({
                target_role: data.resume.target_role,
                match_percentage: data.resume.match_percentage,
                detected_skills: data.resume.detected_skills || [],
                matched_skills: data.resume.matched_skills || [],
                missing_skills: data.resume.missing_skills || [],
                suggestions: data.resume.suggestions || []
            });
        }
    } catch (err) {
        console.error('Failed to load latest resume:', err);
    }
}

function renderResumeReport(analysis) {
    document.getElementById('resume-placeholder').classList.add('hidden');
    const content = document.getElementById('resume-report-content');
    content.classList.remove('hidden');

    document.getElementById('report-target-role').textContent = `${analysis.target_role} Alignment`;
    document.getElementById('report-match-score').textContent = `${analysis.match_percentage}%`;

    const detectedCount = analysis.detected_skills.length;
    document.getElementById('count-detected-skills').textContent = detectedCount;

    const tagsDetected = document.getElementById('tags-detected-skills');
    tagsDetected.innerHTML = analysis.detected_skills.map(s => `<span class="skill-bubble">${s}</span>`).join('') || '<span class="text-muted">No technical skills detected.</span>';

    const tagsMatched = document.getElementById('tags-matched-skills');
    tagsMatched.innerHTML = analysis.matched_skills.map(s => `<span class="skill-tag matched">${s}</span>`).join('') || '<span class="text-muted">None matched yet</span>';

    const tagsMissing = document.getElementById('tags-missing-skills');
    tagsMissing.innerHTML = analysis.missing_skills.map(s => `<span class="skill-tag missing">${s}</span>`).join('') || '<span class="text-muted">All target role skills present!</span>';

    const listSug = document.getElementById('report-suggestions-list');
    listSug.innerHTML = analysis.suggestions.map(s => `<li>${s}</li>`).join('') || `<li>Resume shows solid initial alignment with ${analysis.target_role} baseline expectations.</li>`;
}

// ==========================================================================
// REPORTS & ANALYTICS VISUALIZATIONS (PRESERVED)
// ==========================================================================

async function loadAnalyticsData() {
    try {
        const res = await fetch('/api/analytics-data');
        const resJson = await res.json();
        if (resJson.status !== 'success') return;

        const data = resJson.data;

        if (data.model_comparisons) {
            renderModelsTable(data.model_comparisons);
            renderModelsChart(data.model_comparisons);
        }
        if (data.cross_validation) {
            renderCrossValidationChart(data.cross_validation);
        }
        if (data.shap_importance) {
            renderShapChart(data.shap_importance);
        }
        if (data.risk_summary) {
            renderRiskPieChart(data.risk_summary);
        }
        if (data.placement_comparison) {
            renderBenchmarksChart(data.placement_comparison);
        }
        if (data.eda_summary) {
            const eda = data.eda_summary;
            const total = (eda.training_records || 6353) + (eda.validation_records || 1591) + (eda.test_records || 1984);
            const totalEl = document.getElementById('stat-total-records');
            if (totalEl) totalEl.textContent = total.toLocaleString();
        }
    } catch (err) {
        console.error('Error loading analytics data:', err);
    }
}

function renderModelsTable(models) {
    const tbody = document.getElementById('models-table-body');
    if (!tbody) return;
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

function renderModelsChart(models) {
    const canvas = document.getElementById('chart-models-comparison');
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
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
                { label: 'Accuracy (%)', data: accData, backgroundColor: 'rgba(56, 189, 248, 0.75)', borderRadius: 4 },
                { label: 'F1-Score (%)', data: f1Data, backgroundColor: 'rgba(99, 102, 241, 0.75)', borderRadius: 4 },
                { label: 'ROC-AUC (%)', data: rocAucData, backgroundColor: 'rgba(16, 185, 129, 0.75)', borderRadius: 4 }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { labels: { color: '#cbd5e1', font: { family: 'Plus Jakarta Sans', weight: '600' } } }
            },
            scales: {
                y: { min: 65, max: 100, grid: { color: 'rgba(255, 255, 255, 0.06)' }, ticks: { color: '#94a3b8' } },
                x: { grid: { display: false }, ticks: { color: '#cbd5e1', font: { size: 10, weight: '600' } } }
            }
        }
    });
}

function renderCrossValidationChart(cvList) {
    const canvas = document.getElementById('chart-cv-stability');
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (cvChartInstance) cvChartInstance.destroy();

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
                { label: 'Mean CV Accuracy (%)', data: accuracyMeans, backgroundColor: 'rgba(56, 189, 248, 0.8)', borderRadius: 4 },
                { label: 'Mean Recall (%)', data: recallMeans, backgroundColor: 'rgba(16, 185, 129, 0.8)', borderRadius: 4 },
                { label: 'Mean F1-Score (%)', data: f1Means, backgroundColor: 'rgba(99, 102, 241, 0.8)', borderRadius: 4 },
                { label: 'Mean ROC-AUC (%)', data: rocAucMeans, backgroundColor: 'rgba(192, 132, 252, 0.8)', borderRadius: 4 }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { position: 'top', labels: { color: '#cbd5e1', font: { family: 'Plus Jakarta Sans', weight: '600', size: 10 } } }
            },
            scales: {
                y: { min: 65, max: 100, grid: { color: 'rgba(255, 255, 255, 0.06)' }, ticks: { color: '#94a3b8' } },
                x: { grid: { display: false }, ticks: { color: '#cbd5e1', font: { size: 11, weight: '600' } } }
            }
        }
    });
}

function renderShapChart(shapList) {
    const canvas = document.getElementById('chart-shap');
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (shapChartInstance) shapChartInstance.destroy();

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

    const cleaned = shapList.map(item => ({
        name: featureLabelsMap[item.Feature] || item.Feature.replace('numeric__', '').replace('categorical__', ''),
        val: parseFloat(item.Mean_Absolute_SHAP)
    })).sort((a, b) => b.val - a.val);

    shapChartInstance = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: cleaned.map(c => c.name),
            datasets: [{
                label: 'Mean Absolute SHAP Value',
                data: cleaned.map(c => c.val.toFixed(4)),
                backgroundColor: 'rgba(6, 182, 212, 0.85)',
                borderRadius: 4
            }]
        },
        options: {
            indexAxis: 'y',
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { display: false } },
            scales: {
                x: { grid: { color: 'rgba(255, 255, 255, 0.06)' }, ticks: { color: '#94a3b8' } },
                y: { grid: { display: false }, ticks: { color: '#cbd5e1', font: { size: 10, weight: '600' } } }
            }
        }
    });
}

function renderRiskPieChart(riskList) {
    const canvas = document.getElementById('chart-risk-pie');
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (riskPieChartInstance) riskPieChartInstance.destroy();

    const labels = riskList.map(r => `${r.RiskLevel} Risk (${r.Students})`);
    const counts = riskList.map(r => r.Students);

    riskPieChartInstance = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: labels,
            datasets: [{
                data: counts,
                backgroundColor: [
                    'rgba(16, 185, 129, 0.85)',
                    'rgba(245, 158, 11, 0.85)',
                    'rgba(244, 63, 94, 0.85)'
                ],
                borderColor: '#0f172a',
                borderWidth: 3
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { position: 'bottom', labels: { color: '#cbd5e1', font: { size: 11, weight: '600' }, padding: 15 } }
            },
            cutout: '65%'
        }
    });
}

function renderBenchmarksChart(compList) {
    const canvas = document.getElementById('chart-benchmarks');
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (benchmarksChartInstance) benchmarksChartInstance.destroy();

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
                { label: 'Placed Students Mean (2,611)', data: metrics.map(m => m.placedScaled.toFixed(1)), backgroundColor: 'rgba(16, 185, 129, 0.85)', borderRadius: 4 },
                { label: 'Not Placed Students Mean (3,742)', data: metrics.map(m => m.notPlacedScaled.toFixed(1)), backgroundColor: 'rgba(244, 63, 94, 0.8)', borderRadius: 4 }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { position: 'top', labels: { color: '#cbd5e1', font: { family: 'Plus Jakarta Sans', weight: '600' } } }
            },
            scales: {
                y: { beginAtZero: true, max: 100, grid: { color: 'rgba(255, 255, 255, 0.06)' }, ticks: { color: '#94a3b8' } },
                x: { grid: { display: false }, ticks: { color: '#cbd5e1', font: { size: 10, weight: '600' } } }
            }
        }
    });
}

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
