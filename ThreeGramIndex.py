import pickle
import CompressUtil
'''
This is discarded for the reason that although it's a
correct 3-gram misspell correction,it still has a poor
effect on wrong words
'''

class ThreeGramIndex:
    three_gram_dict = {}
    three_gram_inverted_dict = {}

    @staticmethod
    def init():
        with open(r"Index/BooleanIndex", "rb")as f:
            ThreeGramIndex.three_gram_inverted_dict = pickle.load(f)
            for k, v in ThreeGramIndex.three_gram_inverted_dict.items():
                ThreeGramIndex.three_gram_inverted_dict[k] = CompressUtil.vbdecode(
                    ThreeGramIndex.three_gram_inverted_dict[k])
        ThreeGramIndex.process()
        ThreeGramIndex.sortIndex()
        ThreeGramIndex.storeIndex()
        ThreeGramIndex.releaseSpace()

    @staticmethod
    def function(grams_reference, grams_model):  # grams_reference为可能的单词的3-gram集，grams_model为query的3-gram集
        common_gram = 0
        for i in grams_reference:
            if i in grams_model:
                common_gram = common_gram + 1
        fenmu = len(grams_model) + len(grams_reference) - common_gram  # 并集
        jaccard_coefficient = float(common_gram / fenmu)  # 交集/并集
        return jaccard_coefficient

    @staticmethod
    def process():
        for key in ThreeGramIndex.three_gram_inverted_dict.keys():
            i = 0
            j = 3
            while j <= len(key):
                currstr = key[i:j]
                if ThreeGramIndex.three_gram_dict.__contains__(currstr):
                    ThreeGramIndex.three_gram_dict[currstr].add(key)
                else:
                    ThreeGramIndex.three_gram_dict[currstr] = {key}
                i += 1
                j += 1

    @staticmethod
    def sortIndex():
        for k, v in ThreeGramIndex.three_gram_dict.items():
            ThreeGramIndex.three_gram_dict[k] = sorted(ThreeGramIndex.three_gram_dict[k])

    @staticmethod
    def releaseSpace():
        ThreeGramIndex.three_gram_dict = None

    @staticmethod
    def storeIndex():
        with open(r"Index/ThreeGramIndex", "wb")as f:
            pickle.dump(ThreeGramIndex.three_gram_dict, f)

    @staticmethod
    def loadIndex():
        with open(r"Index/ThreeGramIndex", "rb")as f:
            ThreeGramIndex.three_gram_dict = pickle.load(f)

    @staticmethod
    def getthreegram(str):
        three_gram_list = set()
        i = 0
        j = 3
        while j <= len(str):
            currstr = str[i:j]
            three_gram_list.add(currstr)
            i += 1
            j += 1
        return sorted(three_gram_list)

    @staticmethod
    def correct(query_word):
        if ThreeGramIndex.three_gram_dict is None:
            ThreeGramIndex.loadIndex()
        if query_word.lower() in ThreeGramIndex.three_gram_inverted_dict:
            return query_word.lower()
        else:
            query_three_gram = ThreeGramIndex.getthreegram(query_word.lower())
            ans = []
            currjc = 0
            for i in range(len(query_three_gram)):
                if query_three_gram[i] in ThreeGramIndex.three_gram_dict:
                    for j in range(len(ThreeGramIndex.three_gram_dict[query_three_gram[i]])):
                        tempjc = ThreeGramIndex.function(
                            ThreeGramIndex.getthreegram(ThreeGramIndex.three_gram_dict[query_three_gram[i]][j]),
                            query_three_gram)
                        if tempjc > currjc:
                            for k in range(len(ans)):
                                ans.pop(0)
                            ans.append(ThreeGramIndex.three_gram_dict[query_three_gram[i]][j])
                        elif tempjc == currjc:
                            ans.append(ThreeGramIndex.three_gram_dict[query_three_gram[i]][j])
                        currjc = tempjc
            return set(ans)

if __name__ == "__main__":
    ThreeGramIndex.init()
    print(ThreeGramIndex.correct("various"))
