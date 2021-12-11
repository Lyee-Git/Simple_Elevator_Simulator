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
        positions = [(i, j) for i in range(10) for j in range(2) ]  # 按钮对应的位置
        nameforup = [('▲ %s' % i) for i in range(1, 21)]  # 各楼层控制面板的按钮
        namefordown = [('▼ %s' % i) for i in range(1, 21)]
        # -------左侧布局设置----------#

        num = 0
        for i in nameforup:
            self.button = QPushButton(i)
            self.button.setFont(QFont("Microsoft JhengHei"))
            self.button.setObjectName("up{0}".format(num + 1))
            self.button.clicked.connect(partial(set_goal_outside_up, num + 1))
            self.button.setMinimumHeight(42)
            gridleft.addWidget(self.button, 20 - num, 0)
            num = num + 1

        num = 0
        for i in namefordown:
            self.button = QPushButton(i)
            self.button.setFont(QFont("Microsoft JhengHei"))
            self.button.setObjectName("down{0}".format(num + 1))
            self.button.clicked.connect(partial(set_goal_outside_down, num + 1))
            self.button.setMinimumHeight(42)
            gridleft.addWidget(self.button, 20 - num, 1)
            num = num + 1

        # -------右侧布局设置----------#

        # 数字显示
        for i in range(4):
            self.lcd = QLCDNumber()
            self.lcd.setObjectName("{0}".format(i + 1))
            grid.addWidget(self.lcd, 0, 3 * i, 1, 2)
            #间隙
            self.spacing = QLabel()
            grid.addWidget(self.spacing, 0, 3 * i + 2, 1, 1)

        #电梯内按钮显示
        for m in range(4):
            n = 1
            for position, name in zip(positions, names):
                self.button = QPushButton(name)
                self.button.setObjectName("floor{0}+{1}".format(m + 1, n))
                self.button.clicked.connect(partial(set_goal_inside, m + 1, n))
                self.button.setFont(QFont("Microsoft JhengHei", 10))
                self.button.setMinimumHeight(60)  # 按钮最大高度
                grid.addWidget(self.button, 11 - position[0], position[1] + m * 3)
                n = n + 1

        #暂停按钮
        for i in range(4):
            self.button = QPushButton("暂停")
            self.button.setFont(QFont("Microsoft JhengHei", 12))
            self.button.setObjectName("pause{0}".format(i + 1))
            self.button.clicked.connect(partial(stop, i + 1))
            self.button.setMinimumHeight(40)
            grid.addWidget(self.button, 12, 3 * i, 1, 2)

        #开关门按钮
        for i in range(4):
            self.button = QPushButton("◀▶")
            self.button.setFont(QFont("Microsoft JhengHei", 12))
            self.button.setObjectName("opendoor{0}".format(i + 1))
            self.button.clicked.connect(partial(opendoor, i + 1))
            self.button.setMinimumHeight(40)
            grid.addWidget(self.button, 13, 3 * i, 1, 1)

        for i in range(4):
            self.button = QPushButton("▶◀")
            self.button.setFont(QFont("Microsoft JhengHei", 12))
            self.button.setObjectName("closedoor{0}".format(i + 1))
            self.button.clicked.connect(partial(closedoor, i + 1))
            self.button.setMinimumHeight(40)
            grid.addWidget(self.button, 13, 3 * i + 1, 1, 1)

        #用于OPEN显示的按钮
        for i in range(4):
            self.button = QPushButton()
            self.button.setObjectName("open{0}".format(i + 1))
            self.button.setFont(QFont("Microsoft JhengHei", 12))
            self.button.setMinimumHeight(40)
            grid.addWidget(self.button, 14, 3 * i, 1, 2)

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
                mywindow.findChild(QPushButton, "open{0}".format(self.num)).setText("OPEN")
                mywindow.findChild(QPushButton, "open{0}".format(self.num)).setStyleSheet("QPushButton{background-image: url(background.png)}")
                for i in range(20):
                    if close_door[self.num - 1]:
                        close_door[self.num - 1] = 0
                        break
                    time.sleep(0.2)
                mywindow.findChild(QPushButton, "open{0}".format(self.num)).setText("")
                mywindow.findChild(QPushButton, "open{0}".format(self.num)).setStyleSheet("QPushButton{}")
                if(reach_floor_up[self.num - 1]):
                    reach_floor_up[self.num - 1] = 0
                else:
                    reach_floor_down[self.num - 1] = 0
            self.trigger.emit(self.num)
            time.sleep(0.8)

#主要算法:控制电梯目标、状态的改变
#连接到电梯的线程上  循环执行
def check_change_elev_floor(num):
    if stop[num - 1] == 1:
        pass
    else:
        #到达楼道设定的楼层后，需要转向
        floor[num - 1] += state[num - 1]
        mywindow.findChild(QLCDNumber, "{0}".format(num)).display(floor[num - 1])

        # 对来自内部目标的响应与检查
        reach_inside_goal = not floor[num - 1] in elev_goal_outside_up and not floor[num - 1] in elev_goal_outside_down
        if floor[num - 1] in elev_goal[num - 1] and reach_inside_goal:
            if state[num - 1] == 1:
                reach_floor_up[num - 1] = 1
            else:
                reach_floor_down[num - 1] = 1
            elev_goal[num - 1].discard(floor[num - 1])
            mywindow.findChild(QPushButton, "floor{0}+{1}".format(num, floor[num - 1])).setStyleSheet("QPushButton{}")


        # 对来自外部目标的响应与检查
        if (floor[num - 1] in elev_goal_outside_up and floor[num - 1] in elev_goal[num - 1]):
            if state[num - 1] == 1 or state[num - 1] == 0:
                reach_floor_up[num - 1] = 1
                mywindow.findChild(QPushButton, "up{0}".format(floor[num - 1])).setStyleSheet("QPushButton{}")
                #可能该外部目标同时也是内部目标
                mywindow.findChild(QPushButton, "floor{0}+{1}".format(num, floor[num - 1])).setStyleSheet("QPushButton{}")
                elev_goal[num - 1].discard(floor[num - 1])
                elev_goal_outside_up.discard(floor[num - 1])
            # 特殊情况处理：当下行时恰好接到来自楼道的上行命令，也应该清除对应按钮的按下状态
            elif state[num - 1] == -1 and floor[num - 1] == min(elev_goal[num - 1]):
                reach_floor_down[num - 1] = 1
                mywindow.findChild(QPushButton, "up{0}".format(floor[num - 1])).setStyleSheet("QPushButton{}")
                mywindow.findChild(QPushButton, "floor{0}+{1}".format(num, floor[num - 1])).setStyleSheet("QPushButton{}")
                elev_goal[num - 1].discard(floor[num - 1])
                elev_goal_outside_up.discard(floor[num - 1])

        if (floor[num - 1] in elev_goal_outside_down and floor[num - 1] in elev_goal[num - 1]):
            if state[num - 1] == -1 or state[num - 1] == 0:
                reach_floor_down[num - 1] = 1
                mywindow.findChild(QPushButton, "down{0}".format(floor[num - 1])).setStyleSheet("QPushButton{}")
                mywindow.findChild(QPushButton, "floor{0}+{1}".format(num, floor[num - 1])).setStyleSheet("QPushButton{}")
                elev_goal[num - 1].discard(floor[num - 1])
                elev_goal_outside_down.discard(floor[num - 1])
            # 特殊情况处理：当上行时恰好接到来自楼道的下行命令，也应该清除对应按钮的按下状态
            elif state[num - 1] == 1 and floor[num - 1] == max(elev_goal[num - 1]):
                reach_floor_up[num - 1] = 1
                mywindow.findChild(QPushButton, "down{0}".format(floor[num - 1])).setStyleSheet("QPushButton{}")
                mywindow.findChild(QPushButton, "floor{0}+{1}".format(num, floor[num - 1])).setStyleSheet("QPushButton{}")
                elev_goal[num - 1].discard(floor[num - 1])
                elev_goal_outside_down.discard(floor[num - 1])

        # 状态改变算法
        if state[num - 1] == 0:
            if len(list(elev_goal[num - 1])) != 0 and (max(list(elev_goal[num - 1])) > floor[num - 1]):
                state[num - 1] = 1
            if len(list(elev_goal[num - 1])) != 0 and (min(list(elev_goal[num - 1])) < floor[num - 1]):
                state[num - 1] = -1

        if state[num - 1] == -1:
            if len(list(elev_goal[num - 1])) == 0:
                state[num - 1] = 0
            if len(list(elev_goal[num - 1])) != 0 and (min(list(elev_goal[num - 1])) > floor[num - 1]):
                state[num - 1] = 1

        if state[num - 1] == 1:
            if len(list(elev_goal[num - 1])) == 0:
                state[num - 1] = 0
            if len(list(elev_goal[num - 1])) != 0 and (max(list(elev_goal[num - 1])) < floor[num - 1]):
                state[num - 1] = -1


def stop(num):
    if stop[num - 1] == 1:
        stop[num - 1] = 0
        mywindow.findChild(QPushButton, "pause{0}".format(num)).setText("暂停")
    else:
        stop[num - 1] = 1
        mywindow.findChild(QPushButton, "pause{0}".format(num)).setText("启动")

def opendoor(num):
    if state[num - 1] == 0:
        reach_floor_up[num - 1] = 1

def closedoor(num):
    if state[num - 1] == 0 and (reach_floor_up[num - 1] or reach_floor_down[num - 1]):
        close_door[num -1] = 1

def set_goal_inside(num, flr):  # 设定目标楼层(来自电梯内部的请求）
    mywindow.findChild(QPushButton, "floor{0}+{1}".format(num, flr)).setStyleSheet("QPushButton{background-image: url(background.png)}")
    elev_goal[num - 1].add(flr)

def set_goal_outside_up(flr): # 设定目标楼层(来自楼道的请求）
    if flr == 20:
        return
    mywindow.findChild(QPushButton, "up{0}".format(flr)).setStyleSheet("QPushButton{background-image: url(background.png)}")
    elev_goal_outside_up.add(flr)
    elev_select = elev_schedule(flr, 0)
    elev_goal[elev_select].add(flr)

def set_goal_outside_down(flr): # 设定目标楼层(来自楼道的请求）
    if flr == 1:
        return
    mywindow.findChild(QPushButton, "down{0}".format(flr)).setStyleSheet("QPushButton{background-image: url(background.png)}")
    elev_goal_outside_down.add(flr)
    elev_select = elev_schedule(flr, 1)
    elev_goal[elev_select].add(flr)

#获取电梯调度过程中的优先级
#goal_type: 0上升请求 1下降请求
def elev_schedule(flr, goal_type):
    priority = []
    Priority_table = [[[0.2, 1.0], [0.3, 0.5]], [[0.5, 0.3], [1.0, 0.2]]]
    for i in range(4):
        distancePriority= abs(flr - floor[i]) / 20
        if state[i] == 0:
            statusPriority = 0
        else:
            statusPriority = Priority_table[int(0.5 - state[i] / 2)][goal_type][int(floor[i] > flr)]
        priority.append(0.8 * distancePriority + 0.2 * statusPriority)
    return priority.index(min(priority))

if __name__ == '__main__':
    app = QApplication(sys.argv)
    mywindow = Window()

    #电梯状态 停止：0 上升：1 下降：-1
    state = []
    for i in range(4):
        state.append(0)

    #电梯当前的楼层
    floor = []
    for i in range(4):
        floor.append(1)

    #电梯是否暂停运行（不再提供服务）
    stop = []
    for i in range(4):
        stop.append(0)

    #电梯是否应该关门（提前结束OPEN）
    close_door = []
    for i in range(4):
        close_door.append(0)

    #电梯上升时到达目标楼层后应当开门
    reach_floor_up = [0, 0, 0, 0]

    # 电梯下降时到达目标楼层后应当开门
    reach_floor_down = [0, 0, 0, 0]

    #楼道里向上的请求
    elev_goal_outside_up = set([])

    #楼道里向下的请求
    elev_goal_outside_down = set([])

    #电梯的全局运行目标楼层（包括来自内部的和楼道中的）
    elev_goal = []
    for i in range (4):
        elev_goal.append(set([]))

    #设置四部电梯的线程 启动运行
    elevthreads = []
    for i in range(4):
        elevthreads.append(ElevatorThread(i + 1))
    for i in range(4):
        elevthreads[i].start()
    sys.exit(app.exec_())