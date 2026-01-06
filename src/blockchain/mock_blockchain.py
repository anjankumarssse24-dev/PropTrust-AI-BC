"""
Mock Blockchain Module
Simulates blockchain storage with realistic-looking blockchain data stored in SQLite
No need for Ganache or real blockchain node
"""

import hashlib
import time
import secrets
from typing import Dict, Any
from datetime import datetime


class MockBlockchain:
    """
    Simulated blockchain that generates realistic blockchain values
    and stores them in SQLite database
    """
    
    def __init__(self):
        """Initialize mock blockchain"""
        self.current_block_number = 1000000  # Start from a realistic block number
        self.chain_id = 5777  # Ganache default chain ID for consistency
        self.network_name = "PropTrust Demo Network"
        
    def generate_transaction_hash(self, data: str) -> str:
        """
        Generate a realistic-looking transaction hash
        
        Args:
            data: Input data to hash
            
        Returns:
            Transaction hash in format: 0x[64 hex characters]
        """
        # Combine data with random salt for uniqueness
        salt = secrets.token_hex(16)
        combined = f"{data}_{salt}_{time.time()}"
        
        # Generate SHA-256 hash
        hash_obj = hashlib.sha256(combined.encode())
        tx_hash = f"0x{hash_obj.hexdigest()}"
        
        return tx_hash
    
    def generate_verification_hash(self, verification_data: Dict[str, Any]) -> str:
        """
        Generate verification hash from property data
        
        Args:
            verification_data: Dictionary containing verification results
            
        Returns:
            Verification hash in format: 0x[64 hex characters]
        """
        # Create deterministic hash from verification data
        data_str = str(sorted(verification_data.items()))
        hash_obj = hashlib.sha256(data_str.encode())
        return f"0x{hash_obj.hexdigest()}"
    
    def get_current_timestamp(self) -> int:
        """Get current Unix timestamp"""
        return int(time.time())
    
    def get_next_block_number(self) -> int:
        """
        Get next block number (increments with each call)
        
        Returns:
            Next block number
        """
        self.current_block_number += 1
        return self.current_block_number
    
    def store_verification(
        self,
        property_id: str,
        verification_data: Dict[str, Any],
        risk_score: int
    ) -> Dict[str, Any]:
        """
        Simulate storing verification on blockchain
        
        Args:
            property_id: Unique property identifier
            verification_data: Complete verification results
            risk_score: Risk score (0-100)
            
        Returns:
            Dictionary with blockchain transaction details
        """
        # Generate blockchain-like data
        verification_hash = self.generate_verification_hash(verification_data)
        tx_hash = self.generate_transaction_hash(f"{property_id}_{verification_hash}")
        block_number = self.get_next_block_number()
        timestamp = self.get_current_timestamp()
        
        # Simulate gas cost (realistic values)
        gas_used = 65000 + (len(str(verification_data)) * 10)  # Base gas + data size
        gas_price = 20  # Gwei
        
        # Return blockchain transaction result
        return {
            "success": True,
            "tx_hash": tx_hash,
            "block_number": block_number,
            "verification_hash": verification_hash,
            "timestamp": timestamp,
            "gas_used": gas_used,
            "gas_price": gas_price,
            "network": self.network_name,
            "chain_id": self.chain_id,
            "confirmation_time": "~2 seconds",  # Simulated
            "status": "confirmed"
        }
    
    def verify_record(
        self,
        property_id: str,
        stored_hash: str,
        current_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Verify if stored hash matches current data
        
        Args:
            property_id: Property identifier
            stored_hash: Hash stored in database
            current_data: Current verification data
            
        Returns:
            Verification result with integrity check
        """
        # Generate hash from current data
        current_hash = self.generate_verification_hash(current_data)
        
        # Compare hashes
        is_valid = (stored_hash == current_hash)
        
        return {
            "property_id": property_id,
            "is_valid": is_valid,
            "stored_hash": stored_hash,
            "computed_hash": current_hash,
            "status": "VERIFIED" if is_valid else "TAMPERED",
            "message": "Document integrity verified" if is_valid else "Document has been modified",
            "verified_at": datetime.utcnow().isoformat()
        }
    
    def get_block_info(self, block_number: int) -> Dict[str, Any]:
        """
        Get simulated block information
        
        Args:
            block_number: Block number
            
        Returns:
            Block information
        """
        return {
            "block_number": block_number,
            "timestamp": self.get_current_timestamp(),
            "network": self.network_name,
            "chain_id": self.chain_id,
            "block_hash": f"0x{secrets.token_hex(32)}",
            "parent_hash": f"0x{secrets.token_hex(32)}",
            "gas_limit": 8000000,
            "gas_used": 150000,
            "transaction_count": 5  # Simulated
        }
    
    def get_connection_status(self) -> Dict[str, Any]:
        """
        Get blockchain connection status
        
        Returns:
            Connection status information
        """
        return {
            "connected": True,
            "network": self.network_name,
            "chain_id": self.chain_id,
            "current_block": self.current_block_number,
            "type": "Simulated (SQLite-backed)",
            "status": "operational"
        }


# Global instance
mock_blockchain = MockBlockchain()
