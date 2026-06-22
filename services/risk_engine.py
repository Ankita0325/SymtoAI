# services/risk_engine.py
import json
from typing import Dict, Any, List, Optional
from datetime import datetime

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
            
            # 🆕 NEUROLOGICAL - BACK PAIN (CRITICAL ADDITION)
            'cauda equina': {'score': 80, 'level': 'Critical', 'specialty': 'neurosurgery'},
            'numbness spreading': {'score': 65, 'level': 'Critical', 'specialty': 'neurology'},
            'leg weakness': {'score': 60, 'level': 'High', 'specialty': 'neurology'},
            'loss of bladder control': {'score': 80, 'level': 'Critical', 'specialty': 'neurosurgery'},
            'loss of bowel control': {'score': 80, 'level': 'Critical', 'specialty': 'neurosurgery'},
            'saddle anesthesia': {'score': 75, 'level': 'Critical', 'specialty': 'neurosurgery'},
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
            
            # 🆕 BACK PAIN & NEUROLOGICAL SYMPTOMS (CRITICAL ADDITION)
            'back pain': {'score': 25, 'duration_threshold': 3, 'weight': 1.5, 'is_neurological': True},
            'lower back pain': {'score': 30, 'duration_threshold': 3, 'weight': 1.6, 'is_neurological': True},
            'radiating pain': {'score': 30, 'duration_threshold': 2, 'weight': 1.7, 'is_neurological': True},
            'radiating leg pain': {'score': 35, 'duration_threshold': 2, 'weight': 1.8, 'is_neurological': True},
            'sciatica': {'score': 40, 'duration_threshold': 2, 'weight': 1.8, 'is_neurological': True},
            'numbness': {'score': 35, 'duration_threshold': 2, 'weight': 1.7, 'is_neurological': True},
            'tingling': {'score': 20, 'duration_threshold': 3, 'weight': 1.4, 'is_neurological': True},
            'weakness': {'score': 40, 'duration_threshold': 2, 'weight': 1.8, 'is_neurological': True},
            'leg weakness': {'score': 45, 'duration_threshold': 2, 'weight': 1.9, 'is_neurological': True},
            'spreading numbness': {'score': 55, 'duration_threshold': 1, 'weight': 2.0, 'is_neurological': True},
            'loss of bladder control': {'score': 80, 'duration_threshold': 0, 'weight': 2.5, 'is_neurological': True},
            'loss of bowel control': {'score': 80, 'duration_threshold': 0, 'weight': 2.5, 'is_neurological': True},
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
            
            # 🆕 NEUROLOGICAL INTERACTIONS
            ('back pain', 'radiating leg pain'): 1.8,
            ('back pain', 'numbness'): 2.0,
            ('back pain', 'weakness'): 2.2,
            ('numbness', 'weakness'): 2.0,
            ('radiating pain', 'numbness'): 1.9,
            ('back pain', 'sciatica'): 2.0,
            ('spreading numbness', 'weakness'): 2.5,
            ('back pain', 'loss of bladder control'): 3.0,
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
            'osteoporosis': {'score': 20, 'condition': 'osteoporosis'},
            'spinal stenosis': {'score': 30, 'condition': 'spinal stenosis'},
            'herniated disc': {'score': 25, 'condition': 'herniated disc'},
        }
    
    def calculate_risk(self, symptoms: Dict[str, Any], family_history: Optional[Dict] = None, 
                       duration: int = 0, user_message: str = "", patient_id: Optional[str] = None) -> Dict[str, Any]:
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
            'urgent': bool,
            'patient_id': str or None
        }
        """
        total_score = 0
        risk_factors = []
        critical_findings = []
        specialty = None
        urgent = False
        
        # Get all symptom keys
        symptom_keys = list(symptoms.keys())
        
        # 🆕 STEP 1: Check for critical symptoms first (auto-escalate)
        has_critical = False
        
        # Check for critical neurological symptoms
        neurological_critical = ['numbness spreading', 'leg weakness', 'loss of bladder control', 
                                 'loss of bowel control', 'saddle anesthesia', 'cauda equina']
        
        for symptom_key in symptom_keys:
            symptom_lower = symptom_key.lower()
            
            # Check critical symptoms
            for critical_key, data in self.CRITICAL_SYMPTOMS.items():
                if critical_key in symptom_lower or symptom_lower in critical_key:
                    has_critical = True
                    if critical_key not in critical_findings:
                        critical_findings.append(critical_key)
                    total_score += data['score']
                    risk_factors.append(f"🚨 {critical_key} (Critical - requires immediate attention)")
                    
                    if not specialty:
                        specialty = data['specialty']
                    urgent = True
                    break
        
        # 🆕 STEP 2: Check for neurological red flags in symptom keys
        # Check for numbness + weakness combination
        has_numbness = any('numb' in s.lower() for s in symptom_keys)
        has_weakness = any('weak' in s.lower() for s in symptom_keys)
        has_spreading = any('spread' in s.lower() for s in symptom_keys)
        has_back_pain = any('back' in s.lower() for s in symptom_keys)
        has_radiating = any('radiat' in s.lower() for s in symptom_keys)
        has_leg_pain = any('leg' in s.lower() for s in symptom_keys)
        
        # Neurological red flag: numbness + weakness
        if has_numbness and has_weakness:
            total_score += 40
            risk_factors.append("🚨 Numbness + weakness = neurological red flag")
            urgent = True
            if not specialty:
                specialty = 'neurology'
            has_critical = True
        
        # Neurological red flag: spreading numbness
        if has_spreading and has_numbness:
            total_score += 30
            risk_factors.append("🚨 Spreading numbness - urgent neurological evaluation required")
            urgent = True
            if not specialty:
                specialty = 'neurology'
            has_critical = True
        
        # Sciatica/radicular pain
        if has_back_pain and has_radiating and has_leg_pain:
            total_score += 25
            risk_factors.append("⚠️ Radicular pain with leg involvement - possible nerve compression")
            if not specialty:
                specialty = 'orthopedics/neurology'
        
        # 🆕 STEP 3: Check for "blood" related symptoms explicitly
        blood_symptoms = ['blood in stool', 'bloody stool', 'rectal bleeding', 'blood in urine', 'bloody urine', 'vomiting blood']
        for symptom in symptom_keys:
            if 'blood' in symptom.lower():
                has_critical = True
                if symptom not in critical_findings:
                    critical_findings.append(symptom)
                total_score += 50
                risk_factors.append(f"🚨 {symptom} (Critical - requires immediate attention)")
                if not specialty:
                    if 'stool' in symptom.lower():
                        specialty = 'gastroenterology'
                    elif 'urine' in symptom.lower():
                        specialty = 'urology'
                urgent = True
        
        # 🆕 STEP 4: Regular symptom scoring
        for symptom_key, symptom_value in symptoms.items():
            if not symptom_value:
                continue
                
            symptom_lower = symptom_key.lower()
            
            # Check if symptom matches any regular symptom
            for regular_key, rule in self.REGULAR_SYMPTOMS.items():
                if regular_key in symptom_lower or symptom_lower in regular_key:
                    score = rule['score']
                    
                    # Apply duration multiplier if available
                    if duration > 0 and rule.get('duration_threshold', 999):
                        if duration >= rule['duration_threshold']:
                            score *= rule['weight']
                            risk_factors.append(f"{regular_key} (persistent - {duration} days)")
                        else:
                            risk_factors.append(regular_key)
                    else:
                        risk_factors.append(regular_key)
                    
                    total_score += int(score)
                    break
        
        # STEP 5: Apply interaction multipliers
        for (sym1, sym2), multiplier in self.INTERACTIONS.items():
            if any(sym1 in s.lower() for s in symptom_keys) and any(sym2 in s.lower() for s in symptom_keys):
                total_score = int(total_score * multiplier)
                risk_factors.append(f"⚠️ Combined risk: {sym1} + {sym2}")
        
        # STEP 6: Family history risk
        if family_history:
            family_score = 0
            for relation, conditions in family_history.items():
                if isinstance(conditions, list):
                    for condition in conditions:
                        condition_lower = condition.lower()
                        for rule_key, rule in self.family_history_rules.items():
                            if rule_key in condition_lower:
                                family_score += rule['score']
                                risk_factors.append(f"{rule_key} in {relation}")
                                break
            
            family_score = min(family_score, 30)
            total_score += family_score
        
        # STEP 7: Apply severity multiplier
        if symptoms.get('severity', 1.0) > 1.0:
            total_score = int(total_score * symptoms['severity'])
            risk_factors.append(f"Severity level: {symptoms['severity']}x")
        
        # STEP 8: Cap score at 100
        total_score = min(total_score, 100)
        
        # 🆕 STEP 9: Override: If any critical symptom, score is at least 70
        if critical_findings and total_score < 70:
            total_score = 70
        
        # 🆕 STEP 10: If back pain with numbness, force high risk
        if has_back_pain and has_numbness and has_weakness:
            total_score = max(total_score, 75)
            risk_factors.append("🚨 Back pain + numbness + weakness = HIGH RISK")
            urgent = True
            if not specialty:
                specialty = 'orthopedics/neurology'
        
        # 🆕 STEP 11: If "blood" is mentioned but not detected
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
                    elif 'urine' in user_message.lower():
                        specialty = 'urology'
        
        # STEP 12: Determine risk level
        if critical_findings or total_score >= 85:
            level = 'Critical'
            recommendations = self._get_critical_recommendations(critical_findings, specialty)
        elif total_score >= 70:
            level = 'High'
            recommendations = self._get_high_risk_recommendations(critical_findings, specialty)
        elif total_score >= 45:
            level = 'Moderate'
            recommendations = '📋 We recommend scheduling a doctor consultation within the next few days. Monitor your symptoms closely.'
        elif total_score >= 25:
            level = 'Low'
            recommendations = '✅ Continue monitoring your symptoms. Consider consulting a doctor if symptoms persist or worsen.'
        else:
            level = 'Minimal'
            recommendations = '✅ Your current risk appears minimal. Continue maintaining a healthy lifestyle and monitor any changes.'
        
        # STEP 13: Generate specialty recommendation
        if not specialty:
            if has_back_pain and (has_numbness or has_weakness):
                specialty = 'orthopedics/neurology'
            elif has_back_pain:
                specialty = 'orthopedics'
            elif has_numbness or has_weakness:
                specialty = 'neurology'
            elif critical_findings:
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
            'factors': risk_factors[:10],
            'recommendations': recommendations,
            'specialty': specialty,
            'critical_findings': critical_findings,
            'urgent': urgent or total_score >= 70,
            'patient_id': patient_id,
            'timestamp': datetime.now().isoformat()
        }
    
    def _get_critical_recommendations(self, critical_findings: List[str], specialty: Optional[str]) -> str:
        """Generate recommendations for critical findings"""
        recommendations = []
        
        recommendations.append("🚨 **URGENT: Immediate medical attention required**")
        
        for finding in critical_findings:
            finding_lower = str(finding).lower()
            
            if 'blood' in finding_lower and 'stool' in finding_lower:
                recommendations.append("🩸 **Blood in stool requires immediate evaluation**")
                recommendations.append("🏥 Visit your doctor or emergency room TODAY")
                recommendations.append("📋 Note the color of the blood (bright red vs dark/tarry)")
                recommendations.append("📋 Track how much blood and how often")
                recommendations.append("🚫 Do NOT take aspirin or blood thinners unless prescribed")
            elif 'blood' in finding_lower and 'urine' in finding_lower:
                recommendations.append("🩸 **Blood in urine requires medical evaluation**")
                recommendations.append("🏥 See a urologist or visit urgent care")
                recommendations.append("📋 Note if you have pain with urination")
            elif 'mole' in finding_lower:
                recommendations.append("📅 Schedule an appointment with a **dermatologist** within 1-2 weeks")
                recommendations.append("📸 Take clear photos of the mole with a ruler for scale")
                recommendations.append("❌ Do NOT try to remove or treat the mole yourself")
                recommendations.append("📋 Track the ABCDEs: Asymmetry, Border, Color, Diameter, Evolution")
            elif 'chest' in finding_lower or 'breath' in finding_lower:
                recommendations.append("🚑 If chest pain is severe or radiating, call emergency services")
                recommendations.append("💊 Do not drive yourself to the hospital")
            elif 'loss of bladder control' in finding_lower or 'loss of bowel control' in finding_lower:
                recommendations.append("🚨 **EMERGENCY: Loss of bladder/bowel control requires IMMEDIATE emergency care**")
                recommendations.append("🚑 Call emergency services (911) or go to the ER immediately")
                recommendations.append("⚠️ This could be cauda equina syndrome - a surgical emergency")
            elif 'numbness spreading' in finding_lower or 'leg weakness' in finding_lower:
                recommendations.append("⚠️ **Progressive neurological symptoms require urgent evaluation**")
                recommendations.append("🏥 Go to the Emergency Room or see a neurologist TODAY")
                recommendations.append("📋 Monitor for worsening symptoms")
            elif 'back pain' in finding_lower and 'numbness' in finding_lower:
                recommendations.append("⚠️ **Back pain with neurological symptoms requires urgent evaluation**")
                recommendations.append("🏥 See an orthopedist or neurologist within 24-48 hours")
                recommendations.append("🚑 Go to ER if symptoms worsen or you lose bladder/bowel control")
        
        if specialty:
            recommendations.append(f"👨‍⚕️ **Recommended specialist: {specialty.upper()}**")
        
        recommendations.append("⚠️ This assessment is not a medical diagnosis. Always consult a qualified healthcare professional.")
        
        return "\n".join(recommendations)
    
    def _get_high_risk_recommendations(self, critical_findings: List[str], specialty: Optional[str]) -> str:
        """Generate recommendations for high risk findings"""
        recommendations = []
        
        recommendations.append("⚠️ **HIGH RISK: Medical attention recommended within 24-48 hours**")
        
        for finding in critical_findings:
            finding_lower = str(finding).lower()
            if 'blood' in finding_lower:
                recommendations.append("🩸 Schedule a doctor's appointment as soon as possible")
                recommendations.append("📋 Keep a diary of your symptoms")
            elif 'mole' in finding_lower:
                recommendations.append("📅 See a dermatologist within 1-2 weeks")
            elif 'back pain' in finding_lower and 'numbness' in finding_lower:
                recommendations.append("🦴 See an orthopedist or neurologist within 24-48 hours")
                recommendations.append("🛑 Avoid heavy lifting and bending")
                recommendations.append("🧊 Apply cold packs to lower back for 15-20 minutes")
                recommendations.append("💊 Take OTC pain relievers if safe (consult pharmacist)")
            elif 'numbness' in finding_lower or 'weakness' in finding_lower:
                recommendations.append("🧠 Neurological symptoms require prompt evaluation")
                recommendations.append("📋 Track any changes in symptoms")
        
        if specialty:
            recommendations.append(f"👨‍⚕️ **Recommended specialist: {specialty.upper()}**")
        
        recommendations.append("⚠️ This assessment is not a medical diagnosis. Always consult a qualified healthcare professional.")
        
        return "\n".join(recommendations)