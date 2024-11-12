import pymongo

db = pymongo.MongoClient(host="10.7.0.50", port=27018)['mev']

token = db['tokens'].find_one({"_id":"0xb60FDF036F2ad584f79525B5da76C5c531283A1B".lower()}).get('decimals')

print(token)