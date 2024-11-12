from web3 import Web3
from aiohttp import ClientSession
import json
import asyncio

infura_url = "https://mainnet.infura.io/v3/2650dbb66fdd4718b2e4a47964f97a6a"
w3 = Web3(Web3.HTTPProvider(infura_url))

print(w3.is_connected())

contract_address = "0x5C69bEe701ef814a2B6a3EDD4B1652CB9cc5aA6f"

with open("factory_abi.json") as f:
    contract_abi = json.load(f)

contract = w3.eth.contract(address=contract_address, abi=contract_abi)


async def get_factory(address1, address2):
    result = await asyncio.to_thread(contract.functions.getPair(address1, address2).call)
    return {"path1:": address1, "path2:": address2, "factory": result}


async def get_all():
    with open("data_pair.json", "r") as f:
        data = json.load(f)

    tasks = []
    for item in data:
        path1 = item["_id"]["path1"]
        path2 = item["_id"]["path2"]
        if path1 and path2:
            tasks.append(get_factory(path1, path2))

    results = await asyncio.gather(*tasks)

    with open("results.json", "w") as f:
        json.dump(results, f, indent=4)

    print("done")

if __name__ == "__main__":
    asyncio.run(get_all())


# Hàm gọi hàm getPair bất đồng bộ
async def get_pair(session, path1, path2):
    try:
        pair_address = contract.functions.getPair(path1, path2).call()
        return path1, path2, pair_address
    except Exception as e:
        print(f"Lỗi khi gọi getPair cho cặp {path1}, {path2}: {e}")
        return path1, path2, None

# Hàm chính để đọc tệp JSON và gọi hàm getPair
async def main():
    # Đọc dữ liệu từ tệp JSON
    with open("path_pairs.json", "r") as file:
        data = json.load(file)  # Giả sử JSON có định dạng [{"path1": "0x...", "path2": "0x..."}, ...]

    # Tạo phiên bất đồng bộ
    async with ClientSession() as session:
        tasks = []
        # Tạo các tác vụ cho từng cặp path1, path2
        for pair in data:
            path1 = pair["path1"]
            path2 = pair["path2"]
            task = asyncio.create_task(get_pair(session, path1, path2))
            tasks.append(task)

        # Thực thi tất cả các tác vụ đồng thời và chờ kết quả
        results = await asyncio.gather(*tasks)

    # Lưu kết quả vào tệp
    with open("pair_results.json", "w") as output_file:
        json.dump([{"path1": r[0], "path2": r[1], "pair_address": r[2]} for r in results], output_file, indent=4)

    print("Hoàn tất. Kết quả đã được lưu vào pair_results.json")

# Chạy chương trình
asyncio.run(main())