import time
from web3 import Web3, HTTPProvider
from solc import compile_source

# Web3 setting
rpc_url = "http://localhost:8123"
w3 = Web3(HTTPProvider(rpc_url))
# w3 = Web3(IPCProvider("./chain-data/geth.ipc"))
w3.personal.unlockAccount(w3.eth.accounts[0], "heiler", 0)	# address, password, ?

# Deploy
tx_hash = b"\xf5\x10\xcd\xc1\x9em\xf8\x12)\xbb\xf2/\xf8--C\xa7\xb5\xef\x06\x07\xb6\x1d\xc7\xaf\x05\xd2\xb1\x8e'\x17x"

print("tx_hash: {}".format(tx_hash))

# Contract address
tx_receipt = w3.eth.getTransactionReceipt(tx_hash)
print(tx_receipt)
contract_address = tx_receipt['contractAddress']


# Use contract
contract_instance = w3.eth.contract(contract_address, abi=contract_interface['abi'])
print('contract_address\n')
print(contract_instance.__dict__)
# Get
# print('Contract value: {}'.format(contract_instance.call().participatingInGame()))
# Set
contract_instance.functions.participatingInGame(1).call({'from': w3.eth.accounts[0], 'value': w3.toWei(10, 'ether')})
print('Setting value to data from server')

# Mining
w3.miner.start(1)
time.sleep(5)
w3.miner.stop()


