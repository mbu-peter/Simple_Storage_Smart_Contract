
# Web3.py
import os
from dotenv import load_dotenv
import json
from web3 import Web3
from solcx import compile_standard, install_solc
from web3.middleware import geth_poa_middleware

load_dotenv()


with open("./Contract1.sol", "r") as file:
    contract_file = file.read()

install_solc("0.6.0")

# compile
compiled_contract = compile_standard(
    {
        "language": "Solidity",
        "sources": {"Contract1.sol": {"content": contract_file}},
        "settings": {
            "outputSelection": {
                "*": {
                    "*": ["abi", "metadata", "evm.bytecode", "evm.bytecode.sourceMap"]
                }
            }
        },
    },
    solc_version="0.8.2",
)

with open("compiled_contract.json", "w") as file:
    json.dump(compiled_contract, file)

# get bytecode
bytecode = compiled_contract["contracts"]["Contract1.sol"]["Contract1"]["evm"][
    "bytecode"
]["object"]

# get abi
abi = json.loads(
    compiled_contract["contracts"]["Contract1.sol"]["Contract1"]["metadata"]
)["output"]["abi"]

# Connect to ganache
w3 = Web3(Web3.HTTPProvider(
    "https://sepolia.infura.io/v3/c912d90c2a104307b77c562c3ba70621"))
chain_id = 11155111

if chain_id == 4:
    w3.middleware_onion.inject(geth_poa_middleware, layer=0)
    print(w3.clientVersion)

my_address = "0x4191C657741c2c1919A0a04e58Ce89965161d949"  # use yours!
private_key = os.getenv("PRIVATE_KEY")  # Tumia yako

# Create the contract
Contract1 = w3.eth.contract(abi=abi, bytecode=bytecode)
# Initial Transaction
nonce = w3.eth.get_transaction_count(my_address)
# transact
txn = Contract1.constructor().build_transaction(
    {
        "chainId": chain_id,
        "gasPrice": w3.eth.gas_price,
        "from": my_address,
        "nonce": nonce,
    }
)
# Sign transaction
signed_txn = w3.eth.account.sign_transaction(
    txn, private_key=private_key)
print("Hang tight, Contract id deploying!")
# Send the transaction!
tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
print("Loading.............")
tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
print(
    f"Congratulations! Your contract has been deployed to {tx_receipt.contractAddress}")


contract1 = w3.eth.contract(address=tx_receipt.contractAddress, abi=abi)
print(f"Previous value {contract1.functions.retrieve().call()}")
greeting_transaction = contract1.functions.store(30).build_transaction(
    {
        "chainId": chain_id,
        "gasPrice": w3.eth.gas_price,
        "from": my_address,
        "nonce": nonce + 1,
    }
)
signed_greeting_txn = w3.eth.account.sign_transaction(
    greeting_transaction, private_key=private_key
)
tx_greeting_hash = w3.eth.send_raw_transaction(
    signed_greeting_txn.rawTransaction)
print("Updating stored Value...")
tx_receipt = w3.eth.wait_for_transaction_receipt(tx_greeting_hash)

print(contract1.functions.retrieve().call())
