class RiskEngine:
    def __init__(self):
        # 🆕 CRITICAL: High-risk symptoms that auto-escalate
        self.CRITICAL_SYMPTOMS = {
            # SKIN/MOLE
            'mole changed color': {'score': 60, 'level': 'Critical', 'specialty': 'dermatology'},
            'mole changed shape': {'score': 55, 'level': 'Critical', 'specialty': 'dermatology'},
            'mole changed size': {'score': 55, 'level': 'Critical', 'specialty': 'dermatology'},
            'mole bleeding': {'score': 50, 'level': 'High', 'specialty': 'dermatology'},
            'mole itching': {'score': 40, 'level': 'High', 'specialty': 'dermatology'},
            
            # 🆕 GASTROINTESTINAL (CRITICAL)
            'blood in stool': {'score': 55, 'level': 'High', 'specialty': 'gastroenterology'},
            'bloody stool': {'score': 55, 'level': 'High', 'specialty': 'gastroenterology'},
            'rectal bleeding': {'score': 55, 'level': 'High', 'specialty': 'gastroenterology'},
            
            # 🆕 UROLOGICAL (CRITICAL)
            'blood in urine': {'score': 50, 'level': 'High', 'specialty': 'urology'},
            'bloody urine': {'score': 50, 'level': 'High', 'specialty': 'urology'},
            
            # CARDIOVASCULAR
            'chest pain': {'score': 50, 'level': 'Critical', 'specialty': 'cardiology'},
            'shortness of breath': {'score': 55, 'level': 'Critical', 'specialty': 'pulmonology'},
            
            # NEUROLOGICAL
            'sudden headache': {'score': 50, 'level': 'Critical', 'specialty': 'neurology'},
            'vision changes': {'score': 40, 'level': 'High', 'specialty': 'ophthalmology'},
            
            # OTHER
            'vomiting blood': {'score': 55, 'level': 'Critical', 'specialty': 'gastroenterology'},
        }
        
        # Regular symptom scoring
        self.REGULAR_SYMPTOMS = {
            'fever': {'score': 15, 'duration_threshold': 3, 'weight': 1.5},
            'cough': {'score': 10, 'duration_threshold': 5, 'weight': 1.3},
            'fatigue': {'score': 10, 'duration_threshold': 7, 'weight': 1.2},
            'weight loss': {'score': 25, 'duration_threshold': 14, 'weight': 1.8},
            'headache': {'score': 10, 'duration_threshold': 3, 'weight': 1.2},
            'nausea': {'score': 10, 'duration_threshold': 3, 'weight': 1.2},
            'dizziness': {'score': 15, 'duration_threshold': 2, 'weight': 1.3},
            'sore throat': {'score': 8, 'duration_threshold': 5, 'weight': 1.1},
            'runny nose': {'score': 5, 'duration_threshold': 7, 'weight': 1.0},
            'body aches': {'score': 12, 'duration_threshold': 4, 'weight': 1.2},
            'diarrhea': {'score': 12, 'duration_threshold': 3, 'weight': 1.3},
            'vomiting': {'score': 15, 'duration_threshold': 2, 'weight': 1.4},
            'skin rash': {'score': 15, 'duration_threshold': 5, 'weight': 1.2},
            'skin lesion': {'score': 20, 'duration_threshold': 7, 'weight': 1.5},
            'bruising': {'score': 10, 'duration_threshold': 5, 'weight': 1.1},
            'abdominal pain': {'score': 20, 'duration_threshold': 3, 'weight': 1.4},
        }
        
        # Symptom interactions
        self.INTERACTIONS = {
            ('fatigue', 'blood in stool'): 1.8,
            ('fatigue', 'mole changed color'): 1.8,
            ('fatigue', 'weight loss'): 1.7,
            ('fever', 'cough'): 1.3,
            ('fever', 'body aches'): 1.3,
            ('chest pain', 'shortness of breath'): 2.0,
            ('nausea', 'dizziness'): 1.4,
            ('vomiting', 'diarrhea'): 1.5,
            ('headache', 'vision changes'): 1.8,
            ('blood in stool', 'abdominal pain'): 1.7,
            ('blood in stool', 'weight loss'): 1.9,
        }
        
        # Family history risk rules
        self.family_history_rules = {
            'diabetes': {'score': 25, 'condition': 'diabetes'},
            'hypertension': {'score': 20, 'condition': 'hypertension'},
            'heart disease': {'score': 30, 'condition': 'heart disease'},
            'cancer': {'score': 35, 'condition': 'cancer'},
            'colon cancer': {'score': 45, 'condition': 'colon cancer'},
            'colorectal cancer': {'score': 45, 'condition': 'colorectal cancer'},
            'skin cancer': {'score': 40, 'condition': 'skin cancer'},
            'melanoma': {'score': 45, 'condition': 'melanoma'},
            'asthma': {'score': 20, 'condition': 'asthma'},
            'arthritis': {'score': 15, 'condition': 'arthritis'},
            'thyroid': {'score': 20, 'condition': 'thyroid'},
            'anemia': {'score': 15, 'condition': 'anemia'},
            'crohn': {'score': 35, 'condition': 'crohn disease'},
            'ulcerative colitis': {'score': 35, 'condition': 'ulcerative colitis'},
            'ibd': {'score': 35, 'condition': 'inflammatory bowel disease'},
        }
    
    def calculate_risk(self, symptoms, family_history=None, duration=0, user_message=""):
        """
        Calculate risk score based on symptoms and family history
        
        Returns:
        {
            'score': int (0-100),
            'level': str ('Minimal', 'Low', 'Moderate', 'High', 'Critical'),
            'factors': list,
            'recommendations': str,
            'specialty': str or None,
            'critical_findings': list,
            'urgent': bool
        }
        """
        total_score = 0
        risk_factors = []
        critical_findings = []
        specialty = None
        urgent = False
        
        # 🆕 STEP 1: Check for critical symptoms first (auto-escalate)
        has_critical = False
        
        # Get all symptom keys for matching
        symptom_keys = list(symptoms.keys())
        
        # Check each symptom against critical symptoms
        for symptom_key in symptom_keys:
            for critical_key, data in self.CRITICAL_SYMPTOMS.items():
                # Check if symptom matches critical symptom (partial match)
                if critical_key in symptom_key.lower() or symptom_key.lower() in critical_key:
                    has_critical = True
                    critical_findings.append(critical_key)
                    total_score += data['score']
                    risk_factors.append(f"🚨 {critical_key} (Critical - requires immediate attention)")
                    
                    # Set specialty if not already set
                    if not specialty:
                        specialty = data['specialty']
                    urgent = True
                    break
        
        # 🆕 STEP 2: Check for "blood" related symptoms explicitly
        blood_symptoms = ['blood in stool', 'bloody stool', 'rectal bleeding', 'blood in urine', 'bloody urine', 'vomiting blood']
        for symptom in symptom_keys:
            if 'blood' in symptom.lower():
                has_critical = True
                if symptom not in critical_findings:
                    critical_findings.append(symptom)
                    total_score += 50  # High score for any blood-related symptom
                    risk_factors.append(f"🚨 {symptom} (Critical - requires immediate attention)")
                    if not specialty:
                        if 'stool' in symptom.lower():
                            specialty = 'gastroenterology'
                        elif 'urine' in symptom.lower():
                            specialty = 'urology'
                    urgent = True
        
        # 🆕 STEP 3: Regular symptom scoring (if no critical symptoms)
        if not has_critical:
            for symptom, present in symptoms.items():
                if present and symptom in self.REGULAR_SYMPTOMS:
                    rule = self.REGULAR_SYMPTOMS[symptom]
                    score = rule['score']
                    
                    # Apply duration multiplier if available
                    if duration > 0 and rule.get('duration_threshold', 999):
                        if duration >= rule['duration_threshold']:
                            score *= rule['weight']
                            risk_factors.append(f"{symptom} (persistent - {duration} days)")
                        else:
                            risk_factors.append(symptom)
                    else:
                        risk_factors.append(symptom)
                    
                    total_score += score
        
        # STEP 4: Apply interaction multipliers
        for (sym1, sym2), multiplier in self.INTERACTIONS.items():
            if any(sym1 in s.lower() for s in symptom_keys) and any(sym2 in s.lower() for s in symptom_keys):
                total_score = int(total_score * multiplier)
                risk_factors.append(f"⚠️ Combined risk: {sym1} + {sym2}")
        
        # STEP 5: Family history risk
        if family_history:
            family_score = 0
            for relation, conditions in family_history.items():
                for condition in conditions:
                    condition_lower = condition.lower()
                    for rule_key, rule in self.family_history_rules.items():
                        if rule_key in condition_lower:
                            family_score += rule['score']
                            risk_factors.append(f"{rule_key} in {relation}")
                            break
            
            # Cap family history contribution at 30
            family_score = min(family_score, 30)
            total_score += family_score
        
        # STEP 6: Apply severity multiplier
        if symptoms.get('severity', 1.0) > 1.0:
            total_score = int(total_score * symptoms['severity'])
            risk_factors.append(f"Severity level: {symptoms['severity']}x")
        
        # STEP 7: Cap score at 100
        total_score = min(total_score, 100)
        
        # 🆕 STEP 8: Override: If any critical symptom, score is at least 70
        if critical_findings and total_score < 70:
            total_score = 70
        
        # 🆕 STEP 9: If "blood" is mentioned but not detected, force score
        if user_message and 'blood' in user_message.lower():
            if not has_critical:
                has_critical = True
                critical_findings.append('blood related symptom')
                total_score = max(total_score, 70)
                risk_factors.append("🚨 Blood-related symptom detected")
                urgent = True
                if not specialty:
                    if 'stool' in user_message.lower() or 'bowel' in user_message.lower():
                        specialty = 'gastroenterology'
        
        # STEP 10: Determine risk level
        if critical_findings or total_score >= 85:
            level = 'Critical'
            recommendations = self._get_critical_recommendations(critical_findings, specialty)
        elif total_score >= 70:
            level = 'High'
            recommendations = self._get_high_risk_recommendations(critical_findings, specialty)
        elif total_score >= 45:
            level = 'Moderate'
            recommendations = 'We recommend scheduling a doctor consultation within the next few days. Monitor your symptoms closely.'
        elif total_score >= 25:
            level = 'Low'
            recommendations = 'Continue monitoring your symptoms. Consider consulting a doctor if symptoms persist or worsen.'
        else:
            level = 'Minimal'
            recommendations = 'Your current risk appears minimal. Continue maintaining a healthy lifestyle and monitor any changes.'
        
        # 🆕 STEP 11: Generate specialty recommendation
        if not specialty and critical_findings:
            if any('mole' in str(f).lower() for f in critical_findings):
                specialty = 'dermatology'
            elif any('blood' in str(f).lower() for f in critical_findings):
                if 'stool' in str(f).lower() or 'bowel' in str(f).lower():
                    specialty = 'gastroenterology'
                elif 'urine' in str(f).lower():
                    specialty = 'urology'
                else:
                    specialty = 'internal medicine'
            elif 'chest' in str(critical_findings) or 'breath' in str(critical_findings):
                specialty = 'cardiology/pulmonology'
            elif 'headache' in str(critical_findings) or 'vision' in str(critical_findings):
                specialty = 'neurology'
        
        return {
            'score': total_score,
            'level': level,
            'factors': risk_factors[:10],  # Limit to top 10
            'recommendations': recommendations,
            'specialty': specialty,
            'critical_findings': critical_findings,
            'urgent': urgent or total_score >= 70
        }
    
    def _get_critical_recommendations(self, critical_findings, specialty):
        """Generate recommendations for critical findings"""
        recommendations = []
        
        recommendations.append("🚨 **URGENT: Immediate medical attention required**")
        
        for finding in critical_findings:
            if 'blood' in finding.lower() and 'stool' in finding.lower():
                recommendations.append("🩸 **Blood in stool requires immediate evaluation**")
                recommendations.append("🏥 Visit your doctor or emergency room TODAY")
                recommendations.append("📋 Note the color of the blood (bright red vs dark/tarry)")
                recommendations.append("📋 Track how much blood and how often")
                recommendations.append("🚫 Do NOT take aspirin or blood thinners unless prescribed")
            elif 'blood' in finding.lower() and 'urine' in finding.lower():
                recommendations.append("🩸 **Blood in urine requires medical evaluation**")
                recommendations.append("🏥 See a urologist or visit urgent care")
                recommendations.append("📋 Note if you have pain with urination")
            elif 'mole' in finding.lower():
                recommendations.append("📅 Schedule an appointment with a **dermatologist** within 1-2 weeks")
                recommendations.append("📸 Take clear photos of the mole with a ruler for scale")
                recommendations.append("❌ Do NOT try to remove or treat the mole yourself")
                recommendations.append("📋 Track the ABCDEs: Asymmetry, Border, Color, Diameter, Evolution")
            elif 'chest' in finding.lower() or 'breath' in finding.lower():
                recommendations.append("🚑 If chest pain is severe or radiating, call emergency services")
                recommendations.append("💊 Do not drive yourself to the hospital")
        
        if specialty:
            recommendations.append(f"👨‍⚕️ **Recommended specialist: {specialty.upper()}**")
        
        recommendations.append("⚠️ This assessment is not a medical diagnosis. Always consult a qualified healthcare professional.")
        
        return "\n".join(recommendations)
    
    def _get_high_risk_recommendations(self, critical_findings, specialty):
        """Generate recommendations for high risk findings"""
        recommendations = []
        
        recommendations.append("⚠️ **HIGH RISK: Medical attention recommended within 24-48 hours**")
        
        for finding in critical_findings:
            if 'blood' in finding.lower():
                recommendations.append("🩸 Schedule a doctor's appointment as soon as possible")
                recommendations.append("📋 Keep a diary of your symptoms")
        
        if specialty:
            recommendations.append(f"👨‍⚕️ **Recommended specialist: {specialty.upper()}**")
        
        recommendations.append("⚠️ This assessment is not a medical diagnosis. Always consult a qualified healthcare professional.")
        
        return "\n".join(recommendations)