import re
import traceback
from pymongo import MongoClient
import numpy as np


class MongoCorpus:
    def __init__(self, connect_url, db, collection, field, length, chars_file):
        self.connect_url = connect_url
        self.client = MongoClient(self.connect_url, connect=False)
        self.col = self.client[db][collection]
        self.field = field
        self.length = length
        # 统计导出的字符数
        self.output_dict = {}
        with open(chars_file, "r", encoding="utf-8") as f:
            chars = ''.join(f.readlines()).replace("\n", "")
            for a in chars:
                self.output_dict[a] = 0

    def get_sample(self, img_index):
        try:
            min_weight_key = min(self.output_dict, key=self.output_dict.get)
            cursor = self.col.find({self.field: {"$regex": re.escape(min_weight_key)}}, {self.field: 1})
            skip = np.random.randint(cursor.count() - 1)
            # 查找已导出的文本里
            article: str = cursor.skip(skip).limit(1).next()[self.field]
            # 目标字符在该文集里出现的次数
            key_count = article.count(min_weight_key)
            # 随机取一个目标位置
            target_index = article.index(min_weight_key, 0 if key_count == 1 else np.random.randint(0, key_count-1))
            # {0}X{1}
            # 计算 {1} 的长度来决定 {0} 的可用最大长度
            # {0} 长度                            {1} 长度
            # self.length-1                       0
            # [0, self.length-1]                  >= self.length - 1
            # [self.length-N-1, self.length-1]    0 < N < self.length-1
            left, right = self.length - 1 - min(len(article[target_index + 1:]), self.length - 1), self.length - 1
            right = min(target_index, right)
            assert left <= right
            start = target_index - left if left == right else np.random.randint(target_index - right, target_index - left)
            word = article[start: start + self.length]
            assert len(word) == self.length
            for a in word:
                if a not in self.output_dict:
                    self.output_dict[a] = 1
                else:
                    self.output_dict[a] += 1
        except:
            traceback.print_exc()
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
