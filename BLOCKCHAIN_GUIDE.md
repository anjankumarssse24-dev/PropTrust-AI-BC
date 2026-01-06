# 🔗 PropTrust Blockchain Storage Guide

## Current Status
⚠️ **Blockchain is configured but NOT running** - You need to start Ganache (local Ethereum blockchain)

The error message shows:
```
⚠️ Blockchain not available: Failed to connect to Ethereum node at http://127.0.0.1:8545
```

---

## What is Stored on Blockchain?

For each property verification, the following is stored **immutably** on the blockchain:

1. **Property ID** - Unique identifier (e.g., PRT-80154723)
2. **Verification Hash** - SHA-256 cryptographic hash of the entire verification result
3. **Risk Score** - Risk assessment score (0-100)
4. **Timestamp** - When verification was performed
5. **Verifier Address** - Ethereum address that stored the record
6. **Transaction Hash** - Blockchain transaction ID for audit trail

### Why Blockchain?
- ✅ **Immutable** - Cannot be altered or deleted
- ✅ **Transparent** - Anyone can verify the record
- ✅ **Tamper-Proof** - Any modification is immediately detectable
- ✅ **Audit Trail** - Complete history of all verifications
- ✅ **Court-Admissible** - Cryptographic proof of authenticity

---

## 🚀 Quick Setup (Local Blockchain)

### Option 1: Ganache GUI (Easiest)

1. **Download Ganache**
   ```
   https://trufflesuite.com/ganache/
   ```

2. **Install & Launch Ganache**
   - Double-click the installer
   - Launch Ganache
   - Click "Quickstart" (creates blockchain on port 8545)

3. **Verify Connection**
   - You should see 10 test accounts with 100 ETH each
   - Server should show: `RPC SERVER: HTTP://127.0.0.1:8545`

4. **Deploy Smart Contract**
   ```powershell
   .\venv\Scripts\Activate.ps1
   python blockchain/deploy_contract.py
   ```

5. **Restart PropTrust Server**
   ```powershell
   python -m uvicorn api.main:app --host 127.0.0.1 --port 8000 --reload
   ```

### Option 2: Ganache CLI (Command Line)

1. **Install Node.js** (if not installed)
   ```
   https://nodejs.org/
   ```

2. **Install Ganache CLI**
   ```powershell
   npm install -g ganache
   ```

3. **Start Ganache**
   ```powershell
   ganache --port 8545 --networkId 5777
   ```
   Keep this terminal open!

4. **In a NEW terminal, deploy contract**
   ```powershell
   cd C:\Users\I770144\Documents\property-doc-verification
   .\venv\Scripts\Activate.ps1
   python blockchain/deploy_contract.py
   ```

5. **Start PropTrust**
   ```powershell
   python -m uvicorn api.main:app --host 127.0.0.1 --port 8000 --reload
   ```

---

## 📋 Step-by-Step Deployment

### Step 1: Start Ganache
```powershell
# Open a new PowerShell terminal
ganache --port 8545 --networkId 5777
```

You should see:
```
ganache v7.x.x (@ganache/cli: 0.x.x, @ganache/core: 0.x.x)
Starting RPC server

Available Accounts
==================
(0) 0x... (100 ETH)
(1) 0x... (100 ETH)
...

Listening on 127.0.0.1:8545
```

### Step 2: Deploy Smart Contract
```powershell
# In your project directory
.\venv\Scripts\Activate.ps1
python blockchain/deploy_contract.py
```

You should see:
```
======================================================================
PROPTRUST - SMART CONTRACT DEPLOYMENT
======================================================================

🔗 Connecting to http://127.0.0.1:8545...
✅ Connected!
   Chain ID: 5777
   Latest Block: 0

💰 Deployer Account: 0x...
   Balance: 100.0 ETH

📝 Compiling contract...
✅ Contract compiled successfully!

🚀 Deploying contract...
   Gas estimate: 1500000
   Transaction hash: 0x...
⏳ Waiting for confirmation...
✅ Contract deployed!
   Address: 0x...
   Block Number: 1

💾 Saving contract address to .env...
✅ Contract address saved!

📄 Saving ABI...
✅ ABI saved to: blockchain/PropertyVerification.abi

======================================================================
✅ DEPLOYMENT COMPLETE!
======================================================================
```

### Step 3: Restart PropTrust
```powershell
# Stop current server (Ctrl+C)
python -m uvicorn api.main:app --host 127.0.0.1 --port 8000 --reload
```

You should now see:
```
✅ Blockchain manager initialized
INFO:     Uvicorn running on http://127.0.0.1:8000
```

---

## 🔍 How to Access Blockchain Data

### Method 1: Frontend Display
Upload a document with "Store verification on blockchain" checked:
- **Transaction Hash**: Shows in verification results
- **Block Number**: Displayed in results
- **Verification Hash**: Cryptographic proof
- **Timestamp**: When record was created

### Method 2: Ganache GUI
1. Open Ganache
2. Click "Blocks" tab - See all transactions
3. Click "Transactions" tab - View transaction details
4. Click "Contracts" tab - See deployed contract

### Method 3: API Endpoint
```bash
# Check blockchain status
curl http://127.0.0.1:8000/api/blockchain/status

# Verify a specific property
curl http://127.0.0.1:8000/api/blockchain/verify/PRT-80154723
```

### Method 4: Python Script
```python
from web3 import Web3
import json

# Connect to Ganache
w3 = Web3(Web3.HTTPProvider('http://127.0.0.1:8545'))

# Load contract
with open('blockchain/PropertyVerification.abi', 'r') as f:
    abi = json.load(f)

# Get contract address from .env
contract_address = '0x...'  # From deployment
contract = w3.eth.contract(address=contract_address, abi=abi)

# Query verification
property_id = 'PRT-80154723'
result = contract.functions.getVerification(property_id).call()

print(f"Property ID: {result[0]}")
print(f"Verification Hash: {result[1].hex()}")
print(f"Risk Score: {result[2]}")
print(f"Timestamp: {result[3]}")
print(f"Verifier: {result[4]}")
```

---

## 🗄️ Where is Blockchain Data Stored?

### Local Development (Ganache)
- **Location**: In-memory (lost when Ganache stops)
- **Persistence**: Use Ganache CLI with `--db` flag:
  ```powershell
  ganache --port 8545 --networkId 5777 --db ./data/ganache_db
  ```
  This saves blockchain state to disk

### Production Options

#### Option A: Public Testnet (Free)
- **Sepolia Testnet** (Ethereum)
- **Mumbai Testnet** (Polygon)
- Get free test ETH from faucets
- Update `.env`:
  ```
  BLOCKCHAIN_PROVIDER_URL=https://sepolia.infura.io/v3/YOUR_PROJECT_ID
  ```

#### Option B: Private Network
- Deploy your own Ethereum node
- Use services like Infura, Alchemy, or QuickNode
- Update `.env` with provider URL

#### Option C: Public Mainnet (Costs Real Money)
- Ethereum Mainnet
- Polygon Mainnet (cheaper)
- Binance Smart Chain
- Requires real cryptocurrency for gas fees

---

## 🔐 Security & Access Control

### Current Setup
- **Owner**: Account that deploys the contract
- **Public Read**: Anyone can verify records
- **Controlled Write**: Only authorized accounts can store verifications

### Access Control
The smart contract has built-in access control:
```solidity
modifier onlyOwner() {
    require(msg.sender == owner, "Only owner can call this function");
    _;
}
```

### Production Recommendations
1. **Use a dedicated Ethereum account** (not a test account)
2. **Secure the private key** (hardware wallet recommended)
3. **Set up multi-sig** for critical operations
4. **Monitor gas prices** to optimize transaction costs
5. **Implement rate limiting** to prevent abuse

---

## 📊 Blockchain Verification Workflow

```
User uploads document
         ↓
1. OCR + NER + Risk Assessment
         ↓
2. Generate Semantic Hash (SHA-256)
         ↓
3. Create blockchain transaction
         ↓
4. Smart contract stores:
   - Property ID
   - Verification Hash
   - Risk Score
   - Timestamp
         ↓
5. Transaction mined (confirmed)
         ↓
6. Return transaction hash & block number
         ↓
7. Display in frontend + Save to database
```

---

## 🧪 Testing Blockchain Integration

### Test Script
```powershell
# Activate environment
.\venv\Scripts\Activate.ps1

# Test blockchain connection
python -c "from web3 import Web3; w3 = Web3(Web3.HTTPProvider('http://127.0.0.1:8545')); print(f'Connected: {w3.is_connected()}')"

# Expected output: Connected: True
```

### Test Verification
1. Start Ganache
2. Deploy contract
3. Start PropTrust server
4. Upload a document with blockchain checkbox enabled
5. Check results for:
   - ✅ Transaction Hash
   - ✅ Block Number
   - ✅ Verification Hash
   - ✅ Timestamp

---

## 🐛 Troubleshooting

### Error: "Failed to connect to Ethereum node"
- **Solution**: Start Ganache first
- **Check**: Port 8545 is not used by another application

### Error: "Contract not deployed"
- **Solution**: Run `python blockchain/deploy_contract.py`
- **Check**: `.env` file has `CONTRACT_ADDRESS` set

### Error: "Transaction reverted"
- **Cause**: Duplicate property ID or invalid data
- **Solution**: Check smart contract requirements

### Error: "Insufficient funds"
- **Cause**: Deployer account has no ETH
- **Solution**: In Ganache, each account starts with 100 ETH (test tokens)

### Blockchain checkbox disabled
- **Cause**: Blockchain not configured or connection failed
- **Solution**: Deploy contract and restart server

---

## 📚 Additional Resources

### Documentation
- **Ganache**: https://trufflesuite.com/docs/ganache/
- **Web3.py**: https://web3py.readthedocs.io/
- **Solidity**: https://docs.soliditylang.org/

### PropTrust Files
- Smart Contract: `blockchain/contracts/PropertyVerification.sol`
- Deployment Script: `blockchain/deploy_contract.py`
- Blockchain Manager: `src/blockchain/blockchain_manager.py`
- ABI: `blockchain/PropertyVerification.abi` (created after deployment)

---

## 💡 Quick Commands Reference

```powershell
# Start Ganache (Option 1)
ganache --port 8545 --networkId 5777

# Deploy Contract
.\venv\Scripts\Activate.ps1
python blockchain/deploy_contract.py

# Start PropTrust
python -m uvicorn api.main:app --host 127.0.0.1 --port 8000 --reload

# Check Blockchain Status
curl http://127.0.0.1:8000/api/blockchain/status

# Clear Database (fresh start)
python -c "from src.database import drop_db, init_db; drop_db(); init_db(); print('✅ Database cleared')"
```

---

## 🎯 Next Steps

1. ✅ Download & install Ganache
2. ✅ Start Ganache on port 8545
3. ✅ Deploy smart contract
4. ✅ Restart PropTrust server
5. ✅ Upload document with blockchain enabled
6. ✅ Verify transaction in Ganache
7. ✅ Check verification results in frontend

**Your blockchain data will be immutable and cryptographically secured! 🔐**
