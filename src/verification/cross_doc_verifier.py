"""
Cross-Document Verification Module
Compares RTC and MR (Mutation Register) documents to detect inconsistencies
"""

from typing import Dict, List, Tuple
import json
from pathlib import Path
from difflib import SequenceMatcher


class CrossDocumentVerifier:
    """Verify consistency between RTC and MR documents"""
    
    def __init__(self):
        """Initialize cross-document verifier"""
        self.verification_results = {}
    
    def verify_rtc_vs_mr(
        self, 
        rtc_entities: Dict, 
        mr_entities: Dict,
        rtc_fields: Dict = None,
        mr_fields: Dict = None
    ) -> Dict:
        """
        Compare RTC and MR documents for consistency
        
        Args:
            rtc_entities: Extracted entities from RTC document
            mr_entities: Extracted entities from MR (Mutation Register)
            rtc_fields: Optional structured RTC fields
            mr_fields: Optional structured MR fields
            
        Returns:
            dict: Verification results with matches and mismatches
        """
        print("\n" + "="*70)
        print("CROSS-DOCUMENT VERIFICATION: RTC vs MR")
        print("="*70)
        
        results = {
            "verification_status": "VERIFIED",
            "match_score": 0,
            "total_checks": 0,
            "passed_checks": 0,
            "failed_checks": 0,
            "matches": [],
            "mismatches": [],
            "warnings": [],
            "details": {}
        }
        
        # Check 1: Survey Number Match
        # Try to get from entities first, then from RTC fields
        rtc_surveys = rtc_entities.get('survey_numbers', [])
        if not rtc_surveys and rtc_fields and rtc_fields.get('survey_number'):
            rtc_surveys = [rtc_fields['survey_number']]
        
        mr_surveys = mr_entities.get('survey_numbers', [])
        if not mr_surveys and mr_fields and mr_fields.get('survey_number'):
            mr_surveys = [mr_fields['survey_number']]
        
        survey_result = self._compare_survey_numbers(rtc_surveys, mr_surveys)
        results['total_checks'] += 1
        if survey_result['match']:
            results['passed_checks'] += 1
            results['matches'].append(survey_result)
        else:
            results['failed_checks'] += 1
            results['mismatches'].append(survey_result)
        results['details']['survey_numbers'] = survey_result
        
        # Check 2: Owner Name Match
        # Try to get from entities first, then from RTC fields
        rtc_owners = rtc_entities.get('persons', []) or rtc_entities.get('owner_names', [])
        if not rtc_owners and rtc_fields and rtc_fields.get('owner_name'):
            rtc_owners = [rtc_fields['owner_name']]
        
        mr_owners = mr_entities.get('persons', []) or mr_entities.get('owner_names', [])
        if not mr_owners and mr_fields and mr_fields.get('owner_name'):
            mr_owners = [mr_fields['owner_name']]
        owner_result = self._compare_owners(rtc_owners, mr_owners)
        results['total_checks'] += 1
        if owner_result['match']:
            results['passed_checks'] += 1
            results['matches'].append(owner_result)
        else:
            results['failed_checks'] += 1
            results['mismatches'].append(owner_result)
        results['details']['owner_names'] = owner_result
        
        # Check 3: Date Consistency
        rtc_dates = rtc_entities.get('dates', [])
        mr_dates = mr_entities.get('dates', [])
        date_result = self._compare_dates(rtc_dates, mr_dates)
        results['total_checks'] += 1
        if date_result['match']:
            results['passed_checks'] += 1
            results['matches'].append(date_result)
        elif date_result.get('warning'):
            results['warnings'].append(date_result)
        else:
            results['failed_checks'] += 1
            results['mismatches'].append(date_result)
        results['details']['dates'] = date_result
        
        # Check 4: Mutation Status
        mutation_result = self._check_mutation_status(rtc_entities, mr_entities)
        results['total_checks'] += 1
        if mutation_result['match']:
            results['passed_checks'] += 1
            results['matches'].append(mutation_result)
        else:
            results['warnings'].append(mutation_result)
        results['details']['mutation_status'] = mutation_result
        
        # Check 5: Loan/Encumbrance Cross-Check
        rtc_loans = rtc_entities.get('loan_present', False)
        mr_loans = mr_entities.get('loan_present', False)
        loan_result = self._compare_loans(rtc_entities, mr_entities)
        results['total_checks'] += 1
        if loan_result['match']:
            results['passed_checks'] += 1
            results['matches'].append(loan_result)
        else:
            results['failed_checks'] += 1
            results['mismatches'].append(loan_result)
        results['details']['loans'] = loan_result
        
        # Calculate match score (0-100)
        if results['total_checks'] > 0:
            results['match_score'] = round(
                (results['passed_checks'] / results['total_checks']) * 100
            )
        
        # Set overall verification status
        if results['match_score'] >= 80:
            results['verification_status'] = "VERIFIED"
        elif results['match_score'] >= 60:
            results['verification_status'] = "MINOR_MISMATCH"
        else:
            results['verification_status'] = "MAJOR_MISMATCH"
        
        self._print_results(results)
        
        return results
    
    def _compare_survey_numbers(
        self, 
        rtc_surveys: List[str], 
        mr_surveys: List[str]
    ) -> Dict:
        """Compare survey numbers between RTC and MR"""
        
        rtc_set = set(rtc_surveys)
        mr_set = set(mr_surveys)
        
        common = rtc_set.intersection(mr_set)
        
        if len(common) > 0:
            return {
                "field": "Survey Numbers",
                "match": True,
                "rtc_values": list(rtc_surveys),
                "mr_values": list(mr_surveys),
                "common_values": list(common),
                "message": f"✅ Survey numbers match: {', '.join(common)}"
            }
        elif len(rtc_surveys) == 0 and len(mr_surveys) == 0:
            return {
                "field": "Survey Numbers",
                "match": True,
                "rtc_values": [],
                "mr_values": [],
                "common_values": [],
                "message": "⚠️ No survey numbers found in either document"
            }
        else:
            return {
                "field": "Survey Numbers",
                "match": False,
                "rtc_values": list(rtc_surveys),
                "mr_values": list(mr_surveys),
                "common_values": list(common),
                "message": f"❌ Survey number mismatch - RTC: {rtc_surveys}, MR: {mr_surveys}"
            }
    
    def _compare_owners(
        self, 
        rtc_owners: List[str], 
        mr_owners: List[str]
    ) -> Dict:
        """Compare owner names with fuzzy matching"""
        
        if not rtc_owners and not mr_owners:
            return {
                "field": "Owner Names",
                "match": True,
                "rtc_values": [],
                "mr_values": [],
                "similarity": 0,
                "message": "⚠️ No owner names found in either document"
            }
        
        # Fuzzy matching for owner names
        best_match_score = 0
        matched_pairs = []
        
        for rtc_owner in rtc_owners:
            for mr_owner in mr_owners:
                similarity = self._fuzzy_match(rtc_owner, mr_owner)
                if similarity > best_match_score:
                    best_match_score = similarity
                if similarity >= 0.7:  # 70% similarity threshold
                    matched_pairs.append((rtc_owner, mr_owner, similarity))
        
        if best_match_score >= 0.7:
            return {
                "field": "Owner Names",
                "match": True,
                "rtc_values": rtc_owners,
                "mr_values": mr_owners,
                "matched_pairs": matched_pairs,
                "similarity": round(best_match_score * 100, 2),
                "message": f"✅ Owner names match with {round(best_match_score * 100)}% similarity"
            }
        else:
            return {
                "field": "Owner Names",
                "match": False,
                "rtc_values": rtc_owners,
                "mr_values": mr_owners,
                "matched_pairs": matched_pairs,
                "similarity": round(best_match_score * 100, 2),
                "message": f"❌ Owner name mismatch - RTC: {rtc_owners}, MR: {mr_owners}"
            }
    
    def _compare_dates(
        self, 
        rtc_dates: List[str], 
        mr_dates: List[str]
    ) -> Dict:
        """Compare dates between documents"""
        
        rtc_set = set(rtc_dates)
        mr_set = set(mr_dates)
        
        common = rtc_set.intersection(mr_set)
        
        if len(common) > 0:
            return {
                "field": "Dates",
                "match": True,
                "rtc_values": rtc_dates,
                "mr_values": mr_dates,
                "common_values": list(common),
                "message": f"✅ Common dates found: {', '.join(common)}"
            }
        elif len(rtc_dates) > 0 and len(mr_dates) > 0:
            return {
                "field": "Dates",
                "match": False,
                "warning": True,
                "rtc_values": rtc_dates,
                "mr_values": mr_dates,
                "common_values": [],
                "message": f"⚠️ Different dates - RTC: {rtc_dates[:2]}, MR: {mr_dates[:2]} (may be normal)"
            }
        else:
            return {
                "field": "Dates",
                "match": True,
                "warning": True,
                "rtc_values": rtc_dates,
                "mr_values": mr_dates,
                "common_values": [],
                "message": "⚠️ Insufficient date information"
            }
    
    def _check_mutation_status(
        self, 
        rtc_entities: Dict, 
        mr_entities: Dict
    ) -> Dict:
        """Check if mutation is properly recorded"""
        
        # Check if MR document exists and has valid data
        has_mr_data = (
            len(mr_entities.get('persons', [])) > 0 or 
            len(mr_entities.get('survey_numbers', [])) > 0
        )
        
        if has_mr_data:
            return {
                "field": "Mutation Status",
                "match": True,
                "message": "✅ Mutation Register found and validated",
                "details": "Property mutation is properly recorded"
            }
        else:
            return {
                "field": "Mutation Status",
                "match": False,
                "message": "⚠️ Mutation Register appears incomplete",
                "details": "MR document may be missing critical information"
            }
    
    def _compare_loans(
        self, 
        rtc_entities: Dict, 
        mr_entities: Dict
    ) -> Dict:
        """Compare loan/encumbrance information"""
        
        rtc_loan = rtc_entities.get('loan_present', False)
        mr_loan = mr_entities.get('loan_present', False)
        
        rtc_banks = rtc_entities.get('banks', [])
        mr_banks = mr_entities.get('banks', [])
        
        rtc_amounts = rtc_entities.get('loan_amounts', [])
        mr_amounts = mr_entities.get('loan_amounts', [])
        
        # Check if both documents agree on loan status
        if rtc_loan == mr_loan:
            if rtc_loan:
                return {
                    "field": "Loan/Encumbrance",
                    "match": True,
                    "rtc_loan": True,
                    "mr_loan": True,
                    "rtc_banks": rtc_banks,
                    "mr_banks": mr_banks,
                    "message": "✅ Both documents indicate loan present"
                }
            else:
                return {
                    "field": "Loan/Encumbrance",
                    "match": True,
                    "rtc_loan": False,
                    "mr_loan": False,
                    "message": "✅ Both documents indicate no loan"
                }
        else:
            return {
                "field": "Loan/Encumbrance",
                "match": False,
                "rtc_loan": rtc_loan,
                "mr_loan": mr_loan,
                "rtc_banks": rtc_banks,
                "mr_banks": mr_banks,
                "message": f"❌ Loan status mismatch - RTC: {'Yes' if rtc_loan else 'No'}, MR: {'Yes' if mr_loan else 'No'}"
            }
    
    def _fuzzy_match(self, str1: str, str2: str) -> float:
        """Calculate fuzzy string similarity"""
        return SequenceMatcher(None, str1.lower(), str2.lower()).ratio()
    
    def _print_results(self, results: Dict):
        """Print verification results to console"""
        
        print(f"\n📊 Verification Results:")
        print(f"   Status: {results['verification_status']}")
        print(f"   Match Score: {results['match_score']}/100")
        print(f"   Passed: {results['passed_checks']}/{results['total_checks']}")
        print(f"   Failed: {results['failed_checks']}/{results['total_checks']}")
        
        if results['matches']:
            print(f"\n✅ Matches ({len(results['matches'])}):")
            for match in results['matches']:
                print(f"   • {match['message']}")
        
        if results['mismatches']:
            print(f"\n❌ Mismatches ({len(results['mismatches'])}):")
            for mismatch in results['mismatches']:
                print(f"   • {mismatch['message']}")
        
        if results['warnings']:
            print(f"\n⚠️ Warnings ({len(results['warnings'])}):")
            for warning in results['warnings']:
                print(f"   • {warning['message']}")
    
    def save_results(self, results: Dict, output_path: str):
        """Save verification results to JSON file"""
        
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Cross-verification results saved: {output_file}")
