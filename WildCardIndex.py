import _pickle as Cpickle
import re
import os
import json
'''
直接使用了正则表达式的方式去进行通配符匹配
3-Gram索引构建空间过大，因此转而用正则进行匹配
'''

class WildCardIndex:
    wildcard_index = None

    @staticmethod
    def init():
        WildCardIndex.wildcard_index = {}
        listFile = os.walk(r"IRProjectdata")
        reg = r"data(\d+)\.json"
        for dirPath, dirName, fileName in listFile:
            fileName = sorted(fileName, key=lambda x: int(re.search(reg, x).group(1)))
            for i in range(len(fileName)):
                print(os.path.join(dirPath, fileName[i]))
                WildCardIndex.construct(os.path.join(dirPath, fileName[i]), i + 1)
        WildCardIndex.storeindex()
        WildCardIndex.releasespace()

    @staticmethod
    def construct(fileName, doc_id):
        with open(fileName, "r", encoding="utf-8")as f:
            temp = json.load(f)["text"].split()
            for i in range(len(temp)):
                if temp[i] in WildCardIndex.wildcard_index:
                    WildCardIndex.wildcard_index[temp[i]].add(doc_id)
                else:
                    WildCardIndex.wildcard_index[temp[i]] = set(doc_id)

    @staticmethod
    def releasespace():
        WildCardIndex.wildcard_index = None

    @staticmethod
    def loadindex():
        with open(r"Index/wildcardindex", "rb")as f:
            WildCardIndex.wildcard_index = Cpickle.load(f)

    @staticmethod
    def storeindex():
        with open(r"Index/wildcardindex", "wb")as f:
            Cpickle.dump(WildCardIndex.wildcard_index, f)

    @staticmethod
    def findwordsdoc(rg):
        ans = set()
        for k in WildCardIndex.wildcard_index.keys():
            if re.match(rg, k):
                ans = ans | WildCardIndex.wildcard_index[k]
        return ans

    @staticmethod
    def AND(currList, newList):
        return currList & newList

    @staticmethod
    def OR(currList, newList):
        return currList | newList

    @staticmethod
    def NOT(currList, newList):
        return currList - newList

    @staticmethod
    def search(query):
        if WildCardIndex.wildcard_index is None:
            WildCardIndex.loadindex()
        query_list = query.split()
        str_list = [str for str in query_list if str != "AND" and str != "OR" and str != "NOT"]
        str_doc_list = []

        for str in str_list:
            if "*" in str:
                str_doc_list.append(WildCardIndex.findwordsdoc(str.replace("*",".*")))
            else:
                str_doc_list.append(WildCardIndex.wildcard_index.get(str, {}))

        i = 1
        j = 1
        rtn = str_doc_list[0]
        while j < len(query_list) and i < len(str_doc_list):
            if query_list[j] == "AND":
                rtn = WildCardIndex.AND(rtn, str_doc_list[i])
            elif query_list[j] == "OR":
                rtn = WildCardIndex.OR(rtn, str_doc_list[i])
            elif query_list[j] == "NOT":
                rtn = WildCardIndex.NOT(rtn, query_list[i])
            i += 1
            j += 2

        return list(rtn)

if __name__ == "__main__":
    # WildCardIndex.init()
    print(WildCardIndex.search("bi*in"))
