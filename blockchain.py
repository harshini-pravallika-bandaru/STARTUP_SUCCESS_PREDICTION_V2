# blockchain.py
import os
import json
from web3 import Web3
from web3.middleware.proof_of_authority import ExtraDataToPOAMiddleware
from dotenv import load_dotenv

load_dotenv()

RPC_URL = os.getenv('RPC_URL')
PRIVATE_KEY = os.getenv('PRIVATE_KEY')
CONTRACT_ADDRESS = os.getenv('CONTRACT_ADDRESS')
ABI_FILE = os.getenv('CONTRACT_ABI_FILE', 'contract_abi.json')

if not all([RPC_URL, PRIVATE_KEY, CONTRACT_ADDRESS]):
    raise Exception("Missing required environment variables. Check .env file.")

with open(ABI_FILE, 'r') as f:
    CONTRACT_ABI = json.load(f)

w3 = Web3(Web3.HTTPProvider(RPC_URL))
w3.middleware_onion.inject(ExtraDataToPOAMiddleware, layer=0)

if not w3.is_connected():
    raise Exception("Failed to connect to Ethereum node. Check RPC_URL.")

account = w3.eth.account.from_key(PRIVATE_KEY)
print(f"Account address: {account.address}")
print(f"Account balance (Sepolia ETH): {w3.eth.get_balance(account.address) / 10**18}")

contract = w3.eth.contract(address=CONTRACT_ADDRESS, abi=CONTRACT_ABI)
print("Contract instance created.")

def record_investment_on_chain(startup_owner_address, startup_id, amount, notes):
    print(
        f"Attempting to record investment: startup_owner={startup_owner_address}, startup_id={startup_id}, amount={amount} ETH")

    try:
        amount_wei = int(amount * 10**18)
        nonce = w3.eth.get_transaction_count(account.address, 'pending')
        gas_price = w3.eth.gas_price
        print(f"Nonce: {nonce}, Gas price: {gas_price} wei")

        txn = contract.functions.recordInvestment(
            startup_owner_address,
            startup_id,
            amount_wei,
            notes
        ).build_transaction({
            'from': account.address,
            'nonce': w3.eth.get_transaction_count(account.address),
            'gas': 200000,
            'gasPrice': w3.eth.gas_price
        })
        signed = account.sign_transaction(txn)
        tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
        tx_hash_hex = tx_hash.hex()
        print(f"Transaction sent: {tx_hash_hex}")

        receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=60)
        if receipt.status == 1:
            print(f"Transaction successful: {tx_hash_hex}")
        else:
            print(f"Transaction reverted: {tx_hash_hex}")
            return None

        return tx_hash_hex
    except Exception as e:
        print(f"Blockchain error: {e}")
        return None