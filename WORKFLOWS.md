# 🏠 PROPTRUST - SYSTEM WORKFLOWS

## 📊 Complete System Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│                         USER INTERFACE                            │
│                    (Web Browser - Bootstrap 5)                    │
│                                                                   │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐                │
│  │   Upload   │  │  Results   │  │   Tamper   │                │
│  │  Document  │  │  Display   │  │   Check    │                │
│  └────────────┘  └────────────┘  └────────────┘                │
└───────────────────────────┬──────────────────────────────────────┘
                            │ HTTP/REST API
                            ▼
┌──────────────────────────────────────────────────────────────────┐
│                       FASTAPI BACKEND                             │
│                                                                   │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │              API ENDPOINTS                                  │ │
│  │  /verify/upload  │  /check-tamper  │  /statistics          │ │
│  └────────────────────────────────────────────────────────────┘ │
│                            │                                      │
│  ┌─────────────────────────┼─────────────────────────────────┐  │
│  │              VERIFICATION PIPELINE                          │  │
│  │  ┌──────┐  ┌──────┐  ┌──────┐  ┌──────┐  ┌──────┐        │  │
│  │  │ OCR  │→ │Clean │→ │ NER  │→ │Class │→ │ Risk │        │  │
│  │  └──────┘  └──────┘  └──────┘  └──────┘  └──────┘        │  │
│  └─────────────────────────────────────────────────────────────┘ │
└───────────────┬───────────────────────────────┬──────────────────┘
                │                               │
                ▼                               ▼
┌──────────────────────────────┐   ┌──────────────────────────────┐
│   BLOCKCHAIN LAYER           │   │     DATABASE LAYER           │
│                              │   │                              │
│  ┌────────────────────────┐ │   │  ┌────────────────────────┐ │
│  │  Semantic Hasher       │ │   │  │  SQLAlchemy ORM        │ │
│  │  (SHA-256)             │ │   │  │  Properties Table      │ │
│  └────────────────────────┘ │   │  │  Verifications Table   │ │
│              ▼               │   │  │  Tamper Checks Table   │ │
│  ┌────────────────────────┐ │   │  │  Audit Logs Table      │ │
│  │  Blockchain Manager    │ │   │  └────────────────────────┘ │
│  │  (Web3.py)             │ │   │                              │
│  └────────────────────────┘ │   │  SQLite / PostgreSQL         │
│              ▼               │   └──────────────────────────────┘
│  ┌────────────────────────┐ │
│  │  Smart Contract        │ │
│  │  (Solidity)            │ │
│  │  PropertyVerification  │ │
│  └────────────────────────┘ │
│              ▼               │
│  ┌────────────────────────┐ │
│  │  Ethereum Blockchain   │ │
│  │  (Ganache)             │ │
│  └────────────────────────┘ │
└──────────────────────────────┘
```

---

## 🔄 WORKFLOW 1: Document Verification

```
START: User Uploads Document
    │
    ▼
┌───────────────────────────────┐
│  1. FILE VALIDATION           │
│  - Check format (JPG/PNG/PDF) │
│  - Check size (< 10MB)        │
│  - Save to data/raw_docs/     │
└───────────┬───────────────────┘
            │
            ▼
┌───────────────────────────────┐
│  2. OCR PROCESSING            │
│  - Tesseract + EasyOCR        │
│  - Extract text from image    │
│  - Support Kannada + English  │
│  Output: Raw OCR text         │
└───────────┬───────────────────┘
            │
            ▼
┌───────────────────────────────┐
│  3. TEXT CLEANING             │
│  - Remove noise & stamps      │
│  - Normalize whitespace       │
│  - Fix OCR errors             │
│  Output: Cleaned text         │
└───────────┬───────────────────┘
            │
            ▼
┌───────────────────────────────┐
│  4. TRANSLATION               │
│  - Detect language            │
│  - Kannada → English          │
│  - Preserve structure         │
│  Output: English text         │
└───────────┬───────────────────┘
            │
            ▼
┌───────────────────────────────┐
│  5. ENTITY EXTRACTION (NER)   │
│  - Extract owner names        │
│  - Extract survey numbers     │
│  - Extract loan details       │
│  - Extract case numbers       │
│  - Extract dates              │
│  Output: Structured entities  │
└───────────┬───────────────────┘
            │
            ▼
┌───────────────────────────────┐
│  6. DOCUMENT CLASSIFICATION   │
│  - Classify document type     │
│  - Identify clear title       │
│  - Detect loans/cases         │
│  Output: Classification       │
└───────────┬───────────────────┘
            │
            ▼
┌───────────────────────────────┐
│  7. RISK ASSESSMENT           │
│  - Calculate risk score       │
│  - Identify risk factors      │
│  - Generate recommendations   │
│  Output: Risk score (0-100)   │
└───────────┬───────────────────┘
            │
            ▼
┌───────────────────────────────┐
│  8. SEMANTIC HASHING          │
│  - Normalize verification data│
│  - Include: owner, survey,    │
│    risk score, timestamp      │
│  - Generate SHA-256 hash      │
│  Output: 32-byte hash         │
└───────────┬───────────────────┘
            │
            ▼
┌───────────────────────────────┐
│  9. BLOCKCHAIN STORAGE        │
│  - Connect to Ganache         │
│  - Call storeVerification()   │
│  - Store hash + risk + time   │
│  - Wait for transaction       │
│  Output: TX hash + block #    │
└───────────┬───────────────────┘
            │
            ▼
┌───────────────────────────────┐
│  10. DATABASE STORAGE         │
│  - Create property record     │
│  - Create verification record │
│  - Store extracted entities   │
│  - Link blockchain TX         │
│  - Create audit log           │
└───────────┬───────────────────┘
            │
            ▼
┌───────────────────────────────┐
│  11. DISPLAY RESULTS          │
│  - Show risk score & level    │
│  - Show extracted entities    │
│  - Show risk factors          │
│  - Show blockchain proof      │
│  - Show recommendations       │
└───────────────────────────────┘
            │
            ▼
          END
```

---

## 🔍 WORKFLOW 2: Tamper Detection

```
START: User Re-uploads Document for Verification
    │
    ▼
┌───────────────────────────────┐
│  1. PROPERTY ID INPUT         │
│  - User enters property ID    │
│  - System validates existence │
└───────────┬───────────────────┘
            │
            ▼
┌───────────────────────────────┐
│  2. FETCH BLOCKCHAIN RECORD   │
│  - Query smart contract       │
│  - Get stored hash            │
│  - Get risk score             │
│  - Get timestamp              │
└───────────┬───────────────────┘
            │
            ▼
┌───────────────────────────────┐
│  3. PROCESS CURRENT DOCUMENT  │
│  - Run full verification      │
│  - Extract entities           │
│  - Calculate risk             │
│  - Generate new hash          │
│  (Same as Workflow 1, steps   │
│   2-7, without timestamp)     │
└───────────┬───────────────────┘
            │
            ▼
┌───────────────────────────────┐
│  4. HASH COMPARISON           │
│  - Current hash               │
│  - Blockchain hash            │
│  - Compare byte-by-byte       │
└───────────┬───────────────────┘
            │
    ┌───────┴───────┐
    │               │
    ▼               ▼
┌────────┐      ┌────────┐
│ MATCH  │      │MISMATCH│
└───┬────┘      └───┬────┘
    │               │
    ▼               ▼
┌───────────────────────────────┐
│  5. RISK SCORE COMPARISON     │
│  - Current risk score         │
│  - Blockchain risk score      │
│  - Calculate difference       │
└───────────┬───────────────────┘
            │
            ▼
┌───────────────────────────────┐
│  6. GENERATE TAMPER REPORT    │
│  - Verification status        │
│  - Hash match result          │
│  - Risk score changes         │
│  - Detailed comparison        │
│  - Warnings (if any)          │
└───────────┬───────────────────┘
            │
            ▼
┌───────────────────────────────┐
│  7. DATABASE STORAGE          │
│  - Create tamper check record │
│  - Store comparison results   │
│  - Create audit log           │
└───────────┬───────────────────┘
            │
            ▼
┌───────────────────────────────┐
│  8. DISPLAY RESULTS           │
│  - ✅ VERIFIED (if matched)    │
│  - ❌ TAMPERED (if mismatch)   │
│  - Show hash comparison       │
│  - Show risk comparison       │
│  - Show warnings              │
└───────────────────────────────┘
            │
            ▼
          END
```

---

## 🔐 WORKFLOW 3: Smart Contract Interaction

```
┌─────────────────────────────────────────┐
│  BLOCKCHAIN MANAGER                     │
└─────────────────────────────────────────┘
                │
                ▼
┌─────────────────────────────────────────┐
│  1. CONNECT TO GANACHE                  │
│  - URL: http://127.0.0.1:8545           │
│  - Protocol: HTTP Provider              │
│  - Add PoA middleware                   │
└─────────────────┬───────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────┐
│  2. LOAD SMART CONTRACT                 │
│  - Load ABI from file                   │
│  - Get contract address from .env       │
│  - Create contract instance             │
└─────────────────┬───────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────┐
│  3. GET DEFAULT ACCOUNT                 │
│  - Select first account                 │
│  - Check ETH balance                    │
│  - Verify gas availability              │
└─────────────────┬───────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────┐
│  4. PREPARE TRANSACTION                 │
│  - Function: storeVerification()        │
│  - Args: property_id, hash, risk_score  │
│  - From: default_account                │
└─────────────────┬───────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────┐
│  5. SEND TRANSACTION                    │
│  - Estimate gas                         │
│  - Sign transaction                     │
│  - Broadcast to network                 │
│  Output: Transaction hash               │
└─────────────────┬───────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────┐
│  6. WAIT FOR CONFIRMATION               │
│  - Poll for receipt                     │
│  - Check transaction status             │
│  - Get block number                     │
└─────────────────┬───────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────┐
│  7. PARSE RECEIPT                       │
│  - Contract address: 0x1234...          │
│  - Transaction hash: 0xabcd...          │
│  - Block number: 42                     │
│  - Gas used: 150,000                    │
│  - Status: Success (1) / Failed (0)     │
└─────────────────┬───────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────┐
│  8. RETURN RESULT                       │
│  - tx_hash                              │
│  - block_number                         │
│  - gas_used                             │
│  - status                               │
│  - property_id                          │
│  - contract_address                     │
└─────────────────────────────────────────┘
```

---

## 💾 WORKFLOW 4: Database Operations

```
┌─────────────────────────────────────────┐
│  DATABASE LAYER (SQLAlchemy)            │
└─────────────────────────────────────────┘
                │
    ┌───────────┴───────────┐
    │                       │
    ▼                       ▼
┌─────────┐           ┌─────────┐
│ WRITE   │           │  READ   │
└────┬────┘           └────┬────┘
     │                     │
     ▼                     ▼
┌──────────────────┐  ┌──────────────────┐
│ CREATE PROPERTY  │  │ GET PROPERTY     │
│ - property_id    │  │ - Query by ID    │
│ - doc_type       │  │ - Load relations │
│ - owner_name     │  │ - Return object  │
│ - survey_number  │  │                  │
└────┬─────────────┘  └──────────────────┘
     │
     ▼
┌──────────────────┐  ┌──────────────────┐
│ CREATE           │  │ GET VERIFICATION │
│ VERIFICATION     │  │ - Query by ID    │
│ - verification_id│  │ - Include details│
│ - property_id    │  │ - Load relations │
│ - risk_score     │  │                  │
│ - blockchain_tx  │  │                  │
└────┬─────────────┘  └──────────────────┘
     │
     ▼
┌──────────────────┐  ┌──────────────────┐
│ CREATE           │  │ GET TAMPER       │
│ VERIFICATION     │  │ CHECKS           │
│ DETAIL           │  │ - Query by       │
│ - entities_json  │  │   property_id    │
│ - risk_factors   │  │ - Order by date  │
│ - recommendations│  │ - Paginate       │
└────┬─────────────┘  └──────────────────┘
     │
     ▼
┌──────────────────┐  ┌──────────────────┐
│ CREATE TAMPER    │  │ GET STATISTICS   │
│ CHECK            │  │ - Count total    │
│ - property_id    │  │ - Group by risk  │
│ - tampered       │  │ - Aggregate data │
│ - hash_matched   │  │                  │
└────┬─────────────┘  └──────────────────┘
     │
     ▼
┌──────────────────┐  ┌──────────────────┐
│ CREATE AUDIT LOG │  │ GET AUDIT LOGS   │
│ - operation_type │  │ - Filter by type │
│ - property_id    │  │ - Filter by date │
│ - status         │  │ - Paginate       │
│ - message        │  │                  │
└──────────────────┘  └──────────────────┘
```

---

## 📊 DATA FLOW DIAGRAM

```
                    ┌──────────┐
                    │   USER   │
                    └────┬─────┘
                         │ uploads document
                         ▼
            ┌────────────────────────┐
            │   FRONTEND (Browser)   │
            │  - index.html          │
            │  - main.js             │
            │  - styles.css          │
            └────────┬───────────────┘
                     │ HTTP POST
                     ▼
            ┌────────────────────────┐
            │   FASTAPI BACKEND      │
            │  - main.py             │
            │  - Routes              │
            └────────┬───────────────┘
                     │
        ┌────────────┼────────────┐
        │            │            │
        ▼            ▼            ▼
┌───────────┐  ┌──────────┐  ┌──────────┐
│    OCR    │  │   NER    │  │   RISK   │
│  ENGINE   │  │EXTRACTOR │  │  ENGINE  │
└─────┬─────┘  └────┬─────┘  └────┬─────┘
      │             │              │
      └─────────────┴──────────────┘
                    │ verification data
        ┌───────────┴───────────┐
        │                       │
        ▼                       ▼
┌────────────────┐      ┌────────────────┐
│   BLOCKCHAIN   │      │    DATABASE    │
│   - Hasher     │      │    - CRUD      │
│   - Manager    │      │    - Models    │
│   - Smart      │      │    - SQLite    │
│     Contract   │      │                │
└────────┬───────┘      └────────┬───────┘
         │                       │
         │ stores hash           │ stores details
         │                       │
         ▼                       ▼
┌────────────────┐      ┌────────────────┐
│   ETHEREUM     │      │   DATABASE     │
│   (Ganache)    │      │   FILE         │
│   Block #42    │      │   proptrust.db │
│   TX: 0x1234..│       │                │
└────────────────┘      └────────────────┘
```

---

## 🎯 KEY INTEGRATION POINTS

### 1. Frontend ↔ Backend
- **Protocol**: HTTP REST API
- **Format**: JSON + multipart/form-data
- **Authentication**: None (can add JWT)
- **CORS**: Enabled for all origins

### 2. Backend ↔ Blockchain
- **Library**: Web3.py
- **Connection**: HTTP Provider (Ganache)
- **Gas**: Automatic estimation
- **Signing**: From default account

### 3. Backend ↔ Database
- **ORM**: SQLAlchemy
- **Driver**: SQLite3 / psycopg2
- **Sessions**: Context managers
- **Migrations**: Alembic (optional)

### 4. AI Components Integration
- **OCR**: Tesseract/EasyOCR → Python
- **NER**: spaCy models → Python
- **Classification**: BERT → PyTorch
- **Risk**: Rule-based Python logic

---

**System fully integrated and operational! ✅**
