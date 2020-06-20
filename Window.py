import sys
import json
import re
import MisspellCorrect
from PositionIndex import PositionIndex
from nltk.stem import PorterStemmer
from PyQt5.QtWidgets import *
from PyQt5.QtCore import pyqtSlot, Qt
from PyQt5.Qt import QLineEdit
from VectorSpaceIndex import VectorSpaceIndex
from BooleanIndex import BooleanIndex
from BM25Index import bm25
from WildCardIndex import WildCardIndex
'''
为搜索系统设计的GUI窗口 
'''

class App(QWidget):

    def __init__(self):
        super().__init__()
        self.searchEngine = VectorSpaceIndex
        self.ifCorrect = False
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Searching Engine')
        self.resize(700, 500)
        self.center()
        # 创建选项

        self.rb1 = QRadioButton('布尔检索')
        self.rb2 = QRadioButton('向量空间检索')
        self.rb3 = QRadioButton('BM25')
        self.rb4 = QRadioButton("短语查询(不支持矫正)")
        self.rb6 = QRadioButton("布尔通配符查询(不支持矫正)")
        self.bg1 = QButtonGroup()
        self.bg1.addButton(self.rb1, 1)
        self.bg1.addButton(self.rb2, 2)
        self.bg1.addButton(self.rb3, 3)
        self.bg1.addButton(self.rb4, 4)
        self.bg1.addButton(self.rb6, 5)
        self.bg1.buttonClicked.connect(self.rbclicked)

        self.rb5 = QCheckBox('需要词语矫正')
        self.rb5.stateChanged.connect(self.changestate)

        self.buttonbox = QHBoxLayout()
        self.buttonbox.addWidget(self.rb1)
        self.buttonbox.addWidget(self.rb2)
        self.buttonbox.addWidget(self.rb3)
        self.buttonbox.addWidget(self.rb4)
        self.buttonbox.addWidget(self.rb6)
        self.buttonbox.addWidget(self.rb5)
        # 创建文本框

        self.textbox = QLineEdit()
        self.textbox.resize(280, 40)
        self.button = QPushButton('Search Now ！')
        self.button.clicked.connect(self.on_click)

        # 创建hbox
        self.hbox = QHBoxLayout()
        self.hbox.addWidget(self.textbox)
        self.hbox.addWidget(self.button)
        # 创建列表
        self.listWidget = QListWidget()
        self.listWidget.resize(600, 300)
        self.listWidget.setWindowTitle('Search Result')
        # 单击触发绑定的槽函数
        self.listWidget.itemDoubleClicked.connect(self.clicked)

        # 创建vbox
        self.vbox = QVBoxLayout()
        self.vbox.addLayout(self.buttonbox)
        self.vbox.addLayout(self.hbox)
        self.vbox.addWidget(self.listWidget)
        self.setLayout(self.vbox)
        self.show()

    # 获取该条新闻消息
    def btnClicked(self, title, text):
        self.chile_Win = ChildWindow()
        self.chile_Win.textbox.setText(title + "\n\n" + text)
        self.chile_Win.show()
        self.chile_Win.exec_()

    # 让搜索框居中
    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    # 搜索按钮的单击事件
    @pyqtSlot()
    def on_click(self):
        self.listWidget.clear()
        textboxValue = self.textbox.text()
        ps = PorterStemmer()

        if self.searchEngine is bm25 or self.searchEngine is VectorSpaceIndex:
            textboxValue = textboxValue.lower().split()
            if self.ifCorrect:
                for i in range(len(textboxValue)):
                    textboxValue[i] = ps.stem(MisspellCorrect.correction(textboxValue[i]))
            else:
                for i in range(len(textboxValue)):
                    textboxValue[i] = ps.stem(textboxValue[i])

        if self.searchEngine is BooleanIndex:
            textboxValue = textboxValue.split()
            temp = [str.lower() for str in textboxValue if str != "AND" and str != "OR" and str != "NOT"]
            if self.ifCorrect:
                for i in range(len(temp)):
                    temp[i] = ps.stem(MisspellCorrect.correction(temp[i]))
            else:
                for i in range(len(temp)):
                    temp[i] = ps.stem(temp[i])
            k = 0
            for i in range(len(temp)):
                textboxValue[k] = temp[i]
                k+=2
            textboxValue = ' '.join(textboxValue)

        result = self.searchEngine.search(textboxValue)
        for i in range(len(result)):
            with open(r"IRProjectdata/data" + str(result[i]) + ".json", "r", encoding="utf-8") as f:
                t = json.load(f)["title"]
                self.listWidget.addItem(t + " id=" + str(result[i]))

    # 搜索结果的双击事件
    def clicked(self, item):
        rge = r" id=(\d+)"
        rtvl = re.search(rge, item.text()).group(1)
        with open(r"IRProjectdata/data" + str(rtvl) + ".json", "r", encoding="utf-8")as f:
            temp = json.load(f)
            title = temp["title"]
            text = temp["text"]
            self.btnClicked(title, text)

    # 进行搜索引擎的切换，同时清空内存
    def rbclicked(self):
        if self.bg1.checkedId() == 1:
            self.searchEngine = BooleanIndex
            VectorSpaceIndex.releaseSpace()
            PositionIndex.releasespace()
            bm25.releasespace()
            WildCardIndex.releasespace()
        elif self.bg1.checkedId() == 2:
            self.searchEngine = VectorSpaceIndex
            BooleanIndex.releaseSpace()
            PositionIndex.releasespace()
            bm25.releasespace()
            WildCardIndex.releasespace()
        elif self.bg1.checkedId() == 3:
            self.searchEngine = bm25
            VectorSpaceIndex.releaseSpace()
            BooleanIndex.releaseSpace()
            PositionIndex.releasespace()
            WildCardIndex.releasespace()
        elif self.bg1.checkedId() == 4:
            self.searchEngine = PositionIndex
            VectorSpaceIndex.releaseSpace()
            BooleanIndex.releaseSpace()
            bm25.releasespace()
            WildCardIndex.releasespace()
        elif self.bg1.checkedId() == 5:
            self.searchEngine = WildCardIndex
            PositionIndex.releasespace()
            VectorSpaceIndex.releaseSpace()
            BooleanIndex.releaseSpace()
            bm25.releasespace()

    def changestate(self):
        if self.rb5.isChecked():
            self.ifCorrect = True
        else:
            self.ifCorrect = False

# 用于显示正文内容的子窗口
class ChildWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowFlags(Qt.WindowCloseButtonHint)
        self.setWindowTitle('子窗口')
        self.resize(800, 400)
        self.textbox = QTextEdit(self)
        self.textbox.resize(800, 400)
        self.show()

    def setText(self, text):
        self.textbox.setText(text)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    app.exit(app.exec_())
