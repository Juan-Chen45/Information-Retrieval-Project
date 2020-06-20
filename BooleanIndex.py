import os
import re
import json
import _pickle as Cpickle
import CompressUtil
'''
实现布尔查询算法
'''
class BooleanIndex:

    boolean_index_text_dic = None

    @staticmethod
    def init():
        BooleanIndex.boolean_index_text_dic = {}
        listFile = os.walk(r"IRProjectDataLinguisted")
        reg = r"data(\d+)\.json"
        for dirPath, dirName, fileName in listFile:
            fileName = sorted(fileName, key=lambda x: int(re.search(reg, x).group(1)))
            for i in range(len(fileName)):
                print(os.path.join(dirPath, fileName[i]))
                BooleanIndex.constructBooleanIndex(os.path.join(dirPath, fileName[i]), i + 1)
        BooleanIndex.sortIndex()
        BooleanIndex.storeIndex()
        BooleanIndex.releaseSpace()

    @staticmethod
    def constructBooleanIndex(fileName, doc_id):
        with open(fileName, "r", encoding="utf-8") as f:
            temp = json.load(f)["text"]
            for str in temp:
                if str in BooleanIndex.boolean_index_text_dic:
                    BooleanIndex.boolean_index_text_dic[str].add(doc_id)
                else:
                    BooleanIndex.boolean_index_text_dic[str] = {doc_id}

    @staticmethod
    def sortIndex():
        for k, v in BooleanIndex.boolean_index_text_dic.items():
            BooleanIndex.boolean_index_text_dic[k] = sorted(BooleanIndex.boolean_index_text_dic[k])

    @staticmethod
    def storeIndex():
        with open(r"Index/BooleanIndex", "wb")as f:
            # for k,v in BooleanIndex.boolean_index_text_dic.items():
            #     BooleanIndex.boolean_index_text_dic[k] = CompressUtil.vbencode(BooleanIndex.boolean_index_text_dic[k])
            Cpickle.dump(BooleanIndex.boolean_index_text_dic, f)

    @staticmethod
    def loadIndex():
        with open(r"Index/BooleanIndex", "rb")as f:
            BooleanIndex.boolean_index_text_dic = Cpickle.load(f)
            # for k,v in BooleanIndex.boolean_index_text_dic.items():
            #     BooleanIndex.boolean_index_text_dic[k] = CompressUtil.vbdecode(BooleanIndex.boolean_index_text_dic[k])

    @staticmethod
    def releaseSpace():
        BooleanIndex.boolean_index_text_dic = None

    @staticmethod
    def search(query):
        if BooleanIndex.boolean_index_text_dic is None:
            BooleanIndex.loadIndex()
        queryList = query.split()
        currList = []
        currOpe = ''
        for i in range(len(queryList)):
            if i & 1 == 0:
                newList = BooleanIndex.boolean_index_text_dic.get(queryList[i].lower(), [])
                if currOpe == '':
                    pass
                else:
                    if currOpe == 'AND':
                        newList = AND(currList, newList)
                    elif currOpe == 'OR':
                        newList = OR(currList, newList)
                    elif currOpe == 'NOT':
                        newList = NOT(currList, newList)
                    else:
                        pass
            else:
                currOpe = queryList[i]
            currList = newList

        if len(currList)>1001:
            return currList[:1000]
        else:
            return currList


def AND(currList, newList):
    ans = []
    i = 0
    j = 0
    while (i < len(currList) and j < len(newList)):
        if (currList[i] == newList[j]):
            ans.append(currList[i])
            i += 1
            j += 1
        elif (currList[i] < newList[j]):
            i += 1
        else:
            j += 1
    return ans


def OR(currList, newList):
    set1 = set(currList)
    set2 = set(newList)
    return sorted(set1 | set2)


def NOT(currList, newList):
    set1 = set(currList)
    set2 = set(newList)
    return sorted(set1 - set2)


if __name__ == "__main__":
    # BooleanIndex.init()
    print(BooleanIndex.search("I"))
