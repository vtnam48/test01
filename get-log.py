from web3 import Web3

# Connect to Infura
infura_url = "http://10.7.0.58:8545/"
web3 = Web3(Web3.HTTPProvider(infura_url))

# Transaction hash
tx_hash = "0xce0cbe62bdc71a4e4949c3c7475fee60da1b8a7f53e68ca87eba1a6950d258ce"

try:
    receipt = web3.eth.get_transaction_receipt(tx_hash)
    logs = receipt['logs']

    # # Format logs for readability
    # formatted_logs = ""
    # for index, log in enumerate(logs):
    #     formatted_logs += f"Log #{index + 1}:\n"
    #     formatted_logs += f"Address: {log['address']}\n"
    #     # Convert each topic to a hex string
    #     topics = [topic.hex() if isinstance(topic, bytes) else topic for topic in log['topics']]
    #     formatted_logs += f"Topics: {', '.join(topics)}\n"
    #     formatted_logs += f"Data: {log['data']}\n"
    #     formatted_logs += "-" * 33 + "\n"
    #
    # # Save formatted logs to a .txt file
    # with open('transaction_logs.txt', 'w') as f:
    #     f.write(formatted_logs)

    print(logs)
    print('Formatted transaction logs saved to transaction_logs.txt')
except Exception as e:
    print('Error fetching logs:', e)