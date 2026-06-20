from flask import Flask, render_template, request, jsonify, session
import json
import os
from datetime import datetime
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
FAMILY_HISTORY_FILE = 'data/family_history.json'
REPORTS_FILE = 'data/reports.json'
SYMPTOMS_FILE = 'data/symptoms.json'
CONVERSATIONS_FILE = 'data/conversations.json'
PATIENTS_FILE = 'data/patients.json'

# Initialize data files
os.makedirs('data', exist_ok=True)
for file in [FAMILY_HISTORY_FILE, REPORTS_FILE, SYMPTOMS_FILE, CONVERSATIONS_FILE, PATIENTS_FILE]:
    if not os.path.exists(file):
        with open(file, 'w') as f:
            json.dump({}, f)

# Store conversation history in memory
conversation_history = {}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat')
def chat():
    return render_template('chat.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/family-history')
def family_history():
    return render_template('family_history.html')

@app.route('/reports')
def reports():
    return render_template('reports.html')

@app.route('/api/chat', methods=['POST'])
def handle_chat():
    """Handle chat messages with full context"""
    data = request.json
    user_message = data.get('message', '')
    session_id = data.get('session_id', 'default')
    
    # Initialize conversation history for this session
    if session_id not in conversation_history:
        conversation_history[session_id] = []
    
    # Add user message to history
    conversation_history[session_id].append({
        'role': 'user',
        'content': user_message,
        'timestamp': datetime.now().isoformat()
    })
    
    # Parse symptoms from message
    symptoms = symptom_parser.parse(user_message)
    
    # Get family history for this user
    family_history = load_json(FAMILY_HISTORY_FILE).get(session_id, {})
    
    # Check if user mentioned family in message
    family_keywords = ['father', 'mother', 'brother', 'sister', 'grandfather', 
                       'grandmother', 'family', 'parent', 'aunt', 'uncle', 
                       'grandparent', 'diabetes', 'hypertension', 'heart', 'cancer']
    
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
    
    # Generate follow-up questions
    follow_up = question_generator.generate_questions_with_context(
        symptoms, 
        user_message, 
        recent_messages
    )
    
    # Get response from Groq with full context
    groq_response = groq_service.get_response(
        user_message, 
        symptoms, 
        family_history
    )
    
    # Add bot response to history
    conversation_history[session_id].append({
        'role': 'assistant',
        'content': groq_response,
        'timestamp': datetime.now().isoformat()
    })
    
    # Save everything to JSON
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
    """Get final diagnosis based on all collected data"""
    data = request.json
    session_id = data.get('session_id', 'default')
    
    # Get all conversation history
    all_conversations = load_json(CONVERSATIONS_FILE)
    conversations = all_conversations.get(session_id, [])
    
    # Get symptoms
    all_symptoms = load_json(SYMPTOMS_FILE)
    symptoms_data = all_symptoms.get(session_id, [])
    
    # Get family history
    all_family = load_json(FAMILY_HISTORY_FILE)
    family_history = all_family.get(session_id, {})
    
    # Get comprehensive diagnosis from Groq
    diagnosis = groq_service.get_comprehensive_diagnosis(
        conversations,
        symptoms_data,
        family_history
    )
    
    # Calculate risk score
    latest_symptoms = symptoms_data[-1]['symptoms'] if symptoms_data else {}
    risk_result = risk_engine.calculate_risk(
        latest_symptoms,
        family_history,
        latest_symptoms.get('duration', 0)
    )
    
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
        'diagnosis': diagnosis,
        'family_history': family_history,
        'symptoms': symptoms_data,
        'report': report,
        'patient_id': session_id,
        'date': report['date']
    })

@app.route('/api/dashboard/<session_id>', methods=['GET'])
def get_dashboard_data(session_id):
    """Get all dashboard data for a patient"""
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
    """Get complete patient data"""
    all_patients = load_json(PATIENTS_FILE)
    return jsonify(all_patients.get(session_id, {}))

@app.route('/api/patients', methods=['GET'])
def get_all_patients():
    """Get all patients"""
    return jsonify(load_json(PATIENTS_FILE))

@app.route('/api/family-history', methods=['POST'])
def save_family_history():
    data = request.json
    session_id = data.get('session_id', 'default')
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
    all_data = load_json(FAMILY_HISTORY_FILE)
    return jsonify(all_data.get(session_id, {}))

@app.route('/api/symptoms/<session_id>', methods=['GET'])
def get_symptom_timeline(session_id):
    all_data = load_json(SYMPTOMS_FILE)
    return jsonify(all_data.get(session_id, []))

@app.route('/api/conversation/<session_id>', methods=['GET'])
def get_conversation(session_id):
    all_data = load_json(CONVERSATIONS_FILE)
    return jsonify(all_data.get(session_id, []))

@app.route('/api/reports/<session_id>', methods=['GET'])
def get_reports(session_id):
    all_data = load_json(REPORTS_FILE)
    patient_reports = []
    for report_id, report in all_data.items():
        if report.get('patient_id') == session_id:
            report['report_id'] = report_id
            patient_reports.append(report)
    return jsonify(patient_reports)

@app.route('/api/chat/reset', methods=['POST'])
def reset_conversation():
    data = request.json
    session_id = data.get('session_id', 'default')
    
    if session_id in conversation_history:
        conversation_history[session_id] = []
        save_conversation(session_id, [])
    
    return jsonify({'status': 'success', 'message': 'Conversation reset'})

def extract_family_history_from_message(message):
    """Extract family history from user message"""
    message = message.lower()
    family_data = {}
    
    relations = ['father', 'mother', 'brother', 'sister', 'grandfather', 
                 'grandmother', 'aunt', 'uncle', 'cousin', 'parent']
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
    """Save complete patient data to patients.json"""
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