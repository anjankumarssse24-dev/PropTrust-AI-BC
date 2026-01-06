# 🏠 PropTrust - AI-Blockchain Property Document Verification System

> **Secure, Transparent, and Tamper-Proof Property Verification**

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104-green.svg)](https://fastapi.tiangolo.com/)
[![Ethereum](https://img.shields.io/badge/Ethereum-Ganache-purple.svg)](https://trufflesuite.com/ganache/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 📖 Overview

**PropTrust** is a revolutionary property document verification system that combines:
- **🤖 Artificial Intelligence**: Automated OCR, NLP, and risk assessment
- **⛓️ Blockchain Technology**: Immutable verification records and tamper detection
- **🔍 Transparency**: Clear, explainable verification process
- **🛡️ Security**: Cryptographic hashing and decentralized storage

### Key Features

✅ **AI-Powered Verification**
- Multilingual OCR (Kannada + English)
- Automatic entity extraction (Owner, Survey No, Loans, Cases)
- Document classification
- Explainable risk scoring (0-100)

✅ **Blockchain Integration**
- Immutable hash storage on Ethereum
- Tamper detection by hash comparison
- Complete audit trail
- Private blockchain deployment

✅ **Comprehensive Analysis**
- Loan/Encumbrance detection
- Legal case identification
- Mutation status verification
- Cross-document validation (RTC vs MR)

✅ **Modern Web Interface**
- Intuitive document upload
- Real-time verification status
- Interactive risk visualization
- Blockchain proof display

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    USER UPLOADS DOCUMENT                     │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│              AI VERIFICATION PIPELINE                        │
│  OCR → Clean → Translate → NER → Classify → Risk Score     │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│           SEMANTIC HASH GENERATION (SHA-256)                 │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│         BLOCKCHAIN STORAGE (Smart Contract)                  │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│              DISPLAY RESULTS + BLOCKCHAIN PROOF              │
└─────────────────────────────────────────────────────────────┘
```

---

## 🛠️ Technology Stack

| Component | Technology |
|-----------|-----------|
| **Backend** | Python 3.8+, FastAPI |
| **AI/ML** | spaCy, Tesseract OCR, EasyOCR, BERT |
| **Blockchain** | Ethereum (Ganache), Solidity, Web3.py |
| **Database** | SQLite / PostgreSQL, SQLAlchemy |
| **Frontend** | HTML5, CSS3, JavaScript, Bootstrap 5 |
| **Security** | SHA-256, Cryptographic Hashing |

---

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Node.js 14+ (for Ganache)
- Tesseract OCR

### Installation (5 minutes)

```bash
# 1. Clone repository
git clone <repository-url>
cd property-doc-verification

# 2. Install Python dependencies
pip install -r requirements.txt
python -m spacy download en_core_web_sm

# 3. Install Ganache (blockchain)
npm install -g ganache

# 4. Start Ganache
ganache --port 8545 --networkId 5777

# 5. Deploy Smart Contract (in new terminal)
cd blockchain
python deploy_contract.py

# 6. Initialize Database
python -c "from src.database import init_db; init_db()"

# 7. Start API Server
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

### Access the System
- **Web UI**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Ganache**: http://127.0.0.1:8545

---

## 📊 Project Structure

```
property-doc-verification/
│
├── blockchain/                 # Smart contracts & deployment
│   ├── contracts/
│   │   └── PropertyVerification.sol
│   ├── build/                 # Compiled contracts
│   └── deploy_contract.py
│
├── src/
│   ├── blockchain/            # 🆕 Blockchain integration
│   │   ├── blockchain_manager.py
│   │   ├── semantic_hasher.py
│   │   └── tamper_detector.py
│   │
│   ├── database/              # 🆕 Database models & CRUD
│   │   ├── models.py
│   │   ├── database.py
│   │   └── crud.py
│   │
│   ├── ocr/                   # OCR engine
│   ├── preprocessing/         # Text cleaning
│   ├── translation/           # Kannada → English
│   ├── ner/                   # Entity extraction
│   ├── classifier/            # Document classification
│   ├── risk/                  # Risk scoring
│   ├── verification/          # Cross-document verification
│   └── reports/               # Report generation
│
├── frontend/                  # 🆕 Web UI
│   ├── index.html
│   ├── css/styles.css
│   └── js/main.js
│
├── api/
│   └── main.py               # 🆕 Enhanced FastAPI with blockchain
│
├── data/
│   ├── raw_docs/             # Uploaded documents
│   ├── images/               # Test images
│   ├── ocr_text/             # OCR outputs
│   └── reports/              # Generated reports
│
├── requirements.txt          # 🆕 Updated with blockchain deps
├── SETUP_GUIDE.md           # 🆕 Detailed setup instructions
├── QUICKSTART.md            # 🆕 Fast setup guide
├── PROPTRUST_ENHANCEMENT_PLAN.md  # 🆕 Architecture & roadmap
└── README.md                # This file
```

---

## 🎯 Usage Examples

### 1. Verify Property Document

**Via Web UI:**
1. Open http://localhost:8000
2. Select document type (RTC/MR/EC)
3. Upload document image/PDF
4. Click "Verify Document"
5. View AI results + Blockchain proof

**Via API:**
```bash
curl -X POST "http://localhost:8000/api/verify/upload" \
  -F "file=@document.jpg" \
  -F "document_type=RTC" \
  -F "store_on_blockchain=true"
```

### 2. Check for Tampering

```bash
curl -X POST "http://localhost:8000/api/blockchain/check-tamper?property_id=PRT-XXXXXXXX" \
  -F "file=@document.jpg"
```

### 3. Get Verification Record

```bash
curl "http://localhost:8000/api/verification/VER-XXXXXXXX"
```

---

## 🔍 How It Works

### AI Verification Process

1. **OCR Processing**: Extract text from scanned documents
2. **Text Cleaning**: Remove noise, normalize text
3. **Translation**: Convert Kannada to English
4. **Entity Extraction**: Identify owner, survey number, loans, cases
5. **Classification**: Categorize document type and status
6. **Risk Scoring**: Calculate risk (0-100) based on factors:
   - Loan detected: 30 points
   - Mutation issues: 25 points
   - Owner mismatch: 25 points
   - Outdated records: 10 points
   - Legal cases: 10 points

### Blockchain Storage

1. **Normalize Data**: Extract key fields (owner, survey, risk)
2. **Generate Hash**: SHA-256 of normalized data
3. **Store on Chain**: Call smart contract `storeVerification()`
4. **Return Proof**: Transaction hash + block number

### Tamper Detection

1. **Re-verify Document**: Process same document again
2. **Generate New Hash**: Without timestamp (for comparison)
3. **Fetch Blockchain Hash**: Query smart contract
4. **Compare Hashes**: Match = Authentic, Mismatch = Tampered
5. **Display Result**: Clear tamper status

---

## 📈 System Statistics

Get real-time statistics:
```bash
curl "http://localhost:8000/api/statistics"
```

Response:
```json
{
  "total_properties": 25,
  "total_verifications": 30,
  "risk_distribution": {
    "low": 10,
    "medium": 15,
    "high": 5
  },
  "tampered_documents": 2
}
```

---

## 🔒 Security Features

- ✅ **Immutable Storage**: Blockchain prevents data modification
- ✅ **Cryptographic Hashing**: SHA-256 ensures data integrity
- ✅ **Private Network**: Local/private Ethereum (not public)
- ✅ **No PII on Chain**: Only hashes stored, not documents
- ✅ **Audit Trail**: Complete verification history
- ✅ **Tamper Detection**: Automatic hash comparison

---

## 🧪 Testing

### Run Unit Tests
```bash
pytest tests/
```

### Test Individual Components

**Blockchain Connection:**
```python
from src.blockchain import BlockchainManager
manager = BlockchainManager()
print(f"Connected: {manager.w3.is_connected()}")
```

**Hash Generation:**
```python
from src.blockchain import SemanticHasher
hasher = SemanticHasher()
data = {"property_id": "TEST-001", "risk_score": 45}
hash_result = hasher.generate_hash(data)
print(f"Hash: {hash_result}")
```

**Tamper Detection:**
```python
from src.blockchain import TamperDetector
detector = TamperDetector()
result = detector.check_tamper("PRT-001", verification_data)
print(f"Tampered: {result['tampered']}")
```

---

## 📚 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Landing page |
| `/api/health` | GET | Health check |
| `/api/verify/upload` | POST | Upload & verify document |
| `/api/blockchain/check-tamper` | POST | Check for tampering |
| `/api/verification/{id}` | GET | Get verification record |
| `/api/property/{id}` | GET | Get property info |
| `/api/blockchain/status` | GET | Blockchain status |
| `/api/statistics` | GET | System statistics |
| `/docs` | GET | Interactive API docs |

Full API documentation: http://localhost:8000/docs

---

## 🎓 Research Contributions

1. **Semantic Hashing for Land Documents**
   - Novel approach to property document verification
   - Deterministic hash generation from structured data

2. **AI-Guided Blockchain Anchoring**
   - Combining AI intelligence with blockchain immutability
   - Explainable and auditable verification

3. **Domain-Specific Framework**
   - Tailored for Indian property documents (RTC, MR, EC)
   - Multilingual support (Kannada + English)

4. **Explainable Tamper Detection**
   - Transparent verification process
   - Clear indication of modifications

---

## 🌟 Future Enhancements

- [ ] Multi-user authentication system
- [ ] Mobile app (React Native)
- [ ] Advanced ML models (IndicBERT fine-tuning)
- [ ] Real-time notifications
- [ ] Integration with government databases
- [ ] PDF report generation
- [ ] Analytics dashboard
- [ ] Support for more document types (Form 15, Sale Deeds)
- [ ] Deployment on public testnet (Sepolia/Goerli)

---

## 📝 Documentation

- **Quick Start**: [QUICKSTART.md](QUICKSTART.md)
- **Setup Guide**: [SETUP_GUIDE.md](SETUP_GUIDE.md)
- **Enhancement Plan**: [PROPTRUST_ENHANCEMENT_PLAN.md](PROPTRUST_ENHANCEMENT_PLAN.md)
- **API Documentation**: http://localhost:8000/docs

---

## 🤝 Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License.

---

## 🆘 Support

For issues or questions:
- **GitHub Issues**: [Create an issue](https://github.com/your-repo/issues)
- **Email**: support@proptrust.com
- **Documentation**: See `SETUP_GUIDE.md`

---

## 👥 Authors

- **Development Team**: Property Verification Research Group
- **Blockchain Integration**: PropTrust Team
- **AI/ML Models**: Research & Development

---

## 🏆 Acknowledgments

- spaCy for NLP capabilities
- Tesseract OCR for text extraction
- Ethereum Foundation for blockchain technology
- FastAPI for modern API framework
- Bootstrap for UI components

---

## 📊 Project Status

🟢 **Active Development** - Version 2.0

- ✅ AI Verification Pipeline (Complete)
- ✅ Blockchain Integration (Complete)
- ✅ Tamper Detection (Complete)
- ✅ Web Frontend (Complete)
- ✅ Database Layer (Complete)
- ✅ API Endpoints (Complete)
- 🔄 Testing & Documentation (In Progress)
- 🔄 Deployment (In Progress)

---

**Built with ❤️ for transparent and secure property verification**

🏠 **PropTrust** - Making Property Verification Trustworthy
