import os
import re
import json
import math
import pickle
import collections

class VectorSpaceIndex:

    vertor_space_index = None
    doc_len = None
    cnt = 0

    @staticmethod
    def init():
        VectorSpaceIndex.vertor_space_index = {}
        VectorSpaceIndex.doc_len = {}
        listFile = os.walk(r"IRProjectDataLinguisted")
        reg = r"data(\d+)\.json"
        for dirPath, dirName, fileName in listFile:
            fileName = sorted(fileName, key=lambda x: int(re.search(reg, x).group(1)))
            for i in range(len(fileName)):
                print(os.path.join(dirPath, fileName[i]))
                VectorSpaceIndex.cnt += 1
                VectorSpaceIndex.constructVerctorIndex(os.path.join(dirPath, fileName[i]), i + 1)
        VectorSpaceIndex.sortIndex()
        VectorSpaceIndex.storeIndex()
        VectorSpaceIndex.releaseSpace()

    @staticmethod
    def constructVerctorIndex(fileName, doc_id):
        with open(fileName, "r", encoding="utf-8")as f:
            temp = json.load(f)["text"]
            for str in temp:
                if (VectorSpaceIndex.vertor_space_index.__contains__(str)):
                    if doc_id in VectorSpaceIndex.vertor_space_index[str]:
                        VectorSpaceIndex.vertor_space_index[str][doc_id] += 1
                    else:
                        VectorSpaceIndex.vertor_space_index[str][doc_id] = 1
                else:
                    VectorSpaceIndex.vertor_space_index[str] = {doc_id: 1}

    @staticmethod
    def sortIndex():
        for k, v in VectorSpaceIndex.vertor_space_index.items():
            curr = [len(VectorSpaceIndex.vertor_space_index[k])]
            curr.extend(sorted([[x, y] for x, y in VectorSpaceIndex.vertor_space_index[k].items()], key=lambda z: z[0]))
            VectorSpaceIndex.vertor_space_index[k] = curr

        for k, v in VectorSpaceIndex.vertor_space_index.items():
            idf = math.log(VectorSpaceIndex.cnt / VectorSpaceIndex.vertor_space_index[k][0], 10)
            for i in range(len(VectorSpaceIndex.vertor_space_index[k])):
                if i == 0:
                    continue
                tf = (1 + math.log(VectorSpaceIndex.vertor_space_index[k][i][1], 10))
                VectorSpaceIndex.doc_len[VectorSpaceIndex.vertor_space_index[k][i][0]] = VectorSpaceIndex.doc_len.get(
                    VectorSpaceIndex.vertor_space_index[k][i][0], 0) + idf * tf * idf * tf

    @staticmethod
    def storeIndex():
        with open(r"Index/VectorIndex", "wb")as f:
            pickle.dump(VectorSpaceIndex.vertor_space_index, f)
        with open(r"Index/VectorIndexDocLen", "wb")as f:
            pickle.dump(VectorSpaceIndex.doc_len, f)
        with open(r"Index/Vectorcnt","wb")as f:
            pickle.dump(VectorSpaceIndex.cnt,f)

    @staticmethod
    def loadIndex():
        with open(r"Index/VectorIndex", "rb")as f:
            VectorSpaceIndex.vertor_space_index = pickle.load(f)
        with open(r"Index/VectorIndexDocLen", "rb")as f:
            VectorSpaceIndex.doc_len = pickle.load(f)
        with open(r"Index/Vectorcnt","rb")as f:
            VectorSpaceIndex.cnt = pickle.load(f)

    @staticmethod
    def releaseSpace():
        VectorSpaceIndex.vertor_space_index = None
        VectorSpaceIndex.doc_len = None

    @staticmethod
    def search(query):
        if VectorSpaceIndex.doc_len is None or VectorSpaceIndex.vertor_space_index is None:
            VectorSpaceIndex.loadIndex()

        listToBeProcess = []
        for i in range(len(query)):
            listToBeProcess.append(VectorSpaceIndex.vertor_space_index.get(query[i], []))
        counter = set()
        for i in range(len(listToBeProcess)):
            for k in range(len(listToBeProcess[i])):
                if k == 0:
                    continue
                else:
                    counter.add(listToBeProcess[i][k][0])
        grade = {}
        for i in counter:
            grade[i] = 0
        querycount = collections.Counter(query)
        for i in range(len(listToBeProcess)):
            for k in range(len(listToBeProcess[i])):
                if k == 0:
                    continue
                idf = math.log(VectorSpaceIndex.cnt / listToBeProcess[i][0], 10)
                doc_vector = idf * (1 + math.log(listToBeProcess[i][k][1], 10))
                query_vector = (1 + math.log(querycount[query[i]], 10)) * idf
                grade[listToBeProcess[i][k][0]] += doc_vector * query_vector

        rank = []
        for k, v in grade.items():
            grade[k] = grade[k] / math.sqrt(VectorSpaceIndex.doc_len[k])
            rank.append((k, grade[k]))

        rank = [x[0] for x in sorted(rank, key=lambda x: x[1], reverse=True)]

        if len(rank)>1001:
            return rank[:1000]
        else:
            return rank


if __name__ == "__main__":
    # VectorSpaceIndex.init()
    print(VectorSpaceIndex.search("cnbc"))
