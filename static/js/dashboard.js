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
        const response = await fetch(`/api/dashboard/${sessionId}`);
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        console.log('📊 Dashboard data received:', data);
        
        updatePatientInfo(data);
        updateRiskAssessment(data);
        updateSymptoms(data);
        updateFamilyHistory(data);
        updateDiagnosis(data);
        updateRiskFactors(data);
        
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
// UPDATE FUNCTIONS
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
        const level = report.risk_level || 'Not Assessed';
        if (riskLevel) {
            riskLevel.textContent = level;
            riskLevel.className = `text-3xl font-bold mt-2 risk-${level.toLowerCase()}`;
        }
        
        const score = report.risk_score || 0;
        if (riskScore) {
            riskScore.textContent = score + '/100';
        }
        
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
        
        if (recommendations) {
            if (report.recommendations) {
                recommendations.innerHTML = report.recommendations.replace(/\n/g, '<br>');
            } else {
                recommendations.innerHTML = 'No recommendations available.';
            }
        }
    } else {
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
    
    const latest = symptomsData[symptomsData.length - 1];
    const symptoms = latest.symptoms || {};
    
    container.innerHTML = '';
    const excludeKeys = ['duration', 'duration_unit'];
    let hasSymptoms = false;
    
    for (const [symptom, present] of Object.entries(symptoms)) {
        if (!excludeKeys.includes(symptom) && present) {
            hasSymptoms = true;
            const tag = document.createElement('span');
            tag.className = 'symptom-tag';
            tag.textContent = symptom.replace(/_/g, ' ');
            container.appendChild(tag);
        }
    }
    
    if (symptoms.duration) {
        const durationTag = document.createElement('span');
        durationTag.className = 'symptom-tag bg-yellow-100 text-yellow-800';
        durationTag.innerHTML = `<i class="fa-solid fa-clock text-yellow-600 mr-1"></i> ${symptoms.duration} ${symptoms.duration_unit || 'days'}`;
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
            <a href="/family-history" class="text-blue-600 hover:text-blue-800 text-sm flex items-center gap-1 mt-1"><i class="fa-solid fa-plus-circle"></i> Add Family History</a>
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
    html += `<a href="/family-history" class="text-blue-600 hover:text-blue-800 text-sm mt-3 inline-flex items-center gap-1"><i class="fa-solid fa-pen-to-square"></i> Edit Family History</a>`;
    
    container.innerHTML = html;
}

// ============================================================
// DIAGNOSIS - SINGLE BUTTONS ONLY (FIXED)
// ============================================================

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
    
    const reportId = report.report_id || 'report_' + Date.now();
    
    let html = `
        <div class="bg-gray-50 p-5 rounded-xl border border-gray-200">
            <div class="flex justify-between items-start mb-4 flex-wrap gap-2">
                <h4 class="font-semibold text-gray-700 flex items-center"><i class="fa-solid fa-clipboard-check text-blue-600 mr-2"></i> Diagnosis Summary</h4>
                <span class="text-xs font-mono bg-gray-200 text-gray-600 px-2 py-0.5 rounded">#${reportId}</span>
            </div>
            
            <div class="mb-4">
                <h4 class="font-semibold text-gray-700 flex items-center mb-1"><i class="fa-solid fa-list-check text-blue-600 mr-2"></i> Symptoms</h4>
                ${report.symptoms && report.symptoms.length > 0 
                    ? report.symptoms.map(s => `<div class="bullet-item">${s.message}</div>`).join('')
                    : '<p class="text-gray-500 text-sm">No symptoms recorded.</p>'
                }
            </div>
            
            <div class="mb-4">
                <h4 class="font-semibold text-gray-700 flex items-center mb-1"><i class="fa-solid fa-dna text-blue-600 mr-2"></i> Family History</h4>
                ${report.family_history && Object.keys(report.family_history).length > 0
                    ? Object.entries(report.family_history).map(([rel, conds]) => 
                        `<div class="bullet-item"><span class="capitalize font-medium text-gray-800">${rel}</span>: ${conds.join(', ').replace(/_/g, ' ')}</div>`
                      ).join('')
                    : '<p class="text-gray-500 text-sm">No family history recorded.</p>'
                }
            </div>
            
            <div class="mb-4">
                <h4 class="font-semibold text-gray-700 flex items-center mb-1"><i class="fa-solid fa-stethoscope text-blue-600 mr-2"></i> Conditions</h4>
                ${report.diagnosis && report.diagnosis.conditions && report.diagnosis.conditions.length > 0
                    ? report.diagnosis.conditions.map((c, i) => 
                        `<div class="numbered-item"><span class="number">${i+1}.</span> ${c}</div>`
                      ).join('')
                    : '<p class="text-gray-500 text-sm">No conditions identified.</p>'
                }
            </div>
            
            <div class="mb-4">
                <h4 class="font-semibold text-gray-700 flex items-center mb-1"><i class="fa-solid fa-triangle-exclamation text-blue-600 mr-2"></i> Risk</h4>
                <div class="bullet-item">Risk Level: <span class="font-bold ${report.risk_level === 'High' ? 'text-red-600' : report.risk_level === 'Moderate' ? 'text-yellow-600' : 'text-green-600'}">${report.risk_level}</span></div>
                <div class="bullet-item">Risk Score: ${report.risk_score}/100</div>
                ${report.risk_factors && report.risk_factors.length > 0
                    ? report.risk_factors.map(f => `<div class="bullet-item" style="padding-left:24px;">- ${f}</div>`).join('')
                    : ''
                }
            </div>
            
            <div class="mb-4">
                <h4 class="font-semibold text-gray-700 flex items-center mb-1"><i class="fa-solid fa-pills text-blue-600 mr-2"></i> Recommendations</h4>
                ${report.recommendations
                    ? report.recommendations.split('\n').filter(r => r.trim()).map(r => 
                        `<div class="bullet-item">${r.trim()}</div>`
                      ).join('')
                    : '<p class="text-gray-500 text-sm">No recommendations available.</p>'
                }
            </div>
            
            <!-- BUTTONS - ONLY ONCE AT THE BOTTOM -->
            <div class="mt-5 pt-4 border-t border-gray-200">
                <div class="flex flex-wrap gap-2">
                    <button onclick="generateQRCode('${reportId}')" 
                            class="bg-purple-600 text-white px-4 py-2 rounded-lg hover:bg-purple-700 transition text-sm flex items-center gap-2">
                        <i class="fa-solid fa-qrcode"></i> Generate QR Code
                    </button>
                    <button onclick="window.print()" 
                            class="bg-gray-600 text-white px-4 py-2 rounded-lg hover:bg-gray-700 transition text-sm flex items-center gap-2">
                        <i class="fa-solid fa-print"></i> Print Report
                    </button>
                </div>
                <p class="text-xs text-gray-400 mt-2">QR Code contains patient details and full health report</p>
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
// QR CODE FUNCTIONS (FIXED)
// ============================================================

async function generateQRCode(reportId) {
    try {
        console.log('Generating QR code for report:', reportId);
        showNotification('Generating QR code...', 'info');
        
        const response = await fetch(`/api/report/${reportId}/qr`);
        console.log('QR API Response status:', response.status);
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        console.log('QR Data received:', data);
        
        if (data.qr_code) {
            displayPatientQRCode(data);
        } else {
            showNotification('Failed to generate QR code - no data', 'error');
        }
    } catch (error) {
        console.error('Error generating QR code:', error);
        showNotification('Error generating QR code: ' + error.message, 'error');
    }
}

function displayPatientQRCode(data) {
    const modal = document.createElement('div');
    modal.id = 'qr-modal';
    modal.className = 'fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50';
    modal.innerHTML = `
        <div class="bg-white rounded-xl p-8 max-w-md w-full mx-4 shadow-2xl max-h-[90vh] overflow-y-auto">
            <div class="flex justify-between items-center mb-4">
                <h3 class="text-xl font-bold text-gray-800 flex items-center"><i class="fa-solid fa-qrcode text-purple-600 mr-2"></i> Patient QR Code</h3>
                <button onclick="closeQRModal()" class="text-gray-500 hover:text-gray-700 text-2xl">
                    <i class="fa-solid fa-xmark"></i>
                </button>
            </div>
            
            <div class="bg-blue-50 p-4 rounded-lg mb-4">
                <div class="flex justify-between items-center">
                    <div>
                        <p class="text-xs text-gray-500">Patient</p>
                        <p class="font-bold text-gray-800">${data.patient_name || 'Unknown'}</p>
                        <p class="text-sm text-gray-600">${data.patient_email || 'N/A'}</p>
                    </div>
                    <div class="text-right">
                        <p class="text-xs text-gray-500">Risk Level</p>
                        <span class="font-bold ${data.risk_level === 'High' ? 'text-red-600' : data.risk_level === 'Moderate' ? 'text-yellow-600' : 'text-green-600'}">
                            ${data.risk_level || 'N/A'}
                        </span>
                        <p class="text-sm text-gray-600">Score: ${data.risk_score || 0}/100</p>
                    </div>
                </div>
            </div>
            
            <div class="text-center">
                <p class="text-sm text-gray-600 mb-4">Scan this QR code to view full report</p>
                <div class="bg-white p-4 rounded-lg inline-block border-2 border-gray-200 shadow-inner">
                    <img src="data:image/png;base64,${data.qr_code}" 
                         alt="QR Code" 
                         class="w-56 h-56 mx-auto">
                </div>
                <div class="mt-4 flex flex-wrap gap-2 justify-center">
                    <a href="/api/report/${data.report_id}/qr/download" 
                       class="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition text-sm flex items-center gap-1">
                        <i class="fa-solid fa-download"></i> Download QR
                    </a>
                    <button onclick="shareReport('${data.report_url}')" 
                            class="bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 transition text-sm flex items-center gap-1">
                        <i class="fa-solid fa-share-nodes"></i> Share
                    </button>
                </div>
            </div>
        </div>
    `;
    
    document.body.appendChild(modal);
}

function closeQRModal() {
    const modal = document.getElementById('qr-modal');
    if (modal) {
        modal.remove();
    }
}

function shareReport(reportUrl) {
    if (navigator.share) {
        navigator.share({
            title: 'My Health Report - SwasthyaAI',
            text: 'View my comprehensive health assessment report:',
            url: reportUrl
        }).catch(() => {});
    } else {
        navigator.clipboard.writeText(reportUrl).then(() => {
            showNotification('✅ Report URL copied to clipboard!', 'success');
        }).catch(() => {
            alert(`Share this URL:\n${reportUrl}`);
        });
    }
}

function showNotification(message, type = 'success') {
    const colors = {
        success: 'bg-green-50 border-green-200 text-green-800 shadow-md',
        error: 'bg-red-50 border-red-200 text-red-800 shadow-md',
        warning: 'bg-yellow-50 border-yellow-200 text-yellow-800 shadow-md',
        info: 'bg-blue-50 border-blue-200 text-blue-800 shadow-md'
    };
    
    const icons = {
        success: '<i class="fa-solid fa-circle-check text-green-600"></i>',
        error: '<i class="fa-solid fa-circle-xmark text-red-600"></i>',
        warning: '<i class="fa-solid fa-triangle-exclamation text-yellow-600"></i>',
        info: '<i class="fa-solid fa-circle-info text-blue-600"></i>'
    };
    
    const div = document.createElement('div');
    div.className = `fixed top-4 right-4 px-4 py-3 rounded-lg border ${colors[type] || colors.info} z-50 shadow-lg max-w-md transition-all duration-300`;
    div.innerHTML = `
        <div class="flex items-center space-x-3">
            <span class="text-lg">${icons[type] || ''}</span>
            <span class="font-medium text-sm">${message}</span>
        </div>
    `;
    document.body.appendChild(div);
    
    setTimeout(() => {
        div.style.opacity = '0';
        div.style.transform = 'translateY(-20px)';
        setTimeout(() => {
            div.remove();
        }, 500);
    }, 3000);
}

// ============================================================
// REFRESH & AUTO-UPDATE
// ============================================================

function refreshDashboard() {
    console.log('🔄 Manual refresh requested');
    loadAllDashboardData();
}

setInterval(function() {
    loadAllDashboardData();
}, 30000);

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
    if (e.ctrlKey && (e.key === 'r' || e.key === 'R')) {
        e.preventDefault();
        refreshDashboard();
    }
    
    if (e.key === 'Escape') {
        closeQRModal();
    }
});

// ============================================================
// EXPOSE FOR DEBUGGING
// ============================================================

window.dashboard = {
    sessionId: sessionId,
    loadAllDashboardData: loadAllDashboardData,
    refreshDashboard: refreshDashboard,
    generateQRCode: generateQRCode,
    closeQRModal: closeQRModal,
    shareReport: shareReport,
    showNotification: showNotification
};

console.log('🔧 Dashboard debugging tools: window.dashboard');
console.log('✅ Dashboard Module Loaded Successfully!');