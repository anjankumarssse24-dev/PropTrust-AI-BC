"""
Tamper Detector Module
Detects document tampering by comparing current hash with blockchain record
"""

from typing import Dict, Any, Optional
from .semantic_hasher import SemanticHasher
from .blockchain_manager import BlockchainManager
from datetime import datetime


class TamperDetector:
    """Detect tampering in property documents"""
    
    def __init__(
        self,
        blockchain_manager: BlockchainManager = None,
        semantic_hasher: SemanticHasher = None
    ):
        """
        Initialize tamper detector
        
        Args:
            blockchain_manager: BlockchainManager instance
            semantic_hasher: SemanticHasher instance
        """
        self.blockchain_manager = blockchain_manager or BlockchainManager()
        self.semantic_hasher = semantic_hasher or SemanticHasher()
    
    def check_tamper(
        self,
        property_id: str,
        current_verification_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Check if document has been tampered with
        
        Args:
            property_id: Property identifier
            current_verification_data: Current verification results
            
        Returns:
            dict: Tamper detection results
            {
                "tampered": False,
                "match_status": "VERIFIED",
                "current_hash": "abc123...",
                "blockchain_hash": "abc123...",
                "risk_score_changed": False,
                "details": {...}
            }
        """
        print("\n" + "="*70)
        print("TAMPER DETECTION CHECK")
        print("="*70)
        
        results = {
            "property_id": property_id,
            "tampered": False,
            "match_status": "UNKNOWN",
            "current_hash": None,
            "blockchain_hash": None,
            "current_risk_score": None,
            "blockchain_risk_score": None,
            "risk_score_changed": False,
            "hash_matched": False,
            "verification_exists": False,
            "checked_at": datetime.now().isoformat(),
            "details": {},
            "warnings": []
        }
        
        try:
            # Step 1: Check if property exists on blockchain
            is_verified = self.blockchain_manager.is_verified(property_id)
            results["verification_exists"] = is_verified
            
            if not is_verified:
                results["match_status"] = "NOT_FOUND"
                results["warnings"].append(
                    "Property not found on blockchain. This is the first verification."
                )
                print(f"⚠️  Property {property_id} not found on blockchain")
                return results
            
            # Step 2: Get blockchain record
            blockchain_record = self.blockchain_manager.get_verification(property_id)
            results["blockchain_hash"] = blockchain_record["verification_hash"]
            results["blockchain_risk_score"] = blockchain_record["risk_score"]
            results["blockchain_timestamp"] = blockchain_record["timestamp"]
            results["blockchain_verifier"] = blockchain_record["verifier"]
            
            print(f"📜 Blockchain Record:")
            print(f"   Hash: {blockchain_record['verification_hash'][:16]}...")
            print(f"   Risk Score: {blockchain_record['risk_score']}")
            
            # Step 3: Generate current hash (without timestamp for comparison)
            current_hash = self.semantic_hasher.generate_hash(
                current_verification_data,
                include_timestamp=False
            )
            results["current_hash"] = current_hash
            results["current_risk_score"] = current_verification_data.get("risk_score", 0)
            
            print(f"\n🔍 Current Document:")
            print(f"   Hash: {current_hash[:16]}...")
            print(f"   Risk Score: {results['current_risk_score']}")
            
            # Step 4: Compare hashes
            blockchain_hash_without_prefix = blockchain_record["verification_hash"]
            if blockchain_hash_without_prefix.startswith("0x"):
                blockchain_hash_without_prefix = blockchain_hash_without_prefix[2:]
            
            hash_matched = (current_hash == blockchain_hash_without_prefix)
            results["hash_matched"] = hash_matched
            
            # Step 5: Check risk score changes
            risk_score_changed = (
                results["current_risk_score"] != results["blockchain_risk_score"]
            )
            results["risk_score_changed"] = risk_score_changed
            
            # Step 6: Determine tamper status
            if hash_matched and not risk_score_changed:
                results["tampered"] = False
                results["match_status"] = "VERIFIED"
                print(f"\n✅ VERIFICATION SUCCESS: Document is authentic")
                
            elif hash_matched and risk_score_changed:
                results["tampered"] = False
                results["match_status"] = "VERIFIED_WITH_CHANGES"
                results["warnings"].append(
                    "Hash matched but risk score changed. "
                    "This may indicate risk assessment model update."
                )
                print(f"\n⚠️  PARTIAL MATCH: Hash verified but risk score changed")
                
            else:
                results["tampered"] = True
                results["match_status"] = "TAMPERED"
                results["warnings"].append(
                    "Hash mismatch detected! Document may have been tampered with."
                )
                print(f"\n❌ TAMPER DETECTED: Hash mismatch!")
            
            # Step 7: Detailed comparison
            results["details"] = self._generate_detailed_comparison(
                current_verification_data,
                blockchain_record,
                results
            )
            
        except Exception as e:
            results["match_status"] = "ERROR"
            results["warnings"].append(f"Error during tamper check: {str(e)}")
            print(f"\n❌ Error: {e}")
        
        return results
    
    def _generate_detailed_comparison(
        self,
        current_data: Dict[str, Any],
        blockchain_record: Dict[str, Any],
        results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate detailed comparison report"""
        
        # Normalize current data
        normalized_current = self.semantic_hasher.normalize_data(current_data)
        
        comparison = {
            "hash_comparison": {
                "current": results["current_hash"][:32] + "...",
                "blockchain": results["blockchain_hash"][:32] + "...",
                "matched": results["hash_matched"]
            },
            "risk_score_comparison": {
                "current": results["current_risk_score"],
                "blockchain": results["blockchain_risk_score"],
                "difference": abs(
                    results["current_risk_score"] - results["blockchain_risk_score"]
                ),
                "changed": results["risk_score_changed"]
            },
            "key_fields": {
                "owner_name": normalized_current.get("owner_name", "UNKNOWN"),
                "survey_number": normalized_current.get("survey_number", "UNKNOWN"),
                "loan_detected": normalized_current.get("loan_detected", False),
                "legal_case_detected": normalized_current.get("legal_case_detected", False)
            },
            "blockchain_metadata": {
                "timestamp": blockchain_record["timestamp"],
                "verifier": blockchain_record["verifier"],
                "block_verified": True
            }
        }
        
        return comparison
    
    def generate_tamper_report(
        self,
        tamper_results: Dict[str, Any]
    ) -> str:
        """
        Generate human-readable tamper detection report
        
        Args:
            tamper_results: Results from check_tamper()
            
        Returns:
            str: Formatted report
        """
        report_lines = []
        report_lines.append("="*70)
        report_lines.append("TAMPER DETECTION REPORT")
        report_lines.append("="*70)
        report_lines.append(f"Property ID: {tamper_results['property_id']}")
        report_lines.append(f"Check Time: {tamper_results['checked_at']}")
        report_lines.append("")
        
        # Status
        status = tamper_results['match_status']
        if status == "VERIFIED":
            report_lines.append("✅ STATUS: VERIFIED - Document is authentic")
        elif status == "TAMPERED":
            report_lines.append("❌ STATUS: TAMPERED - Document has been modified")
        elif status == "NOT_FOUND":
            report_lines.append("⚠️  STATUS: NOT FOUND - First verification")
        else:
            report_lines.append(f"⚠️  STATUS: {status}")
        
        report_lines.append("")
        
        # Hash comparison
        if tamper_results.get("blockchain_hash"):
            report_lines.append("HASH COMPARISON:")
            report_lines.append(f"  Current:    {tamper_results['current_hash'][:32]}...")
            report_lines.append(f"  Blockchain: {tamper_results['blockchain_hash'][:32]}...")
            report_lines.append(f"  Matched: {'✅ Yes' if tamper_results['hash_matched'] else '❌ No'}")
            report_lines.append("")
        
        # Risk score comparison
        if tamper_results.get("blockchain_risk_score") is not None:
            report_lines.append("RISK SCORE COMPARISON:")
            report_lines.append(f"  Current:    {tamper_results['current_risk_score']}")
            report_lines.append(f"  Blockchain: {tamper_results['blockchain_risk_score']}")
            report_lines.append(f"  Changed: {'⚠️  Yes' if tamper_results['risk_score_changed'] else '✅ No'}")
            report_lines.append("")
        
        # Warnings
        if tamper_results["warnings"]:
            report_lines.append("WARNINGS:")
            for warning in tamper_results["warnings"]:
                report_lines.append(f"  ⚠️  {warning}")
            report_lines.append("")
        
        report_lines.append("="*70)
        
        return "\n".join(report_lines)


# Example usage
if __name__ == "__main__":
    import json
    
    # Sample verification data
    sample_data = {
        "property_id": "PRT-178-001",
        "document_type": "RTC",
        "owner_name": "RAJESH KUMAR",
        "survey_number": "178/1",
        "risk_score": 45,
        "risk_level": "Medium",
        "loan_detected": True,
        "legal_case_detected": False,
        "mutation_status": "COMPLETED",
        "risk_factors": ["LOAN_PRESENT", "OUTDATED_RECORD"]
    }
    
    # Initialize detector
    detector = TamperDetector()
    
    # Check for tampering
    results = detector.check_tamper("PRT-178-001", sample_data)
    
    print("\n" + json.dumps(results, indent=2, default=str))
    
    # Generate report
    report = detector.generate_tamper_report(results)
    print("\n" + report)
