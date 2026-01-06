// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

/**
 * @title PropertyVerification
 * @dev Smart contract for storing property document verification hashes
 * Ensures immutable audit trail for property document verification
 */
contract PropertyVerification {
    
    // Structure to store verification record
    struct VerificationRecord {
        string propertyId;           // Unique property identifier
        bytes32 verificationHash;    // SHA-256 hash of verification result
        uint256 riskScore;           // Risk score (0-100)
        uint256 timestamp;           // Verification timestamp
        address verifier;            // Address that performed verification
        bool exists;                 // Flag to check if record exists
    }
    
    // Mapping: propertyId => VerificationRecord
    mapping(string => VerificationRecord) private verifications;
    
    // Array to store all property IDs (for iteration)
    string[] private propertyIds;
    
    // Mapping: propertyId => array of verification hashes (for history)
    mapping(string => bytes32[]) private verificationHistory;
    
    // Events
    event VerificationStored(
        string indexed propertyId,
        bytes32 verificationHash,
        uint256 riskScore,
        uint256 timestamp,
        address verifier
    );
    
    event VerificationUpdated(
        string indexed propertyId,
        bytes32 oldHash,
        bytes32 newHash,
        uint256 timestamp
    );
    
    // Owner of the contract
    address public owner;
    
    // Modifier to restrict access to owner
    modifier onlyOwner() {
        require(msg.sender == owner, "Only owner can call this function");
        _;
    }
    
    // Constructor
    constructor() {
        owner = msg.sender;
    }
    
    /**
     * @dev Store a new verification record
     * @param _propertyId Unique property identifier
     * @param _verificationHash SHA-256 hash of verification result
     * @param _riskScore Risk score (0-100)
     */
    function storeVerification(
        string memory _propertyId,
        bytes32 _verificationHash,
        uint256 _riskScore
    ) public returns (bool) {
        require(bytes(_propertyId).length > 0, "Property ID cannot be empty");
        require(_riskScore <= 100, "Risk score must be between 0 and 100");
        require(_verificationHash != bytes32(0), "Hash cannot be empty");
        
        // If property already exists, update it
        if (verifications[_propertyId].exists) {
            bytes32 oldHash = verifications[_propertyId].verificationHash;
            
            // Store in history
            verificationHistory[_propertyId].push(oldHash);
            
            // Update record
            verifications[_propertyId].verificationHash = _verificationHash;
            verifications[_propertyId].riskScore = _riskScore;
            verifications[_propertyId].timestamp = block.timestamp;
            verifications[_propertyId].verifier = msg.sender;
            
            emit VerificationUpdated(
                _propertyId,
                oldHash,
                _verificationHash,
                block.timestamp
            );
        } else {
            // Create new record
            verifications[_propertyId] = VerificationRecord({
                propertyId: _propertyId,
                verificationHash: _verificationHash,
                riskScore: _riskScore,
                timestamp: block.timestamp,
                verifier: msg.sender,
                exists: true
            });
            
            // Add to property IDs array
            propertyIds.push(_propertyId);
            
            emit VerificationStored(
                _propertyId,
                _verificationHash,
                _riskScore,
                block.timestamp,
                msg.sender
            );
        }
        
        return true;
    }
    
    /**
     * @dev Get verification record for a property
     * @param _propertyId Property identifier
     */
    function getVerification(string memory _propertyId) 
        public 
        view 
        returns (
            string memory propertyId,
            bytes32 verificationHash,
            uint256 riskScore,
            uint256 timestamp,
            address verifier,
            bool exists
        ) 
    {
        VerificationRecord memory record = verifications[_propertyId];
        return (
            record.propertyId,
            record.verificationHash,
            record.riskScore,
            record.timestamp,
            record.verifier,
            record.exists
        );
    }
    
    /**
     * @dev Check if a property has been verified
     * @param _propertyId Property identifier
     */
    function isVerified(string memory _propertyId) public view returns (bool) {
        return verifications[_propertyId].exists;
    }
    
    /**
     * @dev Get verification history for a property
     * @param _propertyId Property identifier
     */
    function getVerificationHistory(string memory _propertyId) 
        public 
        view 
        returns (bytes32[] memory) 
    {
        return verificationHistory[_propertyId];
    }
    
    /**
     * @dev Verify hash matches stored hash
     * @param _propertyId Property identifier
     * @param _hash Hash to verify
     */
    function verifyHash(string memory _propertyId, bytes32 _hash) 
        public 
        view 
        returns (bool) 
    {
        require(verifications[_propertyId].exists, "Property not found");
        return verifications[_propertyId].verificationHash == _hash;
    }
    
    /**
     * @dev Get total number of verified properties
     */
    function getTotalVerifications() public view returns (uint256) {
        return propertyIds.length;
    }
    
    /**
     * @dev Get property ID by index
     * @param _index Index in the array
     */
    function getPropertyIdByIndex(uint256 _index) 
        public 
        view 
        returns (string memory) 
    {
        require(_index < propertyIds.length, "Index out of bounds");
        return propertyIds[_index];
    }
    
    /**
     * @dev Get risk score for a property
     * @param _propertyId Property identifier
     */
    function getRiskScore(string memory _propertyId) 
        public 
        view 
        returns (uint256) 
    {
        require(verifications[_propertyId].exists, "Property not found");
        return verifications[_propertyId].riskScore;
    }
}
