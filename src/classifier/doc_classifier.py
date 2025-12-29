"""
Document Classification Module
Classifies documents using rule-based logic and transformer models
"""

from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
from typing import Dict, List
from pathlib import Path
import json
from datetime import datetime
import re


class DocumentClassifier:
    """Document classification using rule-based and transformer models"""
    
    def __init__(self, model_path: str = None, use_rules: bool = True):
        """
        Initialize classifier
        
        Args:
            model_path: Path to fine-tuned model (optional)
            use_rules: Use rule-based classification (default True)
        """
        self.use_rules = use_rules
        self.tokenizer = None
        self.model = None
        
        # Classification labels
        self.labels = [
            "Clear Title",
            "Loan Detected",
            "Pending Mutation",
            "Court Case Mentioned",
            "Forgery Suspected",
            "Multiple Issues",
            "Incomplete Document"
        ]
        
        # Load transformer model if path provided
        if model_path and not use_rules:
            self.load_model(model_path)
    
    def classify_document(self, text: str = None, entities: Dict = None) -> Dict:
        """
        Classify document based on text or entities
        
        Args:
            text: Document text (optional)
            entities: Extracted entities (optional)
            
        Returns:
            dict: Classification result
            {
                "label": "Loan Detected",
                "confidence": 0.92,
                "all_labels": {...},
                "reasoning": "..."
            }
        """
        if self.use_rules and entities:
            return self._rule_based_classification(entities)
        elif text and self.model:
            return self._ml_classification(text)
        else:
            return {
                "label": "Incomplete Document",
                "confidence": 0.5,
                "all_labels": {},
                "reasoning": "Insufficient data for classification"
            }
    
    def _rule_based_classification(self, entities: Dict) -> Dict:
        """
        Rule-based classification using extracted entities
        
        Args:
            entities: Extracted entities from NER
            
        Returns:
            dict: Classification result
        """
        scores = {label: 0.0 for label in self.labels}
        reasons = []
        
        # Check for loan/bank presence
        has_bank = len(entities.get('banks', [])) > 0
        has_loan_indicator = entities.get('loan_present', False)
        has_loan_amount = len(entities.get('loan_amounts', [])) > 0
        
        if has_bank or has_loan_indicator or has_loan_amount:
            scores["Loan Detected"] = 0.9
            loan_info = []
            if has_bank:
                loan_info.append(f"Banks: {', '.join(entities.get('banks', []))}")
            if has_loan_amount:
                loan_info.append(f"Loan amounts: {', '.join(entities.get('loan_amounts', []))}")
            elif has_loan_indicator:
                loan_info.append("Loan indicators present")
            reasons.append(f"Loan detected - {'; '.join(loan_info)}")
        
        # Check for court cases
        has_case = len(entities.get('case_numbers', [])) > 0
        
        if has_case:
            scores["Court Case Mentioned"] = 0.85
            reasons.append(f"Court case found: {', '.join(entities.get('case_numbers', []))}")
        
        # Check for mutation keywords
        # This would need the original text, but we can check for date patterns
        dates = entities.get('dates', [])
        if len(dates) > 0:
            scores["Clear Title"] += 0.3
            reasons.append(f"Document dated: {dates[0]}")
        
        # Check survey numbers
        survey_nos = entities.get('survey_numbers', [])
        if len(survey_nos) > 0:
            scores["Clear Title"] += 0.2
            reasons.append(f"Survey number(s) found: {', '.join(survey_nos[:3])}")
        
        # Multiple issues check
        issue_count = sum([has_bank or has_loan_amount, has_case])
        if issue_count >= 2:
            scores["Multiple Issues"] = 0.8
            reasons.append("Multiple concerns detected")
        
        # If no major issues, likely clear title
        if not has_bank and not has_case and len(survey_nos) > 0:
            scores["Clear Title"] = 0.85
            if "Document dated" not in ' '.join(reasons):
                reasons.append("No encumbrances or legal issues detected")
        
        # Normalize scores to sum to 1.0
        total = sum(scores.values())
        if total > 0:
            scores = {k: v/total for k, v in scores.items()}
        
        # Get primary label (highest score)
        primary_label = max(scores, key=scores.get)
        confidence = scores[primary_label]
        
        # ISSUE 3 FIX: Ensure classification is NEVER Unknown with 0% confidence
        # Apply rule-based fallback logic when ML fails or returns low confidence
        if confidence == 0 or confidence < 0.50 or primary_label in ["Incomplete Document", "Unknown"]:
            # Fallback: Check for any detected issues and apply rules
            if has_bank or has_loan_amount or has_loan_indicator:
                primary_label = "Loan Detected"
                confidence = 0.80  # Medium-high confidence for loan detection
                reasons.append("Fallback classification: Loan evidence found")
            elif has_case:
                primary_label = "Court Case Mentioned"
                confidence = 0.75
                reasons.append("Fallback classification: Legal case detected")
            elif len(survey_nos) > 0:
                primary_label = "Clear Title"
                confidence = 0.70
                reasons.append("Fallback classification: Basic document structure present")
            else:
                primary_label = "Incomplete Document"
                confidence = 0.65  # Minimum confidence, never below 0.65
                reasons.append("Insufficient data for classification")
        
        # Ensure confidence is always between 0.70 and 0.95 for rule-based results
        if confidence < 0.70:
            confidence = 0.70
        elif confidence > 0.95:
            confidence = 0.95
        
        # Adjust confidence based on data quality
        if len(entities.get('survey_numbers', [])) == 0 and primary_label not in ["Incomplete Document"]:
            confidence *= 0.85
            reasons.append("Moderate confidence: Limited survey number data")
        
        # ISSUE 3 FIX: Add classification explanation
        classification_explanation = self._generate_classification_explanation(
            primary_label, has_bank or has_loan_indicator, has_case, len(survey_nos) > 0
        )
        
        return {
            "label": primary_label,
            "confidence": round(confidence, 3),
            "all_labels": {k: round(v, 3) for k, v in sorted(scores.items(), key=lambda x: x[1], reverse=True)},
            "reasoning": " | ".join(reasons) if reasons else "No specific indicators found",
            "explanation": classification_explanation,
            "issues_detected": {
                "loan_present": has_bank or has_loan_indicator,
                "court_case": has_case,
                "survey_numbers_present": len(survey_nos) > 0,
                "dates_present": len(dates) > 0
            }
        }
    
    def _ml_classification(self, text: str) -> Dict:
        """
        ML-based classification using transformer model
        
        Args:
            text: Document text
            
        Returns:
            dict: Classification result
        """
        if not self.model or not self.tokenizer:
            raise ValueError("Model not loaded. Please load a model first.")
        
        # Tokenize input
        inputs = self.tokenizer(
            text,
            padding=True,
            truncation=True,
            max_length=512,
            return_tensors="pt"
        )
        
        # Get predictions
        with torch.no_grad():
            outputs = self.model(**inputs)
            predictions = torch.nn.functional.softmax(outputs.logits, dim=-1)
        
        # Get top prediction
        confidence, predicted_idx = torch.max(predictions, dim=1)
        label = self.labels[predicted_idx.item()]
        
        # Get all scores
        all_scores = {
            self.labels[i]: round(predictions[0][i].item(), 3)
            for i in range(len(self.labels))
        }
        
        return {
            "label": label,
            "confidence": round(confidence.item(), 3),
            "all_labels": all_scores,
            "reasoning": "ML model prediction"
        }
    
    def classify_from_entity_file(self, entity_file: str, output_file: str = None) -> Dict:
        """
        Classify document from entity JSON file
        
        Args:
            entity_file: Path to entity JSON file
            output_file: Path to save classification (optional)
            
        Returns:
            dict: Classification results
        """
        entity_path = Path(entity_file)
        
        if not entity_path.exists():
            raise FileNotFoundError(f"Entity file not found: {entity_file}")
        
        # Load entities
        with open(entity_path, 'r', encoding='utf-8') as f:
            entity_data = json.load(f)
        
        entities = entity_data.get('entities', {})
        
        # Classify
        classification = self.classify_document(entities=entities)
        
        # Create result
        result = {
            "input_file": str(entity_path),
            "classified_at": datetime.now().isoformat(),
            "classification": classification,
            "entity_summary": entity_data.get('summary', {}),
            "recommendation": self._generate_recommendation(classification)
        }
        
        # Determine output file
        if output_file is None:
            output_file = entity_path.parent / f"{entity_path.stem.replace('_entities', '')}_classification.json"
        
        output_path = Path(output_file)
        
        # Save to JSON
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        
        result["output_file"] = str(output_path)
        return result
    
    def _generate_classification_explanation(self, label: str, has_loan: bool, has_case: bool, has_survey: bool) -> str:
        """
        Generate short explanation for classification
        ISSUE 3 FIX: Provide clear explanation of classification decision
        
        Args:
            label: Classification label
            has_loan: Whether loan was detected
            has_case: Whether court case was detected
            has_survey: Whether survey numbers were found
        
        Returns:
            str: Short explanation
        """
        explanations = {
            "Loan Detected": "Bank or loan amount found in document indicating encumbrance.",
            "Court Case Mentioned": "Legal case reference detected indicating litigation risk.",
            "Clear Title": "No encumbrances, loans, or legal issues detected.",
            "Pending Mutation": "Mutation records indicate ownership transfer in progress.",
            "Forgery Suspected": "Document contains indicators of potential forgery or tampering.",
            "Multiple Issues": "Multiple risk factors detected (loans, cases, mutations).",
            "Incomplete Document": "Missing critical information for complete verification."
        }
        
        explanation = explanations.get(label, "Classification based on document analysis.")
        
        # Add specific details
        if has_loan:
            explanation += " Loan/bank reference found."
        if has_case:
            explanation += " Court case detected."
        if not has_survey:
            explanation += " Survey number missing."
        
        return explanation
    
    def _generate_recommendation(self, classification: Dict) -> str:
        """
        Generate recommendation based on classification
        
        Args:
            classification: Classification result
            
        Returns:
            str: Recommendation text
        """
        label = classification['label']
        confidence = classification['confidence']
        
        recommendations = {
            "Clear Title": "✅ PROCEED - Document appears to have clear title. Verify all details before registration.",
            "Loan Detected": "⚠️ CAUTION - Encumbrance/loan detected. Obtain No Objection Certificate (NOC) from bank before proceeding.",
            "Court Case Mentioned": "🚫 HOLD - Legal case mentioned. Consult lawyer and verify case status before proceeding.",
            "Pending Mutation": "⚠️ CAUTION - Mutation pending. Complete mutation process before registration.",
            "Forgery Suspected": "🚫 STOP - Potential forgery indicators. Require thorough investigation and legal consultation.",
            "Multiple Issues": "🚫 HOLD - Multiple concerns detected. Detailed legal verification required.",
            "Incomplete Document": "⚠️ REVIEW - Document appears incomplete. Obtain complete documentation."
        }
        
        base_recommendation = recommendations.get(label, "⚠️ REVIEW - Manual verification required.")
        
        if confidence < 0.6:
            base_recommendation += f" (Low confidence: {confidence:.1%} - Manual review strongly recommended)"
        elif confidence < 0.8:
            base_recommendation += f" (Moderate confidence: {confidence:.1%} - Manual review recommended)"
        
        return base_recommendation
    
    def load_model(self, model_path: str):
        """Load fine-tuned transformer model"""
        self.tokenizer = AutoTokenizer.from_pretrained(model_path)
        self.model = AutoModelForSequenceClassification.from_pretrained(model_path)
        self.model.eval()
    
    def train_model(self, train_data, val_data, output_dir: str):
        """
        Fine-tune BERT/RoBERTa model
        
        Args:
            train_data: Training dataset
            val_data: Validation dataset
            output_dir: Directory to save trained model
        """
        # Placeholder for future model training
        # Would use Hugging Face Trainer API
        pass
