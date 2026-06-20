class RiskEngine:
    def __init__(self):
        self.risk_rules = {
            'fever': {
                'score': 15,
                'condition': lambda duration: duration > 3 if duration else False,
                'weight': 1.5
            },
            'cough': {
                'score': 10,
                'condition': lambda duration: duration > 5 if duration else False,
                'weight': 1.3
            },
            'chest pain': {
                'score': 30,
                'condition': lambda duration: duration > 1 if duration else False,
                'weight': 2.0
            },
            'shortness of breath': {
                'score': 35,
                'condition': lambda duration: duration > 1 if duration else False,
                'weight': 2.0
            },
            'fatigue': {
                'score': 10,
                'condition': lambda duration: duration > 7 if duration else False,
                'weight': 1.2
            },
            'weight loss': {
                'score': 25,
                'condition': lambda duration: duration > 14 if duration else False,
                'weight': 1.8
            },
            'headache': {
                'score': 10,
                'condition': lambda duration: duration > 3 if duration else False,
                'weight': 1.2
            }
        }
        
        self.family_history_rules = {
            'diabetes': {'score': 25, 'condition': 'diabetes'},
            'hypertension': {'score': 20, 'condition': 'hypertension'},
            'heart disease': {'score': 30, 'condition': 'heart disease'},
            'cancer': {'score': 35, 'condition': 'cancer'},
            'asthma': {'score': 20, 'condition': 'asthma'},
            'arthritis': {'score': 15, 'condition': 'arthritis'}
        }
    
    def calculate_risk(self, symptoms, family_history, duration=0):
        """Calculate risk score based on symptoms and family history"""
        total_score = 0
        risk_factors = []
        
        # Calculate symptom-based risk
        for symptom, present in symptoms.items():
            if present and symptom in self.risk_rules:
                rule = self.risk_rules[symptom]
                score = rule['score']
                
                # Apply duration multiplier if available
                if duration > 0 and rule['condition'](duration):
                    score *= rule['weight']
                    risk_factors.append(f"{symptom} (persistent - {duration} days)")
                else:
                    risk_factors.append(symptom)
                
                total_score += score
        
        # Calculate family history risk
        for relation, conditions in family_history.items():
            for condition in conditions:
                if condition in self.family_history_rules:
                    rule = self.family_history_rules[condition]
                    total_score += rule['score']
                    risk_factors.append(f"{condition} in {relation}")
        
        # Determine risk level
        if total_score >= 70:
            level = 'High'
            recommendations = 'Please seek immediate medical attention. Contact your healthcare provider or visit the emergency room.'
        elif total_score >= 40:
            level = 'Moderate'
            recommendations = 'We recommend scheduling a doctor consultation within the next few days. Monitor your symptoms closely.'
        elif total_score >= 20:
            level = 'Low'
            recommendations = 'Continue monitoring your symptoms. Consider consulting a doctor if symptoms persist or worsen.'
        else:
            level = 'Minimal'
            recommendations = 'Your current risk appears minimal. Continue maintaining a healthy lifestyle and monitor any changes.'
        
        return {
            'score': total_score,
            'level': level,
            'factors': risk_factors,
            'recommendations': recommendations
        }