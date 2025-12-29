# Property Document Verification System

AI-powered property document verification system for legal title verification, encumbrance detection, cross-document validation, and risk assessment.

## 🎯 Project Overview

This system automates the verification of property documents (RTC, MR, EC, Sale Deeds) using OCR, NLP, and Machine Learning to detect:
- Ownership details
- Encumbrances (loans, mortgages)
- Legal cases
- Mutation status
- **Cross-document verification (RTC vs MR consistency)**
- Risk assessment

## 🏗️ Architecture

```
Document Upload (RTC + MR)
   ↓
OCR & Cleaning (Kannada/English)
   ↓
Translation (Kannada → English)
   ↓
Entity Extraction (NER Model)
   ↓
Document Classification (Transformer)
   ↓
Cross-Document Verification (RTC vs MR)
   ↓
Combined Risk Scoring
   ↓
Comprehensive Verification Report
```

## 🛠️ Technology Stack

| Layer               | Technology                     |
| ------------------- | ------------------------------ |
| Backend API         | FastAPI                        |
| OCR                 | Tesseract + EasyOCR (Kannada + English) |
| Translation         | Google Translate API           |
| Text Cleaning       | Python + Regex                 |
| NER                 | spaCy / IndicNER / Custom BERT |
| Classification      | Fine-tuned BERT / RoBERTa      |
| Cross-Verification  | Custom comparison engine       |
| Risk Scoring        | Python logic                   |
| Storage             | SQLite                         |
| Language            | Python                         |

## 📁 Project Structure

```
property-doc-verification/
│
├── data/
│   ├── raw_docs/          # original JPG/PDF files
│   ├── images/            # extracted images from PDFs
│   ├── ocr_text/          # OCR output text files
│   └── reports/           # generated HTML reports
│
├── src/
│   ├── ocr/               # OCR engine (EasyOCR + Tesseract)
│   ├── translation/       # Kannada to English translation
│   ├── preprocessing/     # Text cleaning
│   ├── ner/               # Entity extraction
│   ├── classifier/        # Document classification
│   ├── verification/      # Cross-document verification
│   ├── risk/              # Risk scoring engine
│   ├── reports/           # Report generation
│   └── utils/             # Utilities
│
├── api/
│   └── main.py            # FastAPI application
│
├── notebooks/             # Experiments
│
├── run_verification.py            # Single document verification
├── run_multi_doc_verification.py  # Multi-document verification (RTC vs MR)
├── requirements.txt
└── README.md
```

## 🚀 Installation

### Prerequisites
- Python 3.8+
- Tesseract OCR

### Install Tesseract

**Windows:**
```bash
# Download from: https://github.com/UB-Mannheim/tesseract/wiki
# Add to PATH
```

**Linux:**
```bash
sudo apt-get install tesseract-ocr
```

### Install Python Dependencies

```bash
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

## 📊 Development Phases

### ✅ Phase 1: Document Ingestion & OCR (Week 1-2)
- File upload (PDF/JPG/PNG)
- OCR processing (EasyOCR + Tesseract)
- Multi-language support (Kannada + English)
- Image enhancement

### ✅ Phase 1.5: Translation (Week 2)
- Kannada to English translation
- Preserve document structure

### ✅ Phase 2: Text Preprocessing (Week 2-3)
- Noise removal
- Text normalization
- OCR error correction

### ✅ Phase 3: Entity Extraction (NER) (Week 3-4)
- Extract: Owner, Survey No, Bank, Loan, Case No, Date
- Train custom spaCy NER model

### ✅ Phase 4: Document Classification (Week 5-6)
- Fine-tune BERT/RoBERTa
- Classify: Clear Title, Loan Detected, Court Case, etc.

### ✅ Phase 5: Rule-based Risk Scoring (Week 7)
- Explainable risk calculation
- No AI - fully auditable

### ✅ Phase 6: Verification Report (Week 8)
- Generate comprehensive reports
- Using Python templates (Jinja2)

### ✅ Phase 7: Cross-Document Verification (Week 9)
- **RTC vs MR comparison**
- Survey number matching
- Owner name verification (fuzzy matching)
- Loan status cross-check
- Date consistency validation
- Mutation status verification
- Combined risk scoring

### ✅ Phase 8: FastAPI Microservice (Week 9-10)
- REST API endpoints
- Complete verification pipeline

### ✅ Phase 9: Testing & Evaluation (Week 10-11)
- NER metrics: Precision, Recall, F1
- Classification accuracy
- Rule validation
- Cross-document verification accuracy

### ✅ Phase 10: Documentation & Paper (Week 11-12)
- Research paper
- Technical documentation

## 🚀 Usage

### Single Document Verification

Verify a single RTC or MR document:

```bash
# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Run verification
python run_verification.py data/images/178.1_page_1.png
```

### Multi-Document Verification (RTC + MR)

**This is the recommended approach for complete property verification:**

```bash
# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Verify RTC against MR document
python run_multi_doc_verification.py data/images/178.1_page_1.png data/images/MR.png
```

**What it does:**
1. ✅ Processes RTC document (OCR → Translation → NER → Classification → Risk)
2. ✅ Processes MR document (same pipeline)
3. ✅ **Cross-verifies** both documents:
   - Survey number matching
   - Owner name consistency
   - Loan status verification
   - Date alignment
   - Mutation status check
4. ✅ Calculates **combined risk score**
5. ✅ Generates comprehensive HTML report

**Output:**
- `data/ocr_text/178.1_page_1_vs_MR_cross_verification.json`
- `data/ocr_text/178.1_page_1_vs_MR_combined_risk.json`
- `data/reports/178.1_page_1_vs_MR_combined_verification_report.html`

## 🔌 API Usage

### Start the Server

```bash
cd api
python main.py
```

Server runs at: `http://localhost:8000`

### API Endpoints

#### Verify Document
```bash
POST /verify/document
```

**Response:**
```json
{
  "property_id": "PRT-001",
  "score": 82,
  "status": "Minor Issues",
  "entities": {
    "owner": "Ravi Kumar",
    "survey_no": "45/2A",
    "loan": true,
    "bank": "SBI"
  },
  "classification": {
    "label": "Loan Detected",
    "confidence": 0.92
  },
  "risk_assessment": {
    "risk_score": 75,
    "risk_level": "High",
    "factors": ["Loan present", "Mutation pending"]
  }
}
```

## 📈 Evaluation Metrics

- **NER**: Precision, Recall, F1-Score
- **Classification**: Accuracy, F1-Score
- **Risk Engine**: Rule validation

## 🎓 Research Contributions

- ✔ Working AI system
- ✔ Multi-language support (Kannada + English)
- ✔ Cross-document verification capability
- ✔ No dependency on ChatGPT
- ✔ Fully explainable
- ✔ Research-grade
- ✔ Industry-ready

## 🔬 Key Features

### 1. Multi-Language OCR
- Supports Kannada and English documents
- Automatic language detection
- High accuracy with EasyOCR

### 2. Intelligent Translation
- Kannada → English translation
- Preserves document structure
- Handles mixed-language content

### 3. Advanced NER
- Extracts property-specific entities
- Custom trained models
- High precision and recall

### 4. Cross-Document Verification
- **RTC vs MR comparison**
- Survey number matching
- Owner verification with fuzzy matching
- Loan status cross-check
- Identifies discrepancies automatically

### 5. Risk Scoring
- Rule-based, explainable
- Single document risk
- Combined multi-document risk
- Court-safe and auditable

### 6. Comprehensive Reports
- HTML visualization
- Side-by-side document comparison
- Match/mismatch highlighting
- Actionable recommendations

## 📝 License

[Add your license here]

## 👥 Contributors

[Add contributors]

## 📧 Contact

[Add contact information]
