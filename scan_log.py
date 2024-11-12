from web3 import Web3
from eth_abi import decode
import pymongo
from dotenv import load_dotenv
import os

load_dotenv()
infura_url = os.getenv("NODE_URL")
hex_swap = "0xd78ad95fa46c994b6551d0da85fc275fe613ce37657fb8d5e3d130840159d822"
db = pymongo.MongoClient(host=os.getenv("HOST"), port=int(os.getenv("PORT")))['mev']
provider = Web3.HTTPProvider("https://docs-demo.quiknode.pro/")
w3 = Web3(Web3.HTTPProvider(infura_url))

pair_contract_abi = [
    {"constant": True, "inputs": [], "name": "token0", "outputs": [{"name": "", "type": "address"}],
     "type": "function"},
    {"constant": True, "inputs": [], "name": "token1", "outputs": [{"name": "", "type": "address"}],
     "type": "function"}
]


def hex_to_int(hex_str):
    return int(hex_str, 16)


def decode_rs(num: int):
    bit_length = num.bit_length() + 1
    uint32_bits = 32
    u112_bits = 112

    ts = num >> (bit_length - uint32_bits)
    shift_for_second_part = bit_length - uint32_bits - u112_bits
    rs1 = (num >> shift_for_second_part) & ((1 << u112_bits) - 1)
    rs0 = num & ((1 << u112_bits) - 1)

    return ts, rs0, rs1


def process(tx_hash):
    tx_receipt = w3.eth.get_transaction_receipt(tx_hash)

    pair_contracts = []
    for log in tx_receipt['logs']:
        contract_address = log['address']
        topics0 = log['topics'][0].to_0x_hex()
        data_bytes = log['data']

        if topics0 == hex_swap:
            pair_contracts.append({'contract_address': contract_address, 'data': data_bytes})

    for item in pair_contracts:
        try:
            pair_address = item['contract_address']
            data = item['data']
            pair_contract = w3.eth.contract(address=pair_address, abi=pair_contract_abi)

            blockHash_hex = tx_receipt['logs'][0]['blockHash']

            token0_address = pair_contract.functions.token0().call()
            token1_address = pair_contract.functions.token1().call()

            token0_decimals = db['tokens'].find_one({"_id": token0_address.lower()}).get('decimals')
            token1_decimals = db['tokens'].find_one({"_id": token1_address.lower()}).get('decimals')

            tx_index = tx_receipt['logs'][0]['transactionIndex']
            print("-----------------------------------------------")
            print(f"Uniswap Pair Contract: {pair_address}")
            print(f"Token 1 Address (token0): {token0_address}")
            print(f"Token 2 Address (token1): {token1_address}")
            print(token0_decimals, token1_decimals)
            print(f"BlockHash: {blockHash_hex.to_0x_hex()}")
            print(f"Transaction index: {tx_index}")
            decoded_data = decode(['uint256', 'uint256', 'uint256', 'uint256'], data)
            print(decoded_data)
            token0_amount = decoded_data[0] / (10 ** token0_decimals)
            token1_amount = decoded_data[1] / (10 ** token1_decimals)

            print(f"token0 : {token0_amount}")
            print(f"token1 : {token1_amount}")

            result = provider.make_request('debug_storageRangeAt',
                                           [blockHash_hex.to_0x_hex(),
                                            tx_index,
                                            pair_address,
                                            "0x0000000000000000000000000000000000000000000000000000000000000000", 8])

            reserve = result["result"]["storage"]
            target_key = "0x0000000000000000000000000000000000000000000000000000000000000008"
            value = next((item['value'] for item in reserve.values() if item['key'] == target_key), None)

            num_converted = hex_to_int(value)
            ts, rs0, rs1 = decode_rs(num_converted)
            print(f"ts: {ts}, rs0: {rs0}, rs1: {rs1}")
            res0 = rs0 / (10 ** token0_decimals)
            res1 = rs1 / (10 ** token1_decimals)
            print(f"ts: {ts}, rs0: {res0}, rs1: {res1}")

            print("-----------------------------------------------")

            print("########################################################")
            print("Result:")
            print(f"Token0 in pool: {100 * token0_amount / res0}")
            print(f"Token1 in pool: {100 * token1_amount / res1}")
            print("########################################################")

        except Exception as e:
            print(f"Error: {e}")


if __name__ == '__main__':
    tx_hash = "0xce0cbe62bdc71a4e4949c3c7475fee60da1b8a7f53e68ca87eba1a6950d258ce"
    process(tx_hash)
