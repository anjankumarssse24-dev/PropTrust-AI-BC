"""
CRUD Operations for Database
"""

from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime
from . import models


# ============= Property CRUD =============

def create_property(
    db: Session,
    property_id: str,
    document_type: str,
    document_path: str = None,
    owner_name: str = None,
    survey_number: str = None,
    user_id: str = None,
    file_hash: str = None
) -> models.Property:
    """Create new property record"""
    db_property = models.Property(
        property_id=property_id,
        document_type=document_type,
        document_path=document_path,
        file_hash=file_hash,
        owner_name=owner_name,
        survey_number=survey_number,
        user_id=user_id
    )
    db.add(db_property)
    db.commit()
    db.refresh(db_property)
    return db_property


def get_property(db: Session, property_id: str) -> Optional[models.Property]:
    """Get property by ID"""
    return db.query(models.Property).filter(
        models.Property.property_id == property_id
    ).first()


def get_property_by_file_hash(db: Session, file_hash: str) -> Optional[models.Property]:
    """Get property by file hash (for deduplication)"""
    return db.query(models.Property).filter(
        models.Property.file_hash == file_hash
    ).first()


def get_properties(db: Session, skip: int = 0, limit: int = 100) -> List[models.Property]:
    """Get all properties"""
    return db.query(models.Property).offset(skip).limit(limit).all()


# ============= Verification CRUD =============

def create_verification(
    db: Session,
    verification_id: str,
    property_id: str,
    risk_score: int,
    risk_level: str,
    verification_status: str,
    blockchain_hash: str,
    blockchain_tx_hash: str = None,
    blockchain_block_number: int = None,
    blockchain_timestamp: int = None
) -> models.VerificationRecord:
    """Create new verification record"""
    db_verification = models.VerificationRecord(
        verification_id=verification_id,
        property_id=property_id,
        risk_score=risk_score,
        risk_level=risk_level,
        verification_status=verification_status,
        blockchain_hash=blockchain_hash,
        blockchain_tx_hash=blockchain_tx_hash,
        blockchain_block_number=blockchain_block_number,
        blockchain_timestamp=blockchain_timestamp
    )
    db.add(db_verification)
    db.commit()
    db.refresh(db_verification)
    return db_verification


def get_verification(db: Session, verification_id: str) -> Optional[models.VerificationRecord]:
    """Get verification by ID"""
    return db.query(models.VerificationRecord).filter(
        models.VerificationRecord.verification_id == verification_id
    ).first()


def get_verifications_by_property(
    db: Session,
    property_id: str
) -> List[models.VerificationRecord]:
    """Get all verifications for a property"""
    return db.query(models.VerificationRecord).filter(
        models.VerificationRecord.property_id == property_id
    ).all()


def get_latest_verification(
    db: Session,
    property_id: str
) -> Optional[models.VerificationRecord]:
    """Get latest verification for a property"""
    return db.query(models.VerificationRecord).filter(
        models.VerificationRecord.property_id == property_id
    ).order_by(models.VerificationRecord.verified_at.desc()).first()


# ============= Verification Detail CRUD =============

def create_verification_detail(
    db: Session,
    verification_id: str,
    owner_name: str = None,
    survey_number: str = None,
    land_extent: str = None,
    entities_json: Dict = None,
    classification_json: Dict = None,
    loan_detected: bool = False,
    loan_amount: str = None,
    bank_name: str = None,
    legal_case_detected: bool = False,
    case_number: str = None,
    mutation_status: str = None,
    risk_factors: List = None,
    recommendations: List = None,
    ocr_text: str = None,
    translated_text: str = None
) -> models.VerificationDetail:
    """Create verification detail record"""
    db_detail = models.VerificationDetail(
        verification_id=verification_id,
        owner_name=owner_name,
        survey_number=survey_number,
        land_extent=land_extent,
        entities_json=entities_json or {},
        classification_json=classification_json or {},
        loan_detected=loan_detected,
        loan_amount=loan_amount,
        bank_name=bank_name,
        legal_case_detected=legal_case_detected,
        case_number=case_number,
        mutation_status=mutation_status,
        risk_factors=risk_factors or [],
        recommendations=recommendations or [],
        ocr_text=ocr_text,
        translated_text=translated_text
    )
    db.add(db_detail)
    db.commit()
    db.refresh(db_detail)
    return db_detail


def get_verification_detail(
    db: Session,
    verification_id: str
) -> Optional[models.VerificationDetail]:
    """Get verification detail"""
    return db.query(models.VerificationDetail).filter(
        models.VerificationDetail.verification_id == verification_id
    ).first()


# ============= Tamper Check CRUD =============

def create_tamper_check(
    db: Session,
    property_id: str,
    tampered: bool,
    match_status: str,
    current_hash: str = None,
    blockchain_hash: str = None,
    hash_matched: bool = None,
    current_risk_score: int = None,
    blockchain_risk_score: int = None,
    risk_score_changed: bool = None,
    details_json: Dict = None,
    warnings: List = None
) -> models.TamperCheck:
    """Create tamper check record"""
    db_check = models.TamperCheck(
        property_id=property_id,
        tampered=tampered,
        match_status=match_status,
        current_hash=current_hash,
        blockchain_hash=blockchain_hash,
        hash_matched=hash_matched,
        current_risk_score=current_risk_score,
        blockchain_risk_score=blockchain_risk_score,
        risk_score_changed=risk_score_changed,
        details_json=details_json or {},
        warnings=warnings or []
    )
    db.add(db_check)
    db.commit()
    db.refresh(db_check)
    return db_check


def get_tamper_checks(
    db: Session,
    property_id: str,
    skip: int = 0,
    limit: int = 100
) -> List[models.TamperCheck]:
    """Get tamper check history for a property"""
    return db.query(models.TamperCheck).filter(
        models.TamperCheck.property_id == property_id
    ).order_by(models.TamperCheck.check_time.desc()).offset(skip).limit(limit).all()


# ============= Audit Log CRUD =============

def create_audit_log(
    db: Session,
    operation_type: str,
    property_id: str = None,
    user_id: str = None,
    status: str = "SUCCESS",
    message: str = None,
    metadata_json: Dict = None
) -> models.AuditLog:
    """Create audit log entry"""
    db_log = models.AuditLog(
        operation_type=operation_type,
        property_id=property_id,
        user_id=user_id,
        status=status,
        message=message,
        metadata_json=metadata_json or {}
    )
    db.add(db_log)
    db.commit()
    db.refresh(db_log)
    return db_log


def get_audit_logs(
    db: Session,
    property_id: str = None,
    operation_type: str = None,
    skip: int = 0,
    limit: int = 100
) -> List[models.AuditLog]:
    """Get audit logs with optional filters"""
    query = db.query(models.AuditLog)
    
    if property_id:
        query = query.filter(models.AuditLog.property_id == property_id)
    
    if operation_type:
        query = query.filter(models.AuditLog.operation_type == operation_type)
    
    return query.order_by(models.AuditLog.timestamp.desc()).offset(skip).limit(limit).all()


# ============= Statistics =============

def get_statistics(db: Session) -> Dict[str, Any]:
    """Get system statistics"""
    total_properties = db.query(models.Property).count()
    total_verifications = db.query(models.VerificationRecord).count()
    total_tamper_checks = db.query(models.TamperCheck).count()
    
    # Count by risk level
    low_risk = db.query(models.VerificationRecord).filter(
        models.VerificationRecord.risk_level == "Low"
    ).count()
    medium_risk = db.query(models.VerificationRecord).filter(
        models.VerificationRecord.risk_level == "Medium"
    ).count()
    high_risk = db.query(models.VerificationRecord).filter(
        models.VerificationRecord.risk_level == "High"
    ).count()
    
    # Tampered documents
    tampered_count = db.query(models.TamperCheck).filter(
        models.TamperCheck.tampered == True
    ).count()
    
    return {
        "total_properties": total_properties,
        "total_verifications": total_verifications,
        "total_tamper_checks": total_tamper_checks,
        "risk_distribution": {
            "low": low_risk,
            "medium": medium_risk,
            "high": high_risk
        },
        "tampered_documents": tampered_count
    }


# ============= Delete Operations =============

def delete_verification(db: Session, property_id: str) -> bool:
    """Delete verification and all related records for a property"""
    try:
        # Delete in correct order to respect foreign key constraints
        
        # 1. Delete audit logs
        db.query(models.AuditLog).filter(
            models.AuditLog.property_id == property_id
        ).delete(synchronize_session=False)
        
        # 2. Delete tamper checks
        db.query(models.TamperCheck).filter(
            models.TamperCheck.property_id == property_id
        ).delete(synchronize_session=False)
        
        # 3. Get verification IDs for this property
        verification_ids = [v.verification_id for v in db.query(models.VerificationRecord).filter(
            models.VerificationRecord.property_id == property_id
        ).all()]
        
        # 4. Delete verification details
        for ver_id in verification_ids:
            db.query(models.VerificationDetail).filter(
                models.VerificationDetail.verification_id == ver_id
            ).delete(synchronize_session=False)
        
        # 5. Delete verification records
        db.query(models.VerificationRecord).filter(
            models.VerificationRecord.property_id == property_id
        ).delete(synchronize_session=False)
        
        # 6. Delete property
        db.query(models.Property).filter(
            models.Property.property_id == property_id
        ).delete(synchronize_session=False)
        
        db.commit()
        return True
    except Exception as e:
        db.rollback()
        print(f"Error deleting verification: {e}")
        return False
