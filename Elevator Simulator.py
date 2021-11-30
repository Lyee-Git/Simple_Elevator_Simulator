import sys
import time
from functools import partial
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

#图形界面设置
class Window(QWidget):

    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        mylayout = QHBoxLayout()
        gridleft = QGridLayout()
        grid = QGridLayout()
        grid.setSpacing(0)
        gridleft.setSpacing(0)
        globalwg = QWidget()  # 准备左右侧两各个部件
        leftwg = QWidget()
        leftwg.setLayout(gridleft) # 部件设置局部布局
        globalwg.setLayout(grid)
        mylayout.addWidget(leftwg) # 部件加至全局布局
        mylayout.addWidget(globalwg)
        self.setLayout(mylayout)  # 窗体本体设置全局布局
        names = [('%s' % i) for i in range(1, 21)]  # 电梯按钮编号
        positions = [(i, j) for j in range(2) for i in range(10)]  # 位置
        nameforup = [('▲ %s' % i) for i in range(1, 21)]  # 各楼层控制面板的按钮
        namefordown = [('▼ %s' % i) for i in range(1, 21)]
        # -------左侧布局设置----------#

        j = 0
        for i in nameforup:
            self.button = QPushButton(i)
            self.button.setFont(QFont("Microsoft YaHei"))
            self.button.setObjectName("up{0}".format(j + 1))
            self.button.setMinimumHeight(42)
            gridleft.addWidget(self.button, 20 - j, 0)
            j = j + 1

        j = 0
        for i in namefordown:
            self.button = QPushButton(i)
            self.button.setFont(QFont("Microsoft YaHei"))
            self.button.setObjectName("down{0}".format(j + 1))
            self.button.setMinimumHeight(42)
            gridleft.addWidget(self.button, 20 - j, 1)
            j = j + 1

        # -------右侧布局设置----------#

        # 数字显示
        for i in range(4):
            self.lcd = QLCDNumber()
            self.lcd.setObjectName("{0}".format(i + 1))
            grid.addWidget(self.lcd, 0, 3 * i, 2, 2)

        #电梯内按钮显示
        for m in range(4):
            n = 1
            for position, name in zip(positions, names):
                self.button = QPushButton(name)
                self.button.setObjectName("floor{0}+{1}".format(m + 1, n))
                self.button.setFont(QFont("Microsoft YaHei", 10))
                self.button.setMaximumHeight(60)  # 按钮最大高度
                grid.addWidget(self.button, position[0] + 2, position[1] + m * 3)
                n = n + 1

        #暂停按钮
        for i in range(4):
            self.button = QPushButton("暂停")
            self.button.setFont(QFont("Microsoft YaHei", 12))
            self.button.setObjectName("pause{0}".format(i + 1))
            self.button.setMinimumHeight(40)
            grid.addWidget(self.button, 12, 3 * i, 1, 2)

        #用于OPEN显示的按钮
        for i in range(4):
            self.button = QPushButton()
            self.button.setObjectName("open{0}".format(i + 1))
            self.button.setMinimumHeight(80)
            grid.addWidget(self.button, 13, 3 * i, 1, 2)

        self.setWindowTitle('Elevator Simulator For OS Lab2')
        self.show()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    mywindow = Window()
    sys.exit(app.exec_())