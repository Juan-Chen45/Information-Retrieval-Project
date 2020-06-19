import math
import os
import re
import json
import pickle


def init():
    doc_len_bm25 = {}
    listFile = os.walk(r"IRProjectDataLinguisted")
    reg = r"data(\d+)\.json"
    for dirPath, dirName, fileName in listFile:
        fileName = sorted(fileName, key=lambda x: int(re.search(reg, x).group(1)))
        for i in range(len(fileName)):
            print(os.path.join(dirPath, fileName[i]))
            build_doc_len(os.path.join(dirPath, fileName[i]), i + 1, doc_len_bm25)
    storeIndex(doc_len_bm25)

def build_doc_len(fileName, doc_id, dic):
    with open(fileName, "r", encoding="utf-8")as f:
        length = len(json.load(f)["text"])
        dic[doc_id] = length



def storeIndex(dic):
    with open(r"Index/bm25lenindex", "wb")as f:
        pickle.dump(dic, f)


def loadIndex():
    with open(r"Index/bm25lenindex", "rb")as f:
        return pickle.load(f)


def loaddict():
    with open(r"Index/VectorIndex", "rb")as f:
        temp = pickle.load(f)
        for k in temp.keys():
            temp[k] = temp[k][1:]
    return temp


def search(query):
    doc_len = loadIndex()
    dictionary = loaddict()

    bm25 = BM25(query, doc_len, dictionary)
    scores = bm25.simall()
    scores = sorted(scores, key=lambda x: x[1], reverse=True)
    ans = []
    if len(scores) > 1001:
        for i in range(1000):
            ans.append(scores[i][0])
        return ans
    else:
        for i in range(len(scores)):
            ans.append(scores[i][0])
        return ans


class BM25:
    def __init__(self, query, doc_len, dictionary):
        self.D = len(doc_len)
        self.avgdl = sum(doc_len) / self.D
        self.idf = {}
        self.k1 = 1.5
        self.b = 0.75
        self.query = query
        self.doc_len = doc_len
        self.dictionary = dictionary
        self.init()

    def init(self):
        for k, v in self.dictionary.items():
            self.idf[k] = math.log(self.D - len(self.dictionary[k]) + 0.5) - math.log(len(self.dictionary[k]) + 0.5)

    def sim(self, doc, index):
        score = 0
        for word in doc:
            flag = False
            idx = 0
            l = self.dictionary.get(word, [])
            for i in range(len(l)):
                if index == l[i][0]:
                    flag = True
                    idx = i
                    break
            if not flag:
                continue
            d = self.doc_len[index]
            score += (self.idf[word] * self.dictionary[word][idx][1] * (self.k1 + 1)
                      / (self.dictionary[word][idx][1] + self.k1 * (1 - self.b + self.b * d / self.avgdl)))
        return tuple([index, score])

    # 这里假设文档ID从1开始
    def simall(self):
        scores = []
        for index in range(self.D):
            score = self.sim(self.query, index + 1)
            scores.append(score)
        return scores


