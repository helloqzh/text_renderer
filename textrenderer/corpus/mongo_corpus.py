import sys
from pymongo import MongoClient
import numpy as np


class MongoCorpus:
    def __init__(self, connect_url, db, collection, length):
        self.connect_url = connect_url
        self.client = MongoClient(self.connect_url, connect=False)
        self.col = self.client[db][collection]
        self.length = length

    def get_sample(self, img_index):
        try:
            skip = np.random.randint(self.col.count() - 1)
            article = self.col.find().skip(skip).limit(1).next()["article"]
            start = np.random.randint(0, len(article) - self.length)
            word = article[start: start + self.length]
        except:
            print("Unexpected error:", sys.exc_info()[0])
            raise
        return word


def update_mongodb_weight():
    """统计文集的权重 = 每个字符的频率相加/字符数"""
    client = MongoClient("mongodb://localhost:27017")
    col = client.kbw.jiji
    # 统计出现的字符，以及频率
    alphabet_dict = {}
    for x in col.find():
        article = x['article']
        for a in article:
            if a in alphabet_dict:
                alphabet_dict[a] += 1
            else:
                alphabet_dict[a] = 1
    for x in col.find():
        article = x['article']
        weight = x['weight']
        for a in article:
            weight += alphabet_dict[a]
        weight = int(weight/len(article))
        col.update_one({"_id": x["_id"]}, {"$set": {"weight": weight}})
    items = sorted(alphabet_dict.items(), key=lambda item: item[1], reverse=True)
    print(''.join([x[0] for x in items]))
    print(','.join([str(x[1]) for x in items]))


if __name__ == "__main__":
    update_mongodb_weight()
