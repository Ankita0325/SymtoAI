# services/groq_service.py
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
        
        family_info = ""
        if family_history:
            family_info = "\nFamily History:\n"
            for relation, conditions in family_history.items():
                family_info += f"- {relation}: {', '.join(conditions)}\n"
        
        prompt = f"""
        You are SwasthyaAI, a compassionate health screening assistant.
        
        User says: "{user_message}"
        Detected symptoms: {symptom_list}
        Duration: {duration} {duration_unit}
        {family_info}
        
        CRITICAL FORMATTING INSTRUCTIONS:
        
        Structure your response in the following EXACT format:
        
        𝗦𝗬𝗠𝗣𝗧𝗢𝗠 𝗔𝗖𝗞𝗡𝗢𝗪𝗟𝗘𝗗𝗚𝗠𝗘𝗡𝗧
        • [Empathetic acknowledgment of their symptoms]
        
        𝗙𝗢𝗟𝗟𝗢𝗪-𝗨𝗣 𝗤𝗨𝗘𝗦𝗧𝗜𝗢𝗡𝗦
        • [Question 1 - specific and relevant]
        • [Question 2 - specific and relevant]
        • [Question 3 - specific and relevant]
        
        𝗣𝗢𝗦𝗦𝗜𝗕𝗟𝗘 𝗖𝗢𝗡𝗦𝗜𝗗𝗘𝗥𝗔𝗧𝗜𝗢𝗡𝗦
        • [General health insight 1]
        • [General health insight 2]
        
        𝗥𝗘𝗖𝗢𝗠𝗠𝗘𝗡𝗗𝗔𝗧𝗜𝗢𝗡𝗦
        • [Recommendation 1 - actionable]
        • [Recommendation 2 - actionable]
        • [Recommendation 3 - actionable]
        
        𝗪𝗛𝗘𝗡 𝗧𝗢 𝗦𝗘𝗘𝗞 𝗛𝗘𝗟𝗣
        • [Clear guidance on when to see a doctor]
        • [Emergency warning signs if applicable]
        
        Keep each section concise. Use bullet points (•). Be professional and warm.
        """
        
        try:
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are SwasthyaAI, a health screening assistant. Always respond in structured point form with clear sections."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5,
                max_tokens=600,
            )
            return completion.choices[0].message.content
        except Exception as e:
            print(f"❌ Groq API error: {e}")
            return self.get_mock_response(user_message, symptoms)
    
    def get_comprehensive_diagnosis(self, conversations, symptoms_data, family_history):
        """Get structured comprehensive diagnosis from Groq"""
        if not self.client:
            return self.get_mock_diagnosis()
        
        # Format conversation
        conv_text = ""
        for msg in conversations[-10:]:
            role = "User" if msg['role'] == 'user' else "Assistant"
            conv_text += f"{role}: {msg['content']}\n"
        
        # Format symptoms
        symptoms_text = ""
        for entry in symptoms_data[-5:]:
            symptoms_text += f"{entry['timestamp']}: {entry['message']}\n"
        
        # Format family history
        family_text = ""
        for relation, conditions in family_history.items():
            family_text += f"- {relation}: {', '.join(conditions)}\n"
        
        prompt = f"""
        You are SwasthyaAI, a medical health screening assistant.
        
        Based on the patient data below, provide a comprehensive health assessment:
        
        CONVERSATION HISTORY:
        {conv_text}
        
        SYMPTOM TIMELINE:
        {symptoms_text}
        
        FAMILY HISTORY:
        {family_text}
        
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
        """
        
        try:
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are SwasthyaAI, a medical health screening assistant. Always respond in structured, point-form format with clear sections and headings."},
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
                conditions.append(line)
            if in_conditions and line and not line.startswith('•') and not line.startswith('1.') and not line.startswith('2.'):
                in_conditions = False
        
        return conditions[:5]
    
    def extract_risk_level(self, text):
        """Extract risk level from structured response"""
        text_lower = text.lower()
        if 'high' in text_lower and 'risk' in text_lower:
            return 'High'
        elif 'moderate' in text_lower and 'risk' in text_lower:
            return 'Moderate'
        elif 'low' in text_lower and 'risk' in text_lower:
            return 'Low'
        return 'Moderate'
    
    def get_mock_response(self, user_message, symptoms):
        """Structured mock response when Groq API fails"""
        symptom_list = list(symptoms.keys())
        symptom_list = [s for s in symptom_list if s not in ['duration', 'duration_unit']]
        
        if not symptom_list:
            return """
📋 𝗦𝗬𝗠𝗣𝗧𝗢𝗠 𝗔𝗖𝗞𝗡𝗢𝗪𝗟𝗘𝗗𝗚𝗠𝗘𝗡𝗧
• I notice you haven't mentioned any specific symptoms

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

📋 𝗙𝗢𝗟𝗟𝗢𝗪-𝗨𝗣 𝗤𝗨𝗘𝗦𝗧𝗜𝗢𝗡𝗦
• Can you tell me more about when these symptoms started?
• Have you taken any medication for these symptoms?
• Do you have any other symptoms not mentioned?

📋 𝗥𝗘𝗖𝗢𝗠𝗠𝗘𝗡𝗗𝗔𝗧𝗜𝗢𝗡𝗦
• Consider scheduling a doctor consultation
• Monitor your symptoms and track any changes
• Stay hydrated and get adequate rest
"""
    
    def get_mock_diagnosis(self):
        """Structured mock comprehensive diagnosis"""
        return {
            'summary': """
=========================================================
📋 𝗖𝗢𝗠𝗣𝗥𝗘𝗛𝗘𝗡𝗦𝗜𝗩𝗘 𝗛𝗘𝗔𝗟𝗧𝗛 𝗔𝗦𝗦𝗘𝗦𝗦𝗠𝗘𝗡𝗧
=========================================================

📊 𝗦𝗬𝗠𝗣𝗧𝗢𝗠 𝗦𝗨𝗠𝗠𝗔𝗥𝗬
• Multiple symptoms reported
• Duration and severity need monitoring

🏥 𝗣𝗢𝗦𝗦𝗜𝗕𝗟𝗘 𝗖𝗢𝗡𝗗𝗜𝗧𝗜𝗢𝗡𝗦
1. Viral infection
2. Stress-related symptoms
3. Seasonal illness

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
            'conditions': ['Viral infection', 'Stress-related symptoms', 'Seasonal illness'],
            'risk_level': 'Moderate'
        }