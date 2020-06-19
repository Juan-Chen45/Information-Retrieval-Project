import os
import json
import nltk
import BooleanIndex
import VectorSpaceIndex
import BM25Index
import PositionIndex
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer

# Used to filter out some useless information in IRProjectRawData
# only save the title and text of the news into IRProjectData

all_files = []
listFile = os.walk(r"IRProjectRawData")
for dirPath, dirName, fileName in listFile:
    for names in fileName:
        all_files.append(os.path.join(dirPath, names))

os.mkdir("IRProjectdata")
cnt = 0
for i in range(len(all_files)):
    with open(all_files[i], mode="r", encoding="utf-8") as f1:
        temp = json.loads(f1.read())
        map = {"title": temp["title"], "text": temp["text"]}
        with open(r"IRProjectdata/data" + str(cnt + 1) + ".json", mode="w", encoding="utf-8") as f2:
            json.dump(map, f2)
            cnt += 1
    print("Processing raw file " + str(i))

os.mkdir("IRProjectDataLinguisted")
os.mkdir(r"Index")

ps = PorterStemmer()
for i in range(len(all_files)):
    with open(r"IRProjectdata/data" + str(cnt) + ".json", mode="r", encoding="utf-8") as f1:
        map = json.load(f1)
        stop_words = set(stopwords.words("english"))
        puct = {",", ".", "'", "!", ":", "?", "|", "''"}
        puretitle = [ps.stem(x).lower() for x in nltk.word_tokenize(map["title"]) if x.lower() not in puct]
        puretext = [ps.stem(x).lower() for x in nltk.word_tokenize(map["text"]) if x.lower()  not in puct]
        temp = {"title": puretitle, "text": puretext}
        with open(r"IRProjectDataLinguisted/data" + str(cnt) + ".json", mode="w", encoding="utf-8") as f2:
            json.dump(temp, f2)
            cnt -= 1
    print("Processing LinguistFile " + str(cnt))


BooleanIndex.BooleanIndex.init()
VectorSpaceIndex.VectorSpaceIndex.init()
BM25Index.init()
PositionIndex.PositionIndex.init()
