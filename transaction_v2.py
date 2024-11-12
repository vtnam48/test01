import pymongo
import multiprocessing
import logging
import random

from pymongo.synchronous.database import Database

multiprocessing.set_start_method('fork')

def main():

    db = pymongo.MongoClient(host="10.7.0.50", port=27018)['mev']

    print(db['pools'].count_documents({"protocol": "UniSwapV2"}))

    # v2_pairs = db['pools'].distinct('_id', {"protocol": "UniSwapV2"})
    # print("len ", len(v2_pairs))
    result = db['pools'].aggregate([
        {
            "$match": {
                "protocol": "UniSwapV2"
            }
        },
        {
            "$group": {
                "_id": "$_id"
            }
        }
    ])

    v2_pairs = [x['_id'] for x in list(result)]

    v2_router = ['0xCeB90E4C17d626BE0fACd78b79c9c87d7ca181b3'.lower(), '0xEfF92A263d31888d860bD50809A8D171709b7b1c'.lower(), '0x03f7724180AA6b939894B5Ca4314783B0b36b329'.lower(), '0xd9e1cE17f2641f24aE83637ab66a2cca9C378B9F'.lower(), '0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D'.lower()]
    bundle_ids = db['bundles'].distinct('_id', {"types": "arbitrage", "mevAddress": "0x00000000009e50a7ddb7a7b0e2ee6604fd120e49", "signalTxs": {"$size": 1}})
    a = db["bundles"]

    total_item = len(bundle_ids)

    number_process = 20
    item_per_process = int(total_item / number_process) + 1
    # item_per_process = 10
    processes = []
    manager = multiprocessing.Manager()
    return_dict = manager.dict()

    for i in range(0, number_process):
        bundle_list = random.sample(bundle_ids, min(item_per_process, len(bundle_ids)))
        bundle_ids = [x for x in bundle_ids if x not in bundle_list]
        print(len(bundle_ids))
        p = multiprocessing.Process(target=process, args=(f"P_{i}", db, bundle_list, return_dict, v2_pairs))
        p.start()
        processes.append(p)

    for p in processes:
        p.join()

    output = []
    for k, v in return_dict.items():
        # print(k, v)
        output.extend(v)
    print(output)


    # output = []
    # counter = 0



    # bundle_list = []
    # multiprocessing.Process(target=process, args=(db, bundle_list, return_dict))


    # for b in bundles:
    #     counter += 1
    #     print("Index: {}, Check bundle: {}".format(counter, b["_id"]))
    #     signal = b["signalTxs"][0]
    #     signal_tx = db['transactions'].find_one({"_id": signal})
    #     signal_in_v2 = signal_tx['raw']['to'] in v2_router
    #     if not signal_in_v2:
    #         continue
    #     searcher = b['searcherTxs'][0]
    #     searcher_tx = db['transactions'].find_one({"_id": searcher})
    #     mev_in_v2 = only_v2_pair(v2_pairs, searcher_tx['pools'])

    #     if mev_in_v2:
    #         print("Bundle: {}  only v2".format(b["_id"]))
    #         output.append(b["_id"])

    # print("Running done!")
    # print(counter)
    # print(output)

def process(p_id: str, db: Database, bundle_ids: list, return_dict, v2_pairs):
    v2_router = ['0xCeB90E4C17d626BE0fACd78b79c9c87d7ca181b3'.lower(), '0xEfF92A263d31888d860bD50809A8D171709b7b1c'.lower(), '0x03f7724180AA6b939894B5Ca4314783B0b36b329'.lower(), '0xd9e1cE17f2641f24aE83637ab66a2cca9C378B9F'.lower(), '0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D'.lower()]
    counter = 0
    output = []
    for b_id in bundle_ids:
        b = db['bundles'].find_one({"_id": b_id})
        counter += 1
        print("Index: {}, Check bundle: {}".format(counter, b["_id"]))
        signal = b["signalTxs"][0]
        signal_tx = db['transactions'].find_one({"_id": signal})
        signal_in_v2 = signal_tx['raw']['to'] in v2_router
        if not signal_in_v2:
            continue
        searcher = b['searcherTxs'][0]
        searcher_tx = db['transactions'].find_one({"_id": searcher})
        mev_in_v2 = only_v2_pair(v2_pairs, searcher_tx['pools'])

        if mev_in_v2:
            print("Bundle: {}  only v2".format(b["_id"]))
            output.append(b["_id"])

    return_dict[p_id] = output


def only_v2_pair(v2pairs: list, pool_list: list):
    r = set(v2pairs) & set(pool_list)
    return len(r) == len(pool_list)




if __name__ == "__main__":
    main()