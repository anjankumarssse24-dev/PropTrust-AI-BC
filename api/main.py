"""
PropTrust - AI-Blockchain Property Document Verification API
Enhanced with blockchain integration and tamper detection
"""

from fastapi import FastAPI, UploadFile, File, HTTPException, Depends, Query
from fastapi.responses import JSONResponse, HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import Dict, Optional
from pydantic import BaseModel
import os
import sys
import json
import uuid
import hashlib
from datetime import datetime
from pathlib import Path
from io import BytesIO

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from ocr.ocr_engine import OCREngine
from preprocessing.clean_text import TextCleaner
from ner.ner_extractor import NERExtractor
from classifier.doc_classifier import DocumentClassifier
from risk.risk_engine import RiskEngine
from utils.file_utils import FileUtils
from blockchain import BlockchainManager, SemanticHasher, TamperDetector, mock_blockchain
from database import get_db, init_db, crud
from translation.translator import TextTranslator
from reports.report_generator import ReportGenerator
from extract_rtc_fields import extract_rtc_fields

app = FastAPI(
    title="PropTrust API",
    description="AI-Blockchain Property Document Verification System",
    version="2.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
frontend_path = Path(__file__).parent.parent / "frontend"
if frontend_path.exists():
    app.mount("/static", StaticFiles(directory=str(frontend_path)), name="static")

# Initialize components
ocr_engine = OCREngine()
text_cleaner = TextCleaner()
ner_extractor = NERExtractor()
classifier = DocumentClassifier()
risk_engine = RiskEngine()
translator = TextTranslator()
report_generator = ReportGenerator()

# Initialize blockchain components (will be configured on first use)
blockchain_manager = None
semantic_hasher = SemanticHasher()
tamper_detector = None

# Initialize database
try:
    init_db()
    print("✅ Database initialized")
except Exception as e:
    print(f"⚠️  Database initialization warning: {e}")


# ============= Pydantic Models =============

class VerificationRequest(BaseModel):
    """Verification request"""
    document_type: str = "RTC"
    store_on_blockchain: bool = True


class TamperCheckRequest(BaseModel):
    """Tamper check request"""
    property_id: str


# ============= Helper Functions =============

def get_blockchain_manager():
    """Get or initialize blockchain manager"""
    global blockchain_manager, tamper_detector
    if blockchain_manager is None:
        try:
            blockchain_manager = BlockchainManager()
            tamper_detector = TamperDetector(blockchain_manager, semantic_hasher)
            print("✅ Blockchain manager initialized")
        except Exception as e:
            print(f"⚠️  Blockchain not available: {e}")
    return blockchain_manager


def generate_property_id() -> str:
    """Generate unique property ID"""
    return f"PRT-{uuid.uuid4().hex[:8].upper()}"


def calculate_file_hash(file_content: bytes) -> str:
    """Calculate SHA256 hash of file content"""
    return hashlib.sha256(file_content).hexdigest()


def save_uploaded_file(file_content: bytes, property_id: str, filename: str) -> str:
    """Save uploaded file and return path"""
    upload_dir = Path("data/raw_docs")
    upload_dir.mkdir(parents=True, exist_ok=True)
    
    file_extension = Path(filename).suffix
    file_path = upload_dir / f"{property_id}{file_extension}"
    
    with open(file_path, "wb") as f:
        f.write(file_content)
    
    return str(file_path)


# ============= API Endpoints =============

@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve landing page"""
    index_file = frontend_path / "index.html"
    if index_file.exists():
        with open(index_file, 'r', encoding='utf-8') as f:
            return f.read()
    return {"status": "active", "service": "PropTrust API", "version": "2.0.0"}


@app.get("/js/main.js")
async def serve_main_js():
    """Serve main.js directly"""
    js_file = frontend_path / "js" / "main.js"
    if js_file.exists():
        return FileResponse(js_file, media_type="application/javascript")
    raise HTTPException(status_code=404, detail="JavaScript file not found")


@app.get("/api/health")
async def health_check():
    """API health check"""
    return {
        "status": "active",
        "service": "PropTrust API",
        "version": "2.0.0",
        "blockchain": "demo_blockchain_active",
        "ai_enabled": True
    }


@app.post("/api/verify/upload")
async def verify_document(
    file: UploadFile = File(...),
    document_type: str = "RTC",
    store_on_blockchain: bool = True,
    db: Session = Depends(get_db)
):
    """
    Complete verification pipeline with blockchain storage
    
    Flow:
    1. Upload document
    2. OCR processing
    3. Text cleaning & translation
    4. NER extraction
    5. Document classification
    6. Risk scoring
    7. Generate semantic hash
    8. Store on blockchain (optional)
    9. Save to database
    10. Return results
    """
    try:
        print("\n" + "="*70)
        print("PROPTRUST VERIFICATION PIPELINE")
        print("="*70)
        
        # Read file content first to calculate hash
        file_content = file.file.read()
        file_hash = calculate_file_hash(file_content)
        print(f"📝 Document Hash: {file_hash[:16]}...")
        
        # Check if document already exists in database
        existing_property = crud.get_property_by_file_hash(db, file_hash)
        
        if existing_property:
            print(f"✅ Document already verified! Using cached result.")
            print(f"🆔 Existing Property ID: {existing_property.property_id}")
            
            # Get existing verification
            existing_verification = crud.get_latest_verification(db, existing_property.property_id)
            
            if existing_verification:
                # Try to get detail, use getattr to avoid AttributeError
                detail = getattr(existing_verification, 'details', None) or getattr(existing_verification, 'detail', None)
                
                if detail:
                    return JSONResponse({
                        "status": "success",
                        "message": "Document already verified (cached result)",
                        "cached": True,
                        "property_id": existing_property.property_id,
                        "verification_id": existing_verification.verification_id,
                        "risk_score": existing_verification.risk_score,
                        "risk_level": existing_verification.risk_level,
                        "verification_date": existing_verification.verified_at.isoformat(),
                        "document_type": existing_property.document_type,
                        "owner_name": detail.owner_name,
                        "survey_number": detail.survey_number,
                        "risk_assessment": {
                            "risk_score": existing_verification.risk_score,
                            "risk_level": existing_verification.risk_level,
                            "risk_factors": detail.risk_factors or [],
                            "recommendations": detail.recommendations or []
                        },
                        "risk_factors": detail.risk_factors or {},
                        "recommendations": detail.recommendations or [],
                        "entities": detail.entities_json or {},
                        "classification": detail.classification_json or {},
                        "rtc_fields": {},  # RTC fields not stored in detail for cached results
                        "ocr_stats": {
                            "pages_processed": 1,
                            "chars_original": 0,
                            "chars_cleaned": 0,
                            "text_preview": None
                        },
                        "blockchain": {
                            "hash": existing_verification.blockchain_hash,
                            "tx_hash": existing_verification.blockchain_tx_hash,
                            "block_number": existing_verification.blockchain_block_number
                        }
                    })
                else:
                    # No detail found, reprocess the document
                    print("⚠️  No detailed data found, reprocessing document...")
            else:
                # No verification found, reprocess
                print("⚠️  No verification record found, processing document...")
        
        # New document - generate property ID
        property_id = generate_property_id()
        print(f"🆔 New Property ID: {property_id}")
        
        # Save file
        file_path = save_uploaded_file(file_content, property_id, file.filename)
        print(f"📁 File saved: {file_path}")
        
        # Step 1: OCR
        print("\n📸 Step 1: OCR Processing...")
        ocr_text = ocr_engine.extract_text(file_path)
        
        # Step 2: Clean text
        print("🧹 Step 2: Text Cleaning...")
        cleaned_text = text_cleaner.clean_text(ocr_text)
        
        # Step 3: Translation (if Kannada)
        print("🌐 Step 3: Translation...")
        translation_result = translator.translate_text(cleaned_text)
        translated_text = translation_result.get('translated_text', cleaned_text)
        
        # Step 4: NER
        print("🔍 Step 4: Entity Extraction...")
        entities = ner_extractor.extract_entities(translated_text)
        
        # Step 4.5: Extract RTC-specific fields
        print("📋 Step 4.5: Extracting RTC Fields...")
        rtc_fields = extract_rtc_fields(translated_text, file.filename)
        
        # CRITICAL FIX: Inject survey numbers from rtc_fields into entities
        # This ensures survey numbers from filename (authoritative source) are used
        if rtc_fields.get('survey_number'):
            survey = rtc_fields['survey_number']
            hissa = rtc_fields.get('hissa_number')
            
            # Override entities with filename-based survey numbers
            entities['survey_numbers'] = [survey]
            if hissa:
                entities['survey_numbers'].append(f"{survey}*{hissa}")
            
            print(f"   [ENTITIES] Survey numbers set from filename: {entities['survey_numbers']}")
        
        # Step 5: Classification
        print("📊 Step 5: Document Classification...")
        classification = classifier.classify_document(translated_text, entities)
        print(f"   Classification type: {type(classification)}")
        print(f"   Classification: {classification}")
        
        # Step 6: Risk Assessment
        print("⚠️  Step 6: Risk Assessment...")
        risk_assessment = risk_engine.calculate_risk_score(entities, classification)
        print(f"   Risk assessment: {risk_assessment}")
        
        # Prepare verification data
        verification_data = {
            "property_id": property_id,
            "document_type": document_type,
            "owner_name": entities.get("persons", [None])[0],
            "survey_number": entities.get("survey_numbers", [None])[0],
            "risk_score": risk_assessment["risk_score"],
            "risk_level": risk_assessment["risk_level"],
            "loan_detected": entities.get("loan_present", False),
            "legal_case_detected": len(entities.get("case_numbers", [])) > 0,
            "mutation_status": "DETECTED" if "mutation" in cleaned_text.lower() else "UNKNOWN",
            "risk_factors": risk_assessment.get("factors", []) if isinstance(risk_assessment.get("factors", []), list) else [],
            "verified_at": datetime.now().isoformat(),
            "entities": entities,
            "classification": classification
        }
        
        blockchain_result = None
        verification_hash = None
        
        # Step 7 & 8: Mock Blockchain storage (Demo mode - stored in SQLite)
        if store_on_blockchain:
            try:
                print("\n🔗 Step 7: Generating Verification Hash...")
                # Use include_timestamp=False for deterministic hash that can be verified later
                verification_hash = semantic_hasher.generate_hash(verification_data, include_timestamp=False)
                print(f"   Hash: {verification_hash[:32]}...")
                
                print("⛓️  Step 8: Storing on Demo Blockchain (SQLite-backed)...")
                blockchain_result = mock_blockchain.store_verification(
                    property_id=property_id,
                    verification_data=verification_data,
                    risk_score=risk_assessment["risk_score"]
                )
                print(f"   ✅ Transaction: {blockchain_result['tx_hash'][:16]}...")
                print(f"   ✅ Block Number: {blockchain_result['block_number']}")
                print(f"   ✅ Status: {blockchain_result['status']}")
            except Exception as e:
                print(f"   ⚠️  Blockchain error: {e}")
        
        # Step 9: Database storage
        print("\n💾 Step 9: Saving to Database...")
        verification_id = f"VER-{uuid.uuid4().hex[:8].upper()}"  # Define before try block
        try:
            # Create property record with file hash
            db_property = crud.create_property(
                db=db,
                property_id=property_id,
                document_type=document_type,
                document_path=file_path,
                owner_name=verification_data["owner_name"],
                survey_number=verification_data["survey_number"],
                file_hash=file_hash  # Add file hash for deduplication
            )
            
            # Create verification record
            db_verification = crud.create_verification(
                db=db,
                verification_id=verification_id,
                property_id=property_id,
                risk_score=risk_assessment["risk_score"],
                risk_level=risk_assessment["risk_level"],
                verification_status="VERIFIED",
                blockchain_hash=verification_hash or "N/A",
                blockchain_tx_hash=blockchain_result["tx_hash"] if blockchain_result else None,
                blockchain_block_number=blockchain_result["block_number"] if blockchain_result else None,
                blockchain_timestamp=blockchain_result["timestamp"] if blockchain_result else None
            )
            
            # Create verification detail
            crud.create_verification_detail(
                db=db,
                verification_id=verification_id,
                owner_name=verification_data["owner_name"],
                survey_number=verification_data["survey_number"],
                entities_json=entities,
                classification_json=classification,
                loan_detected=verification_data["loan_detected"],
                legal_case_detected=verification_data["legal_case_detected"],
                risk_factors=verification_data["risk_factors"],
                recommendations=risk_assessment.get("recommendations", []),
                ocr_text=cleaned_text,
                translated_text=translated_text
            )
            
            # Audit log
            crud.create_audit_log(
                db=db,
                operation_type="VERIFY",
                property_id=property_id,
                status="SUCCESS",
                message="Document verified successfully",
                metadata_json={"blockchain_stored": bool(blockchain_result)}
            )
            
            print("   ✅ Database saved")
        except Exception as e:
            print(f"   ⚠️  Database error: {e}")
        
        # Step 10: Return results
        print("\n✅ VERIFICATION COMPLETE")
        print("="*70 + "\n")
        
        return {
            "success": True,
            "property_id": property_id,
            "verification_id": verification_id,
            "risk_score": risk_assessment["risk_score"],
            "risk_level": risk_assessment["risk_level"],
            "verification_status": "VERIFIED",
            "owner_name": rtc_fields.get('owner_name') or entities.get("owner_names", [None])[0],
            "survey_number": rtc_fields.get('survey_number'),
            "hissa_number": rtc_fields.get('hissa_number'),
            "survey_hissa_combined": rtc_fields.get('survey_hissa_combined'),
            "land_extent": rtc_fields.get('land_extent'),
            "rtc_fields": rtc_fields,
            "entities": entities,
            "classification": classification,
            "risk_assessment": risk_assessment,
            "risk_factors": risk_assessment.get("risk_breakdown", {}),
            "recommendations": risk_assessment.get("recommendations", []),
            "ocr_text": cleaned_text,
            "ocr_text_original": ocr_text,
            "translated_text": translated_text if translated_text != cleaned_text else None,
            "ocr_stats": {
                "pages_processed": 1,
                "chars_original": len(ocr_text),
                "chars_cleaned": len(cleaned_text),
                "text_preview": cleaned_text[:500] if cleaned_text else None
            },
            "blockchain": {
                "stored": bool(blockchain_result),
                "hash": verification_hash[:32] + "..." if verification_hash else None,
                "tx_hash": blockchain_result["tx_hash"] if blockchain_result else None,
                "block_number": blockchain_result["block_number"] if blockchain_result else None
            } if blockchain_result else None,
            "verified_at": datetime.now().isoformat()
        }
    
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/blockchain/store/{property_id}")
async def store_on_blockchain(
    property_id: str,
    db: Session = Depends(get_db)
):
    """
    Store an existing verification on blockchain
    
    This endpoint allows users to store verification results on blockchain
    after reviewing the AI analysis results.
    """
    try:
        print("\n" + "="*70)
        print("BLOCKCHAIN STORAGE REQUEST")
        print("="*70)
        print(f"🆔 Property ID: {property_id}")
        
        # Get blockchain manager
        bc_manager = get_blockchain_manager()
        if not bc_manager or not bc_manager.contract:
            # Use mock blockchain as fallback
            print("⚠️  Using mock blockchain (local SQLite)")
            bc_manager = mock_blockchain
        
        # Get property from database
        db_property = crud.get_property(db, property_id)
        if not db_property:
            raise HTTPException(status_code=404, detail="Property not found")
        
        # Get verification record
        db_verification = db.query(crud.models.VerificationRecord).filter(
            crud.models.VerificationRecord.property_id == property_id
        ).first()
        
        if not db_verification:
            raise HTTPException(status_code=404, detail="Verification record not found")
        
        # Check if already stored
        if db_verification.blockchain_tx_hash:
            return {
                "success": True,
                "already_stored": True,
                "message": "Verification already stored on blockchain",
                "blockchain": {
                    "stored": True,
                    "hash": db_verification.blockchain_hash,
                    "tx_hash": db_verification.blockchain_tx_hash,
                    "block_number": db_verification.blockchain_block_number,
                    "timestamp": db_verification.blockchain_timestamp
                }
            }
        
        # Prepare verification data for blockchain
        verification_data = {
            "property_id": property_id,
            "owner_name": db_property.owner_name,
            "survey_number": db_property.survey_number,
            "risk_score": db_verification.risk_score,
            "risk_level": db_verification.risk_level,
            "verification_status": db_verification.verification_status
        }
        
        # Generate hash
        print("🔗 Generating verification hash...")
        verification_hash = semantic_hasher.generate_hash(verification_data)
        print(f"   Hash: {verification_hash[:32]}...")
        
        # Store on blockchain
        print("⛓️  Storing on blockchain...")
        blockchain_result = bc_manager.store_verification(
            property_id=property_id,
            verification_hash=verification_hash,
            risk_score=db_verification.risk_score,
            metadata={
                "owner": db_property.owner_name,
                "survey_number": db_property.survey_number,
                "risk_level": db_verification.risk_level
            }
        )
        
        print(f"   ✅ Transaction: {blockchain_result['tx_hash'][:16]}...")
        print(f"   ✅ Block Number: {blockchain_result['block_number']}")
        print(f"   ✅ Status: {blockchain_result['status']}")
        
        # Update database with blockchain info
        db_verification.blockchain_hash = verification_hash
        db_verification.blockchain_tx_hash = blockchain_result["tx_hash"]
        db_verification.blockchain_block_number = blockchain_result["block_number"]
        db_verification.blockchain_timestamp = blockchain_result["timestamp"]
        db.commit()
        
        # Audit log
        crud.create_audit_log(
            db=db,
            operation_type="BLOCKCHAIN_STORE",
            property_id=property_id,
            status="SUCCESS",
            message="Verification stored on blockchain",
            metadata_json={"tx_hash": blockchain_result["tx_hash"]}
        )
        
        print("✅ BLOCKCHAIN STORAGE COMPLETE")
        print("="*70 + "\n")
        
        return {
            "success": True,
            "property_id": property_id,
            "message": "Verification successfully stored on blockchain",
            "blockchain": {
                "stored": True,
                "hash": verification_hash,
                "tx_hash": blockchain_result["tx_hash"],
                "block_number": blockchain_result["block_number"],
                "timestamp": blockchain_result["timestamp"]
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        raise HTTPException(status_code=500, detail=f"Error storing on blockchain: {str(e)}")


@app.post("/api/blockchain/check-tamper")
async def check_tamper(
    property_id: str = Query(..., description="Property ID to check"),
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Check if document has been tampered with
    
    Compares current document hash with blockchain record
    """
    try:
        print("\n" + "="*70)
        print("TAMPER DETECTION CHECK")
        print("="*70)
        print(f"🆔 Property ID: {property_id}")
        
        # Get blockchain manager
        bc_manager = get_blockchain_manager()
        if not bc_manager or not bc_manager.contract:
            # Use mock blockchain as fallback
            print("⚠️  Using mock blockchain (local SQLite)")
            bc_manager = mock_blockchain
            
        # Initialize tamper detector with the manager
        tamper_detector_instance = TamperDetector(bc_manager, semantic_hasher)
        
        # Save file temporarily
        file_content = await file.read()
        temp_path = save_uploaded_file(file_content, f"{property_id}_temp", file.filename)
        
        # Process document (same pipeline as verification)
        print("📸 Processing document...")
        ocr_text = ocr_engine.extract_text(temp_path)
        cleaned_text = text_cleaner.clean_text(ocr_text)
        translation_result = translator.translate_text(cleaned_text)
        translated_text = translation_result.get('translated_text', cleaned_text)
        entities = ner_extractor.extract_entities(translated_text)
        classification = classifier.classify_document(translated_text, entities)
        risk_assessment = risk_engine.calculate_risk_score(entities, classification)
        
        # Prepare verification data with safe fallbacks
        risk_factors = risk_assessment.get("factors", [])
        if risk_factors and isinstance(risk_factors, list):
            risk_factors_list = [f.get("description", str(f)) if isinstance(f, dict) else str(f) for f in risk_factors]
        else:
            risk_factors_list = []
        
        current_data = {
            "property_id": property_id,
            "document_type": "RTC",
            "owner_name": entities.get("persons", ["Unknown"])[0] if entities.get("persons") else "Unknown",
            "survey_number": entities.get("survey_numbers", ["Unknown"])[0] if entities.get("survey_numbers") else "Unknown",
            "risk_score": risk_assessment.get("risk_score", 0),
            "risk_level": risk_assessment.get("risk_level", "Unknown"),
            "loan_detected": entities.get("loan_present", False),
            "legal_case_detected": len(entities.get("case_numbers", [])) > 0,
            "mutation_status": "DETECTED" if "mutation" in cleaned_text.lower() else "UNKNOWN",
            "risk_factors": risk_factors_list
        }
        
        # Check for tampering
        print("🔍 Checking for tampering...")
        
        # Get the original verification from database
        property_obj = crud.get_property(db, property_id)
        if not property_obj:
            return {
                "success": False,
                "tamper_check": {
                    "tampered": False,
                    "match_status": "NOT_FOUND",
                    "message": "Property not found in database. Please verify it first."
                }
            }
        
        # Get blockchain record from database
        verifications = crud.get_verifications_by_property(db, property_id)
        if not verifications or not verifications[0].blockchain_hash:
            return {
                "success": True,
                "property_id": property_id,
                "tamper_check": {
                    "tampered": False,
                    "match_status": "NOT_STORED",
                    "message": "Document was verified but not stored on blockchain yet."
                },
                "report": "⚠️ Property verified but not yet anchored on blockchain."
            }
        
        original_verification = verifications[0]
        detail = crud.get_verification_detail(db, original_verification.verification_id)
        
        # Generate hash for current document (exclude timestamp for comparison)
        current_hash = semantic_hasher.generate_hash(current_data, include_timestamp=False)
        blockchain_hash = original_verification.blockchain_hash
        
        # Compare hashes
        hash_matched = current_hash == blockchain_hash
        risk_score_changed = abs(current_data["risk_score"] - original_verification.risk_score) > 5
        
        tamper_results = {
            "property_id": property_id,
            "tampered": not hash_matched or risk_score_changed,
            "match_status": "VERIFIED" if hash_matched and not risk_score_changed else "TAMPERED",
            "current_hash": current_hash[:32] + "...",
            "blockchain_hash": blockchain_hash[:32] + "..." if blockchain_hash else None,
            "hash_matched": hash_matched,
            "current_risk_score": current_data["risk_score"],
            "blockchain_risk_score": original_verification.risk_score,
            "risk_score_changed": risk_score_changed,
            "checked_at": datetime.now().isoformat(),
            "warnings": [],
            "details": {
                "owner_name_match": current_data["owner_name"] == (detail.owner_name if detail else None),
                "survey_number_match": current_data["survey_number"] == (detail.survey_number if detail else None),
                "original_verified_at": original_verification.verified_at.isoformat() if original_verification.verified_at else None,
                "blockchain_tx": original_verification.blockchain_tx_hash
            }
        }
        
        if not hash_matched:
            tamper_results["warnings"].append("⚠️ Document hash does not match blockchain record")
        if risk_score_changed:
            tamper_results["warnings"].append(f"⚠️ Risk score changed from {original_verification.risk_score} to {current_data['risk_score']}")
        
        # Save tamper check to database
        try:
            crud.create_tamper_check(
                db=db,
                property_id=property_id,
                tampered=tamper_results["tampered"],
                match_status=tamper_results["match_status"],
                current_hash=tamper_results.get("current_hash"),
                blockchain_hash=tamper_results.get("blockchain_hash"),
                hash_matched=tamper_results.get("hash_matched"),
                current_risk_score=tamper_results.get("current_risk_score"),
                blockchain_risk_score=tamper_results.get("blockchain_risk_score"),
                risk_score_changed=tamper_results.get("risk_score_changed"),
                details_json=tamper_results.get("details", {}),
                warnings=tamper_results.get("warnings", [])
            )
            
            # Audit log
            crud.create_audit_log(
                db=db,
                operation_type="TAMPER_CHECK",
                property_id=property_id,
                status="SUCCESS" if not tamper_results["tampered"] else "TAMPERED",
                message=f"Tamper check: {tamper_results['match_status']}"
            )
        except Exception as e:
            print(f"   ⚠️  Database error: {e}")
        
        # Generate report
        if tamper_results["match_status"] == "VERIFIED":
            report = f"✅ Document VERIFIED - No tampering detected\n"
            report += f"Hash Match: ✓\nRisk Score: {tamper_results['current_risk_score']}\n"
        elif tamper_results["match_status"] == "TAMPERED":
            report = f"❌ TAMPERING DETECTED\n"
            report += "\n".join(tamper_results["warnings"])
        else:
            report = f"⚠️ Status: {tamper_results['match_status']}\n"
        
        print("\n" + report)
        
        # Clean up temp file
        Path(temp_path).unlink(missing_ok=True)
        
        return {
            "success": True,
            "property_id": property_id,
            "tamper_check": tamper_results,
            "report": report
        }
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/verification/{verification_id}")
async def get_verification(verification_id: str, db: Session = Depends(get_db)):
    """Get verification record by ID"""
    verification = crud.get_verification(db, verification_id)
    if not verification:
        raise HTTPException(status_code=404, detail="Verification not found")
    
    detail = crud.get_verification_detail(db, verification_id)
    
    return {
        "verification_id": verification.verification_id,
        "property_id": verification.property_id,
        "risk_score": verification.risk_score,
        "risk_level": verification.risk_level,
        "verification_status": verification.verification_status,
        "blockchain": {
            "hash": verification.blockchain_hash,
            "tx_hash": verification.blockchain_tx_hash,
            "block_number": verification.blockchain_block_number
        },
        "verified_at": verification.verified_at.isoformat(),
        "details": {
            "owner_name": detail.owner_name if detail else None,
            "survey_number": detail.survey_number if detail else None,
            "loan_detected": detail.loan_detected if detail else None,
            "legal_case_detected": detail.legal_case_detected if detail else None,
            "risk_factors": detail.risk_factors if detail else [],
            "recommendations": detail.recommendations if detail else []
        } if detail else None
    }


@app.get("/api/property/{property_id}")
async def get_property_info(property_id: str, db: Session = Depends(get_db)):
    """Get property information"""
    property_obj = crud.get_property(db, property_id)
    if not property_obj:
        raise HTTPException(status_code=404, detail="Property not found")
    
    verifications = crud.get_verifications_by_property(db, property_id)
    
    return {
        "property_id": property_obj.property_id,
        "document_type": property_obj.document_type,
        "owner_name": property_obj.owner_name,
        "survey_number": property_obj.survey_number,
        "uploaded_at": property_obj.uploaded_at.isoformat(),
        "verification_count": len(verifications),
        "latest_verification": verifications[0].verification_id if verifications else None
    }


@app.delete("/api/verification/{property_id}")
async def delete_verification(property_id: str, db: Session = Depends(get_db)):
    """Delete verification and all related records"""
    property_obj = crud.get_property(db, property_id)
    if not property_obj:
        raise HTTPException(status_code=404, detail="Verification not found")
    
    success = crud.delete_verification(db, property_id)
    
    if success:
        # Log deletion
        crud.create_audit_log(
            db=db,
            operation_type="DELETE",
            property_id=property_id,
            status="SUCCESS",
            message=f"Verification {property_id} deleted",
            metadata_json={"deleted_at": datetime.now().isoformat()}
        )
        
        return {
            "success": True,
            "message": f"Verification {property_id} deleted successfully",
            "property_id": property_id
        }
    else:
        raise HTTPException(status_code=500, detail="Failed to delete verification")


@app.get("/api/blockchain/status")
async def blockchain_status():
    """Get blockchain connection status (Mock Demo Blockchain)"""
    try:
        status = mock_blockchain.get_connection_status()
        return {
            "connected": status["connected"],
            "network": status["network"],
            "chain_id": status["chain_id"],
            "current_block": status["current_block"],
            "type": status["type"],
            "status": status["status"],
            "message": "Demo blockchain active (SQLite-backed)"
        }
    except Exception as e:
        return {
            "connected": False,
            "error": str(e),
            "message": "Blockchain service unavailable"
        }


@app.get("/api/statistics")
async def get_statistics(db: Session = Depends(get_db)):
    """Get system statistics"""
    try:
        stats = crud.get_statistics(db)
        return {
            "success": True,
            "statistics": stats
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/audit-logs")
async def get_audit_logs(
    property_id: Optional[str] = None,
    operation_type: Optional[str] = None,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get audit logs"""
    logs = crud.get_audit_logs(db, property_id, operation_type, limit=limit)
    return {
        "success": True,
        "count": len(logs),
        "logs": [
            {
                "id": log.id,
                "timestamp": log.timestamp.isoformat(),
                "operation_type": log.operation_type,
                "property_id": log.property_id,
                "status": log.status,
                "message": log.message
            }
            for log in logs
        ]
    }


@app.post("/ocr/extract")
async def extract_text(file: UploadFile = File(...)) -> Dict:
    """Extract text from document using OCR"""
    try:
        temp_path = save_uploaded_file(file, f"temp_{uuid.uuid4().hex[:8]}")
        ocr_text = ocr_engine.extract_text(temp_path)
        Path(temp_path).unlink(missing_ok=True)
        return {"success": True, "text": ocr_text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/ner/extract")
async def extract_entities(text: str) -> Dict:
    """Extract entities from text"""
    try:
        entities = ner_extractor.extract_entities(text)
        return {"success": True, "entities": entities}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/classify")
async def classify_document_endpoint(text: str) -> Dict:
    """Classify document"""
    try:
        classification = classifier.classify_document(text)
        return {"success": True, "classification": classification}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
