// static/js/family.js

// ============================================================
// SESSION MANAGEMENT
// ============================================================

// Use consistent session ID across the entire application
const sessionId = localStorage.getItem('swasthya_session_id') || 'user_' + Date.now();
localStorage.setItem('swasthya_session_id', sessionId);

console.log('🏥 Family History Session ID:', sessionId);

// ============================================================
// DOM READY - INITIALIZE
// ============================================================

document.addEventListener('DOMContentLoaded', function() {
    // Load existing family history
    loadFamilyHistory();
    
    // Setup form submission
    const form = document.getElementById('family-form');
    if (form) {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            addFamilyHistory();
        });
    }
    
    // Debug: Check if elements exist
    console.log('📋 Family History Elements:');
    console.log('- Form:', document.getElementById('family-form') ? '✅' : '❌');
    console.log('- Records:', document.getElementById('family-records') ? '✅' : '❌');
    console.log('- Relation:', document.getElementById('relation') ? '✅' : '❌');
    console.log('- Condition:', document.getElementById('condition') ? '✅' : '❌');
});

// ============================================================
// LOAD FAMILY HISTORY FROM API
// ============================================================

async function loadFamilyHistory() {
    try {
        console.log('🔄 Loading family history for session:', sessionId);
        
        const response = await fetch(`/api/family-history/${sessionId}`);
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        console.log('📊 Family history data loaded:', data);
        
        displayFamilyHistory(data);
        
    } catch (error) {
        console.error('❌ Error loading family history:', error);
        const container = document.getElementById('family-records');
        if (container) {
            container.innerHTML = `
                <div class="bg-red-50 border border-red-200 p-4 rounded-lg">
                    <p class="text-red-600">⚠️ Error loading family history.</p>
                    <p class="text-red-500 text-sm">Please refresh the page and try again.</p>
                </div>
            `;
        }
    }
}

// ============================================================
// DISPLAY FAMILY HISTORY
// ============================================================

function displayFamilyHistory(data) {
    const container = document.getElementById('family-records');
    if (!container) {
        console.error('❌ Container element not found!');
        return;
    }
    
    container.innerHTML = '';
    
    // Check if we have data
    if (!data || Object.keys(data).length === 0) {
        container.innerHTML = `
            <div class="text-center py-8">
                <p class="text-gray-500">No family history records added yet.</p>
                <p class="text-gray-400 text-sm mt-2">Add your family history using the form on the left.</p>
            </div>
        `;
        return;
    }
    
    // Check if data has any valid entries
    let hasValidRecords = false;
    
    Object.entries(data).forEach(([relation, conditions]) => {
        // Skip if conditions is empty or null
        if (!conditions || conditions.length === 0) return;
        hasValidRecords = true;
        
        // Create record card
        const div = document.createElement('div');
        div.className = 'bg-gray-50 p-3 rounded-lg mb-2 border border-gray-200 hover:shadow-md transition-shadow';
        div.innerHTML = `
            <div class="flex justify-between items-start">
                <div>
                    <h4 class="font-semibold text-gray-700 capitalize">${relation}</h4>
                    <div class="flex flex-wrap gap-1 mt-1">
                        ${conditions.map(condition => 
                            `<span class="symptom-tag">${condition.replace(/_/g, ' ')}</span>`
                        ).join('')}
                    </div>
                </div>
                <button onclick="removeRelation('${relation}')" 
                        class="text-red-500 hover:text-red-700 px-2 py-1 hover:bg-red-50 rounded transition"
                        title="Remove ${relation}">
                    ✕
                </button>
            </div>
        `;
        container.appendChild(div);
    });
    
    // If no valid records found
    if (!hasValidRecords) {
        container.innerHTML = `
            <div class="text-center py-8">
                <p class="text-gray-500">No family history records added yet.</p>
                <p class="text-gray-400 text-sm mt-2">Add your family history using the form on the left.</p>
            </div>
        `;
    }
}

// ============================================================
// ADD FAMILY HISTORY
// ============================================================

async function addFamilyHistory() {
    const relation = document.getElementById('relation').value;
    const condition = document.getElementById('condition').value;
    
    console.log('📝 Adding family history:', { relation, condition });
    
    // Validation
    if (!relation) {
        alert('Please select a family member.');
        return;
    }
    
    if (!condition || condition === 'none') {
        alert('Please select a valid medical condition.');
        return;
    }
    
    try {
        const requestData = {
            session_id: sessionId,
            family_data: {
                [relation]: [condition]
            }
        };
        
        console.log('📤 Sending data:', requestData);
        
        const response = await fetch('/api/family-history', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(requestData)
        });
        
        const result = await response.json();
        console.log('📥 Response:', result);
        
        if (response.ok) {
            // Reload family history
            await loadFamilyHistory();
            
            // Show success message
            showNotification(`✅ ${relation}: ${condition} added successfully!`, 'success');
            
            // Reset form to default values
            document.getElementById('relation').value = 'father';
            document.getElementById('condition').value = 'diabetes';
            
        } else {
            showNotification('❌ Error: ' + (result.message || 'Failed to save'), 'error');
        }
        
    } catch (error) {
        console.error('❌ Error adding family history:', error);
        showNotification('❌ Error adding family history. Please try again.', 'error');
    }
}

// ============================================================
// REMOVE FAMILY HISTORY
// ============================================================

async function removeRelation(relation) {
    console.log('🗑️ Removing relation:', relation);
    
    if (!confirm(`Remove ${relation} from family history?`)) {
        return;
    }
    
    try {
        const response = await fetch('/api/family-history', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                session_id: sessionId,
                family_data: {
                    [relation]: []
                }
            })
        });
        
        const result = await response.json();
        console.log('📥 Remove response:', result);
        
        if (response.ok) {
            await loadFamilyHistory();
            showNotification(`✅ ${relation} removed successfully!`, 'success');
        } else {
            showNotification('❌ Error removing: ' + (result.message || 'Failed to remove'), 'error');
        }
        
    } catch (error) {
        console.error('❌ Error removing relation:', error);
        showNotification('❌ Error removing. Please try again.', 'error');
    }
}

// ============================================================
// NOTIFICATIONS
// ============================================================

function showNotification(message, type = 'success') {
    const colors = {
        success: 'bg-green-50 border-green-500 text-green-700',
        error: 'bg-red-50 border-red-500 text-red-700',
        warning: 'bg-yellow-50 border-yellow-500 text-yellow-700',
        info: 'bg-blue-50 border-blue-500 text-blue-700'
    };
    
    const icon = {
        success: '✅',
        error: '❌',
        warning: '⚠️',
        info: 'ℹ️'
    };
    
    const div = document.createElement('div');
    div.className = `fixed top-4 right-4 px-4 py-3 rounded-lg border ${colors[type] || colors.info} z-50 shadow-lg max-w-md transition-all duration-500`;
    div.innerHTML = `
        <div class="flex items-center space-x-2">
            <span class="text-xl">${icon[type] || 'ℹ️'}</span>
            <span>${message}</span>
        </div>
    `;
    document.body.appendChild(div);
    
    // Auto remove after 3 seconds
    setTimeout(() => {
        div.style.opacity = '0';
        div.style.transform = 'translateY(-20px)';
        setTimeout(() => {
            div.remove();
        }, 500);
    }, 3000);
}

// ============================================================
// DEBUGGING TOOLS (Available in browser console)
// ============================================================

// Expose functions for debugging
window.debug = {
    sessionId: sessionId,
    loadFamilyHistory: loadFamilyHistory,
    addFamilyHistory: addFamilyHistory,
    removeRelation: removeRelation,
    showNotification: showNotification,
    getSessionId: () => sessionId
};

console.log('🔧 Debugging tools available: window.debug');
console.log('   - window.debug.sessionId');
console.log('   - window.debug.loadFamilyHistory()');
console.log('   - window.debug.addFamilyHistory()');
console.log('   - window.debug.removeRelation()');

// ============================================================
// AUTO-REFRESH ON VISIBILITY CHANGE
// ============================================================

document.addEventListener('visibilitychange', function() {
    if (!document.hidden) {
        console.log('👁️ Page became visible, refreshing family history...');
        loadFamilyHistory();
    }
});

// ============================================================
// KEYBOARD SHORTCUTS
// ============================================================

document.addEventListener('keydown', function(e) {
    // Ctrl+R to refresh family history
    if (e.ctrlKey && e.key === 'r') {
        e.preventDefault();
        console.log('🔄 Manual refresh triggered');
        loadFamilyHistory();
        showNotification('🔄 Family history refreshed!', 'info');
    }
});

console.log('✅ Family History Module Loaded Successfully!');
console.log(`📋 Session ID: ${sessionId}`);