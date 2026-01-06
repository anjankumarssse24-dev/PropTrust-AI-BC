"""
Database Models for PropTrust
"""

from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base


class Property(Base):
    """Property document record"""
    __tablename__ = "properties"
    
    id = Column(Integer, primary_key=True, index=True)
    property_id = Column(String(100), unique=True, index=True, nullable=False)
    document_type = Column(String(50), nullable=False)  # RTC, MR, EC, etc.
    document_path = Column(String(500))  # Path to original document
    file_hash = Column(String(64), index=True)  # SHA-256 hash for deduplication
    owner_name = Column(String(200))
    survey_number = Column(String(100))
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    user_id = Column(String(100), nullable=True)  # Optional: for multi-user system
    
    # Relationships
    verifications = relationship("VerificationRecord", back_populates="property", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Property(property_id='{self.property_id}', type='{self.document_type}')>"


class VerificationRecord(Base):
    """Verification record with blockchain reference"""
    __tablename__ = "verification_records"
    
    id = Column(Integer, primary_key=True, index=True)
    verification_id = Column(String(100), unique=True, index=True, nullable=False)
    property_id = Column(String(100), ForeignKey("properties.property_id"), nullable=False)
    
    # Verification results
    risk_score = Column(Integer, nullable=False)
    risk_level = Column(String(50))  # Low, Medium, High
    verification_status = Column(String(50))  # VERIFIED, TAMPERED, etc.
    
    # Blockchain references
    blockchain_hash = Column(String(66), nullable=False)  # SHA-256 hash (0x + 64 chars)
    blockchain_tx_hash = Column(String(66))  # Transaction hash
    blockchain_block_number = Column(Integer)
    blockchain_timestamp = Column(Integer)  # Unix timestamp from blockchain
    
    # Metadata
    verified_at = Column(DateTime, default=datetime.utcnow)
    verification_method = Column(String(50), default="AI")  # AI, Manual, etc.
    
    # Relationships
    property = relationship("Property", back_populates="verifications")
    details = relationship("VerificationDetail", back_populates="verification", uselist=False, cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<VerificationRecord(id='{self.verification_id}', risk={self.risk_score})>"


class VerificationDetail(Base):
    """Detailed verification results"""
    __tablename__ = "verification_details"
    
    id = Column(Integer, primary_key=True, index=True)
    verification_id = Column(String(100), ForeignKey("verification_records.verification_id"), unique=True, nullable=False)
    
    # Document fields
    owner_name = Column(String(200))
    survey_number = Column(String(100))
    land_extent = Column(String(100))
    
    # Extracted entities (JSON)
    entities_json = Column(JSON)  # All extracted entities
    
    # Classification results (JSON)
    classification_json = Column(JSON)
    
    # Risk factors
    loan_detected = Column(Boolean, default=False)
    loan_amount = Column(String(50))
    bank_name = Column(String(200))
    legal_case_detected = Column(Boolean, default=False)
    case_number = Column(String(100))
    mutation_status = Column(String(50))
    
    # Risk assessment details (JSON)
    risk_factors = Column(JSON)  # List of risk factors
    recommendations = Column(JSON)  # List of recommendations
    
    # OCR and processing
    ocr_text = Column(Text)  # Full OCR text
    translated_text = Column(Text)  # Translated text
    
    # Relationship
    verification = relationship("VerificationRecord", back_populates="details")
    
    def __repr__(self):
        return f"<VerificationDetail(verification_id='{self.verification_id}')>"


class TamperCheck(Base):
    """Tamper detection check history"""
    __tablename__ = "tamper_checks"
    
    id = Column(Integer, primary_key=True, index=True)
    property_id = Column(String(100), ForeignKey("properties.property_id"), nullable=False)
    
    # Check results
    check_time = Column(DateTime, default=datetime.utcnow)
    tampered = Column(Boolean, nullable=False)
    match_status = Column(String(50))  # VERIFIED, TAMPERED, NOT_FOUND
    
    # Hash comparison
    current_hash = Column(String(64))
    blockchain_hash = Column(String(66))
    hash_matched = Column(Boolean)
    
    # Risk score comparison
    current_risk_score = Column(Integer)
    blockchain_risk_score = Column(Integer)
    risk_score_changed = Column(Boolean)
    
    # Details (JSON)
    details_json = Column(JSON)
    warnings = Column(JSON)
    
    def __repr__(self):
        return f"<TamperCheck(property_id='{self.property_id}', tampered={self.tampered})>"


class AuditLog(Base):
    """Audit log for all operations"""
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Operation details
    operation_type = Column(String(50), nullable=False)  # UPLOAD, VERIFY, TAMPER_CHECK, etc.
    property_id = Column(String(100))
    user_id = Column(String(100))
    
    # Status
    status = Column(String(50))  # SUCCESS, FAILED, WARNING
    message = Column(Text)
    
    # Additional data
    metadata_json = Column(JSON)
    
    def __repr__(self):
        return f"<AuditLog(operation='{self.operation_type}', status='{self.status}')>"
