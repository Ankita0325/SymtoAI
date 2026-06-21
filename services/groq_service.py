import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv(encoding='utf-8-sig')

class GroqService:
    def __init__(self):
        api_key = os.getenv('GROQ_API_KEY')
        if not api_key:
            print("⚠️ WARNING: GROQ_API_KEY not found!")
            self.client = None
            return
        
        self.client = Groq(api_key=api_key)
        self.model = "llama-3.3-70b-versatile"
        print("✅ Groq service initialized successfully!")
    
    def get_response(self, user_message, symptoms, family_history=None):
        """Get structured diagnostic response from Groq"""
        if not self.client:
            return self.get_mock_response(user_message, symptoms)
        
        symptom_list = ", ".join(symptoms.keys()) if symptoms else "no specific symptoms"
        duration = symptoms.get('duration', 'unknown')
        duration_unit = symptoms.get('duration_unit', 'days')
        
        # 🆕 Check for ALL critical symptoms
        has_blood = any('blood' in s.lower() for s in symptoms.keys())
        has_mole = any('mole' in s.lower() for s in symptoms.keys())
        has_chest = any('chest' in s.lower() for s in symptoms.keys())
        has_breath = any('breath' in s.lower() or 'breathing' in s.lower() for s in symptoms.keys())
        has_sudden_headache = any('sudden' in s.lower() and 'headache' in s.lower() for s in symptoms.keys())
        has_vision = any('vision' in s.lower() or 'visual' in s.lower() for s in symptoms.keys())
        
        is_critical = symptoms.get('critical', False)
        critical_type = symptoms.get('critical_type', [])
        
        family_info = ""
        if family_history:
            family_info = "\nFamily History:\n"
            for relation, conditions in family_history.items():
                family_info += f"- {relation}: {', '.join(conditions)}\n"
        
        # 🆕 ENHANCED CRITICAL WARNING PROMPT
        critical_warning = ""
        urgency_level = "Normal"
        
        if has_blood:
            urgency_level = "🔴 HIGH URGENCY"
            critical_warning = """
🚨 **⚠️ CRITICAL SAFETY WARNING ⚠️**

**BLOOD IN STOOL IS A SERIOUS MEDICAL SYMPTOM**
- This is NEVER "minor" or "low risk" until evaluated by a doctor
- Possible causes: gastrointestinal bleeding, inflammatory bowel disease, infections, colorectal issues
- **DO NOT** suggest home remedies (fiber, stool softeners) before medical evaluation
- **DO NOT** reassure that it's "probably just hemorrhoids"
- **MUST** recommend medical evaluation TODAY or TOMORROW at the latest

**YOUR RESPONSE MUST:**
1. Acknowledge the seriousness of blood in stool
2. Recommend seeing a doctor TODAY or TOMORROW
3. Ask about: color of blood (bright red vs dark/tarry), amount, associated pain
4. Ask about: family history of colon cancer, IBD, or gastrointestinal issues
5. NOT minimize or reassure without medical evaluation
"""
        elif has_mole:
            urgency_level = "🔴 HIGH URGENCY"
            critical_warning = """
🚨 **⚠️ CRITICAL SAFETY WARNING ⚠️**

**MOLE CHANGE IS A SERIOUS MEDICAL SYMPTOM**
- This could be a sign of melanoma or skin cancer
- **DO NOT** reassure that it's "probably nothing"
- **MUST** recommend dermatology evaluation within 1-2 weeks

**YOUR RESPONSE MUST:**
1. Acknowledge the seriousness of mole changes
2. Recommend seeing a dermatologist
3. Ask about: ABCDEs (Asymmetry, Border, Color, Diameter, Evolution)
4. Ask about: family history of skin cancer
5. NOT minimize or reassure without medical evaluation
"""
        elif has_chest or has_breath:
            urgency_level = "🔴 CRITICAL URGENCY"
            critical_warning = """
🚨 **⚠️ EXTREME URGENCY WARNING ⚠️**

**CHEST PAIN OR BREATHING DIFFICULTY REQUIRES EMERGENCY CARE**
- This could be a heart attack or serious lung condition
- **MUST** recommend calling emergency services if severe

**YOUR RESPONSE MUST:**
1. Take this VERY seriously
2. Recommend immediate medical attention
3. Ask about: severity, radiation of pain, associated symptoms
4. NOT delay or minimize
"""
        elif has_sudden_headache or has_vision:
            urgency_level = "🔴 HIGH URGENCY"
            critical_warning = """
🚨 **⚠️ CRITICAL SAFETY WARNING ⚠️**

**SUDDEN HEADACHE OR VISION CHANGES REQUIRE URGENT EVALUATION**
- This could indicate a neurological emergency
- **MUST** recommend immediate medical attention

**YOUR RESPONSE MUST:**
1. Take this seriously
2. Recommend urgent medical evaluation
3. Ask about: severity, associated symptoms, onset
4. NOT delay or minimize
"""
        
        prompt = f"""
        You are SwasthyaAI, a medical triage assistant. Your role is to help users understand their symptoms and guide them to appropriate care.
        
        🚨 **CRITICAL RULE: If ANY critical symptom is detected, you MUST treat it with appropriate urgency. DO NOT minimize or reassure without medical evaluation.**
        
        User says: "{user_message}"
        Detected symptoms: {symptom_list}
        Duration: {duration} {duration_unit}
        {family_info}
        
        {critical_warning}
        
        URGENCY LEVEL: {urgency_level}
        
        FORMATTING INSTRUCTIONS:
        
        Structure your response in the following EXACT format:
        
        𝗦𝗬𝗠𝗣𝗧𝗢𝗠 𝗔𝗖𝗞𝗡𝗢𝗪𝗟𝗘𝗗𝗚𝗠𝗘𝗡𝗧
        • [Acknowledge their symptom. If critical, use SERIOUS language, not casual language]
        • [DO NOT say "it could be minor" for critical symptoms]
        
        𝗙𝗢𝗟𝗟𝗢𝗪-𝗨𝗣 𝗤𝗨𝗘𝗦𝗧𝗜𝗢𝗡𝗦
        • [Question 1 - specific and relevant]
        • [Question 2 - specific and relevant]
        • [Question 3 - specific and relevant]
        
        𝗣𝗢𝗦𝗦𝗜𝗕𝗟𝗘 𝗖𝗢𝗡𝗦𝗜𝗗𝗘𝗥𝗔𝗧𝗜𝗢𝗡𝗦
        • [Medical insights - be honest about seriousness]
        • [If critical, list possible serious conditions]
        
        𝗥𝗘𝗖𝗢𝗠𝗠𝗘𝗡𝗗𝗔𝗧𝗜𝗢𝗡𝗦
        • [Actionable recommendations]
        • [For critical: URGENT medical evaluation]
        • [DO NOT suggest home remedies for critical symptoms]
        
        𝗪𝗛𝗘𝗡 𝗧𝗢 𝗦𝗘𝗘𝗞 𝗛𝗘𝗟𝗣
        • [Clear guidance on when to see a doctor]
        • [For critical: "TODAY" or "IMMEDIATELY"]
        • [Emergency warning signs]
        
        Keep each section concise. Use bullet points (•). Be professional and direct.
        
        {"🔴 REMEMBER: For blood in stool, emphasize URGENT medical evaluation. DO NOT suggest home remedies." if has_blood else ""}
        {"🔴 REMEMBER: For mole changes, emphasize dermatology referral. DO NOT minimize." if has_mole else ""}
        {"🔴 REMEMBER: For chest pain/breathing difficulty, emphasize EMERGENCY care if severe." if has_chest or has_breath else ""}
        """
        
        try:
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": """You are SwasthyaAI, a medical triage assistant.

CRITICAL RULES:
1. Blood in stool is NEVER "minor" or "low risk" - ALWAYS recommend urgent medical evaluation
2. Mole changes are NEVER "probably nothing" - ALWAYS recommend dermatology referral
3. Chest pain or breathing difficulty - ALWAYS recommend emergency care if severe
4. Sudden headache or vision changes - ALWAYS recommend urgent evaluation
5. DO NOT suggest home remedies (fiber, stool softeners, etc.) for critical symptoms
6. DO NOT reassure users that critical symptoms are "probably minor"
7. Be direct, honest, and clear about the need for medical evaluation
8. Ask appropriate follow-up questions to gather more information
9. Always include: "This is not a medical diagnosis. Please consult a healthcare professional."

Your tone should be professional, caring, but DIRECT about seriousness when warranted."""},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.4,
                max_tokens=700,
            )
            return completion.choices[0].message.content
        except Exception as e:
            print(f"❌ Groq API error: {e}")
            return self.get_mock_response(user_message, symptoms)
    
    # 🆕 NEW METHOD: get_comprehensive_diagnosis
    def get_comprehensive_diagnosis(self, conversations, symptoms_data, family_history):
        """Get structured comprehensive diagnosis from Groq"""
        if not self.client:
            return self.get_mock_diagnosis()
        
        # Format conversation
        conv_text = ""
        for msg in conversations[-10:]:
            role = "User" if msg['role'] == 'user' else "Assistant"
            # Clean up content (remove excessive newlines)
            content = msg['content'].strip()
            conv_text += f"{role}: {content}\n"
        
        # Format symptoms
        symptoms_text = ""
        for entry in symptoms_data[-5:]:
            symptoms_text += f"{entry['timestamp']}: {entry['message']}\n"
        
        # Format family history
        family_text = ""
        for relation, conditions in family_history.items():
            family_text += f"- {relation}: {', '.join(conditions)}\n"
        
        # 🆕 Check for critical symptoms
        has_critical = False
        critical_symptoms = []
        for entry in symptoms_data:
            if entry.get('has_critical', False):
                has_critical = True
                critical_symptoms.extend(entry.get('critical_type', []))
        
        # 🆕 Check for blood in symptoms
        has_blood = any('blood' in str(entry.get('symptoms', {})).lower() for entry in symptoms_data)
        
        prompt = f"""
        You are SwasthyaAI, a medical health screening assistant.
        
        Based on the patient data below, provide a comprehensive health assessment:
        
        CONVERSATION HISTORY:
        {conv_text}
        
        SYMPTOM TIMELINE:
        {symptoms_text}
        
        FAMILY HISTORY:
        {family_text}
        
        {"🚨 CRITICAL SYMPTOMS DETECTED: " + ", ".join(critical_symptoms) if has_critical else ""}
        {"🚨 BLOOD-RELATED SYMPTOM DETECTED - THIS IS SERIOUS" if has_blood else ""}
        
        CRITICAL FORMATTING INSTRUCTIONS - Use this EXACT structure:
        
        =========================================================
        📋 𝗖𝗢𝗠𝗣𝗥𝗘𝗛𝗘𝗡𝗦𝗜𝗩𝗘 𝗛𝗘𝗔𝗟𝗧𝗛 𝗔𝗦𝗦𝗘𝗦𝗦𝗠𝗘𝗡𝗧
        =========================================================
        
        📊 𝗦𝗬𝗠𝗣𝗧𝗢𝗠 𝗦𝗨𝗠𝗠𝗔𝗥𝗬
        • [Symptom 1: duration/severity]
        • [Symptom 2: duration/severity]
        • [Symptom 3: duration/severity]
        
        🧬 𝗙𝗔𝗠𝗜𝗟𝗬 𝗛𝗜𝗦𝗧𝗢𝗥𝗬 𝗔𝗡𝗔𝗟𝗬𝗦𝗜𝗦
        • [Family history risk factors]
        • [Genetic risk implications]
        
        🏥 𝗣𝗢𝗦𝗦𝗜𝗕𝗟𝗘 𝗖𝗢𝗡𝗗𝗜𝗧𝗜𝗢𝗡𝗦 (𝗹𝗶𝘀𝘁𝗲𝗱 𝗳𝗿𝗼𝗺 𝗺𝗼𝘀𝘁 𝘁𝗼 𝗹𝗲𝗮𝘀𝘁 𝗹𝗶𝗸𝗲𝗹𝘆)
        1. [Condition 1]
        2. [Condition 2]
        3. [Condition 3]
        
        📊 𝗥𝗜𝗦𝗞 𝗔𝗦𝗦𝗘𝗦𝗦𝗠𝗘𝗡𝗧
        • Risk Level: [High/Moderate/Low]
        • Risk Score: [X/100]
        • Key Risk Factors:
          - [Risk factor 1]
          - [Risk factor 2]
        
        💊 𝗥𝗘𝗖𝗢𝗠𝗠𝗘𝗡𝗗𝗔𝗧𝗜𝗢𝗡𝗦
        1. [Actionable recommendation 1]
        2. [Actionable recommendation 2]
        3. [Actionable recommendation 3]
        4. [Actionable recommendation 4]
        
        🚨 𝗪𝗛𝗘𝗡 𝗧𝗢 𝗦𝗘𝗘𝗞 𝗜𝗠𝗠𝗘𝗗𝗜𝗔𝗧𝗘 𝗛𝗘𝗟𝗣
        • [Emergency sign 1]
        • [Emergency sign 2]
        • [Emergency sign 3]
        
        📋 𝗡𝗘𝗫𝗧 𝗦𝗧𝗘𝗣𝗦
        • [Step 1]
        • [Step 2]
        • [Step 3]
        
        {"⚠️ IMPORTANT: Since critical symptoms were detected, ensure risk level is HIGH or CRITICAL." if has_critical else ""}
        {"⚠️ IMPORTANT: Blood in stool requires URGENT medical evaluation. Risk level must be HIGH." if has_blood else ""}
        """
        
        try:
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": """You are SwasthyaAI, a medical health screening assistant. Always respond in structured, point-form format with clear sections and headings.

CRITICAL RULES FOR DIAGNOSIS:
1. If blood in stool is detected: Risk Level = HIGH, recommend gastroenterology
2. If mole changes are detected: Risk Level = HIGH, recommend dermatology
3. If chest pain or breathing difficulty: Risk Level = CRITICAL, recommend emergency care
4. If sudden headache or vision changes: Risk Level = HIGH, recommend neurology
5. NEVER give "Minimal" or "Low" risk for blood, mole changes, or chest pain
6. Be direct and honest about seriousness
7. Always include: "This is not a medical diagnosis. Consult a healthcare professional."""},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=1000,
            )
            
            response_text = completion.choices[0].message.content
            
            return {
                'summary': response_text,
                'conditions': self.extract_conditions(response_text),
                'risk_level': self.extract_risk_level(response_text)
            }
        except Exception as e:
            print(f"❌ Groq API error: {e}")
            return self.get_mock_diagnosis()
    
    def extract_conditions(self, text):
        """Extract possible conditions from structured response"""
        conditions = []
        lines = text.split('\n')
        in_conditions = False
        
        for line in lines:
            line = line.strip()
            if '𝗣𝗢𝗦𝗦𝗜𝗕𝗟𝗘 𝗖𝗢𝗡𝗗𝗜𝗧𝗜𝗢𝗡𝗦' in line or 'POSSIBLE CONDITIONS' in line.upper():
                in_conditions = True
                continue
            if in_conditions and line and (line.startswith('1.') or line.startswith('2.') or line.startswith('3.')):
                # Clean up the condition text
                condition = line.replace('1.', '').replace('2.', '').replace('3.', '').strip()
                conditions.append(condition)
            if in_conditions and line and not line.startswith('•') and not line.startswith('1.') and not line.startswith('2.') and not line.startswith('3.') and not line.startswith('-'):
                in_conditions = False
        
        return conditions[:5]
    
    def extract_risk_level(self, text):
        """Extract risk level from structured response"""
        text_lower = text.lower()
        if 'critical' in text_lower and 'risk' in text_lower:
            return 'Critical'
        elif 'high' in text_lower and 'risk' in text_lower:
            return 'High'
        elif 'moderate' in text_lower and 'risk' in text_lower:
            return 'Moderate'
        elif 'low' in text_lower and 'risk' in text_lower:
            return 'Low'
        return 'Moderate'
    
    def get_mock_response(self, user_message, symptoms):
        """Structured mock response when Groq API fails"""
        symptom_list = list(symptoms.keys())
        symptom_list = [s for s in symptom_list if s not in ['duration', 'duration_unit', 'severity', 'critical', 'critical_type', 'has_mole']]
        
        # 🆕 Check for critical symptoms in mock response
        critical_markers = ['mole', 'chest pain', 'blood in stool', 'blood in urine', 'shortness of breath', 'blood']
        is_critical = any(marker in ' '.join(symptom_list).lower() for marker in critical_markers)
        
        warning = ""
        if is_critical:
            warning = """
🚨 **⚠️ CRITICAL SYMPTOM DETECTED**
• Please seek medical attention immediately
• Do not rely on this AI assessment for diagnosis
• This requires evaluation by a healthcare professional
"""
        
        if not symptom_list:
            return f"""
📋 𝗦𝗬𝗠𝗣𝗧𝗢𝗠 𝗔𝗖𝗞𝗡𝗢𝗪𝗟𝗘𝗗𝗚𝗠𝗘𝗡𝗧
• I notice you haven't mentioned any specific symptoms
{warning if is_critical else ""}

📋 𝗙𝗢𝗟𝗟𝗢𝗪-𝗨𝗣 𝗤𝗨𝗘𝗦𝗧𝗜𝗢𝗡𝗦
• Could you describe how you're feeling in more detail?
• When did you first notice any changes in your health?
• Do you have any other symptoms to share?

📋 𝗥𝗘𝗖𝗢𝗠𝗠𝗘𝗡𝗗𝗔𝗧𝗜𝗢𝗡𝗦
• Please describe your symptoms with details like duration and severity
• Include any family history that might be relevant
"""
        
        return f"""
📋 𝗦𝗬𝗠𝗣𝗧𝗢𝗠 𝗔𝗖𝗞𝗡𝗢𝗪𝗟𝗘𝗗𝗚𝗠𝗘𝗡𝗧
• I notice you're experiencing: {', '.join(symptom_list)}
• Duration: {symptoms.get('duration', 'not specified')} days
{warning}

📋 𝗙𝗢𝗟𝗟𝗢𝗪-𝗨𝗣 𝗤𝗨𝗘𝗦𝗧𝗜𝗢𝗡𝗦
• Can you tell me more about when these symptoms started?
• Have you taken any medication for these symptoms?
• Do you have any other symptoms not mentioned?

📋 𝗥𝗘𝗖𝗢𝗠𝗠𝗘𝗡𝗗𝗔𝗧𝗜𝗢𝗡𝗦
• {"Seek immediate medical attention" if is_critical else "Consider scheduling a doctor consultation"}
• Monitor your symptoms and track any changes
• Stay hydrated and get adequate rest

📋 𝗪𝗛𝗘𝗡 𝗧𝗢 𝗦𝗘𝗘𝗞 𝗛𝗘𝗟𝗣
• {"TODAY - This requires medical evaluation" if is_critical else "If symptoms worsen or persist"}
• If you experience severe pain or difficulty breathing
"""
    
    def get_mock_diagnosis(self):
        """Structured mock comprehensive diagnosis with critical detection"""
        return {
            'summary': """
=========================================================
📋 𝗖𝗢𝗠𝗣𝗥𝗘𝗛𝗘𝗡𝗦𝗜𝗩𝗘 𝗛𝗘𝗔𝗟𝗧𝗛 𝗔𝗦𝗦𝗘𝗦𝗦𝗠𝗘𝗡𝗧
=========================================================

📊 𝗦𝗬𝗠𝗣𝗧𝗢𝗠 𝗦𝗨𝗠𝗠𝗔𝗥𝗬
• Multiple symptoms reported
• Duration and severity need monitoring

🏥 𝗣𝗢𝗦𝗦𝗜𝗕𝗟𝗘 𝗖𝗢𝗡𝗗𝗜𝗧𝗜𝗢𝗡𝗦
1. Gastrointestinal issue
2. Infection
3. Inflammatory condition

📊 𝗥𝗜𝗦𝗞 𝗔𝗦𝗦𝗘𝗦𝗦𝗠𝗘𝗡𝗧
• Risk Level: Moderate
• Risk Score: 45/100

💊 𝗥𝗘𝗖𝗢𝗠𝗠𝗘𝗡𝗗𝗔𝗧𝗜𝗢𝗡𝗦
1. Consult a healthcare professional
2. Monitor symptoms for 2-3 days
3. Stay hydrated and rest

🚨 𝗪𝗛𝗘𝗡 𝗧𝗢 𝗦𝗘𝗘𝗞 𝗛𝗘𝗟𝗣
• If symptoms worsen
• If fever exceeds 103°F
• If you experience difficulty breathing
""",
            'conditions': ['Gastrointestinal issue', 'Infection', 'Inflammatory condition'],
            'risk_level': 'Moderate'
        }