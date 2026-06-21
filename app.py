from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import json
import os
from datetime import datetime
import hashlib
import secrets
from services.symptom_parser import SymptomParser
from services.risk_engine import RiskEngine
from services.groq_service import GroqService
from services.question_generator import QuestionGenerator
from utils.helpers import load_json, save_json

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # Change this in production

# Initialize services
symptom_parser = SymptomParser()
risk_engine = RiskEngine()
groq_service = GroqService()
question_generator = QuestionGenerator()

# Data file paths
USERS_FILE = 'data/users.json'
FAMILY_HISTORY_FILE = 'data/family_history.json'
REPORTS_FILE = 'data/reports.json'
SYMPTOMS_FILE = 'data/symptoms.json'
CONVERSATIONS_FILE = 'data/conversations.json'
PATIENTS_FILE = 'data/patients.json'

# Initialize data files
os.makedirs('data', exist_ok=True)
for file in [USERS_FILE, FAMILY_HISTORY_FILE, REPORTS_FILE, SYMPTOMS_FILE, CONVERSATIONS_FILE, PATIENTS_FILE]:
    if not os.path.exists(file):
        with open(file, 'w') as f:
            json.dump({}, f)

# Store conversation history in memory
conversation_history = {}

# ============================================================
# AUTHENTICATION ROUTES
# ============================================================

@app.route('/login')
def login_page():
    """Login page"""
    return render_template('login.html')

@app.route('/signup')
def signup_page():
    """Signup page"""
    return render_template('signup.html')

@app.route('/logout')
def logout():
    """Logout user"""
    session.clear()
    return redirect(url_for('login_page'))

@app.route('/api/auth/signup', methods=['POST'])
def signup():
    """User registration API"""
    data = request.json
    username = data.get('username', '').strip()
    email = data.get('email', '').strip()
    password = data.get('password', '')
    
    # Validation
    if not username or len(username) < 3:
        return jsonify({'success': False, 'message': 'Username must be at least 3 characters'}), 400
    
    if not email or '@' not in email:
        return jsonify({'success': False, 'message': 'Valid email is required'}), 400
    
    if not password or len(password) < 6:
        return jsonify({'success': False, 'message': 'Password must be at least 6 characters'}), 400
    
    # Check if user exists
    users = load_json(USERS_FILE)
    
    if username in users:
        return jsonify({'success': False, 'message': 'Username already exists'}), 400
    
    for user_id, user_data in users.items():
        if user_data.get('email') == email:
            return jsonify({'success': False, 'message': 'Email already registered'}), 400
    
    # Hash password
    salt = secrets.token_hex(16)
    password_hash = hashlib.sha256((password + salt).encode()).hexdigest()
    
    # Create user
    user_id = f"user_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    users[user_id] = {
        'username': username,
        'email': email,
        'password_hash': password_hash,
        'salt': salt,
        'created_at': datetime.now().isoformat(),
        'last_login': None,
        'user_id': user_id
    }
    
    save_json(USERS_FILE, users)
    
    return jsonify({
        'success': True,
        'message': 'Account created successfully! Please login.',
        'user_id': user_id
    })

@app.route('/api/auth/login', methods=['POST'])
def login():
    """User login API"""
    data = request.json
    username = data.get('username', '').strip()
    password = data.get('password', '')
    
    if not username or not password:
        return jsonify({'success': False, 'message': 'Username and password required'}), 400
    
    users = load_json(USERS_FILE)
    
    # Find user by username
    user = None
    user_id = None
    for uid, u in users.items():
        if u.get('username') == username:
            user = u
            user_id = uid
            break
    
    if not user:
        return jsonify({'success': False, 'message': 'Invalid username or password'}), 401
    
    # Verify password
    salt = user.get('salt')
    password_hash = hashlib.sha256((password + salt).encode()).hexdigest()
    
    if password_hash != user.get('password_hash'):
        return jsonify({'success': False, 'message': 'Invalid username or password'}), 401
    
    # Update last login
    user['last_login'] = datetime.now().isoformat()
    users[user_id] = user
    save_json(USERS_FILE, users)
    
    # Set session
    session['user_id'] = user_id
    session['username'] = username
    session['logged_in'] = True
    
    return jsonify({
        'success': True,
        'message': 'Login successful!',
        'user_id': user_id,
        'username': username,
        'redirect': '/chat'
    })

@app.route('/api/auth/check', methods=['GET'])
def check_auth():
    """Check if user is logged in"""
    if session.get('logged_in'):
        return jsonify({
            'logged_in': True,
            'user_id': session.get('user_id'),
            'username': session.get('username')
        })
    return jsonify({'logged_in': False})

@app.route('/api/auth/user/<user_id>', methods=['GET'])
def get_user(user_id):
    """Get user details"""
    users = load_json(USERS_FILE)
    user = users.get(user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    return jsonify({
        'user_id': user_id,
        'username': user.get('username'),
        'email': user.get('email'),
        'created_at': user.get('created_at'),
        'last_login': user.get('last_login')
    })

# ============================================================
# PROTECTED ROUTES
# ============================================================

@app.route('/')
def index():
    """Home page - redirects to login if not authenticated"""
    if not session.get('logged_in'):
        return redirect(url_for('login_page'))
    return render_template('index.html', username=session.get('username'))

@app.route('/chat')
def chat():
    """Chat page - requires login"""
    if not session.get('logged_in'):
        return redirect(url_for('login_page'))
    return render_template('chat.html', username=session.get('username'))

@app.route('/dashboard')
def dashboard():
    """Dashboard page - requires login"""
    if not session.get('logged_in'):
        return redirect(url_for('login_page'))
    return render_template('dashboard.html', username=session.get('username'))

@app.route('/family-history')
def family_history():
    """Family History page - requires login"""
    if not session.get('logged_in'):
        return redirect(url_for('login_page'))
    return render_template('family_history.html', username=session.get('username'))

@app.route('/reports')
def reports():
    """Reports page - requires login"""
    if not session.get('logged_in'):
        return redirect(url_for('login_page'))
    return render_template('reports.html', username=session.get('username'))

# ============================================================
# 🆕 UPDATED API ROUTES (with Critical Symptom Support)
# ============================================================

@app.route('/api/chat', methods=['POST'])
def handle_chat():
    """Handle chat messages with full context - Requires login"""
    # Check authentication
    if not session.get('logged_in'):
        return jsonify({'error': 'Unauthorized. Please login first.'}), 401
    
    data = request.json
    user_message = data.get('message', '')
    session_id = data.get('session_id', session.get('user_id', 'default'))
    
    # Initialize conversation history for this session
    if session_id not in conversation_history:
        conversation_history[session_id] = []
    
    # Add user message to history
    conversation_history[session_id].append({
        'role': 'user',
        'content': user_message,
        'timestamp': datetime.now().isoformat()
    })
    
    # 🆕 Parse symptoms from message (now includes critical flags)
    symptoms = symptom_parser.parse(user_message)
    
    # 🆕 Check for critical symptoms and log them
    has_critical = symptom_parser.has_critical_symptoms(symptoms)
    critical_warnings = symptom_parser.get_critical_warnings(symptoms) if has_critical else []
    
    # Get family history for this user
    family_history = load_json(FAMILY_HISTORY_FILE).get(session_id, {})
    
    # Check if user mentioned family in message
    family_keywords = ['father', 'mother', 'brother', 'sister', 'grandfather', 
                       'grandmother', 'family', 'parent', 'aunt', 'uncle', 
                       'grandparent', 'diabetes', 'hypertension', 'heart', 'cancer',
                       'skin cancer', 'melanoma']  # 🆕 Added skin cancer keywords
    
    if any(word in user_message.lower() for word in family_keywords):
        extracted_family = extract_family_history_from_message(user_message)
        if extracted_family:
            all_family = load_json(FAMILY_HISTORY_FILE)
            if session_id not in all_family:
                all_family[session_id] = {}
            for relation, conditions in extracted_family.items():
                if relation in all_family[session_id]:
                    existing = set(all_family[session_id][relation])
                    existing.update(conditions)
                    all_family[session_id][relation] = list(existing)
                else:
                    all_family[session_id][relation] = conditions
            save_json(FAMILY_HISTORY_FILE, all_family)
            family_history = all_family.get(session_id, {})
    
    # Get recent conversation context
    recent_messages = conversation_history[session_id][-8:] if conversation_history[session_id] else []
    
    # 🆕 Generate follow-up questions (now includes mole/skin questions)
    follow_up = question_generator.generate_questions_with_context(
        symptoms, 
        user_message, 
        recent_messages
    )
    
    # 🆕 If critical symptoms detected, add warning to follow-up
    if has_critical:
        follow_up.insert(0, "⚠️ **URGENT**: Your symptoms require medical attention. Please schedule a doctor's appointment immediately.")
        if any('mole' in w.lower() for w in critical_warnings):
            follow_up.insert(1, "📸 Please take clear photos of the mole with a ruler for scale before your appointment.")
    
    # Get response from Groq with full context
    groq_response = groq_service.get_response(
        user_message, 
        symptoms, 
        family_history
    )
    
    # 🆕 Add critical warning to Groq response if needed
    if has_critical and critical_warnings:
        warning_header = "🚨 **CRITICAL SYMPTOM DETECTED**\n\n"
        for warning in critical_warnings:
            warning_header += f"• {warning}\n"
        warning_header += "\n" + "="*50 + "\n\n"
        groq_response = warning_header + groq_response
    
    # Add bot response to history
    conversation_history[session_id].append({
        'role': 'assistant',
        'content': groq_response,
        'timestamp': datetime.now().isoformat()
    })
    
    # Save everything to JSON
    save_conversation(session_id, conversation_history[session_id])
    save_user_symptoms(session_id, symptoms, user_message)
    
    # 🆕 Return enhanced response with critical flags
    return jsonify({
        'response': groq_response,
        'symptoms': symptoms,
        'follow_up': follow_up,
        'conversation_count': len(conversation_history[session_id]),
        'family_history': family_history,
        'session_id': session_id,
        'has_critical_symptoms': has_critical,
        'critical_warnings': critical_warnings,
        'risk_escalated': has_critical  # Frontend can use this to show alerts
    })

@app.route('/api/diagnose', methods=['POST'])
def diagnose():
    """Get final diagnosis based on all collected data - Requires login"""
    # Check authentication
    if not session.get('logged_in'):
        return jsonify({'error': 'Unauthorized. Please login first.'}), 401
    
    data = request.json
    session_id = data.get('session_id', session.get('user_id', 'default'))
    
    # Get all conversation history
    all_conversations = load_json(CONVERSATIONS_FILE)
    conversations = all_conversations.get(session_id, [])
    
    # Get symptoms
    all_symptoms = load_json(SYMPTOMS_FILE)
    symptoms_data = all_symptoms.get(session_id, [])
    
    # Get family history
    all_family = load_json(FAMILY_HISTORY_FILE)
    family_history = all_family.get(session_id, {})
    
    # 🆕 Get the latest symptoms with all data (including critical flags)
    latest_symptoms = symptoms_data[-1]['symptoms'] if symptoms_data else {}
    duration = latest_symptoms.get('duration', 0)
    
    # 🆕 Calculate risk score with FULL symptom data
    risk_result = risk_engine.calculate_risk(
        symptoms=latest_symptoms,
        family_history=family_history,
        duration=duration,
        user_message=symptoms_data[-1].get('message', '') if symptoms_data else ''
    )
    
    # Get comprehensive diagnosis from Groq
    diagnosis = groq_service.get_comprehensive_diagnosis(
        conversations,
        symptoms_data,
        family_history
    )
    
    # 🆕 Add risk data to diagnosis
    if 'summary' in diagnosis:
        risk_summary = f"\n\n📊 **RISK ASSESSMENT**\n• Risk Level: {risk_result['level']}\n• Risk Score: {risk_result['score']}/100\n"
        if risk_result.get('specialty'):
            risk_summary += f"• Recommended Specialist: {risk_result['specialty'].upper()}\n"
        if risk_result.get('critical_findings'):
            risk_summary += "• Critical Findings: " + ", ".join(risk_result['critical_findings']) + "\n"
        if risk_result.get('urgent'):
            risk_summary += "• 🚨 URGENT: Immediate medical attention recommended\n"
        diagnosis['summary'] = diagnosis['summary'] + risk_summary
    
    # Generate complete report
    report = {
        'patient_id': session_id,
        'date': datetime.now().isoformat(),
        'symptoms': symptoms_data,
        'family_history': family_history,
        'conversation': conversations,
        'diagnosis': diagnosis,
        'risk_score': risk_result['score'],
        'risk_level': risk_result['level'],
        'risk_factors': risk_result['factors'],
        'recommendations': risk_result['recommendations'],
        'specialty': risk_result.get('specialty'),
        'critical_findings': risk_result.get('critical_findings', []),
        'urgent': risk_result.get('urgent', False),
        'summary': diagnosis.get('summary', '')
    }
    
    # Save report
    save_report(report)
    
    # Save patient data
    save_patient_data(session_id, report)
    
    return jsonify({
        'risk_score': risk_result['score'],
        'risk_level': risk_result['level'],
        'risk_factors': risk_result['factors'],
        'recommendations': risk_result['recommendations'],
        'specialty': risk_result.get('specialty'),
        'critical_findings': risk_result.get('critical_findings', []),
        'urgent': risk_result.get('urgent', False),
        'diagnosis': diagnosis,
        'family_history': family_history,
        'symptoms': symptoms_data,
        'report': report,
        'patient_id': session_id,
        'date': report['date']
    })

@app.route('/api/dashboard/<session_id>', methods=['GET'])
def get_dashboard_data(session_id):
    """Get all dashboard data for a patient - Requires login"""
    # Check authentication
    if not session.get('logged_in'):
        return jsonify({'error': 'Unauthorized. Please login first.'}), 401
    
    # Get patient data
    all_patients = load_json(PATIENTS_FILE)
    patient_data = all_patients.get(session_id, {})
    
    # Get latest report
    all_reports = load_json(REPORTS_FILE)
    patient_reports = []
    for report_id, report in all_reports.items():
        if report.get('patient_id') == session_id:
            patient_reports.append(report)
    
    latest_report = patient_reports[-1] if patient_reports else None
    
    # Get family history
    all_family = load_json(FAMILY_HISTORY_FILE)
    family_history = all_family.get(session_id, {})
    
    # Get symptoms
    all_symptoms = load_json(SYMPTOMS_FILE)
    symptoms_data = all_symptoms.get(session_id, [])
    
    # 🆕 Count critical symptoms
    critical_count = 0
    if latest_report:
        critical_count = len(latest_report.get('critical_findings', []))
    
    return jsonify({
        'patient_id': session_id,
        'patient_data': patient_data,
        'latest_report': latest_report,
        'family_history': family_history,
        'symptoms': symptoms_data,
        'total_visits': len(patient_reports),
        'has_data': latest_report is not None,
        'critical_count': critical_count,
        'urgent': latest_report.get('urgent', False) if latest_report else False
    })

@app.route('/api/patient/<session_id>', methods=['GET'])
def get_patient_data(session_id):
    """Get complete patient data - Requires login"""
    if not session.get('logged_in'):
        return jsonify({'error': 'Unauthorized. Please login first.'}), 401
    
    all_patients = load_json(PATIENTS_FILE)
    return jsonify(all_patients.get(session_id, {}))

@app.route('/api/patients', methods=['GET'])
def get_all_patients():
    """Get all patients - Requires login"""
    if not session.get('logged_in'):
        return jsonify({'error': 'Unauthorized. Please login first.'}), 401
    
    return jsonify(load_json(PATIENTS_FILE))

@app.route('/api/family-history', methods=['POST'])
def save_family_history():
    """Save family medical history - Requires login"""
    if not session.get('logged_in'):
        return jsonify({'error': 'Unauthorized. Please login first.'}), 401
    
    data = request.json
    session_id = data.get('session_id', session.get('user_id', 'default'))
    family_data = data.get('family_data', {})
    
    all_data = load_json(FAMILY_HISTORY_FILE)
    
    if session_id in all_data:
        for relation, conditions in family_data.items():
            if relation in all_data[session_id]:
                existing = set(all_data[session_id][relation])
                new_conditions = set(conditions)
                all_data[session_id][relation] = list(existing.union(new_conditions))
            else:
                all_data[session_id][relation] = conditions
    else:
        all_data[session_id] = family_data
    
    save_json(FAMILY_HISTORY_FILE, all_data)
    
    return jsonify({'status': 'success', 'message': 'Family history saved'})

@app.route('/api/family-history/<session_id>', methods=['GET'])
def get_family_history(session_id):
    """Get family medical history - Requires login"""
    if not session.get('logged_in'):
        return jsonify({'error': 'Unauthorized. Please login first.'}), 401
    
    all_data = load_json(FAMILY_HISTORY_FILE)
    return jsonify(all_data.get(session_id, {}))

@app.route('/api/symptoms/<session_id>', methods=['GET'])
def get_symptom_timeline(session_id):
    """Get symptom timeline - Requires login"""
    if not session.get('logged_in'):
        return jsonify({'error': 'Unauthorized. Please login first.'}), 401
    
    all_data = load_json(SYMPTOMS_FILE)
    return jsonify(all_data.get(session_id, []))

@app.route('/api/conversation/<session_id>', methods=['GET'])
def get_conversation(session_id):
    """Get conversation history - Requires login"""
    if not session.get('logged_in'):
        return jsonify({'error': 'Unauthorized. Please login first.'}), 401
    
    all_data = load_json(CONVERSATIONS_FILE)
    return jsonify(all_data.get(session_id, []))

@app.route('/api/reports/<session_id>', methods=['GET'])
def get_reports(session_id):
    """Get patient reports - Requires login"""
    if not session.get('logged_in'):
        return jsonify({'error': 'Unauthorized. Please login first.'}), 401
    
    all_data = load_json(REPORTS_FILE)
    patient_reports = []
    for report_id, report in all_data.items():
        if report.get('patient_id') == session_id:
            report['report_id'] = report_id
            patient_reports.append(report)
    return jsonify(patient_reports)

@app.route('/api/chat/reset', methods=['POST'])
def reset_conversation():
    """Reset conversation - Requires login"""
    if not session.get('logged_in'):
        return jsonify({'error': 'Unauthorized. Please login first.'}), 401
    
    data = request.json
    session_id = data.get('session_id', session.get('user_id', 'default'))
    
    if session_id in conversation_history:
        conversation_history[session_id] = []
        save_conversation(session_id, [])
    
    return jsonify({'status': 'success', 'message': 'Conversation reset'})

# ============================================================
# 🆕 HELPER FUNCTIONS (UPDATED)
# ============================================================

def extract_family_history_from_message(message):
    """Extract family history from user message - Updated with skin conditions"""
    message = message.lower()
    family_data = {}
    
    relations = ['father', 'mother', 'brother', 'sister', 'grandfather', 
                 'grandmother', 'aunt', 'uncle', 'cousin', 'parent', 'grandparent',
                 'sibling', 'spouse', 'child']  # 🆕 Added more relations
    
    # 🆕 Added skin cancer and more conditions
    conditions = ['diabetes', 'hypertension', 'heart disease', 'cancer', 'stroke', 
                  'kidney disease', 'asthma', 'arthritis', 'depression', 'alzheimer',
                  'skin cancer', 'melanoma', 'thyroid', 'anemia', 'autoimmune',
                  'lupus', 'psoriasis', 'eczema', 'high cholesterol', 'obesity']
    
    for relation in relations:
        if relation in message:
            for condition in conditions:
                if condition in message:
                    if relation not in family_data:
                        family_data[relation] = []
                    family_data[relation].append(condition.replace(' ', '_'))
    
    return family_data

def save_conversation(session_id, messages):
    all_data = load_json(CONVERSATIONS_FILE)
    all_data[session_id] = messages
    save_json(CONVERSATIONS_FILE, all_data)

def save_user_symptoms(session_id, symptoms, message):
    all_data = load_json(SYMPTOMS_FILE)
    
    if session_id not in all_data:
        all_data[session_id] = []
    
    # 🆕 Store complete symptom data including critical flags
    all_data[session_id].append({
        'timestamp': datetime.now().isoformat(),
        'message': message,
        'symptoms': symptoms,
        'has_critical': symptoms.get('critical', False),
        'critical_type': symptoms.get('critical_type', []),
        'severity': symptoms.get('severity', 1.0),
        'duration': symptoms.get('duration', 0),
        'duration_unit': symptoms.get('duration_unit', 'days')
    })
    
    save_json(SYMPTOMS_FILE, all_data)

def save_report(report):
    all_data = load_json(REPORTS_FILE)
    report_id = f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    all_data[report_id] = report
    save_json(REPORTS_FILE, all_data)

def save_patient_data(session_id, report):
    """Save complete patient data to patients.json"""
    all_patients = load_json(PATIENTS_FILE)
    
    if session_id not in all_patients:
        all_patients[session_id] = {
            'patient_id': session_id,
            'created_at': datetime.now().isoformat(),
            'visits': [],
            'critical_alerts': []  # 🆕 Track critical alerts
        }
    
    # 🆕 Track critical alerts
    if report.get('urgent', False):
        all_patients[session_id]['critical_alerts'].append({
            'date': datetime.now().isoformat(),
            'risk_level': report.get('risk_level'),
            'critical_findings': report.get('critical_findings', []),
            'specialty': report.get('specialty')
        })
    
    all_patients[session_id]['visits'].append({
        'date': datetime.now().isoformat(),
        'report': report
    })
    all_patients[session_id]['last_visit'] = datetime.now().isoformat()
    all_patients[session_id]['last_risk_level'] = report.get('risk_level')
    all_patients[session_id]['last_risk_score'] = report.get('risk_score')
    
    save_json(PATIENTS_FILE, all_patients)

if __name__ == '__main__':
    app.run(debug=True, port=5000)