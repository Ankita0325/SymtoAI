const chatMessages = document.getElementById('chat-messages');
const chatInput = document.getElementById('chat-input');
const sendBtn = document.getElementById('send-btn');
const symptomInfo = document.getElementById('symptom-info');
const symptomList = document.getElementById('symptom-list');
const questionList = document.getElementById('question-list');
const familyPrompt = document.getElementById('family-history-prompt');

let sessionId = localStorage.getItem('swasthya_session_id');
if (!sessionId) {
    sessionId = 'user_' + Date.now();
    localStorage.setItem('swasthya_session_id', sessionId);
}

let isProcessing = false;
let conversationCount = 0;

// Send message on Enter key
chatInput.addEventListener('keypress', function(e) {
    if (e.key === 'Enter') {
        sendMessage();
    }
});

async function sendMessage() {
    const message = chatInput.value.trim();
    if (!message || isProcessing) return;

    chatInput.value = '';
    addMessage(message, 'user');
    
    const typingIndicator = addTypingIndicator();
    
    try {
        isProcessing = true;
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                message: message,
                session_id: sessionId
            })
        });
        
        const data = await response.json();
        
        typingIndicator.remove();
        addMessage(data.response, 'bot');
        
        conversationCount = data.conversation_count || 0;
        updateSymptomInfo(data.symptoms, data.follow_up);
        
        if (data.ask_family_history) {
            familyPrompt.classList.remove('hidden');
        }
        
    } catch (error) {
        console.error('Error:', error);
        typingIndicator.remove();
        addMessage('Sorry, I encountered an error. Please try again.', 'bot');
    } finally {
        isProcessing = false;
    }
}

function addMessage(text, sender) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `flex items-start mb-4 ${sender === 'user' ? 'justify-end' : 'justify-start'}`;
    
    const messageContent = document.createElement('div');
    messageContent.className = sender === 'user' ? 'message-user' : 'message-bot';
    
    if (sender === 'bot') {
        let formattedText = text;
        formattedText = formattedText.replace(/\n/g, '<br>');
        
        const sections = [
            { pattern: /📋\s*(𝗦𝗬𝗠𝗣𝗧𝗢𝗠\s+𝗔𝗖𝗞𝗡𝗢𝗪𝗟𝗘𝗗𝗚𝗠𝗘𝗡𝗧|SYMPTOM\s+ACKNOWLEDGEMENT|Symptom\s+Acknowledgement|COMPREHENSIVE\s+HEALTH\s+ASSESSMENT|𝗖𝗢𝗠𝗣𝗥𝗘𝗛𝗘𝗡𝗦𝗜𝗩𝗘\s+𝗛𝗘𝗔𝗟𝗧𝗛\s+𝗔𝗦𝗦𝗘𝗦𝗦𝗠𝗘𝗡𝗧)/gi, icon: '<i class="fa-solid fa-clipboard-check text-blue-600 mr-2"></i>', class: 'section-header' },
            { pattern: /📋\s*(𝗙𝗢𝗟𝗟𝗢𝗪-𝗨𝗣\s+𝗤𝗨𝗘𝗦𝗧𝗜𝗢𝗡𝗦|FOLLOW-UP\s+QUESTIONS|Follow-up\s+Questions)/gi, icon: '<i class="fa-solid fa-circle-question text-blue-600 mr-2"></i>', class: 'section-header' },
            { pattern: /📊\s*(𝗦𝗬𝗠𝗣𝗧𝗢𝗠\s+𝗦𝗨𝗠𝗠𝗔𝗥𝗬|SYMPTOM\s+SUMMARY|Symptom\s+Summary)/gi, icon: '<i class="fa-solid fa-list-check text-blue-600 mr-2"></i>', class: 'section-header' },
            { pattern: /🧬\s*(𝗙𝗔𝗠𝗜𝗟𝗬\s+𝗛𝗜𝗦𝗧𝗢𝗥𝗬\s+𝗔𝗡𝗔𝗟𝗬𝗦𝗜𝗦|FAMILY\s+HISTORY\s+ANALYSIS|Family\s+History\s+Analysis)/gi, icon: '<i class="fa-solid fa-dna text-blue-600 mr-2"></i>', class: 'section-header' },
            { pattern: /🏥\s*(𝗣𝗢𝗦𝗦𝗜𝗕𝗟𝗘\s+𝗖𝗢𝗡𝗗𝗜𝗧𝗜𝗢𝗡𝗦|POSSIBLE\s+CONDITIONS|Possible\s+Conditions)/gi, icon: '<i class="fa-solid fa-stethoscope text-blue-600 mr-2"></i>', class: 'section-header' },
            { pattern: /📊\s*(𝗥𝗜𝗦𝗞\s+𝗔𝗦𝗦𝗘𝗦𝗦𝗠𝗘𝗡𝗧|RISK\s+ASSESSMENT|Risk\s+Assessment)/gi, icon: '<i class="fa-solid fa-chart-simple text-blue-600 mr-2"></i>', class: 'section-header' },
            { pattern: /💊\s*(𝗥𝗘𝗖𝗢𝗠𝗠𝗘𝗡𝗗𝗔𝗧𝗜𝗢𝗡𝗦|RECOMMENDATIONS|Recommendations)/gi, icon: '<i class="fa-solid fa-pills text-blue-600 mr-2"></i>', class: 'section-header' },
            { pattern: /🚨\s*(𝗪𝗛𝗘𝗡\s+𝗧𝗢\s+𝗦𝗘𝗘𝗞\s+𝗛𝗘𝗟𝗣|WHEN\s+TO\s+SEEK\s+HELP|When\s+to\s+Seek\s+Help)/gi, icon: '<i class="fa-solid fa-circle-exclamation text-red-600 mr-2"></i>', class: 'section-header risk-high' },
            { pattern: /📋\s*(𝗡𝗘𝗫𝗧\s+𝗦𝗧𝗘𝗣𝗦|NEXT\s+STEPS|Next\s+Steps)/gi, icon: '<i class="fa-solid fa-arrow-right text-blue-600 mr-2"></i>', class: 'section-header' },
            { pattern: /=========================================================/g, icon: '', class: 'divider' }
        ];
        
        sections.forEach(({ pattern, icon, class: className }) => {
            if (className === 'divider') {
                formattedText = formattedText.replace(pattern, `<div class="${className}"></div>`);
            } else {
                formattedText = formattedText.replace(pattern, (match, p1) => {
                    return `<div class="${className}">${icon}${p1}</div>`;
                });
            }
        });
        
        formattedText = formattedText.replace(/•\s*(.*?)(<br>|$)/g, (match, content) => {
            return `<div class="bullet-item">• ${content}</div>`;
        });
        
        formattedText = formattedText.replace(/(\d+)\.\s*(.*?)(<br>|$)/g, (match, num, content) => {
            return `<div class="numbered-item"><span class="number">${num}.</span> ${content}</div>`;
        });
        
        formattedText = formattedText
            .replace(/Risk Level:\s*High/g, 'Risk Level: <span class="risk-high-badge">High</span>')
            .replace(/Risk Level:\s*Moderate/g, 'Risk Level: <span class="risk-moderate-badge">Moderate</span>')
            .replace(/Risk Level:\s*Low/g, 'Risk Level: <span class="risk-low-badge">Low</span>')
            .replace(/Risk Level:\s*Minimal/g, 'Risk Level: <span class="risk-low-badge">Minimal</span>');
        
        messageContent.innerHTML = formattedText;
    } else {
        messageContent.innerHTML = text.replace(/\n/g, '<br>');
    }
    
    messageDiv.appendChild(messageContent);
    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function addTypingIndicator() {
    const div = document.createElement('div');
    div.className = 'flex items-start mb-4 justify-start';
    div.innerHTML = `
        <div class="message-bot">
            <div class="loading-dots">
                <span>●</span>
                <span>●</span>
                <span>●</span>
            </div>
        </div>
    `;
    chatMessages.appendChild(div);
    chatMessages.scrollTop = chatMessages.scrollHeight;
    return div;
}

function updateSymptomInfo(symptoms, followUp) {
    symptomInfo.classList.remove('hidden');
    
    symptomList.innerHTML = '';
    const excludeKeys = ['duration', 'duration_unit'];
    
    if (symptoms && Object.keys(symptoms).length > 0) {
        Object.keys(symptoms).forEach(symptom => {
            if (!excludeKeys.includes(symptom)) {
                const tag = document.createElement('span');
                tag.className = 'symptom-tag';
                tag.textContent = symptom.replace(/_/g, ' ');
                symptomList.appendChild(tag);
            }
        });
        
        if (symptoms.duration) {
            const durationTag = document.createElement('span');
            durationTag.className = 'symptom-tag bg-yellow-100 text-yellow-800';
            durationTag.textContent = `⏱ ${symptoms.duration} ${symptoms.duration_unit || 'days'}`;
            symptomList.appendChild(durationTag);
        }
    } else {
        symptomList.innerHTML = '<span class="text-gray-500">No symptoms detected yet.</span>';
    }
    
    questionList.innerHTML = '';
    if (followUp && followUp.length > 0) {
        followUp.forEach(question => {
            const li = document.createElement('li');
            li.className = 'text-gray-700 mb-1';
            li.textContent = question;
            questionList.appendChild(li);
        });
    } else {
        questionList.innerHTML = '<li class="text-gray-500">No follow-up questions available.</li>';
    }
}

async function analyzeRisk() {
    try {
        addMessage('Analyzing your symptoms and generating comprehensive diagnosis...', 'bot');
        
        const response = await fetch('/api/diagnose', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                session_id: sessionId
            })
        });
        
        const data = await response.json();
        
        let diagnosisText = `
=========================================================
📋 COMPREHENSIVE HEALTH ASSESSMENT
=========================================================

📊 SYMPTOM SUMMARY
${data.symptoms?.map(s => `• ${s.message}`).join('\n') || '• No symptoms recorded'}

🧬 FAMILY HISTORY ANALYSIS
${Object.entries(data.family_history || {}).map(([relation, conditions]) => 
    `• ${relation.charAt(0).toUpperCase() + relation.slice(1)}: ${conditions.join(', ').replace(/_/g, ' ')}`
).join('\n') || '• No family history recorded'}

🏥 POSSIBLE CONDITIONS
${data.diagnosis?.conditions?.map(c => `• ${c}`).join('\n') || '• No specific conditions identified'}

📊 RISK ASSESSMENT
• Risk Level: ${data.risk_level}
• Risk Score: ${data.risk_score}/100
• Risk Factors:
${data.risk_factors?.map(f => `  - ${f}`).join('\n') || '  - No specific risk factors'}

💊 RECOMMENDATIONS
${data.recommendations?.split('\n').filter(r => r.trim()).map(r => `• ${r.trim()}`).join('\n') || '• Consult a healthcare professional'}

🚨 WHEN TO SEEK HELP
• If symptoms worsen or persist
• If you experience difficulty breathing
• If you develop severe pain
• If you have concerns about your health

📋 NEXT STEPS
• Schedule a doctor consultation
• Monitor your symptoms daily
• Keep this report for your records

📊 Report saved to Dashboard
`;
        
        addMessage(diagnosisText, 'bot');
        
        // Save report data to localStorage
        localStorage.setItem('lastReport', JSON.stringify(data));
        
        // Add dashboard link
        addMessage('<i class="fa-solid fa-chart-line text-blue-600 mr-1.5"></i> View your full report on the <a href="/dashboard" style="color:#1a56db;text-decoration:underline;">Dashboard</a>', 'bot');
        
    } catch (error) {
        console.error('Error analyzing risk:', error);
        addMessage('Sorry, I encountered an error generating the diagnosis. Please try again.', 'bot');
    }
}

async function resetConversation() {
    if (confirm('Reset conversation history?')) {
        try {
            const response = await fetch('/api/chat/reset', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    session_id: sessionId
                })
            });
            
            if (response.ok) {
                const chatMessages = document.getElementById('chat-messages');
                const firstMessage = chatMessages.children[0];
                chatMessages.innerHTML = '';
                if (firstMessage) {
                    chatMessages.appendChild(firstMessage);
                }
                document.getElementById('symptom-info').classList.add('hidden');
                document.getElementById('family-history-prompt').classList.add('hidden');
                conversationCount = 0;
                
                const resetMsg = document.createElement('div');
                resetMsg.className = 'text-center text-gray-500 text-sm my-4';
                resetMsg.innerHTML = '<i class="fa-solid fa-rotate-left text-gray-500 mr-1.5"></i> Conversation has been reset';
                chatMessages.appendChild(resetMsg);
                chatMessages.scrollTop = chatMessages.scrollHeight;
            }
        } catch (error) {
            console.error('Error resetting conversation:', error);
            addMessage('Error resetting conversation. Please try again.', 'bot');
        }
    }
}

async function loadConversation() {
    try {
        const response = await fetch(`/api/conversation/${sessionId}`);
        const messages = await response.json();
        
        if (messages && messages.length > 0) {
            const recent = messages.slice(-10);
            recent.forEach(msg => {
                if (msg.role === 'user') {
                    addMessage(msg.content, 'user');
                } else {
                    addMessage(msg.content, 'bot');
                }
            });
            
            const symptomsResponse = await fetch(`/api/symptoms/${sessionId}`);
            const symptomsData = await symptomsResponse.json();
            if (symptomsData && symptomsData.length > 0) {
                const lastEntry = symptomsData[symptomsData.length - 1];
                updateSymptomInfo(lastEntry.symptoms, []);
            }
        }
    } catch (error) {
        console.error('Error loading conversation:', error);
    }
}

document.addEventListener('DOMContentLoaded', loadConversation);

chatInput.addEventListener('keydown', function(e) {
    if (e.key === 'Enter' && e.ctrlKey) {
        sendMessage();
    }
});