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
            ],
            # 🆕 SKIN/MOLE QUESTIONS
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
            ]
        }
    
    def generate_questions(self, symptoms, user_message):
        """Generate follow-up questions based on symptoms"""
        questions = []
        current_symptoms = list(symptoms.keys())
        current_symptoms = [s for s in current_symptoms if s not in ['duration', 'duration_unit', 'severity', 'critical', 'critical_type', 'has_mole']]
        
        # 🆕 Check for mole/skin symptoms first (priority)
        mole_symptoms = ['mole changed color', 'mole changed shape', 'mole changed size', 
                        'mole bleeding', 'mole itching', 'skin rash', 'skin lesion']
        
        for symptom in current_symptoms[:3]:
            # Check if symptom matches any mole-related key
            for mole_key in mole_symptoms:
                if mole_key in symptom:
                    if 'mole' in self.follow_up_questions:
                        questions.extend(self.follow_up_questions['mole'][:3])
                    break
            
            # Regular symptom questions
            if symptom in self.follow_up_questions:
                questions.extend(self.follow_up_questions[symptom][:2])
        
        # 🆕 If no questions generated, use generic
        if not questions:
            questions = [
                "Could you describe your symptoms in more detail?",
                "How long have you been experiencing these symptoms?",
                "Do you have any other symptoms not mentioned?"
            ]
        
        # 🆕 If mole symptoms detected, add specific follow-up
        if any('mole' in s for s in current_symptoms):
            questions.insert(0, "⚠️ Since you mentioned a mole change, have you noticed any of these: asymmetry, irregular border, multiple colors, or diameter larger than 6mm?")
        
        return questions[:5]  # Return top 5
    
    # 🆕 NEW METHOD: generate_questions_with_context
    def generate_questions_with_context(self, symptoms, user_message, recent_messages=None):
        """
        Generate follow-up questions considering conversation context
        
        Args:
            symptoms: Dict of detected symptoms
            user_message: Current user message
            recent_messages: List of recent conversation messages
            
        Returns:
            List of follow-up questions
        """
        asked_questions = []
        
        # Extract previously asked questions from conversation history
        if recent_messages:
            for msg in recent_messages:
                if msg.get('role') == 'assistant':
                    content = msg.get('content', '').lower()
                    # Extract question topics that were already asked
                    question_topics = ['temperature', 'medication', 'chills', 'cough', 'headache', 
                                     'appetite', 'sleep', 'nausea', 'chest', 'breath', 'dizziness',
                                     'activity', 'pain', 'vision', 'swallow', 'mucus', 'blood',
                                     'stress', 'weight', 'digestive', 'fever', 'mole', 'asymmetry',
                                     'border', 'color', 'diameter', 'itching', 'bleeding']
                    for topic in question_topics:
                        if topic in content:
                            asked_questions.append(topic)
        
        # Get base questions
        questions = self.generate_questions(symptoms, user_message)
        
        # Filter out questions that were already asked
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
        
        # 🆕 If no questions left, generate context-aware fallback
        if not filtered_questions:
            symptom_list = [s for s in symptoms.keys() if s not in ['duration', 'duration_unit', 'severity', 'critical', 'critical_type', 'has_mole']]
            
            # Check for critical symptoms first
            if 'mole changed color' in symptom_list or 'mole changed shape' in symptom_list or 'mole changed size' in symptom_list:
                filtered_questions = [
                    "Have you taken photos of the mole to track changes?",
                    "Do you have any family history of skin cancer or melanoma?",
                    "Have you had any significant sun exposure or sunburns in the past?"
                ]
            elif 'fever' in symptom_list:
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
                # Generic fallback
                filtered_questions = [
                    "Could you describe your symptoms in more detail?",
                    "When did these symptoms first start?",
                    "Have you had any similar symptoms in the past?"
                ]
        
        return filtered_questions[:3]  # Return max 3 questions