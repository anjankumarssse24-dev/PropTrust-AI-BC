"""
Blockchain Manager Module
Handles Web3 integration and smart contract interaction
"""

from web3 import Web3
from web3.middleware import geth_poa_middleware
import json
from pathlib import Path
from typing import Dict, Any, Optional, Tuple
import os
from dotenv import load_dotenv

load_dotenv()


class BlockchainManager:
    """Manage blockchain operations for property verification"""
    
    def __init__(
        self,
        provider_url: str = None,
        contract_address: str = None,
        contract_abi_path: str = None
    ):
        """
        Initialize blockchain connection
        
        Args:
            provider_url: Ethereum node URL (default: Ganache local)
            contract_address: Deployed contract address
            contract_abi_path: Path to contract ABI JSON
        """
        # Load configuration
        self.provider_url = provider_url or os.getenv(
            'BLOCKCHAIN_PROVIDER_URL', 
            'http://127.0.0.1:8545'
        )
        self.contract_address = contract_address or os.getenv('CONTRACT_ADDRESS')
        
        # Initialize Web3
        self.w3 = Web3(Web3.HTTPProvider(self.provider_url))
        
        # Add PoA middleware for Ganache
        self.w3.middleware_onion.inject(geth_poa_middleware, layer=0)
        
        # Check connection
        if not self.w3.is_connected():
            raise ConnectionError(
                f"Failed to connect to Ethereum node at {self.provider_url}"
            )
        
        print(f"✅ Connected to Ethereum node")
        print(f"   Chain ID: {self.w3.eth.chain_id}")
        print(f"   Latest Block: {self.w3.eth.block_number}")
        
        # Set default account (first account from Ganache)
        self.default_account = self.w3.eth.accounts[0] if self.w3.eth.accounts else None
        if self.default_account:
            print(f"   Default Account: {self.default_account}")
        
        # Load contract
        self.contract = None
        if self.contract_address and contract_abi_path:
            self.load_contract(contract_abi_path, self.contract_address)
    
    def load_contract(self, abi_path: str, contract_address: str):
        """
        Load smart contract
        
        Args:
            abi_path: Path to contract ABI JSON
            contract_address: Contract address
        """
        # Load ABI
        with open(abi_path, 'r') as f:
            contract_abi = json.load(f)
        
        # Convert address to checksum format
        contract_address = self.w3.to_checksum_address(contract_address)
        
        # Create contract instance
        self.contract = self.w3.eth.contract(
            address=contract_address,
            abi=contract_abi
        )
        
        self.contract_address = contract_address
        print(f"✅ Contract loaded at: {self.contract_address}")
    
    def deploy_contract(
        self,
        contract_bytecode: str,
        contract_abi: list,
        deployer_account: str = None
    ) -> str:
        """
        Deploy smart contract
        
        Args:
            contract_bytecode: Compiled contract bytecode
            contract_abi: Contract ABI
            deployer_account: Account to deploy from
            
        Returns:
            str: Deployed contract address
        """
        deployer_account = deployer_account or self.default_account
        
        # Create contract instance
        Contract = self.w3.eth.contract(abi=contract_abi, bytecode=contract_bytecode)
        
        # Build transaction
        tx_hash = Contract.constructor().transact({'from': deployer_account})
        
        # Wait for transaction receipt
        tx_receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
        
        contract_address = tx_receipt.contractAddress
        print(f"✅ Contract deployed at: {contract_address}")
        
        # Load the deployed contract
        self.contract = self.w3.eth.contract(
            address=contract_address,
            abi=contract_abi
        )
        self.contract_address = contract_address
        
        return contract_address
    
    def store_verification(
        self,
        property_id: str,
        verification_hash: bytes,
        risk_score: int,
        from_account: str = None
    ) -> Dict[str, Any]:
        """
        Store verification hash on blockchain
        
        Args:
            property_id: Unique property identifier
            verification_hash: SHA-256 hash (32 bytes)
            risk_score: Risk score (0-100)
            from_account: Account to send transaction from
            
        Returns:
            dict: Transaction details
            {
                "tx_hash": "0x...",
                "block_number": 123,
                "gas_used": 50000,
                "status": "success"
            }
        """
        if not self.contract:
            raise ValueError("Contract not loaded. Call load_contract() first.")
        
        from_account = from_account or self.default_account
        
        # Convert hash to bytes32 format
        if isinstance(verification_hash, str):
            verification_hash = bytes.fromhex(verification_hash)
        
        # Ensure hash is 32 bytes
        if len(verification_hash) != 32:
            raise ValueError("Verification hash must be 32 bytes")
        
        # Build transaction
        tx = self.contract.functions.storeVerification(
            property_id,
            verification_hash,
            risk_score
        ).transact({'from': from_account})
        
        # Wait for transaction receipt
        tx_receipt = self.w3.eth.wait_for_transaction_receipt(tx)
        
        # Parse result
        result = {
            "tx_hash": tx_receipt.transactionHash.hex(),
            "block_number": tx_receipt.blockNumber,
            "gas_used": tx_receipt.gasUsed,
            "status": "success" if tx_receipt.status == 1 else "failed",
            "property_id": property_id,
            "contract_address": self.contract_address
        }
        
        print(f"✅ Verification stored on blockchain")
        print(f"   Property ID: {property_id}")
        print(f"   Transaction: {result['tx_hash']}")
        print(f"   Block: {result['block_number']}")
        
        return result
    
    def get_verification(self, property_id: str) -> Dict[str, Any]:
        """
        Retrieve verification record from blockchain
        
        Args:
            property_id: Property identifier
            
        Returns:
            dict: Verification record
            {
                "property_id": "PRT-001",
                "verification_hash": "0x...",
                "risk_score": 45,
                "timestamp": 1234567890,
                "verifier": "0x...",
                "exists": True
            }
        """
        if not self.contract:
            raise ValueError("Contract not loaded")
        
        # Call contract function
        result = self.contract.functions.getVerification(property_id).call()
        
        return {
            "property_id": result[0],
            "verification_hash": result[1].hex(),
            "risk_score": result[2],
            "timestamp": result[3],
            "verifier": result[4],
            "exists": result[5]
        }
    
    def verify_hash(self, property_id: str, verification_hash: bytes) -> bool:
        """
        Verify if hash matches stored hash
        
        Args:
            property_id: Property identifier
            verification_hash: Hash to verify (32 bytes)
            
        Returns:
            bool: True if hashes match
        """
        if not self.contract:
            raise ValueError("Contract not loaded")
        
        # Convert hash if needed
        if isinstance(verification_hash, str):
            verification_hash = bytes.fromhex(verification_hash)
        
        # Call contract function
        return self.contract.functions.verifyHash(
            property_id,
            verification_hash
        ).call()
    
    def is_verified(self, property_id: str) -> bool:
        """
        Check if property has been verified
        
        Args:
            property_id: Property identifier
            
        Returns:
            bool: True if verified
        """
        if not self.contract:
            raise ValueError("Contract not loaded")
        
        return self.contract.functions.isVerified(property_id).call()
    
    def get_verification_history(self, property_id: str) -> list:
        """
        Get verification history for a property
        
        Args:
            property_id: Property identifier
            
        Returns:
            list: List of historical hashes
        """
        if not self.contract:
            raise ValueError("Contract not loaded")
        
        history = self.contract.functions.getVerificationHistory(property_id).call()
        return [h.hex() for h in history]
    
    def get_total_verifications(self) -> int:
        """Get total number of verified properties"""
        if not self.contract:
            raise ValueError("Contract not loaded")
        
        return self.contract.functions.getTotalVerifications().call()
    
    def get_risk_score(self, property_id: str) -> int:
        """Get risk score for a property"""
        if not self.contract:
            raise ValueError("Contract not loaded")
        
        return self.contract.functions.getRiskScore(property_id).call()
    
    def get_transaction_details(self, tx_hash: str) -> Dict[str, Any]:
        """
        Get transaction details
        
        Args:
            tx_hash: Transaction hash
            
        Returns:
            dict: Transaction details
        """
        tx = self.w3.eth.get_transaction(tx_hash)
        tx_receipt = self.w3.eth.get_transaction_receipt(tx_hash)
        
        return {
            "hash": tx_hash,
            "block_number": tx_receipt.blockNumber,
            "from": tx['from'],
            "to": tx['to'],
            "gas_used": tx_receipt.gasUsed,
            "status": "success" if tx_receipt.status == 1 else "failed",
            "timestamp": self.w3.eth.get_block(tx_receipt.blockNumber).timestamp
        }


# Example usage
if __name__ == "__main__":
    # Initialize blockchain manager
    manager = BlockchainManager()
    
    # Example: Store verification
    sample_hash = b'\x00' * 32  # Placeholder hash
    
    try:
        result = manager.store_verification(
            property_id="PRT-TEST-001",
            verification_hash=sample_hash,
            risk_score=45
        )
        print(f"\n✅ Stored verification:")
        print(json.dumps(result, indent=2))
        
        # Retrieve verification
        verification = manager.get_verification("PRT-TEST-001")
        print(f"\n✅ Retrieved verification:")
        print(json.dumps(verification, indent=2, default=str))
        
    except Exception as e:
        print(f"❌ Error: {e}")
