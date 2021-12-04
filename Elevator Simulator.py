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
        grid.setSpacing(1)
        gridleft.setSpacing(0)
        globalwg = QWidget()  # 准备左右侧两各个部件
        leftwg = QWidget()
        leftwg.setLayout(gridleft) # 部件设置局部布局
        globalwg.setLayout(grid)
        mylayout.addWidget(leftwg) # 部件加至全局布局
        mylayout.addWidget(globalwg)
        self.setLayout(mylayout)  # 窗体本体设置全局布局
        names = [('%s' % i) for i in range(1, 21)]  # 电梯按钮编号
        positions = [(i, j) for j in range(2) for i in range(10)]  # 按钮对应的位置
        nameforup = [('▲ %s' % i) for i in range(1, 21)]  # 各楼层控制面板的按钮
        namefordown = [('▼ %s' % i) for i in range(1, 21)]
        # -------左侧布局设置----------#

        j = 0
        for i in nameforup:
            self.button = QPushButton(i)
            self.button.setFont(QFont("Microsoft JhengHei"))
            self.button.setObjectName("up{0}".format(j + 1))
            self.button.setMinimumHeight(42)
            gridleft.addWidget(self.button, 20 - j, 0)
            j = j + 1

        j = 0
        for i in namefordown:
            self.button = QPushButton(i)
            self.button.setFont(QFont("Microsoft JhengHei"))
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
                self.button.setFont(QFont("Microsoft JhengHei", 10))
                self.button.setMaximumHeight(60)  # 按钮最大高度
                grid.addWidget(self.button, position[0] + 2, position[1] + m * 3)
                n = n + 1

        #暂停按钮
        for i in range(4):
            self.button = QPushButton("暂停")
            self.button.setFont(QFont("Microsoft JhengHei", 12))
            self.button.setObjectName("pause{0}".format(i + 1))
            self.button.setMinimumHeight(60)
            grid.addWidget(self.button, 12, 3 * i, 1, 2)

        #用于OPEN显示的按钮
        for i in range(4):
            self.button = QPushButton()
            self.button.setObjectName("open{0}".format(i + 1))
            self.button.setMinimumHeight(60)
            grid.addWidget(self.button, 13, 3 * i, 1, 2)

        #Global Setting
        self.setGeometry(100, 100, 300, 220)
        self.setWindowTitle('Elevator Simulator For OS Lab2')
        self.show()

#本次lab利用pyqt线程来模拟四部电梯的运行
class ElevatorThread(QThread):

    trigger = pyqtSignal(int)

    def __init__(self, _num):
        super(ElevatorThread, self).__init__()
        self.num = _num
        self.trigger.connect(check_change_elev_floor)

    def run(self):
        while (1):
            if reach_floor_up[self.num - 1] == 1 or reach_floor_down[self.num - 1] == 1:
                ex.findChild(QPushButton, "open{0}".format(self.num)).setStyleSheet("QPushButton{background-image: url(open.png)}")
                time.sleep(5)
                ex.findChild(QPushButton, "open{0}".format(self.num)).setStyleSheet("QPushButton{}")
                if(reach_floor_up[self.num - 1]):
                    reach_floor_up[self.num - 1] = 0
                else:
                    reach_floor_down[self.num - 1] = 0
            self.trigger.emit(self.num)
            time.sleep(1)

def check_change_elev_floor(num):
    pass

def pause(num):
    if pause[num - 1] == 1:
        pause[num - 1] = 0
        ex.findChild(QPushButton, "pause{0}".format(num)).setText("暂停")
    else:
        pause[num - 1] = 1
        ex.findChild(QPushButton, "pause{0}".format(num)).setText("启动")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    mywindow = Window()

    #电梯状态 停止：0 上升：1 下降：-1
    elevator_state = []
    for i in range(4):
        elevator_state.append(0)

    #电梯当前的楼层
    elevator_floor = []
    for i in range(4):
        elevator_floor.append(1)

    #电梯是否暂停运行（不再提供服务）
    pause = []
    for i in range(4):
        elevator_floor.append(0)

    #电梯上升时到达目标楼层后应当开门
    reach_floor_up = [0, 0, 0, 0]

    # 电梯下降时到达目标楼层后应当开门
    reach_floor_down = [0, 0, 0, 0]

    #楼道里向上的请求
    floor_request_up = set([])

    #楼道里向下的请求
    floor_request_up = set([])

    #电梯内用户请求
    elevator_goal1 = set([])
    elevator_goal2 = set([])
    elevator_goal3 = set([])
    elevator_goal4 = set([])
    elevator_goal = [elevator_goal1, elevator_goal2, elevator_goal3, elevator_goal4]

    sys.exit(app.exec_())