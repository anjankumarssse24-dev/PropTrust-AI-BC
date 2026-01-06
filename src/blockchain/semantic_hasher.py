"""
Semantic Hasher Module
Generates deterministic SHA-256 hashes from verification results
"""

import hashlib
import json
from typing import Dict, Any
from datetime import datetime


class SemanticHasher:
    """Generate semantic hashes for property verification results"""
    
    def __init__(self):
        """Initialize semantic hasher"""
        self.encoding = 'utf-8'
    
    def normalize_data(self, verification_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize verification data for consistent hashing
        
        Args:
            verification_data: Raw verification results
            
        Returns:
            dict: Normalized data ready for hashing
        """
        # Extract key fields
        normalized = {
            "property_id": verification_data.get("property_id", "UNKNOWN"),
            "document_type": verification_data.get("document_type", "RTC"),
            "risk_score": verification_data.get("risk_score", 0),
            "risk_level": verification_data.get("risk_level", "UNKNOWN"),
            
            # Owner information
            "owner_name": self._normalize_name(
                verification_data.get("owner_name") or 
                verification_data.get("entities", {}).get("persons", [None])[0]
            ),
            
            # Property details
            "survey_number": self._normalize_survey(
                verification_data.get("survey_number") or
                verification_data.get("entities", {}).get("survey_numbers", [None])[0]
            ),
            
            # Critical findings
            "loan_detected": verification_data.get("loan_detected", False),
            "legal_case_detected": verification_data.get("legal_case_detected", False),
            "mutation_status": verification_data.get("mutation_status", "UNKNOWN"),
            
            # Risk factors
            "risk_factors": sorted(verification_data.get("risk_factors", [])),
            
            # Verification metadata (optional, can be excluded for re-verification)
            "verified_at": verification_data.get("verified_at", 
                                               datetime.now().isoformat())
        }
        
        return normalized
    
    def _normalize_name(self, name: str) -> str:
        """Normalize person name"""
        if not name:
            return "UNKNOWN"
        # Convert to uppercase, remove extra spaces
        return " ".join(name.strip().upper().split())
    
    def _normalize_survey(self, survey: str) -> str:
        """Normalize survey number"""
        if not survey:
            return "UNKNOWN"
        # Remove spaces, convert to uppercase
        return survey.strip().upper().replace(" ", "")
    
    def generate_hash(
        self, 
        verification_data: Dict[str, Any],
        include_timestamp: bool = True
    ) -> str:
        """
        Generate SHA-256 hash from verification data
        
        Args:
            verification_data: Verification results
            include_timestamp: Whether to include timestamp in hash
                              (False for tamper detection - re-verification)
        
        Returns:
            str: SHA-256 hash (hex string)
        """
        # Normalize data
        normalized = self.normalize_data(verification_data)
        
        # Remove timestamp if not needed (for re-verification comparison)
        if not include_timestamp:
            normalized.pop("verified_at", None)
        
        # Sort keys for deterministic JSON
        json_string = json.dumps(normalized, sort_keys=True, ensure_ascii=False)
        
        # Generate SHA-256 hash
        hash_object = hashlib.sha256(json_string.encode(self.encoding))
        hash_hex = hash_object.hexdigest()
        
        return hash_hex
    
    def generate_hash_bytes(
        self, 
        verification_data: Dict[str, Any],
        include_timestamp: bool = True
    ) -> bytes:
        """
        Generate SHA-256 hash as bytes (for blockchain storage)
        
        Args:
            verification_data: Verification results
            include_timestamp: Whether to include timestamp
            
        Returns:
            bytes: SHA-256 hash (32 bytes)
        """
        hash_hex = self.generate_hash(verification_data, include_timestamp)
        return bytes.fromhex(hash_hex)
    
    def verify_hash(
        self,
        verification_data: Dict[str, Any],
        expected_hash: str,
        include_timestamp: bool = False
    ) -> bool:
        """
        Verify if data matches expected hash
        
        Args:
            verification_data: Current verification data
            expected_hash: Expected hash (from blockchain)
            include_timestamp: Whether timestamp was included in original hash
            
        Returns:
            bool: True if hashes match
        """
        current_hash = self.generate_hash(verification_data, include_timestamp)
        return current_hash == expected_hash
    
    def get_hash_metadata(self, verification_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get hash along with metadata for storage
        
        Args:
            verification_data: Verification results
            
        Returns:
            dict: Hash metadata
            {
                "hash": "a3f8c9e2...",
                "hash_bytes": b"...",
                "property_id": "PRT-001",
                "risk_score": 45,
                "algorithm": "SHA-256",
                "timestamp": "2024-01-15T10:30:00"
            }
        """
        hash_hex = self.generate_hash(verification_data, include_timestamp=True)
        
        return {
            "hash": hash_hex,
            "hash_bytes": bytes.fromhex(hash_hex),
            "property_id": verification_data.get("property_id", "UNKNOWN"),
            "risk_score": verification_data.get("risk_score", 0),
            "algorithm": "SHA-256",
            "timestamp": datetime.now().isoformat(),
            "data_normalized": True
        }


# Example usage
if __name__ == "__main__":
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
        "risk_factors": ["LOAN_PRESENT", "OUTDATED_RECORD"],
        "verified_at": "2024-01-15T10:30:00"
    }
    
    hasher = SemanticHasher()
    
    # Generate hash
    hash_result = hasher.generate_hash(sample_data)
    print(f"Generated Hash: {hash_result}")
    
    # Get full metadata
    metadata = hasher.get_hash_metadata(sample_data)
    print(f"\nHash Metadata:")
    print(json.dumps(metadata, indent=2, default=str))
    
    # Verify hash
    is_valid = hasher.verify_hash(sample_data, hash_result, include_timestamp=True)
    print(f"\nHash Verification: {is_valid}")
