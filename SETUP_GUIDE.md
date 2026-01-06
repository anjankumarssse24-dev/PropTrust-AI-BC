# 🏠 PROPTRUST - SETUP GUIDE
## AI-Blockchain Property Document Verification System

---

## 📋 PREREQUISITES

### Required Software
- Python 3.8 or higher
- Node.js 14+ (for Ganache)
- Tesseract OCR
- Git

---

## 🚀 INSTALLATION STEPS

### Step 1: Install Python Dependencies

```bash
# Install core dependencies
pip install -r requirements.txt

# Install blockchain dependencies
pip install -r blockchain_requirements.txt

# Download spaCy model
python -m spacy download en_core_web_sm
```

### Step 2: Install Tesseract OCR

**Windows:**
1. Download from: https://github.com/UB-Mannheim/tesseract/wiki
2. Install to `C:\Program Files\Tesseract-OCR`
3. Add to PATH: `C:\Program Files\Tesseract-OCR`

**Linux:**
```bash
sudo apt-get update
sudo apt-get install tesseract-ocr
sudo apt-get install tesseract-ocr-kan  # Kannada support
```

**macOS:**
```bash
brew install tesseract
```

### Step 3: Install Ganache (Local Blockchain)

**Option A: Ganache CLI (Recommended)**
```bash
npm install -g ganache
```

**Option B: Ganache GUI**
Download from: https://trufflesuite.com/ganache/

### Step 4: Install Solidity Compiler

```bash
npm install -g solc
```

### Step 5: Set Up Environment Variables

```bash
# Copy example env file
cp .env.example .env

# Edit .env with your configuration
```

Example `.env`:
```
DATABASE_URL=sqlite:///./data/proptrust.db
BLOCKCHAIN_PROVIDER_URL=http://127.0.0.1:8545
CONTRACT_ADDRESS=
API_HOST=0.0.0.0
API_PORT=8000
```

---

## ⛓️ BLOCKCHAIN SETUP

### Step 1: Start Ganache

**Using Ganache CLI:**
```bash
ganache --port 8545 --networkId 5777
```

**Using Ganache GUI:**
1. Open Ganache
2. Create new workspace
3. Set RPC Server to `HTTP://127.0.0.1:8545`
4. Save workspace

**Expected Output:**
```
Ganache CLI v7.x.x

Available Accounts:
(0) 0x1234... (100 ETH)
(1) 0x5678... (100 ETH)
...

Private Keys:
(0) 0xabcd...
(1) 0xef01...

Listening on 127.0.0.1:8545
```

### Step 2: Compile Smart Contract

```bash
cd blockchain/contracts

# Compile PropertyVerification.sol
solc --optimize --abi --bin PropertyVerification.sol -o ../build/
```

This creates:
- `PropertyVerification.abi` (Contract interface)
- `PropertyVerification.bin` (Bytecode)

### Step 3: Deploy Smart Contract

**Option A: Using Python Script**

Create `blockchain/deploy_contract.py`:
```python
from web3 import Web3
import json

# Connect to Ganache
w3 = Web3(Web3.HTTPProvider('http://127.0.0.1:8545'))
print(f"Connected: {w3.is_connected()}")

# Load compiled contract
with open('build/PropertyVerification.abi', 'r') as f:
    abi = json.load(f)

with open('build/PropertyVerification.bin', 'r') as f:
    bytecode = f.read()

# Deploy
account = w3.eth.accounts[0]
Contract = w3.eth.contract(abi=abi, bytecode=bytecode)
tx_hash = Contract.constructor().transact({'from': account})
tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

contract_address = tx_receipt.contractAddress
print(f"\n✅ Contract deployed at: {contract_address}")
print(f"   Block: {tx_receipt.blockNumber}")
print(f"   Gas Used: {tx_receipt.gasUsed}")

# Save address to .env
with open('../.env', 'a') as f:
    f.write(f"\nCONTRACT_ADDRESS={contract_address}")
```

Run:
```bash
cd blockchain
python deploy_contract.py
```

**Option B: Manual Deployment via Remix**

1. Go to https://remix.ethereum.org/
2. Create new file: `PropertyVerification.sol`
3. Paste contract code
4. Compile
5. Deploy to "Injected Web3" (connect to Ganache via MetaMask)
6. Copy contract address to `.env`

---

## 💾 DATABASE SETUP

### Initialize Database

```bash
# Create database tables
python -c "from src.database import init_db; init_db()"
```

**Expected Output:**
```
✅ Database initialized
```

This creates `data/proptrust.db` with tables:
- properties
- verification_records
- verification_details
- tamper_checks
- audit_logs

---

## 🧪 TESTING THE SETUP

### Test 1: Blockchain Connection

```python
from src.blockchain import BlockchainManager

manager = BlockchainManager()
print(f"Connected: {manager.w3.is_connected()}")
print(f"Block: {manager.w3.eth.block_number}")
```

### Test 2: Smart Contract

```python
from src.blockchain import BlockchainManager

manager = BlockchainManager(
    contract_address="YOUR_CONTRACT_ADDRESS",
    contract_abi_path="blockchain/build/PropertyVerification.abi"
)

# Test storage
test_hash = b'\x00' * 32
result = manager.store_verification("TEST-001", test_hash, 50)
print(f"Transaction: {result['tx_hash']}")

# Verify
verification = manager.get_verification("TEST-001")
print(f"Retrieved: {verification}")
```

### Test 3: API

```bash
# Terminal 1: Start API
uvicorn api.main:app --reload --port 8000

# Terminal 2: Test
curl http://localhost:8000/api/health
```

**Expected Response:**
```json
{
  "status": "active",
  "service": "PropTrust API",
  "version": "2.0.0",
  "blockchain": "connected",
  "ai_enabled": true
}
```

---

## 🌐 RUNNING THE SYSTEM

### Step 1: Start Ganache (if not running)
```bash
ganache --port 8545
```

### Step 2: Start API Server
```bash
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

### Step 3: Access the System
- Web UI: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Ganache UI: http://127.0.0.1:8545 (if using GUI)

---

## 📊 TESTING WITH SAMPLE DOCUMENT

### Using Existing Test Data

```bash
# Run verification on existing document
python run_verification.py data/images/178.1.jpg
```

### Using API

```bash
# Upload and verify document
curl -X POST "http://localhost:8000/api/verify/upload" \
  -F "file=@data/images/178.1.jpg" \
  -F "document_type=RTC" \
  -F "store_on_blockchain=true"
```

**Expected Response:**
```json
{
  "success": true,
  "property_id": "PRT-XXXXXXXX",
  "risk_score": 45,
  "risk_level": "Medium",
  "blockchain": {
    "stored": true,
    "hash": "a3f8c9e2...",
    "tx_hash": "0x1234...",
    "block_number": 3
  }
}
```

---

## 🔍 VERIFY TAMPER DETECTION

```bash
# Check tamper status
curl -X POST "http://localhost:8000/api/blockchain/check-tamper?property_id=PRT-XXXXXXXX" \
  -F "file=@data/images/178.1.jpg"
```

---

## 🛠️ TROUBLESHOOTING

### Issue: Ganache not connecting

**Solution:**
```bash
# Check if Ganache is running
curl http://localhost:8545

# Restart Ganache
ganache --port 8545 --networkId 5777
```

### Issue: Contract deployment failed

**Solution:**
```bash
# Check account has ETH
from web3 import Web3
w3 = Web3(Web3.HTTPProvider('http://127.0.0.1:8545'))
print(w3.eth.get_balance(w3.eth.accounts[0]))
```

### Issue: OCR not working

**Solution:**
```bash
# Test Tesseract
tesseract --version

# Check PATH
echo $PATH  # Linux/Mac
echo %PATH%  # Windows
```

### Issue: Database errors

**Solution:**
```bash
# Recreate database
python -c "from src.database import drop_db, init_db; drop_db(); init_db()"
```

---

## 📚 NEXT STEPS

1. ✅ System setup complete
2. 🌐 Customize frontend (frontend/index.html)
3. 🔐 Add authentication (optional)
4. 📱 Deploy to production
5. 📊 Add analytics dashboard

---

## 🆘 SUPPORT

If you encounter issues:
1. Check logs in terminal
2. Verify Ganache is running
3. Check `.env` configuration
4. Ensure all dependencies installed
5. Review error messages carefully

---

**Congratulations! Your PropTrust system is ready! 🎉**
