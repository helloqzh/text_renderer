import random
from pymongo import MongoClient
import numpy as np

from textrenderer.corpus.corpus import Corpus


class MongoCorpus(Corpus):

    def load(self):
        """
        Load one corpus file as one line , and get random {self.length} words as result
        """
        if self.corpus_dir.startswith("mongodb:"):
            # mongodb://localhost:27017
            client = MongoClient(self.corpus_dir)
            db = client.kbw
            self.mongo = True
            self.col = db.jiji
            self.document_count = self.col.count()
            print("mongodb documents count:%d" % self.document_count)
        else:
            # 加载语料文件
            self.load_corpus_path()

            for i, p in enumerate(self.corpus_path):
                print_end = '\n' if i == len(self.corpus_path) - 1 else '\r'
                print("Loading chn corpus: {}/{}".format(i + 1, len(self.corpus_path)), end=print_end)
                with open(p, encoding='utf-8') as f:
                    whole_line = f.readline()

                # 在 crnn/libs/label_converter 中 encode 时还会进行过滤
                whole_line = ''.join(filter(lambda x: x in self.charsets, whole_line))

                if len(whole_line) > self.length:
                    self.corpus.append(whole_line)

    def get_sample(self, img_index):
        if self.mongo:
            skip = np.random.randint(self.document_count - 1)
            article = self.col.find().skip(skip).limit(1).next()["article"]
            start = np.random.randint(0, len(article) - self.length)
            word = article[start: start + self.length]
            return word
        else:
            # 每次 gen_word，随机选一个预料文件，随机获得长度为 word_length 的字符
            line = random.choice(self.corpus)

            start = np.random.randint(0, len(line) - self.length)

            word = line[start:start + self.length]
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
