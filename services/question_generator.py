class QuestionGenerator:
    def __init__(self):
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
            ]
        }
    
    def generate_questions(self, symptoms, user_message):
        """Generate follow-up questions based on symptoms"""
        questions = []
        current_symptoms = list(symptoms.keys())
        current_symptoms = [s for s in current_symptoms if s not in ['duration', 'duration_unit']]
        
        for symptom in current_symptoms[:3]:
            if symptom in self.follow_up_questions:
                questions.extend(self.follow_up_questions[symptom][:2])
        
        if not questions:
            questions = [
                "Could you describe your symptoms in more detail?",
                "How long have you been experiencing these symptoms?",
                "Do you have any other symptoms not mentioned?"
            ]
        
        return questions
    
    def generate_questions_with_context(self, symptoms, user_message, recent_messages=None):
        """Generate follow-up questions considering conversation context"""
        asked_questions = []
        if recent_messages:
            for msg in recent_messages:
                if msg.get('role') == 'assistant':
                    content = msg.get('content', '').lower()
                    question_topics = ['temperature', 'medication', 'chills', 'cough', 'headache', 
                                     'appetite', 'sleep', 'nausea', 'chest', 'breath', 'dizziness',
                                     'activity', 'pain', 'vision', 'swallow', 'mucus', 'blood',
                                     'stress', 'weight', 'digestive', 'fever']
                    for topic in question_topics:
                        if topic in content:
                            asked_questions.append(topic)
        
        questions = self.generate_questions(symptoms, user_message)
        
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
        
        if not filtered_questions:
            symptom_list = [s for s in symptoms.keys() if s not in ['duration', 'duration_unit']]
            
            if 'fever' in symptom_list:
                filtered_questions = [
                    "Have you noticed any rash or skin changes?",
                    "Are you able to keep fluids down?",
                    "Have you been in contact with anyone who's sick?"
                ]
            elif 'headache' in symptom_list:
                filtered_questions = [
                    "Does light or sound make your headache worse?",
                    "Have you had any visual changes?",
                    "Is the headache affecting your daily activities?"
                ]
            elif 'fatigue' in symptom_list:
                filtered_questions = [
                    "How has your sleep been lately?",
                    "Are you experiencing any muscle weakness?",
                    "Have you had any changes in your appetite?"
                ]
            elif 'chest pain' in symptom_list:
                filtered_questions = [
                    "Does the pain radiate to your arm or jaw?",
                    "Are you feeling anxious or stressed?",
                    "Do you have any history of heart problems?"
                ]
            elif 'cough' in symptom_list:
                filtered_questions = [
                    "Are you coughing up any mucus or blood?",
                    "Does the cough keep you awake at night?",
                    "Have you had any fever with the cough?"
                ]
            else:
                filtered_questions = [
                    "Could you describe your symptoms in more detail?",
                    "When did these symptoms first start?",
                    "Have you had any similar symptoms in the past?"
                ]
        
        return filtered_questions[:3]