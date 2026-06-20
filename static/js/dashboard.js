// static/js/dashboard.js
// ============================================================
// COMPLETELY DYNAMIC DASHBOARD - No Hardcoded Data
// ============================================================

const sessionId = localStorage.getItem('swasthya_session_id') || 'user_' + Date.now();
localStorage.setItem('swasthya_session_id', sessionId);

console.log('📊 Dashboard Session ID:', sessionId);

// ============================================================
// DOM READY - LOAD ALL DATA
// ============================================================

document.addEventListener('DOMContentLoaded', function() {
    loadAllDashboardData();
    
    // Setup refresh button
    const refreshBtn = document.getElementById('refresh-dashboard');
    if (refreshBtn) {
        refreshBtn.addEventListener('click', function() {
            loadAllDashboardData();
        });
    }
});

// ============================================================
// MAIN LOAD FUNCTION
// ============================================================

async function loadAllDashboardData() {
    console.log('🔄 Loading all dashboard data...');
    
    try {
        // Load from the new dashboard API
        const response = await fetch(`/api/dashboard/${sessionId}`);
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        console.log('📊 Dashboard data received:', data);
        
        // Update all sections
        updatePatientInfo(data);
        updateRiskAssessment(data);
        updateSymptoms(data);
        updateFamilyHistory(data);
        updateDiagnosis(data);
        updateRiskFactors(data);
        
        // Show data status
        if (data.has_data) {
            console.log('✅ Dashboard data loaded successfully');
        } else {
            console.log('ℹ️ No data yet. Start a chat and get a diagnosis.');
            showEmptyState();
        }
        
    } catch (error) {
        console.error('❌ Error loading dashboard data:', error);
        showErrorState();
    }
}

// ============================================================
// UPDATE FUNCTIONS - Each section is dynamic
// ============================================================

function updatePatientInfo(data) {
    const patientId = document.getElementById('patient-id');
    const lastVisit = document.getElementById('last-visit');
    const totalVisits = document.getElementById('total-visits');
    
    if (patientId) patientId.textContent = data.patient_id || sessionId;
    
    if (lastVisit) {
        if (data.patient_data && data.patient_data.last_visit) {
            lastVisit.textContent = new Date(data.patient_data.last_visit).toLocaleString();
        } else if (data.latest_report && data.latest_report.date) {
            lastVisit.textContent = new Date(data.latest_report.date).toLocaleString();
        } else {
            lastVisit.textContent = '-';
        }
    }
    
    if (totalVisits) {
        totalVisits.textContent = data.total_visits || 0;
    }
}

function updateRiskAssessment(data) {
    const riskLevel = document.getElementById('risk-level');
    const riskScore = document.getElementById('risk-score');
    const recommendations = document.getElementById('recommendations');
    const progressFill = document.getElementById('risk-progress-fill');
    
    const report = data.latest_report;
    
    if (report) {
        // Risk Level
        const level = report.risk_level || 'Not Assessed';
        if (riskLevel) {
            riskLevel.textContent = level;
            riskLevel.className = `text-3xl font-bold mt-2 risk-${level.toLowerCase()}`;
        }
        
        // Risk Score
        const score = report.risk_score || 0;
        if (riskScore) {
            riskScore.textContent = score + '/100';
        }
        
        // Progress Bar
        if (progressFill) {
            progressFill.style.width = `${Math.min(score, 100)}%`;
            if (score >= 70) {
                progressFill.style.background = '#ef4444';
            } else if (score >= 40) {
                progressFill.style.background = '#f59e0b';
            } else {
                progressFill.style.background = '#10b981';
            }
        }
        
        // Recommendations
        if (recommendations) {
            if (report.recommendations) {
                recommendations.innerHTML = report.recommendations.replace(/\n/g, '<br>');
            } else {
                recommendations.innerHTML = 'No recommendations available.';
            }
        }
    } else {
        // No data - show empty state
        if (riskLevel) riskLevel.textContent = 'Not Assessed';
        if (riskScore) riskScore.textContent = '-';
        if (recommendations) recommendations.textContent = 'No recommendations yet. Get a diagnosis from the chat.';
        if (progressFill) progressFill.style.width = '0%';
    }
}

function updateSymptoms(data) {
    const container = document.getElementById('symptoms-list');
    if (!container) return;
    
    const symptomsData = data.symptoms || [];
    
    if (symptomsData.length === 0) {
        container.innerHTML = '<p class="text-gray-500">No symptoms recorded yet.</p>';
        return;
    }
    
    // Get latest symptoms
    const latest = symptomsData[symptomsData.length - 1];
    const symptoms = latest.symptoms || {};
    
    container.innerHTML = '';
    const excludeKeys = ['duration', 'duration_unit'];
    let hasSymptoms = false;
    
    // Display each symptom as a tag
    for (const [symptom, present] of Object.entries(symptoms)) {
        if (!excludeKeys.includes(symptom) && present) {
            hasSymptoms = true;
            const tag = document.createElement('span');
            tag.className = 'symptom-tag';
            tag.textContent = symptom.replace(/_/g, ' ');
            container.appendChild(tag);
        }
    }
    
    // Display duration if available
    if (symptoms.duration) {
        const durationTag = document.createElement('span');
        durationTag.className = 'symptom-tag bg-yellow-100 text-yellow-800';
        durationTag.textContent = `⏱ ${symptoms.duration} ${symptoms.duration_unit || 'days'}`;
        container.appendChild(durationTag);
    }
    
    if (!hasSymptoms) {
        container.innerHTML = '<p class="text-gray-500">No symptoms recorded yet.</p>';
    }
}

function updateFamilyHistory(data) {
    const container = document.getElementById('family-history-display');
    if (!container) return;
    
    const familyHistory = data.family_history || {};
    
    if (Object.keys(familyHistory).length === 0) {
        container.innerHTML = `
            <p class="text-gray-500">No family history recorded.</p>
            <a href="/family-history" class="text-blue-600 hover:text-blue-800 text-sm">➕ Add Family History</a>
        `;
        return;
    }
    
    let html = '<div class="space-y-2">';
    for (const [relation, conditions] of Object.entries(familyHistory)) {
        if (!conditions || conditions.length === 0) continue;
        html += `
            <div class="flex items-center justify-between p-2 bg-gray-50 rounded">
                <span class="font-semibold text-gray-700 capitalize">${relation}:</span>
                <span class="text-gray-600">${conditions.join(', ').replace(/_/g, ' ')}</span>
            </div>
        `;
    }
    html += '</div>';
    html += `<a href="/family-history" class="text-blue-600 hover:text-blue-800 text-sm mt-2 inline-block">✏️ Edit Family History</a>`;
    
    container.innerHTML = html;
}

function updateDiagnosis(data) {
    const container = document.getElementById('diagnosis-display');
    if (!container) return;
    
    const report = data.latest_report;
    
    if (!report) {
        container.innerHTML = `
            <div class="text-center py-8">
                <p class="text-gray-500">No diagnosis available.</p>
                <p class="text-gray-400 text-sm mt-2">Go to <a href="/chat" class="text-blue-600">Chat</a> and click "Get Diagnosis".</p>
            </div>
        `;
        return;
    }
    
    // Build dynamic diagnosis display
    let html = `
        <div class="bg-gray-50 p-4 rounded-lg">
            <div class="mb-4">
                <h4 class="font-semibold text-gray-700">📊 Symptoms Summary</h4>
                ${report.symptoms && report.symptoms.length > 0 
                    ? report.symptoms.map(s => `<div class="bullet-item">• ${s.message}</div>`).join('')
                    : '<p class="text-gray-500">No symptoms recorded.</p>'
                }
            </div>
            
            <div class="mb-4">
                <h4 class="font-semibold text-gray-700">🧬 Family History</h4>
                ${report.family_history && Object.keys(report.family_history).length > 0
                    ? Object.entries(report.family_history).map(([rel, conds]) => 
                        `<div class="bullet-item">• ${rel}: ${conds.join(', ').replace(/_/g, ' ')}</div>`
                      ).join('')
                    : '<p class="text-gray-500">No family history recorded.</p>'
                }
            </div>
            
            <div class="mb-4">
                <h4 class="font-semibold text-gray-700">🏥 Possible Conditions</h4>
                ${report.diagnosis && report.diagnosis.conditions && report.diagnosis.conditions.length > 0
                    ? report.diagnosis.conditions.map((c, i) => 
                        `<div class="numbered-item"><span class="number">${i+1}.</span> ${c}</div>`
                      ).join('')
                    : '<p class="text-gray-500">No conditions identified.</p>'
                }
            </div>
            
            <div class="mb-4">
                <h4 class="font-semibold text-gray-700">📊 Risk Assessment</h4>
                <div class="bullet-item">• Risk Level: <span class="font-bold ${report.risk_level === 'High' ? 'text-red-600' : report.risk_level === 'Moderate' ? 'text-yellow-600' : 'text-green-600'}">${report.risk_level}</span></div>
                <div class="bullet-item">• Risk Score: ${report.risk_score}/100</div>
                <div class="bullet-item">• Risk Factors:</div>
                ${report.risk_factors && report.risk_factors.length > 0
                    ? report.risk_factors.map(f => `<div class="bullet-item" style="padding-left:24px;">- ${f}</div>`).join('')
                    : '<div class="bullet-item" style="padding-left:24px;">No specific risk factors</div>'
                }
            </div>
            
            <div class="mb-4">
                <h4 class="font-semibold text-gray-700">💊 Recommendations</h4>
                ${report.recommendations
                    ? report.recommendations.split('\n').filter(r => r.trim()).map(r => 
                        `<div class="bullet-item">• ${r.trim()}</div>`
                      ).join('')
                    : '<p class="text-gray-500">No recommendations available.</p>'
                }
            </div>
            
            <div>
                <h4 class="font-semibold text-gray-700">📋 Next Steps</h4>
                <div class="bullet-item">• Schedule a doctor consultation</div>
                <div class="bullet-item">• Monitor your symptoms daily</div>
                <div class="bullet-item">• Keep this report for your records</div>
            </div>
        </div>
    `;
    
    container.innerHTML = html;
}

function updateRiskFactors(data) {
    const container = document.getElementById('risk-factors');
    if (!container) return;
    
    const report = data.latest_report;
    
    if (!report || !report.risk_factors || report.risk_factors.length === 0) {
        container.innerHTML = '<p class="text-gray-500">No risk factors identified.</p>';
        return;
    }
    
    container.innerHTML = report.risk_factors.map(factor => 
        `<div class="flex items-center space-x-2">
            <span class="w-2 h-2 bg-red-500 rounded-full"></span>
            <span>${factor}</span>
        </div>`
    ).join('');
}

function showEmptyState() {
    const diagnosisDisplay = document.getElementById('diagnosis-display');
    if (diagnosisDisplay) {
        diagnosisDisplay.innerHTML = `
            <div class="text-center py-8">
                <p class="text-gray-500">No health data yet.</p>
                <p class="text-gray-400 text-sm mt-2">Start by chatting with the <a href="/chat" class="text-blue-600">AI Health Assistant</a>.</p>
            </div>
        `;
    }
}

function showErrorState() {
    const diagnosisDisplay = document.getElementById('diagnosis-display');
    if (diagnosisDisplay) {
        diagnosisDisplay.innerHTML = `
            <div class="text-center py-8 bg-red-50 rounded-lg">
                <p class="text-red-600">⚠️ Error loading dashboard data.</p>
                <p class="text-red-500 text-sm mt-2">Please refresh the page or try again later.</p>
                <button onclick="loadAllDashboardData()" class="mt-3 bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700">
                    🔄 Retry
                </button>
            </div>
        `;
    }
}

// ============================================================
// REFRESH & AUTO-UPDATE
// ============================================================

function refreshDashboard() {
    console.log('🔄 Manual refresh requested');
    loadAllDashboardData();
}

// Auto-refresh every 30 seconds
setInterval(function() {
    loadAllDashboardData();
}, 30000);

// Refresh when page becomes visible
document.addEventListener('visibilitychange', function() {
    if (!document.hidden) {
        console.log('👁️ Page became visible, refreshing...');
        loadAllDashboardData();
    }
});

// ============================================================
// KEYBOARD SHORTCUTS
// ============================================================

document.addEventListener('keydown', function(e) {
    // Ctrl+R or Ctrl+Shift+R to refresh dashboard
    if (e.ctrlKey && (e.key === 'r' || e.key === 'R')) {
        e.preventDefault();
        refreshDashboard();
    }
});

// ============================================================
// EXPOSE FOR DEBUGGING
// ============================================================

window.dashboard = {
    sessionId: sessionId,
    loadAllDashboardData: loadAllDashboardData,
    refreshDashboard: refreshDashboard,
    updatePatientInfo: updatePatientInfo,
    updateRiskAssessment: updateRiskAssessment,
    updateSymptoms: updateSymptoms,
    updateFamilyHistory: updateFamilyHistory,
    updateDiagnosis: updateDiagnosis,
    updateRiskFactors: updateRiskFactors
};

console.log('🔧 Dashboard debugging tools available: window.dashboard');
console.log('   - window.dashboard.refreshDashboard()');
console.log('   - window.dashboard.loadAllDashboardData()');
console.log('   - window.dashboard.sessionId');

console.log('✅ Dashboard Module Loaded Successfully!');