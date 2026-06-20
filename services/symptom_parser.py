import re

class SymptomParser:
    def __init__(self):
        # Common symptoms and their keywords
        self.symptom_keywords = {
            'fever': ['fever', 'temperature', 'high temp', 'hot', 'chills'],
            'cough': ['cough', 'coughing', 'hacking'],
            'headache': ['headache', 'head pain', 'migraine', 'throbbing head'],
            'fatigue': ['fatigue', 'tired', 'exhausted', 'weak', 'low energy'],
            'chest pain': ['chest pain', 'chest tightness', 'heart pain'],
            'shortness of breath': ['shortness of breath', 'breathing difficulty', 'breathless', 'hard to breathe'],
            'weight loss': ['weight loss', 'lost weight', 'losing weight'],
            'nausea': ['nausea', 'sick stomach', 'queasy'],
            'dizziness': ['dizzy', 'dizziness', 'lightheaded', 'vertigo'],
            'sore throat': ['sore throat', 'throat pain', 'scratchy throat'],
            'runny nose': ['runny nose', 'stuffy nose', 'congestion', 'blocked nose'],
            'body aches': ['body aches', 'muscle pain', 'achiness', 'soreness'],
            'diarrhea': ['diarrhea', 'loose stools', 'bowel'],
            'vomiting': ['vomit', 'vomiting', 'threw up', 'puking']
        }
    
    def parse(self, message):
        """Extract symptoms from user message"""
        message = message.lower()
        detected_symptoms = {}
        
        for symptom, keywords in self.symptom_keywords.items():
            for keyword in keywords:
                if keyword in message:
                    detected_symptoms[symptom] = True
                    break
        
        # Extract duration if mentioned
        duration_patterns = [
            r'(\d+)\s*days?',
            r'(\d+)\s*weeks?',
            r'(\d+)\s*months?',
            r'(\d+)\s*hours?'
        ]
        
        for pattern in duration_patterns:
            match = re.search(pattern, message)
            if match:
                detected_symptoms['duration'] = int(match.group(1))
                if 'days' in pattern:
                    detected_symptoms['duration_unit'] = 'days'
                elif 'weeks' in pattern:
                    detected_symptoms['duration_unit'] = 'weeks'
                break
        
        return detected_symptoms