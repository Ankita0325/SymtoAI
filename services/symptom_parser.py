import re

class SymptomParser:
    def __init__(self):
        # Common symptoms and their keywords
        self.symptom_keywords = {
            'fever': ['fever', 'temperature', 'high temp', 'hot', 'chills'],
            'cough': ['cough', 'coughing', 'hacking'],
            'headache': ['headache', 'head pain', 'migraine', 'throbbing head'],
            'fatigue': ['fatigue', 'tired', 'exhausted', 'weak', 'low energy', 'lethargic'],
            'chest pain': ['chest pain', 'chest tightness', 'heart pain'],
            'shortness of breath': ['shortness of breath', 'breathing difficulty', 'breathless', 'hard to breathe'],
            'weight loss': ['weight loss', 'lost weight', 'losing weight'],
            'nausea': ['nausea', 'sick stomach', 'queasy'],
            'dizziness': ['dizzy', 'dizziness', 'lightheaded', 'vertigo'],
            'sore throat': ['sore throat', 'throat pain', 'scratchy throat'],
            'runny nose': ['runny nose', 'stuffy nose', 'congestion', 'blocked nose'],
            'body aches': ['body aches', 'muscle pain', 'achiness', 'soreness'],
            'diarrhea': ['diarrhea', 'loose stools', 'bowel'],
            'vomiting': ['vomit', 'vomiting', 'threw up', 'puking'],
            
            # 🆕 CRITICAL: Skin and mole symptoms
            'mole changed color': ['mole changed color', 'mole colour change', 'mole turned', 'mole darken', 'mole lighten'],
            'mole changed shape': ['mole changed shape', 'mole shape change', 'mole irregular', 'mole asymmetrical', 'mole border'],
            'mole changed size': ['mole changed size', 'mole grew', 'mole bigger', 'mole enlarged', 'mole increased'],
            'mole bleeding': ['mole bleeding', 'mole blood', 'mole oozing', 'mole crust'],
            'mole itching': ['mole itchy', 'mole itch', 'mole irritated', 'mole scaly'],
            'skin rash': ['rash', 'redness', 'skin irritation', 'itchy skin', 'hives', 'bumps', 'blisters'],
            'skin lesion': ['lesion', 'sore', 'ulcer', 'wound', 'growth', 'lump on skin'],
            'bruising': ['bruise', 'bruising', 'black and blue', 'hematoma'],
            
            # 🆕 Additional critical symptoms
            'blood in stool': ['blood in stool', 'bloody stool', 'blood in poop', 'rectal bleeding'],
            'blood in urine': ['blood in urine', 'bloody urine', 'blood in pee', 'hematuria'],
            'vision changes': ['vision changes', 'blurry vision', 'double vision', 'loss of vision', 'eye sight'],
            'sudden headache': ['sudden headache', 'worst headache', 'explosive headache', 'thunderclap'],
        }
        
        # 🆕 Critical symptom markers (for risk escalation)
        self.CRITICAL_KEYWORDS = {
            'mole': ['mole', 'melanoma', 'skin cancer'],
            'changed': ['changed', 'change', 'changing', 'different', 'new'],
            'color': ['color', 'colour', 'black', 'brown', 'red', 'white', 'blue', 'dark', 'light', 'multicolored'],
            'shape': ['shape', 'border', 'edge', 'irregular', 'asymmetrical', 'notched', 'scalloped'],
            'size': ['size', 'diameter', 'grew', 'bigger', 'larger', 'increase', 'expanded'],
            'bleeding': ['bleeding', 'blood', 'oozing', 'crust', 'scab', 'weeping'],
            'itching': ['itch', 'itchy', 'itching', 'scratch', 'irritated', 'tender'],
        }
        
        # 🆕 Severity modifiers
        self.SEVERITY_MODIFIERS = {
            'severe': 2.0,
            'extreme': 2.5,
            'excruciating': 3.0,
            'unbearable': 3.0,
            'mild': 0.5,
            'slight': 0.5,
            'moderate': 1.0,
            'occasional': 0.7,
            'constant': 1.5,
            'persistent': 1.3,
            'sudden': 1.8,
            'gradual': 0.8,
            'worsening': 1.5,
            'improving': 0.6,
        }
    
    def parse(self, message):
        """Extract symptoms from user message with severity and modifiers"""
        message = message.lower()
        detected_symptoms = {}
        critical_flags = []
        
        # Check for mole-related symptoms (special handling)
        if 'mole' in message:
            detected_symptoms['has_mole'] = True
            
            # Check for specific mole changes
            if any(word in message for word in ['color', 'colour', 'dark', 'light', 'black', 'brown', 'red', 'white', 'blue']):
                detected_symptoms['mole changed color'] = True
                critical_flags.append('mole_color_change')
            
            if any(word in message for word in ['shape', 'border', 'irregular', 'asymmetrical', 'notched', 'scalloped']):
                detected_symptoms['mole changed shape'] = True
                critical_flags.append('mole_shape_change')
            
            if any(word in message for word in ['size', 'grew', 'bigger', 'larger', 'expanded', 'increase']):
                detected_symptoms['mole changed size'] = True
                critical_flags.append('mole_size_change')
            
            if any(word in message for word in ['bleed', 'blood', 'oozing', 'crust', 'scab']):
                detected_symptoms['mole bleeding'] = True
                critical_flags.append('mole_bleeding')
            
            if any(word in message for word in ['itch', 'itchy', 'scratch', 'irritated']):
                detected_symptoms['mole itching'] = True
                critical_flags.append('mole_itching')
        
        # Standard symptom detection
        for symptom, keywords in self.symptom_keywords.items():
            if symptom in detected_symptoms:  # Skip if already detected (mole)
                continue
            for keyword in keywords:
                if keyword in message:
                    detected_symptoms[symptom] = True
                    break
        
        # Extract duration if mentioned
        duration_patterns = [
            (r'(\d+)\s*days?', 'days'),
            (r'(\d+)\s*weeks?', 'weeks'),
            (r'(\d+)\s*months?', 'months'),
            (r'(\d+)\s*hours?', 'hours'),
            (r'(\d+)\s*years?', 'years')
        ]
        
        for pattern, unit in duration_patterns:
            match = re.search(pattern, message)
            if match:
                detected_symptoms['duration'] = int(match.group(1))
                detected_symptoms['duration_unit'] = unit
                break
        
        # Extract severity
        severity = 1.0
        for modifier, multiplier in self.SEVERITY_MODIFIERS.items():
            if modifier in message:
                severity = max(severity, multiplier)
        
        if severity != 1.0:
            detected_symptoms['severity'] = severity
        
        # 🆕 Add critical flag if any mole changes detected
        if critical_flags:
            detected_symptoms['critical'] = True
            detected_symptoms['critical_type'] = critical_flags
        
        return detected_symptoms
    
    def has_critical_symptoms(self, symptoms):
        """Check if symptoms contain any critical markers"""
        critical_markers = [
            'mole changed color', 'mole changed shape', 'mole changed size',
            'mole bleeding', 'mole itching', 'chest pain', 
            'shortness of breath', 'blood in stool', 'blood in urine',
            'sudden headache', 'vision changes'
        ]
        
        for marker in critical_markers:
            if symptoms.get(marker, False):
                return True
        return False
    
    def get_critical_warnings(self, symptoms):
        """Get warning messages for critical symptoms"""
        warnings = []
        
        if symptoms.get('mole changed color'):
            warnings.append("⚠️ Mole color change is a critical warning sign for skin cancer")
        if symptoms.get('mole changed shape'):
            warnings.append("⚠️ Mole shape change indicates potential melanoma risk")
        if symptoms.get('mole changed size'):
            warnings.append("⚠️ Growing mole requires immediate dermatologist evaluation")
        if symptoms.get('mole bleeding') or symptoms.get('mole itching'):
            warnings.append("⚠️ Bleeding or itchy mole is a serious concern")
        
        return warnings