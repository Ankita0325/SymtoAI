# services/question_generator.py
import re
from typing import List, Dict, Any, Optional
from datetime import datetime

class QuestionGenerator:
    def __init__(self, groq_service=None):
        # ✅ Optionally inject Groq for AI-generated questions
        self.groq_service = groq_service
        
        # Base question templates (fallback)
        self.follow_up_questions = {
            'fever': [
                "What is your current temperature?",
                "Have you taken any medication for the fever?",
                "Do you have chills along with the fever?",
                "Is the fever constant or does it come and go?",
                "Have you experienced any sweating?"
            ],
            'cough': [
                "Is your cough dry or productive (bringing up mucus)?",
                "How long have you had the cough?",
                "Is it worse at night or during the day?",
                "Do you cough up any blood?",
                "Does coughing cause chest pain?"
            ],
            'chest pain': [
                "Does the pain increase during physical activity?",
                "Do you experience shortness of breath with it?",
                "Is the pain sharp or a dull ache?",
                "Does the pain radiate to your arm or jaw?",
                "Do you feel dizzy or nauseous with the pain?"
            ],
            'headache': [
                "Is the headache throbbing or a dull ache?",
                "Are you sensitive to light or sound?",
                "Have you had headaches like this before?",
                "Do you feel dizzy with the headache?",
                "Does the headache affect your vision?"
            ],
            'fatigue': [
                "How long have you been feeling tired?",
                "Is the fatigue affecting your daily activities?",
                "How many hours of sleep do you get at night?",
                "Do you feel weak or have muscle aches?",
                "Have you experienced any weight changes?"
            ],
            'shortness of breath': [
                "Does it happen at rest or during activity?",
                "Do you have any underlying lung conditions?",
                "Have you had any chest pain with breathing?",
                "Do you feel dizzy when you stand up?",
                "Is it worse when lying down?"
            ],
            'weight loss': [
                "How much weight have you lost?",
                "Is the weight loss intentional?",
                "Have you noticed changes in appetite?",
                "Do you have any digestive issues?",
                "Have you been feeling more stressed?"
            ],
            'nausea': [
                "Does the nausea lead to vomiting?",
                "Is it worse after eating certain foods?",
                "Are you able to keep fluids down?",
                "Do you have any abdominal pain?",
                "Have you experienced any fever with this?"
            ],
            'sore throat': [
                "Does it hurt to swallow?",
                "Do you have swollen glands in your neck?",
                "Is your throat red or do you see white patches?",
                "Do you have a fever with the sore throat?",
                "Have you had any cough with this?"
            ],
            'dizziness': [
                "Does the dizziness happen when you stand up?",
                "Have you felt faint or lightheaded?",
                "Does it come on suddenly or gradually?",
                "Have you had any nausea with it?",
                "Do you have any ringing in your ears?"
            ],
            'body aches': [
                "Where exactly do you feel the aches?",
                "Does it feel like muscle pain or joint pain?",
                "Have you taken any pain relievers?",
                "Do you have a fever with the aches?",
                "Have you had any swelling?"
            ],
            'runny nose': [
                "Is the discharge clear, yellow, or green?",
                "Do you have any sinus pressure or pain?",
                "Is it accompanied by sneezing?",
                "Do you have any fever with this?",
                "Have you had any headache with it?"
            ],
            'mole': [
                "When did you first notice the mole changing?",
                "Has the mole become asymmetrical or irregular in shape?",
                "What color changes have you noticed in the mole?",
                "Has the mole increased in size or diameter?",
                "Is the mole bleeding, oozing, or crusting?",
                "Does the mole itch or feel tender?",
                "Have you had any previous skin cancer or moles removed?",
                "Do you have other moles that look different from this one?",
                "Is the mole raised, flat, or changing texture?",
                "Have you had significant sun exposure or sunburns?"
            ],
            'skin rash': [
                "Where on your body is the rash located?",
                "Does the rash itch, burn, or hurt?",
                "Have you used any new soaps or lotions recently?",
                "Do you have any other symptoms with the rash?",
                "Has the rash spread or changed appearance?"
            ],
            'skin lesion': [
                "How long has the lesion been present?",
                "Is the lesion painful or tender?",
                "Does it bleed or drain fluid?",
                "Have you noticed any changes in its appearance?",
                "Do you have a history of skin conditions?"
            ],
            'blood in stool': [
                "Is the blood bright red or dark/tarry?",
                "Is the blood mixed with stool or on the surface?",
                "Have you had any abdominal pain?",
                "Have you noticed any changes in bowel habits?",
                "Do you have any family history of colon cancer?"
            ],
            'blood in urine': [
                "Is the urine pink, red, or brown?",
                "Do you have any pain with urination?",
                "Have you had any lower back pain?",
                "Do you have any history of kidney stones?",
                "Are you taking any blood-thinning medications?"
            ],
            'vision changes': [
                "Is the vision change sudden or gradual?",
                "Is it in one eye or both eyes?",
                "Do you have any headache with the vision change?",
                "Are you seeing flashes of light or floaters?",
                "Do you have any eye pain or redness?"
            ],
            'sudden headache': [
                "Is this the worst headache of your life?",
                "Did it come on suddenly or build up?",
                "Do you have any nausea or vomiting?",
                "Are you sensitive to light or sound?",
                "Do you have any weakness or numbness?"
            ],
            'back pain': [
                "Is the pain in your lower back, upper back, or neck?",
                "Does the pain radiate to your legs or arms?",
                "What makes the pain better or worse?",
                "Have you had any injury or trauma?",
                "Does the pain affect your ability to move?"
            ],
            'numbness': [
                "Where exactly do you feel numbness?",
                "Is the numbness spreading or staying in one area?",
                "Do you have any tingling or weakness?",
                "Does it affect your ability to move?",
                "Have you had any injuries to that area?"
            ]
        }
        
        # ✅ Dynamic category mapping
        self.symptom_categories = {
            'pain': ['chest pain', 'back pain', 'abdominal pain', 'body aches'],
            'respiratory': ['cough', 'shortness of breath', 'runny nose', 'sore throat'],
            'neurological': ['headache', 'dizziness', 'vision changes', 'numbness', 'sudden headache'],
            'skin': ['mole changed color', 'mole changed shape', 'mole changed size', 'mole bleeding', 
                    'mole itching', 'skin rash', 'skin lesion'],
            'blood': ['blood in stool', 'blood in urine', 'vomiting blood']
        }
    
    def generate_questions(self, symptoms: Dict[str, Any], user_message: str = "", 
                          patient_context: Optional[Dict] = None) -> List[str]:
        """
        Generate follow-up questions based on symptoms
        ✅ Now supports patient context
        """
        questions = []
        current_symptoms = list(symptoms.keys())
        current_symptoms = [s for s in current_symptoms if s not in ['duration', 'duration_unit', 'severity', 'critical', 'critical_type', 'has_mole']]
        
        # ✅ Check for patient context (age, gender, etc.)
        if patient_context:
            questions.extend(self._generate_context_questions(patient_context))
        
        # Check for critical symptoms first
        critical_symptoms = ['mole changed color', 'mole changed shape', 'mole changed size', 
                           'mole bleeding', 'mole itching', 'blood in stool', 'blood in urine',
                           'chest pain', 'shortness of breath', 'sudden headache']
        
        for symptom in current_symptoms[:3]:
            # Check for critical symptoms
            if any(critical in symptom for critical in critical_symptoms):
                questions.extend(self._get_critical_follow_ups(symptom))
            # Check for regular symptoms
            elif symptom in self.follow_up_questions:
                # ✅ Randomize which questions are asked
                import random
                q_list = self.follow_up_questions[symptom]
                selected = random.sample(q_list, min(2, len(q_list)))
                questions.extend(selected)
        
        # If no questions generated, use generic
        if not questions:
            questions = self._get_generic_questions(symptoms)
        
        # ✅ Add personalized questions based on user message
        personalized = self._generate_personalized_questions(user_message, symptoms)
        if personalized:
            questions.extend(personalized)
        
        return questions[:5]
    
    def generate_questions_with_context(self, symptoms: Dict[str, Any], user_message: str, 
                                       recent_messages: Optional[List[Dict]] = None,
                                       patient_context: Optional[Dict] = None) -> List[str]:
        """
        Generate follow-up questions considering conversation context
        ✅ FIXED: Added patient context support
        """
        asked_questions = []
        
        # Extract previously asked questions
        if recent_messages:
            for msg in recent_messages:
                if msg.get('role') == 'assistant':
                    content = msg.get('content', '').lower()
                    # Extract question topics
                    question_topics = ['temperature', 'medication', 'chills', 'cough', 'headache', 
                                     'appetite', 'sleep', 'nausea', 'chest', 'breath', 'dizziness',
                                     'activity', 'pain', 'vision', 'swallow', 'mucus', 'blood',
                                     'stress', 'weight', 'digestive', 'fever', 'mole', 'asymmetry',
                                     'border', 'color', 'diameter', 'itching', 'bleeding']
                    for topic in question_topics:
                        if topic in content:
                            asked_questions.append(topic)
        
        # ✅ Try AI-generated questions first (if available)
        if self.groq_service:
            try:
                ai_questions = self._generate_ai_questions(symptoms, user_message, recent_messages)
                if ai_questions:
                    return ai_questions[:3]
            except Exception as e:
                print(f"⚠️ AI question generation failed: {e}")
        
        # Fallback to template-based questions
        questions = self.generate_questions(symptoms, user_message, patient_context)
        
        # Filter out already asked questions
        filtered_questions = []
        for question in questions:
            question_lower = question.lower()
            already_asked = False
            for asked in asked_questions:
                if asked in question_lower:
                    already_asked = True
                    break
            if not already_asked:
                filtered_questions.append(question)
        
        # If no questions, use context-aware fallback
        if not filtered_questions:
            filtered_questions = self._get_context_aware_fallback(symptoms, user_message)
        
        return filtered_questions[:3]
    
    # ============================================================
    # ✅ NEW: AI-Generated Questions
    # ============================================================
    
    def _generate_ai_questions(self, symptoms: Dict[str, Any], user_message: str, 
                               recent_messages: List[Dict]) -> Optional[List[str]]:
        """Generate questions using Groq AI"""
        if not self.groq_service:
            return None
        
        try:
            symptom_list = ", ".join(symptoms.keys()) if symptoms else "none"
            
            prompt = f"""
            Based on these symptoms: {symptom_list}
            And the patient's message: {user_message}
            
            Generate 3 focused follow-up questions to better understand the patient's condition.
            Questions should be:
            1. Specific and actionable
            2. Not already obvious from the symptoms
            3. Helpful for medical triage
            
            Return only the questions, one per line, without numbering.
            """
            
            # Use Groq to generate questions
            response = self.groq_service.client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": "You are a medical assistant generating follow-up questions."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=200
            )
            
            text = response.choices[0].message.content
            questions = [q.strip() for q in text.split('\n') if q.strip()]
            return questions[:3]
        except Exception as e:
            print(f"⚠️ AI question generation error: {e}")
            return None
    
    # ============================================================
    # ✅ NEW: Personalized Questions
    # ============================================================
    
    def _generate_context_questions(self, context: Dict) -> List[str]:
        """Generate questions based on patient context"""
        questions = []
        
        age = context.get('age')
        if age:
            if age < 18:
                questions.append("Are your parents aware of these symptoms?")
            elif age > 65:
                questions.append("Are you taking any medications for chronic conditions?")
        
        gender = context.get('gender')
        if gender and gender.lower() == 'female':
            questions.append("Could you be pregnant?")
            questions.append("When was your last menstrual period?")
        
        return questions
    
    def _generate_personalized_questions(self, user_message: str, symptoms: Dict) -> List[str]:
        """Generate personalized questions based on user message"""
        questions = []
        user_lower = user_message.lower()
        
        if 'heavy lifting' in user_lower or 'lifting' in user_lower:
            questions.append("What was the weight of the object you lifted?")
            questions.append("Did you use proper lifting technique?")
        
        if 'fall' in user_lower or 'fell' in user_lower:
            questions.append("Did you hit your head during the fall?")
            questions.append("Were you unconscious at any point?")
        
        if 'stress' in user_lower or 'anxious' in user_lower:
            questions.append("Have you been experiencing increased stress lately?")
            questions.append("Are you sleeping well?")
        
        if 'medication' in user_lower or 'medicine' in user_lower:
            questions.append("Are you taking any prescription medications?")
            questions.append("Have you taken any over-the-counter medications?")
        
        return questions
    
    # ============================================================
    # ✅ NEW: Critical Follow-ups
    # ============================================================
    
    def _get_critical_follow_ups(self, symptom: str) -> List[str]:
        """Get critical follow-up questions"""
        critical_questions = {
            'mole': [
                "When did you first notice the mole changing?",
                "Has it changed rapidly or slowly?",
                "Do you have a family history of skin cancer?"
            ],
            'blood': [
                "When did you first notice the blood?",
                "How much blood have you seen?",
                "Are you taking any blood-thinning medications?"
            ],
            'chest': [
                "Does the pain radiate to your arm, neck, or jaw?",
                "Are you feeling short of breath?",
                "Are you feeling dizzy or nauseous?"
            ]
        }
        
        if 'mole' in symptom.lower():
            return critical_questions['mole']
        elif 'blood' in symptom.lower():
            return critical_questions['blood']
        elif 'chest' in symptom.lower():
            return critical_questions['chest']
        return []
    
    def _get_generic_questions(self, symptoms: Dict) -> List[str]:
        """Get generic questions when no specific symptoms detected"""
        return [
            "Could you describe your symptoms in more detail?",
            "How long have you been experiencing these symptoms?",
            "Do you have any other symptoms not mentioned?",
            "Have you taken any medication for these symptoms?",
            "Does anything make the symptoms better or worse?"
        ]
    
    def _get_context_aware_fallback(self, symptoms: Dict, user_message: str) -> List[str]:
        """Generate context-aware fallback questions"""
        symptom_list = [s for s in symptoms.keys() if s not in ['duration', 'duration_unit', 'severity', 'critical', 'critical_type', 'has_mole']]
        user_lower = user_message.lower()
        
        if 'mole' in user_lower or any('mole' in s for s in symptom_list):
            return [
                "Have you taken photos of the mole to track changes?",
                "Do you have any family history of skin cancer or melanoma?",
                "Have you had any significant sun exposure or sunburns in the past?"
            ]
        elif 'fever' in user_lower or 'fever' in ' '.join(symptom_list):
            return [
                "Have you noticed any rash or skin changes?",
                "Are you able to keep fluids down?",
                "Have you been in contact with anyone who's sick?"
            ]
        elif 'headache' in user_lower or 'headache' in ' '.join(symptom_list):
            return [
                "Does light or sound make your headache worse?",
                "Have you had any visual changes?",
                "Is the headache affecting your daily activities?"
            ]
        elif any('blood' in s for s in symptom_list) or 'blood' in user_lower:
            return [
                "When did you first notice the blood?",
                "How much blood have you seen?",
                "Are you taking any blood-thinning medications?"
            ]
        elif any('chest' in s for s in symptom_list) or 'chest' in user_lower:
            return [
                "Does the pain radiate to your arm or jaw?",
                "Are you feeling anxious or stressed?",
                "Do you have any history of heart problems?"
            ]
        else:
            return [
                "Could you describe your symptoms in more detail?",
                "When did these symptoms first start?",
                "Have you had any similar symptoms in the past?"
            ]