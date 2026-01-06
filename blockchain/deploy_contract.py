"""
Smart Contract Deployment Script
"""

from web3 import Web3
import json
import os
from pathlib import Path
from dotenv import load_dotenv, set_key
from solcx import compile_source, install_solc, set_solc_version

load_dotenv()


def deploy_contract():
    """Deploy PropertyVerification smart contract"""
    
    print("="*70)
    print("PROPTRUST - SMART CONTRACT DEPLOYMENT")
    print("="*70)
    
    # Connect to Ganache
    provider_url = os.getenv('BLOCKCHAIN_PROVIDER_URL', 'http://127.0.0.1:8545')
    print(f"\n🔗 Connecting to {provider_url}...")
    
    w3 = Web3(Web3.HTTPProvider(provider_url))
    
    if not w3.is_connected():
        print("❌ Failed to connect to blockchain!")
        print("   Make sure Ganache is running:")
        print("   ganache --port 8545 --networkId 5777")
        return False
    
    print(f"✅ Connected!")
    print(f"   Chain ID: {w3.eth.chain_id}")
    print(f"   Latest Block: {w3.eth.block_number}")
    
    # Get account
    if not w3.eth.accounts:
        print("❌ No accounts available!")
        return False
    
    account = w3.eth.accounts[0]
    balance = w3.eth.get_balance(account)
    print(f"\n💰 Deployer Account: {account}")
    print(f"   Balance: {w3.from_wei(balance, 'ether')} ETH")
    
    # Compile contract
    print(f"\n📝 Compiling contract...")
    
    contract_file = Path(__file__).parent / "contracts" / "PropertyVerification.sol"
    
    if not contract_file.exists():
        print(f"❌ Contract file not found: {contract_file}")
        return False
    
    # Read contract source
    with open(contract_file, 'r') as f:
        contract_source = f.read()
    
    # Set solc version
    try:
        set_solc_version('0.8.19')
    except Exception:
        print("📥 Installing Solidity compiler 0.8.19...")
        install_solc('0.8.19')
        set_solc_version('0.8.19')
    
    # Compile
    compiled_sol = compile_source(
        contract_source,
        output_values=['abi', 'bin'],
        solc_version='0.8.19'
    )
    
    # Extract contract interface
    contract_id, contract_interface = compiled_sol.popitem()
    contract_abi = contract_interface['abi']
    contract_bytecode = contract_interface['bin']
    
    print(f"✅ Contract compiled successfully!")
    
    # Save compiled artifacts
    build_dir = Path(__file__).parent / "build"
    build_dir.mkdir(exist_ok=True)
    
    with open(build_dir / "PropertyVerification.abi", 'w') as f:
        json.dump(contract_abi, f, indent=2)
    
    with open(build_dir / "PropertyVerification.bin", 'w') as f:
        f.write(contract_bytecode)
    
    print(f"💾 Artifacts saved to {build_dir}")
    
    # Deploy contract
    print(f"\n🚀 Deploying contract...")
    
    Contract = w3.eth.contract(abi=contract_abi, bytecode=contract_bytecode)
    
    # Build transaction
    tx_hash = Contract.constructor().transact({'from': account})
    
    print(f"   Transaction: {tx_hash.hex()}")
    print(f"   Waiting for confirmation...")
    
    # Wait for receipt
    tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    
    contract_address = tx_receipt.contractAddress
    
    print(f"\n✅ Contract Deployed!")
    print(f"   Address: {contract_address}")
    print(f"   Block: {tx_receipt.blockNumber}")
    print(f"   Gas Used: {tx_receipt.gasUsed}")
    
    # Save to .env
    env_file = Path(__file__).parent.parent / ".env"
    
    if env_file.exists():
        print(f"\n💾 Updating .env file...")
        set_key(env_file, "CONTRACT_ADDRESS", contract_address)
    else:
        print(f"\n💾 Creating .env file...")
        with open(env_file, 'w') as f:
            f.write(f"BLOCKCHAIN_PROVIDER_URL={provider_url}\n")
            f.write(f"CONTRACT_ADDRESS={contract_address}\n")
    
    print(f"✅ Configuration saved to .env")
    
    # Save ABI to easier location
    abi_copy = Path(__file__).parent / "PropertyVerification.abi"
    with open(abi_copy, 'w') as f:
        json.dump(contract_abi, f, indent=2)
    
    print(f"\n✅ ABI saved to {abi_copy}")
    
    # Test contract
    print(f"\n🧪 Testing contract...")
    
    contract = w3.eth.contract(address=contract_address, abi=contract_abi)
    
    # Test storage with valid hash
    test_hash = w3.keccak(text="TEST_VERIFICATION")
    tx = contract.functions.storeVerification(
        "TEST-001",
        test_hash,
        50
    ).transact({'from': account})
    
    w3.eth.wait_for_transaction_receipt(tx)
    
    # Verify
    result = contract.functions.getVerification("TEST-001").call()
    
    print(f"   Test Property ID: {result[0]}")
    print(f"   Test Risk Score: {result[2]}")
    print(f"   ✅ Contract working correctly!")
    
    print("\n" + "="*70)
    print("DEPLOYMENT COMPLETE!")
    print("="*70)
    print(f"\nNext steps:")
    print(f"1. Start the API: uvicorn api.main:app --reload")
    print(f"2. Open browser: http://localhost:8000")
    print(f"3. Upload a document to test")
    
    return True


if __name__ == "__main__":
    deploy_contract()
