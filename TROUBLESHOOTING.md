# 🚀 PROPTRUST - DEPLOYMENT & TROUBLESHOOTING

## ✅ PRE-DEPLOYMENT CHECKLIST

### System Requirements
- [ ] Python 3.8 or higher installed
- [ ] Node.js 14+ installed (for Ganache)
- [ ] Tesseract OCR installed and in PATH
- [ ] Git installed (optional)
- [ ] 4GB RAM minimum
- [ ] 2GB free disk space

### Dependencies Installed
- [ ] Python packages: `pip install -r requirements.txt`
- [ ] spaCy model: `python -m spacy download en_core_web_sm`
- [ ] Ganache: `npm install -g ganache`

### Configuration
- [ ] `.env` file created (from `.env.example`)
- [ ] Blockchain provider URL set
- [ ] Contract address configured (after deployment)
- [ ] Database URL configured

### Blockchain Setup
- [ ] Ganache running
- [ ] Smart contract compiled
- [ ] Smart contract deployed
- [ ] Contract address saved to `.env`
- [ ] Test transaction successful

### Database Setup
- [ ] Database initialized: `init_db()`
- [ ] Tables created successfully
- [ ] `data/` directory exists
- [ ] Write permissions verified

### API Setup
- [ ] FastAPI dependencies installed
- [ ] All modules importable (no errors)
- [ ] Static files directory exists
- [ ] CORS configured (if needed)

---

## 🐛 COMMON ISSUES & SOLUTIONS

### Issue 1: Ganache Connection Failed

**Symptoms:**
```
❌ Failed to connect to Ethereum node at http://127.0.0.1:8545
```

**Solutions:**

**A. Check if Ganache is running:**
```bash
# Test connection
curl http://localhost:8545

# Should return JSON-RPC response
```

**B. Start Ganache:**
```bash
ganache --port 8545 --networkId 5777
```

**C. Check port availability:**
```bash
# Windows
netstat -an | findstr 8545

# Linux/Mac
netstat -an | grep 8545
```

**D. Try different port:**
```bash
ganache --port 7545 --networkId 5777

# Update .env
BLOCKCHAIN_PROVIDER_URL=http://127.0.0.1:7545
```

---

### Issue 2: Smart Contract Deployment Failed

**Symptoms:**
```
❌ Error deploying contract
ValueError: insufficient funds for gas
```

**Solutions:**

**A. Verify account has ETH:**
```python
from web3 import Web3
w3 = Web3(Web3.HTTPProvider('http://127.0.0.1:8545'))
print(w3.eth.get_balance(w3.eth.accounts[0]))
```

**B. Reset Ganache:**
- Stop Ganache
- Delete workspace
- Restart Ganache
- Re-deploy contract

**C. Use correct network ID:**
```bash
ganache --port 8545 --networkId 5777 --gasLimit 8000000
```

**D. Check Solidity compiler:**
```bash
solc --version
```

---

### Issue 3: Contract Not Found

**Symptoms:**
```
⚠️  Blockchain not available: Contract not loaded
```

**Solutions:**

**A. Verify contract address in `.env`:**
```bash
cat .env | grep CONTRACT_ADDRESS
```

**B. Re-deploy contract:**
```bash
cd blockchain
python deploy_contract.py
```

**C. Check ABI file exists:**
```bash
ls blockchain/build/PropertyVerification.abi
```

**D. Update API with contract address:**
- Copy address from deployment output
- Paste in `.env`
- Restart API server

---

### Issue 4: Database Connection Error

**Symptoms:**
```
sqlalchemy.exc.OperationalError: unable to open database file
```

**Solutions:**

**A. Create data directory:**
```bash
mkdir -p data
```

**B. Initialize database:**
```bash
python -c "from src.database import init_db; init_db()"
```

**C. Check permissions:**
```bash
# Linux/Mac
chmod 755 data/
chmod 644 data/proptrust.db

# Windows - ensure write access to data/ folder
```

**D. Use absolute path:**
```
# In .env
DATABASE_URL=sqlite:///C:/full/path/to/data/proptrust.db
```

---

### Issue 5: OCR Not Working

**Symptoms:**
```
pytesseract.pytesseract.TesseractNotFoundError
```

**Solutions:**

**A. Verify Tesseract installation:**
```bash
tesseract --version
```

**B. Install Tesseract:**

**Windows:**
1. Download: https://github.com/UB-Mannheim/tesseract/wiki
2. Install to `C:\Program Files\Tesseract-OCR`
3. Add to PATH

**Linux:**
```bash
sudo apt-get update
sudo apt-get install tesseract-ocr
sudo apt-get install tesseract-ocr-kan  # Kannada
```

**macOS:**
```bash
brew install tesseract
```

**C. Set Tesseract path manually:**
```python
# In ocr_engine.py
import pytesseract
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
```

---

### Issue 6: spaCy Model Not Found

**Symptoms:**
```
OSError: [E050] Can't find model 'en_core_web_sm'
```

**Solutions:**

**A. Download model:**
```bash
python -m spacy download en_core_web_sm
```

**B. Install manually:**
```bash
pip install https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-3.7.0/en_core_web_sm-3.7.0-py3-none-any.whl
```

**C. Verify installation:**
```python
import spacy
nlp = spacy.load("en_core_web_sm")
print("✅ Model loaded")
```

---

### Issue 7: API Server Won't Start

**Symptoms:**
```
ImportError: cannot import name 'X' from 'Y'
ModuleNotFoundError: No module named 'X'
```

**Solutions:**

**A. Verify all dependencies:**
```bash
pip install -r requirements.txt --upgrade
```

**B. Check Python path:**
```python
import sys
print(sys.path)
```

**C. Install missing modules:**
```bash
pip install web3 sqlalchemy fastapi uvicorn
```

**D. Use virtual environment:**
```bash
# Create venv
python -m venv venv

# Activate
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

---

### Issue 8: Frontend Not Loading

**Symptoms:**
- Blank page
- 404 errors
- Static files not found

**Solutions:**

**A. Verify frontend directory structure:**
```bash
ls frontend/
# Should show: index.html, css/, js/
```

**B. Check static files mounting in API:**
```python
# In api/main.py
app.mount("/static", StaticFiles(directory="frontend"), name="static")
```

**C. Access directly:**
```bash
# Try opening file directly
file:///path/to/frontend/index.html
```

**D. Check browser console:**
- Open DevTools (F12)
- Look for error messages
- Check Network tab for failed requests

---

### Issue 9: File Upload Fails

**Symptoms:**
```
413 Request Entity Too Large
422 Unprocessable Entity
```

**Solutions:**

**A. Increase file size limit:**
```python
# In api/main.py
from fastapi import FastAPI
app = FastAPI()
app.add_middleware(
    ...,
    max_upload_size=10 * 1024 * 1024  # 10MB
)
```

**B. Check file format:**
- Supported: JPG, PNG, PDF
- Max size: 10MB (default)

**C. Verify form data:**
```javascript
// In main.js
const formData = new FormData();
formData.append('file', fileInput.files[0]);
console.log(fileInput.files[0]);  // Check file object
```

---

### Issue 10: Blockchain Transaction Fails

**Symptoms:**
```
ValueError: gas required exceeds allowance
Error: transaction underpriced
```

**Solutions:**

**A. Increase gas limit:**
```bash
ganache --gasLimit 8000000 --gasPrice 20000000000
```

**B. Check account balance:**
```python
balance = w3.eth.get_balance(account)
print(f"Balance: {w3.from_wei(balance, 'ether')} ETH")
```

**C. Reset Ganache:**
- Restart Ganache
- Re-deploy contract
- Update contract address

---

## 🔍 DEBUGGING TECHNIQUES

### Enable Verbose Logging

**API Server:**
```bash
uvicorn api.main:app --reload --log-level debug
```

**Python Script:**
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Test Individual Components

**1. Test Blockchain Connection:**
```python
from src.blockchain import BlockchainManager
manager = BlockchainManager()
print(f"Connected: {manager.w3.is_connected()}")
```

**2. Test Database:**
```python
from src.database import init_db, get_db
init_db()
db = next(get_db())
print("✅ Database OK")
```

**3. Test OCR:**
```python
from src.ocr.ocr_engine import OCREngine
engine = OCREngine()
text = engine.extract_text("test_image.jpg")
print(f"Extracted: {text[:100]}")
```

**4. Test API Endpoint:**
```bash
curl -X GET http://localhost:8000/api/health
```

### Monitor Logs

**API Logs:**
```bash
# In one terminal
uvicorn api.main:app --reload

# Watch output for errors
```

**Ganache Logs:**
```bash
ganache --verbose
```

**Database Queries:**
```python
# In database.py
engine = create_engine(DATABASE_URL, echo=True)  # Enable SQL logging
```

---

## 📊 PERFORMANCE OPTIMIZATION

### 1. Increase Processing Speed

**A. Use GPU for OCR (if available):**
```python
# In ocr_engine.py
reader = easyocr.Reader(['en', 'kn'], gpu=True)
```

**B. Reduce image size:**
```python
# Before OCR
from PIL import Image
img = Image.open(file_path)
img = img.resize((1920, 1080))  # Max dimensions
```

**C. Use async processing:**
```python
# In API
from fastapi import BackgroundTasks

@app.post("/api/verify/upload")
async def verify(file, background_tasks: BackgroundTasks):
    background_tasks.add_task(process_verification, file)
    return {"status": "processing"}
```

### 2. Database Optimization

**A. Add indexes:**
```python
# In models.py
property_id = Column(String, index=True)
```

**B. Use connection pooling:**
```python
# In database.py
engine = create_engine(
    DATABASE_URL,
    pool_size=10,
    max_overflow=20
)
```

### 3. Blockchain Optimization

**A. Batch transactions:**
```python
# Store multiple verifications in one transaction
```

**B. Use faster network:**
```bash
ganache --blockTime 0  # No artificial delay
```

---

## 🛡️ SECURITY CHECKLIST

- [ ] Change default secret keys in `.env`
- [ ] Use HTTPS in production
- [ ] Implement authentication (JWT)
- [ ] Validate file uploads
- [ ] Sanitize user inputs
- [ ] Use environment variables (don't commit `.env`)
- [ ] Enable CORS only for trusted domains
- [ ] Implement rate limiting
- [ ] Use private blockchain (not public testnet)
- [ ] Regular database backups

---

## 📈 MONITORING & MAINTENANCE

### System Health Checks

**1. API Health:**
```bash
curl http://localhost:8000/api/health
```

**2. Blockchain Status:**
```bash
curl http://localhost:8000/api/blockchain/status
```

**3. Database Statistics:**
```bash
curl http://localhost:8000/api/statistics
```

### Regular Maintenance

**1. Clean old files:**
```bash
# Remove temp files older than 7 days
find data/raw_docs -type f -mtime +7 -delete
```

**2. Backup database:**
```bash
cp data/proptrust.db data/backups/proptrust_$(date +%Y%m%d).db
```

**3. Monitor disk space:**
```bash
df -h data/
```

**4. Check logs:**
```bash
tail -f logs/api.log
```

---

## 🔄 UPDATE & UPGRADE

### Update Dependencies

```bash
# Update Python packages
pip install --upgrade -r requirements.txt

# Update npm packages
npm update -g ganache
```

### Database Migration

```bash
# If schema changes
alembic revision --autogenerate -m "description"
alembic upgrade head
```

---

## 📞 GETTING HELP

### Resources
- **Documentation**: See `SETUP_GUIDE.md`
- **API Docs**: http://localhost:8000/docs
- **GitHub Issues**: Create an issue
- **Stack Overflow**: Tag with `proptrust`

### Before Asking for Help

1. Check error messages carefully
2. Search this troubleshooting guide
3. Review relevant documentation
4. Try suggested solutions
5. Collect logs and error details

### What to Include

- Error messages (full text)
- System information (OS, Python version)
- Steps to reproduce
- Expected vs actual behavior
- Relevant logs

---

## ✅ PRODUCTION DEPLOYMENT

### Additional Steps for Production

1. **Use PostgreSQL** instead of SQLite
2. **Enable HTTPS** with SSL certificates
3. **Set up reverse proxy** (Nginx/Apache)
4. **Implement authentication** (JWT)
5. **Use production WSGI server** (Gunicorn)
6. **Set up monitoring** (Prometheus, Grafana)
7. **Enable logging** to files
8. **Regular backups** automated
9. **Use public blockchain** (Testnet/Mainnet)
10. **Load balancing** for scale

---

**System Status: ✅ READY FOR DEPLOYMENT**

🏠 **PropTrust** - Blockchain-Verified Property Documents
