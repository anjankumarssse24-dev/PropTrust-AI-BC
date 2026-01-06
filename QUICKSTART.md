# 🏠 PropTrust - Quick Start Guide

## ⚡ Fast Setup (5 minutes)

### Step 1: Install Dependencies

```bash
# Install Python packages
pip install -r requirements.txt
pip install -r blockchain_requirements.txt
python -m spacy download en_core_web_sm

# Install Ganache (blockchain)
npm install -g ganache
```

### Step 2: Start Ganache

```bash
ganache --port 8545 --networkId 5777
```

Keep this terminal open.

### Step 3: Compile & Deploy Smart Contract

**Option A: Using Solidity Compiler (if installed)**
```bash
cd blockchain/contracts
solc --optimize --abi --bin PropertyVerification.sol -o ../build/
cd ..
python deploy_contract.py
```

**Option B: Skip blockchain for now**
The system will work without blockchain (verification only, no tamper detection).

### Step 4: Create Environment File

```bash
cp .env.example .env
```

Edit `.env` and add contract address (from deployment output).

### Step 5: Initialize Database

```bash
python -c "from src.database import init_db; init_db()"
```

### Step 6: Start API

```bash
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

### Step 7: Open Browser

Go to: http://localhost:8000

---

## 🧪 Test with Sample Document

Upload one of these existing documents:
- `data/images/178.1.jpg`
- `data/images/178.3.jpg`

---

## 📊 What You Can Do

1. **Upload Document** - Verify property documents with AI
2. **View Risk Score** - See automated risk assessment (0-100)
3. **Check Blockchain** - Verification stored immutably
4. **Detect Tampering** - Re-verify to check for modifications

---

## 🆘 Troubleshooting

**Ganache not running?**
```bash
ganache --port 8545
```

**Contract not deployed?**
The system works without blockchain (AI verification only).

**Database errors?**
```bash
python -c "from src.database import drop_db, init_db; drop_db(); init_db()"
```

---

## 📚 Full Documentation

See `SETUP_GUIDE.md` for complete instructions.
See `PROPTRUST_ENHANCEMENT_PLAN.md` for architecture details.

---

**Ready to verify property documents! 🚀**
