from flask import Flask, render_template, request, jsonify, session, redirect, url_for, send_file
import json
import os
from datetime import datetime
import hashlib
import secrets
import qrcode
import io
import base64
from services.symptom_parser import SymptomParser
from services.risk_engine import RiskEngine
from services.groq_service import GroqService
from services.question_generator import QuestionGenerator
from utils.helpers import load_json, save_json

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'

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

conversation_history = {}

# ============================================================
# AUTHENTICATION ROUTES
# ============================================================

@app.route('/login')
def login_page():
    return render_template('login.html')

@app.route('/signup')
def signup_page():
    return render_template('signup.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login_page'))

@app.route('/api/auth/signup', methods=['POST'])
def signup():
    data = request.json
    username = data.get('username', '').strip()
    email = data.get('email', '').strip()
    password = data.get('password', '')
    
    if not username or len(username) < 3:
        return jsonify({'success': False, 'message': 'Username must be at least 3 characters'}), 400
    if not email or '@' not in email:
        return jsonify({'success': False, 'message': 'Valid email is required'}), 400
    if not password or len(password) < 6:
        return jsonify({'success': False, 'message': 'Password must be at least 6 characters'}), 400
    
    users = load_json(USERS_FILE)
    if username in users:
        return jsonify({'success': False, 'message': 'Username already exists'}), 400
    for user_id, user_data in users.items():
        if user_data.get('email') == email:
            return jsonify({'success': False, 'message': 'Email already registered'}), 400
    
    salt = secrets.token_hex(16)
    password_hash = hashlib.sha256((password + salt).encode()).hexdigest()
    user_id = f"user_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    users[user_id] = {
        'username': username, 'email': email, 'password_hash': password_hash,
        'salt': salt, 'created_at': datetime.now().isoformat(),
        'last_login': None, 'user_id': user_id
    }
    save_json(USERS_FILE, users)
    return jsonify({'success': True, 'message': 'Account created successfully! Please login.', 'user_id': user_id})

@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username', '').strip()
    password = data.get('password', '')
    
    if not username or not password:
        return jsonify({'success': False, 'message': 'Username and password required'}), 400
    
    users = load_json(USERS_FILE)
    user = None
    user_id = None
    for uid, u in users.items():
        if u.get('username') == username:
            user = u
            user_id = uid
            break
    
    if not user:
        return jsonify({'success': False, 'message': 'Invalid username or password'}), 401
    
    salt = user.get('salt')
    password_hash = hashlib.sha256((password + salt).encode()).hexdigest()
    if password_hash != user.get('password_hash'):
        return jsonify({'success': False, 'message': 'Invalid username or password'}), 401
    
    user['last_login'] = datetime.now().isoformat()
    users[user_id] = user
    save_json(USERS_FILE, users)
    
    session['user_id'] = user_id
    session['username'] = username
    session['logged_in'] = True
    
    return jsonify({'success': True, 'message': 'Login successful!', 'user_id': user_id, 'username': username, 'redirect': '/chat'})

@app.route('/api/auth/check', methods=['GET'])
def check_auth():
    if session.get('logged_in'):
        return jsonify({'logged_in': True, 'user_id': session.get('user_id'), 'username': session.get('username')})
    return jsonify({'logged_in': False})

@app.route('/api/auth/user/<user_id>', methods=['GET'])
def get_user(user_id):
    users = load_json(USERS_FILE)
    user = users.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    return jsonify({'user_id': user_id, 'username': user.get('username'), 'email': user.get('email'), 'created_at': user.get('created_at'), 'last_login': user.get('last_login')})

# ============================================================
# PROTECTED ROUTES
# ============================================================

@app.route('/')
def index():
    if not session.get('logged_in'):
        return redirect(url_for('login_page'))
    return render_template('index.html', username=session.get('username'))

@app.route('/chat')
def chat():
    if not session.get('logged_in'):
        return redirect(url_for('login_page'))
    return render_template('chat.html', username=session.get('username'))

@app.route('/dashboard')
def dashboard():
    if not session.get('logged_in'):
        return redirect(url_for('login_page'))
    return render_template('dashboard.html', username=session.get('username'))

@app.route('/family-history')
def family_history():
    if not session.get('logged_in'):
        return redirect(url_for('login_page'))
    return render_template('family_history.html', username=session.get('username'))

@app.route('/reports')
def reports():
    if not session.get('logged_in'):
        return redirect(url_for('login_page'))
    return render_template('reports.html', username=session.get('username'))

# ============================================================
# QR CODE ROUTES
# ============================================================

@app.route('/api/report/<report_id>/qr', methods=['GET'])
def generate_report_qr(report_id):
    """Generate QR code for a specific report"""
    if not session.get('logged_in'):
        return jsonify({'error': 'Unauthorized'}), 401
    
    print(f"📱 QR Request for report: {report_id}")
    
    all_reports = load_json(REPORTS_FILE)
    report = all_reports.get(report_id)
    
    if not report:
        print(f"❌ Report not found: {report_id}")
        return jsonify({'error': 'Report not found'}), 404
    
    patient_id = report.get('patient_id')
    all_users = load_json(USERS_FILE)
    user_data = all_users.get(patient_id, {})
    
    qr_data = {
        'report_id': report_id,
        'patient_id': patient_id,
        'patient_name': user_data.get('username', 'Unknown'),
        'patient_email': user_data.get('email', 'N/A'),
        'report_date': report.get('date', 'N/A'),
        'risk_level': report.get('risk_level', 'N/A'),
        'risk_score': report.get('risk_score', 0)
    }
    
    base_url = request.host_url.rstrip('/')
    qr_data_json = json.dumps(qr_data)
    qr_data_b64 = base64.b64encode(qr_data_json.encode()).decode()
    report_url = f"{base_url}/report/view/{report_id}?data={qr_data_b64}"
    
    qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=10, border=4)
    qr.add_data(report_url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    
    img_buffer = io.BytesIO()
    img.save(img_buffer, format='PNG')
    img_buffer.seek(0)
    img_base64 = base64.b64encode(img_buffer.getvalue()).decode('utf-8')
    
    print(f"✅ QR Code generated for: {report_id}")
    
    return jsonify({
        'qr_code': img_base64,
        'report_url': report_url,
        'report_id': report_id,
        'patient_name': qr_data['patient_name'],
        'patient_email': qr_data['patient_email'],
        'risk_level': qr_data['risk_level'],
        'risk_score': qr_data['risk_score']
    })

@app.route('/api/report/<report_id>/qr/download', methods=['GET'])
def download_report_qr(report_id):
    """Download QR code as PNG image"""
    if not session.get('logged_in'):
        return jsonify({'error': 'Unauthorized'}), 401
    
    print(f"📥 Download QR for: {report_id}")
    
    all_reports = load_json(REPORTS_FILE)
    report = all_reports.get(report_id)
    
    if not report:
        return jsonify({'error': 'Report not found'}), 404
    
    patient_id = report.get('patient_id')
    all_users = load_json(USERS_FILE)
    user_data = all_users.get(patient_id, {})
    
    qr_data = {
        'report_id': report_id,
        'patient_name': user_data.get('username', 'Unknown'),
        'patient_email': user_data.get('email', 'N/A'),
        'report_date': report.get('date', 'N/A'),
        'risk_level': report.get('risk_level', 'N/A'),
        'risk_score': report.get('risk_score', 0)
    }
    
    qr_data_json = json.dumps(qr_data)
    qr_data_b64 = base64.b64encode(qr_data_json.encode()).decode()
    base_url = request.host_url.rstrip('/')
    report_url = f"{base_url}/report/view/{report_id}?data={qr_data_b64}"
    
    qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_H, box_size=15, border=4)
    qr.add_data(report_url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="#1a56db", back_color="white")
    
    img_buffer = io.BytesIO()
    img.save(img_buffer, format='PNG')
    img_buffer.seek(0)
    
    return send_file(
        img_buffer,
        mimetype='image/png',
        as_attachment=True,
        download_name=f'report_{report_id}_qr.png'
    )

@app.route('/report/view/<report_id>')
def view_report(report_id):
    """View report from QR code scan"""
    print(f"👁️ Viewing report: {report_id}")
    
    encoded_data = request.args.get('data')
    
    if encoded_data:
        try:
            qr_data_json = base64.b64decode(encoded_data).decode()
            qr_data = json.loads(qr_data_json)
            return render_template('report_view_detailed.html', report_id=report_id, report_data=qr_data)
        except Exception as e:
            print(f"❌ QR decode error: {e}")
    
    all_reports = load_json(REPORTS_FILE)
    report = all_reports.get(report_id)
    
    if not report:
        return render_template('report_not_found.html'), 404
    
    patient_id = report.get('patient_id')
    all_users = load_json(USERS_FILE)
    user_data = all_users.get(patient_id, {})
    
    report_data = {
        'report_id': report_id,
        'patient_id': patient_id,
        'patient_name': user_data.get('username', 'Unknown'),
        'patient_email': user_data.get('email', 'N/A'),
        'report_date': report.get('date', 'N/A'),
        'risk_level': report.get('risk_level', 'N/A'),
        'risk_score': report.get('risk_score', 0),
        'risk_factors': report.get('risk_factors', []),
        'symptoms': report.get('symptoms', []),
        'family_history': report.get('family_history', {}),
        'conditions': report.get('diagnosis', {}).get('conditions', []),
        'recommendations': report.get('recommendations', ''),
        'summary': report.get('summary', '')
    }
    
    return render_template('report_view_detailed.html', report_id=report_id, report_data=report_data)

# ============================================================
# API ROUTES
# ============================================================

@app.route('/api/chat', methods=['POST'])
def handle_chat():
    if not session.get('logged_in'):
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.json
    user_message = data.get('message', '')
    session_id = data.get('session_id', session.get('user_id', 'default'))
    
    if session_id not in conversation_history:
        conversation_history[session_id] = []
    
    conversation_history[session_id].append({
        'role': 'user',
        'content': user_message,
        'timestamp': datetime.now().isoformat()
    })
    
    symptoms = symptom_parser.parse(user_message)
    family_history = load_json(FAMILY_HISTORY_FILE).get(session_id, {})
    
    # Extract family history from message
    family_keywords = ['father', 'mother', 'brother', 'sister', 'grandfather', 'grandmother', 
                       'family', 'parent', 'aunt', 'uncle', 'grandparent', 'diabetes', 
                       'hypertension', 'heart', 'cancer']
    
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
    
    recent_messages = conversation_history[session_id][-8:] if conversation_history[session_id] else []
    follow_up = question_generator.generate_questions_with_context(symptoms, user_message, recent_messages)
    groq_response = groq_service.get_response(user_message, symptoms, family_history)
    
    conversation_history[session_id].append({
        'role': 'assistant',
        'content': groq_response,
        'timestamp': datetime.now().isoformat()
    })
    
    save_conversation(session_id, conversation_history[session_id])
    save_user_symptoms(session_id, symptoms, user_message)
    
    return jsonify({
        'response': groq_response,
        'symptoms': symptoms,
        'follow_up': follow_up,
        'conversation_count': len(conversation_history[session_id]),
        'family_history': family_history,
        'session_id': session_id
    })

@app.route('/api/diagnose', methods=['POST'])
def diagnose():
    if not session.get('logged_in'):
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.json
    session_id = data.get('session_id', session.get('user_id', 'default'))
    
    all_conversations = load_json(CONVERSATIONS_FILE)
    conversations = all_conversations.get(session_id, [])
    all_symptoms = load_json(SYMPTOMS_FILE)
    symptoms_data = all_symptoms.get(session_id, [])
    all_family = load_json(FAMILY_HISTORY_FILE)
    family_history = all_family.get(session_id, {})
    
    diagnosis = groq_service.get_comprehensive_diagnosis(conversations, symptoms_data, family_history)
    latest_symptoms = symptoms_data[-1]['symptoms'] if symptoms_data else {}
    risk_result = risk_engine.calculate_risk(latest_symptoms, family_history, latest_symptoms.get('duration', 0))
    
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
        'summary': diagnosis.get('summary', '')
    }
    
    save_report(report)
    save_patient_data(session_id, report)
    
    return jsonify({
        'risk_score': risk_result['score'],
        'risk_level': risk_result['level'],
        'risk_factors': risk_result['factors'],
        'recommendations': risk_result['recommendations'],
        'diagnosis': diagnosis,
        'family_history': family_history,
        'symptoms': symptoms_data,
        'report': report,
        'patient_id': session_id,
        'date': report['date']
    })

@app.route('/api/dashboard/<session_id>', methods=['GET'])
def get_dashboard_data(session_id):
    if not session.get('logged_in'):
        return jsonify({'error': 'Unauthorized'}), 401
    
    all_patients = load_json(PATIENTS_FILE)
    patient_data = all_patients.get(session_id, {})
    all_reports = load_json(REPORTS_FILE)
    patient_reports = []
    for rid, r in all_reports.items():
        if r.get('patient_id') == session_id:
            r['report_id'] = rid
            patient_reports.append(r)
    latest_report = patient_reports[-1] if patient_reports else None
    all_family = load_json(FAMILY_HISTORY_FILE)
    family_history = all_family.get(session_id, {})
    all_symptoms = load_json(SYMPTOMS_FILE)
    symptoms_data = all_symptoms.get(session_id, [])
    
    return jsonify({
        'patient_id': session_id,
        'patient_data': patient_data,
        'latest_report': latest_report,
        'family_history': family_history,
        'symptoms': symptoms_data,
        'total_visits': len(patient_reports),
        'has_data': latest_report is not None
    })

@app.route('/api/patient/<session_id>', methods=['GET'])
def get_patient_data(session_id):
    if not session.get('logged_in'):
        return jsonify({'error': 'Unauthorized'}), 401
    all_patients = load_json(PATIENTS_FILE)
    return jsonify(all_patients.get(session_id, {}))

@app.route('/api/patients', methods=['GET'])
def get_all_patients():
    if not session.get('logged_in'):
        return jsonify({'error': 'Unauthorized'}), 401
    return jsonify(load_json(PATIENTS_FILE))

@app.route('/api/family-history', methods=['POST'])
def save_family_history():
    if not session.get('logged_in'):
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.json
    session_id = data.get('session_id', session.get('user_id', 'default'))
    family_data = data.get('family_data', {})
    
    all_data = load_json(FAMILY_HISTORY_FILE)
    if session_id in all_data:
        for relation, conditions in family_data.items():
            if relation in all_data[session_id]:
                existing = set(all_data[session_id][relation])
                existing.update(conditions)
                all_data[session_id][relation] = list(existing)
            else:
                all_data[session_id][relation] = conditions
    else:
        all_data[session_id] = family_data
    save_json(FAMILY_HISTORY_FILE, all_data)
    return jsonify({'status': 'success', 'message': 'Family history saved'})

@app.route('/api/family-history/<session_id>', methods=['GET'])
def get_family_history(session_id):
    if not session.get('logged_in'):
        return jsonify({'error': 'Unauthorized'}), 401
    all_data = load_json(FAMILY_HISTORY_FILE)
    return jsonify(all_data.get(session_id, {}))

@app.route('/api/symptoms/<session_id>', methods=['GET'])
def get_symptom_timeline(session_id):
    if not session.get('logged_in'):
        return jsonify({'error': 'Unauthorized'}), 401
    all_data = load_json(SYMPTOMS_FILE)
    return jsonify(all_data.get(session_id, []))

@app.route('/api/conversation/<session_id>', methods=['GET'])
def get_conversation(session_id):
    if not session.get('logged_in'):
        return jsonify({'error': 'Unauthorized'}), 401
    all_data = load_json(CONVERSATIONS_FILE)
    return jsonify(all_data.get(session_id, []))

@app.route('/api/reports/<session_id>', methods=['GET'])
def get_reports(session_id):
    if not session.get('logged_in'):
        return jsonify({'error': 'Unauthorized'}), 401
    all_data = load_json(REPORTS_FILE)
    patient_reports = []
    for report_id, report in all_data.items():
        if report.get('patient_id') == session_id:
            report['report_id'] = report_id
            patient_reports.append(report)
    return jsonify(patient_reports)

@app.route('/api/chat/reset', methods=['POST'])
def reset_conversation():
    if not session.get('logged_in'):
        return jsonify({'error': 'Unauthorized'}), 401
    data = request.json
    session_id = data.get('session_id', session.get('user_id', 'default'))
    if session_id in conversation_history:
        conversation_history[session_id] = []
        save_conversation(session_id, [])
    return jsonify({'status': 'success', 'message': 'Conversation reset'})

# ============================================================
# HELPER FUNCTIONS
# ============================================================

def extract_family_history_from_message(message):
    message = message.lower()
    family_data = {}
    relations = ['father', 'mother', 'brother', 'sister', 'grandfather', 'grandmother', 
                 'aunt', 'uncle', 'cousin', 'parent']
    conditions = ['diabetes', 'hypertension', 'heart disease', 'cancer', 'stroke', 
                  'kidney disease', 'asthma', 'arthritis', 'depression', 'alzheimer']
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
    all_data[session_id].append({
        'timestamp': datetime.now().isoformat(),
        'message': message,
        'symptoms': symptoms
    })
    save_json(SYMPTOMS_FILE, all_data)

def save_report(report):
    all_data = load_json(REPORTS_FILE)
    report_id = f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    all_data[report_id] = report
    save_json(REPORTS_FILE, all_data)

def save_patient_data(session_id, report):
    all_patients = load_json(PATIENTS_FILE)
    if session_id not in all_patients:
        all_patients[session_id] = {
            'patient_id': session_id,
            'created_at': datetime.now().isoformat(),
            'visits': []
        }
    all_patients[session_id]['visits'].append({
        'date': datetime.now().isoformat(),
        'report': report
    })
    all_patients[session_id]['last_visit'] = datetime.now().isoformat()
    save_json(PATIENTS_FILE, all_patients)

if __name__ == '__main__':
    app.run(debug=True, port=5000)