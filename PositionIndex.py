import os
import re
import json
import _pickle as Cpickle
'''
使用位置信息索引来进行短语查询
'''

class PositionIndex:
    position_index = None

    @staticmethod
    def init():
        PositionIndex.position_index = {}
        listFile = os.walk(r"IRProjectdata")
        reg = r"data(\d+)\.json"
        for dirPath, dirName, fileName in listFile:
            fileName = sorted(fileName, key=lambda x: int(re.search(reg, x).group(1)))
            for i in range(len(fileName)):
                print(os.path.join(dirPath, fileName[i]))
                PositionIndex.construct(os.path.join(dirPath, fileName[i]), i + 1)
        PositionIndex.storePositionIndex()
        PositionIndex.releasespace()

    @staticmethod
    def construct(fileName, doc_id):
        with open(fileName, "r", encoding="utf-8")as f:
            temp = json.load(f)["text"].split()
            for i in range(len(temp)):
                if temp[i] in PositionIndex.position_index:
                    if doc_id in PositionIndex.position_index[temp[i]]:
                        PositionIndex.position_index[temp[i]][doc_id].append(i + 1)
                    else:
                        PositionIndex.position_index[temp[i]][doc_id] = [i + 1]
                else:
                    PositionIndex.position_index[temp[i]] = {doc_id: [i + 1]}


    @staticmethod
    def storePositionIndex():
        with open(r"Index/positionindex", "wb")as f:
            Cpickle.dump(PositionIndex.position_index, f)


    @staticmethod
    def loadIndex():
        with open(r"Index/positionindex", "rb")as f:
            PositionIndex.position_index = Cpickle.load(f)


    @staticmethod
    def releasespace():
        PositionIndex.position_index = None

    @staticmethod
    def getProcessList(query_list):
        re = []
        i = 0
        j = 2
        while j < len(query_list):
            re.append(query_list[i:j])
            i += 1
            j += 1
        return re

    @staticmethod
    def AND(partial_list):
        # first = PositionIndex.inverted_index[partial_list[0]]
        first = set(PositionIndex.position_index[partial_list[0]].keys())
        # second = PositionIndex.inverted_index[partial_list[1]]
        second = set(PositionIndex.position_index[partial_list[1]].keys())

        help_list = first & second
        return_list = []
        for i in help_list:
            pos_first = PositionIndex.position_index[partial_list[0]][i]
            pos_second = PositionIndex.position_index[partial_list[1]][i]
            if PositionIndex.futherAND(pos_first, pos_second):
                return_list.append(i)
        return return_list

    def futherAND(currList, newList):
        ans = False
        i = 0
        j = 0
        while (i < len(currList) and j < len(newList)):
            if (currList[i] == newList[j] - 1):
                ans = True
                break
            elif (currList[i] < newList[j] - 1):
                i += 1
            else:
                j += 1
        return ans

    @staticmethod
    def search(query):
        if PositionIndex.position_index is None :
            PositionIndex.loadIndex()
        query_list = PositionIndex.getProcessList(query.split())
        result_list = []
        for i in range(len(query_list)):
            if i == 0:
                result_list = PositionIndex.AND(query_list[i])
            else:
                result_list = set(result_list) & set(PositionIndex.AND(query_list[i]))
        return list(result_list)



