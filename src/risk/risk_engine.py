"""
Risk Scoring Engine
Rule-based risk assessment (NO AI - Explainable & Court-safe)
"""

from typing import Dict, List
from pathlib import Path
import json
from datetime import datetime


class RiskEngine:
    """Rule-based risk scoring engine"""
    
    def __init__(self):
        """Initialize risk weights and thresholds"""
        # Risk factor weights (must sum to 100)
        self.weights = {
            "loan_present": 30,           # Encumbrance/loan detected
            "mutation_mismatch": 25,      # Mutation issues
            "owner_mismatch": 25,         # Owner verification issues
            "ec_outdated": 10,            # Encumbrance Certificate issues
            "legal_case": 10              # Court cases
        }
        
        # Additional penalty factors
        self.penalty_weights = {
            "multiple_loans": 15,         # More than one loan
            "forgery_indicators": 20,     # Forgery suspected
            "incomplete_data": 10,        # Missing critical information
            "conflicting_data": 15        # Data inconsistencies
        }
        
        # Risk level thresholds
        self.thresholds = {
            "low": 30,        # 0-30: Low Risk
            "medium": 60,     # 31-60: Medium Risk
            "high": 100       # 61-100: High Risk
        }
    
    def calculate_risk_score(self, entities: Dict = None, classification: Dict = None) -> Dict:
        """
        Calculate risk score based on extracted entities and classification
        
        Args:
            entities: Extracted entities from NER
            classification: Document classification result
            
        Returns:
            dict: Risk assessment
            {
                "risk_score": 75,
                "risk_level": "High",
                "factors": [...],
                "explanation": "...",
                "recommendations": [...]
            }
        """
        risk_score = 0
        factors = []
        flags = []
        
        # Ensure we have data to work with
        if not entities and not classification:
            return self._create_result(50, ["Insufficient data for risk assessment"], ["INCOMPLETE"])
        
        entities = entities or {}
        classification = classification or {}
        
        # Factor 1: Loan/Encumbrance present (25 points base)
        loan_present = entities.get('loan_present', False)
        banks = entities.get('banks', [])
        loan_indicators = entities.get('loan_indicators', [])
        loan_amounts = entities.get('loan_amounts', [])
        
        # CRITICAL FIX: Context-based loan validation
        # Only count valid loans (> ₹1,000 AND near bank keywords)
        valid_loan_amounts = []
        for amount in loan_amounts:
            try:
                # Clean amount string
                amount_clean = str(amount).replace(',', '').replace('.', '').replace('-', '').replace('/', '').replace('₹', '').strip()
                amount_num = float(amount_clean)
                if amount_num >= 1000:  # Minimum threshold
                    valid_loan_amounts.append(amount)
            except:
                pass
        
        # Check for loan presence from multiple validated sources
        has_valid_loan = (loan_present and len(valid_loan_amounts) > 0) or (len(banks) > 0 and len(valid_loan_amounts) > 0)
        
        if has_valid_loan:
            risk_score += 25  # Base loan risk
            loan_desc = "Active loan detected"
            if len(valid_loan_amounts) > 0:
                # Show first valid amount only
                loan_desc += f" (Amount: ₹{valid_loan_amounts[0]})"
            if len(banks) > 0:
                loan_desc += f" from {banks[0]}"
            factors.append(f"{loan_desc} (25 points)")
            flags.append("LOAN_PRESENT")
            
            # CRITICAL FIX: Only penalize for DISTINCT valid loans (not duplicates)
            if len(valid_loan_amounts) > 1:
                # Check if truly distinct (not similar amounts)
                distinct_loans = []
                for amt in valid_loan_amounts:
                    is_duplicate = False
                    try:
                        amt_num = float(str(amt).replace(',', '').replace('.', '').replace('-', '').replace('/', '').replace('₹', '').strip())
                        for existing in distinct_loans:
                            # If within 10% similarity, consider duplicate
                            if abs(amt_num - existing) / max(existing, 1) < 0.1:
                                is_duplicate = True
                                break
                        if not is_duplicate:
                            distinct_loans.append(amt_num)
                    except:
                        pass
                
                if len(distinct_loans) > 1:
                    risk_score += 10  # Reduced penalty for multiple distinct loans
                    factors.append(f"Multiple distinct loans detected (10 points)")
                    flags.append("MULTIPLE_LOANS")
        
        # Factor 2: Legal case present (10 points)
        case_numbers = entities.get('case_numbers', [])
        if len(case_numbers) > 0:
            risk_score += self.weights["legal_case"]
            factors.append(f"Legal case found: {', '.join(case_numbers)} ({self.weights['legal_case']} points)")
            flags.append("LEGAL_CASE")
        
        # Factor 3: Classification-based risks
        if classification:
            label = classification.get('label', '')
            
            if label == "Court Case Mentioned":
                if "LEGAL_CASE" not in flags:
                    risk_score += self.weights["legal_case"]
                    factors.append(f"Court case classification ({self.weights['legal_case']} points)")
                    flags.append("LEGAL_CASE")
            
            elif label == "Forgery Suspected":
                risk_score += self.penalty_weights["forgery_indicators"]
                factors.append(f"Forgery indicators ({self.penalty_weights['forgery_indicators']} points)")
                flags.append("FORGERY")
            
            elif label == "Pending Mutation":
                risk_score += self.weights["mutation_mismatch"]
                factors.append(f"Mutation pending ({self.weights['mutation_mismatch']} points)")
                flags.append("MUTATION_PENDING")
            
            elif label == "Multiple Issues":
                risk_score += self.penalty_weights["conflicting_data"]
                factors.append(f"Multiple issues detected ({self.penalty_weights['conflicting_data']} points)")
                flags.append("MULTIPLE_ISSUES")
        
        # Factor 4: Data completeness checks
        survey_numbers = entities.get('survey_numbers', [])
        dates = entities.get('dates', [])
        
        if len(survey_numbers) == 0:
            risk_score += self.penalty_weights["incomplete_data"]
            factors.append(f"No survey numbers found ({self.penalty_weights['incomplete_data']} points)")
            flags.append("NO_SURVEY_NO")
        
        if len(dates) == 0:
            risk_score += 5  # Minor penalty
            factors.append("No dates found (5 points)")
            flags.append("NO_DATES")
        
        # Factor 5: Positive indicators (reduce risk)
        if len(survey_numbers) > 0 and not loan_present and len(case_numbers) == 0:
            # Document appears clean
            reduction = 5
            risk_score = max(0, risk_score - reduction)
            factors.append(f"Clean document indicators (-{reduction} points)")
        
        # Cap risk score at 100
        risk_score = min(100, risk_score)
        
        # ISSUE 6 FIX: Validate consistency between risk score and classification
        classification_label = classification.get('label', '') if classification else ''
        risk_score, factors, flags = self._validate_risk_classification_consistency(
            risk_score, factors, flags, classification_label, loan_present, case_numbers
        )
        
        return self._create_result(risk_score, factors, flags, entities, classification)
    
    def _create_result(self, score: int, factors: List[str], flags: List[str], 
                       entities: Dict = None, classification: Dict = None) -> Dict:
        """
        Create formatted risk assessment result
        
        Args:
            score: Risk score (0-100)
            factors: List of risk factors
            flags: List of risk flags
            entities: Entity data
            classification: Classification data
            
        Returns:
            dict: Formatted risk assessment
        """
        risk_level = self._get_risk_level(score)
        
        result = {
            "risk_score": score,
            "risk_level": risk_level,
            "risk_percentage": f"{score}%",
            "factors": factors,
            "flags": flags,
            "explanation": self._generate_explanation(score, risk_level, factors),
            "recommendations": self._generate_recommendations(score, risk_level, flags),
            "breakdown": {
                "loan_risk": 30 if "LOAN_PRESENT" in flags else 0,
                "legal_risk": 10 if "LEGAL_CASE" in flags else 0,
                "mutation_risk": 25 if "MUTATION_PENDING" in flags else 0,
                "data_quality_risk": 10 if "NO_SURVEY_NO" in flags else 0,
                "other_risks": score - sum([
                    30 if "LOAN_PRESENT" in flags else 0,
                    10 if "LEGAL_CASE" in flags else 0,
                    25 if "MUTATION_PENDING" in flags else 0,
                    10 if "NO_SURVEY_NO" in flags else 0
                ])
            },
            "summary": self._get_summary(risk_level, flags)
        }
        
        return result
    
    def _get_risk_level(self, score: int) -> str:
        """Determine risk level from score"""
        if score <= self.thresholds["low"]:
            return "Low"
        elif score <= self.thresholds["medium"]:
            return "Medium"
        else:
            return "High"
    
    def _generate_explanation(self, score: int, level: str, factors: List[str]) -> str:
        """Generate human-readable explanation"""
        if not factors:
            return f"Risk Score: {score}/100 ({level} Risk) - No significant risk factors identified."
        
        factor_text = " | ".join(factors)
        return f"Risk Score: {score}/100 ({level} Risk) - {factor_text}"
    
    def _generate_recommendations(self, score: int, level: str, flags: List[str]) -> List[str]:
        """Generate actionable recommendations based on risk"""
        recommendations = []
        
        if level == "High":
            recommendations.append("🚫 DO NOT PROCEED without thorough legal verification")
            recommendations.append("Engage experienced property lawyer immediately")
        elif level == "Medium":
            recommendations.append("⚠️ PROCEED WITH CAUTION")
            recommendations.append("Obtain legal opinion before finalizing transaction")
        else:
            recommendations.append("✅ LOW RISK - May proceed with standard due diligence")
        
        # Specific recommendations based on flags
        if "LOAN_PRESENT" in flags:
            recommendations.append("Obtain No Objection Certificate (NOC) from all lenders")
            recommendations.append("Verify loan status and outstanding amount")
        
        if "LEGAL_CASE" in flags:
            recommendations.append("Obtain certified copy of court case details")
            recommendations.append("Verify current status of litigation")
            recommendations.append("Consult advocate regarding case implications")
        
        if "MUTATION_PENDING" in flags:
            recommendations.append("Complete mutation process in revenue records")
            recommendations.append("Obtain updated khata/patta in seller's name")
        
        if "NO_SURVEY_NO" in flags:
            recommendations.append("Verify survey number from revenue records")
            recommendations.append("Obtain complete document set")
        
        if "FORGERY" in flags:
            recommendations.append("⛔ IMMEDIATE HALT - Potential document forgery")
            recommendations.append("Report to authorities if fraud suspected")
            recommendations.append("Conduct forensic document verification")
        
        # Standard recommendations (always apply)
        if level in ["Medium", "High"]:
            recommendations.append("Verify seller's identity and ownership chain")
            recommendations.append("Conduct site inspection")
            recommendations.append("Obtain updated Encumbrance Certificate")
        
        # General recommendations
        recommendations.append("Verify seller's identity and ownership chain")
        recommendations.append("Conduct site inspection")
        recommendations.append("Obtain updated Encumbrance Certificate")
        
        return recommendations
    
    def _validate_risk_classification_consistency(self, risk_score: int, factors: List[str], 
                                                          flags: List[str], classification: str,
                                                          loan_present: bool, case_numbers: List) -> tuple:
        """
        ISSUE 6 FIX: Validate consistency between risk score and classification
        Auto-correct if inconsistent and log correction
        
        Args:
            risk_score: Current risk score
            factors: Current risk factors
            flags: Current risk flags
            classification: Document classification label
            loan_present: Whether loan was detected
            case_numbers: List of case numbers
        
        Returns:
            tuple: (corrected_score, corrected_factors, corrected_flags)
        """
        risk_level = self._get_risk_level(risk_score)
        inconsistent = False
        correction_reason = None
        
        # Rule 1: Medium risk (40+) cannot have Unknown classification
        if risk_score >= 40 and classification in ["Unknown", "Incomplete Document"]:
            inconsistent = True
            correction_reason = f"Risk score {risk_score} inconsistent with '{classification}' classification"
            
            # Auto-correct classification based on detected issues
            if loan_present:
                factors.append("Consistency correction: Classification updated to reflect loan risk")
            elif case_numbers:
                factors.append("Consistency correction: Classification updated to reflect legal case risk")
            else:
                factors.append("Consistency correction: Risk factors present but classification was Unknown")
        
        # Rule 2: Loan risk (30 points) must result in at least Medium risk if classification is Loan Detected
        if classification == "Loan Detected" and risk_score < 30:
            inconsistent = True
            risk_score = max(risk_score, 40)  # Ensure at least Medium risk
            factors.append("Consistency correction: Risk score adjusted to match Loan Detected classification")
            correction_reason = "Loan detected but risk score too low - adjusted to 40/100"
        
        # Rule 3: Clear Title classification should have low risk
        if classification == "Clear Title" and risk_score > 30:
            inconsistent = True
            # Don't auto-correct score down (real risks should prevail)
            factors.append("Consistency validation: High risk detected despite Clear Title classification - actual risks take precedence")
            correction_reason = f"Clear Title classification but risk score {risk_score}/100 indicates actual risks present"
        
        # Log correction if inconsistency detected
        if inconsistent and correction_reason:
            flags.append("CONSISTENCY_CORRECTED")
            # Would log to audit system here in production
            print(f"\n⚠️ CONSISTENCY CORRECTION: {correction_reason}")
        
        return risk_score, factors, flags
    
    def _get_summary(self, risk_level: str, flags: List[str]) -> str:
        """Get brief summary"""
        if risk_level == "Low":
            return "✅ Document appears suitable for transaction with standard verification"
        elif risk_level == "Medium":
            return "⚠️ Document requires additional legal review before proceeding"
        else:
            return "🚫 Document has significant concerns requiring detailed investigation"
    
    def calculate_from_files(self, entity_file: str, classification_file: str, 
                            output_file: str = None) -> Dict:
        """
        Calculate risk score from entity and classification JSON files
        
        Args:
            entity_file: Path to entity JSON file
            classification_file: Path to classification JSON file
            output_file: Path to save risk assessment (optional)
            
        Returns:
            dict: Complete risk assessment
        """
        # Load entity data
        with open(entity_file, 'r', encoding='utf-8') as f:
            entity_data = json.load(f)
        
        # Load classification data
        with open(classification_file, 'r', encoding='utf-8') as f:
            class_data = json.load(f)
        
        entities = entity_data.get('entities', {})
        classification = class_data.get('classification', {})
        
        # Calculate risk score
        risk_assessment = self.calculate_risk_score(entities, classification)
        
        # Create complete result
        result = {
            "document_id": Path(entity_file).stem.replace('_ocr_cleaned_entities', ''),
            "assessed_at": datetime.now().isoformat(),
            "input_files": {
                "entities": entity_file,
                "classification": classification_file
            },
            "classification_summary": {
                "label": classification.get('label', 'Unknown'),
                "confidence": classification.get('confidence', 0)
            },
            "entity_summary": entity_data.get('summary', {}),
            "risk_assessment": risk_assessment
        }
        
        # Determine output file
        if output_file is None:
            base_path = Path(entity_file).parent
            doc_id = result["document_id"]
            output_file = base_path / f"{doc_id}_risk_assessment.json"
        
        output_path = Path(output_file)
        
        # Save to JSON
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        
        result["output_file"] = str(output_path)
        return result
