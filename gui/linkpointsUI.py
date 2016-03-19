# -*- coding: utf8 -*-
# -------------------------------------------------------------------------------
# Name:        linkpointsUI.py
# Purpose:     a game which links points to a gragh and enjoy
#
# Author:      qin.shuq
#
# Created:      12/06/2014
# Copyright:   (c) qin.shuq 2014
# Licence:     ONLY BE USED FOR STUDY
#-------------------------------------------------------------------------------


import wx
import time
import math
import os
import threading
import copy
from LinkPointStrategy import *


class LinkPointsFrame(wx.Frame):
    '''
       generate dotSize * dotSize dotted graph and app ui
    '''
    def __init__(self, parent, title, dotSize=18, uiSize=(810,560)):
        wx.Frame.__init__(self, parent, title=title, size=uiSize)
        self.mainPanel = None            # 主面板，用于绘制点阵图
        self.dc = None                   # 用于绘制图形的对象
        self.dotSize = dotSize           # 点阵图大小设定，形成 dotSize * dotSize 点阵图
        self.displayDemoTimer = None     # 欣赏模式下自动显示已有创作的定时器
        self.validPointsRange = set()    # 拖拽模式时有效点的范围  set([px, py])
        self.isCreateMode = False        # 是否创作模式
        self.origin = 10                 # 原点的实际坐标
        self.pointRadius = 3             # 点使用实心圆圈表示，增大点击范围
        self.mousePostion = MousePositionEachPressAndRelease()   # 拖拽时记录下鼠标所在位置
        self.currWork = []               # 记录创作模式的当前工作以便于保存
        self.history = WorkHistory()     # 记录当前工作状态的历史，便于回退及前进

        panelSize = self.GetClientSize()

        topBottomMargin = 20
        leftRightMargin = 30
        uiWidth = panelSize[0] - leftRightMargin
        panelHeight = panelSize[1] - topBottomMargin

        self.intervalBetweenPoints = (panelHeight-self.origin*2) / (self.dotSize-1)

        self.validPointsRange = self.obtainRealCoordsOfDottedPoints()

        self.mainPanelSize = (panelHeight, panelHeight)
        self.ctrlPanelSize = (uiWidth - self.mainPanelSize[0], panelHeight)

        self.initUI()
        self.Centre()


    def initUI(self):

        ### UI Design follows top-down thinking and down-top building

        bigPanel = wx.Panel(self, name="WhileWindow")
        font = wx.Font(12, wx.ROMAN, wx.NORMAL, wx.NORMAL)

        hboxLayout = wx.BoxSizer(wx.HORIZONTAL)
        self.mainpanel = wx.Panel(bigPanel, name="mainPanel", size=self.mainPanelSize)
        self.mainpanel.SetBackgroundColour('#fffff0')

        self.mainpanel.Bind(wx.EVT_KEY_DOWN, self.onKeyDown)
        self.mainpanel.Bind(wx.EVT_LEFT_DOWN, self.mouseLeftPressHandler)
        #self.mainpanel.Bind(wx.EVT_MOTION, self.mouseMoveHandler)
        self.mainpanel.Bind(wx.EVT_LEFT_UP, self.mouseLeftReleaseHandler)


        ctrlPanel = wx.Panel(bigPanel, name="ctrlPanel", size=self.ctrlPanelSize)

        hboxLayout.Add(self.mainpanel, 0, wx.EXPAND|wx.ALL, 10)
        hboxLayout.Add(ctrlPanel, 0, wx.EXPAND|wx.ALL, 10)
        bigPanel.SetSizer(hboxLayout)

        topPanel = wx.Panel(ctrlPanel, name="topPanel")
        tipInfo ="How to Play: \n\nJust link points to build a graph, \nSo Easy And Enjoy Yourself !\n\n"
        keyInfo = "Press ESC to quit. \nPress z to back.\nPress x to forward.\n"
        staticText = wx.StaticText(topPanel, label=decodeUTF8(tipInfo+keyInfo))
        staticText.SetFont(font)

        btnBoxSizer = wx.GridSizer(8,2, 10, 5)

        buttonSize = (100, 30)
        enterCreateModeBtn = wx.Button(ctrlPanel, name="createMode", label=decodeUTF8("创作模式"), size=buttonSize)
        enterDemoModeBtn = wx.Button(ctrlPanel, name="demoMode", label=decodeUTF8("欣赏模式"), size=buttonSize)
        saveBtn = wx.Button(ctrlPanel, name="SaveWork", label=decodeUTF8("保存工作"), size=buttonSize)
        restoreBtn = wx.Button(ctrlPanel, name="restore", label=decodeUTF8("恢复已存工作"), size=buttonSize)

        self.Bind(wx.EVT_BUTTON, self.enterCreateMode, enterCreateModeBtn)
        self.Bind(wx.EVT_BUTTON, self.enterDemoMode, enterDemoModeBtn)
        self.Bind(wx.EVT_BUTTON, self.saveWork, saveBtn)
        self.Bind(wx.EVT_BUTTON, self.restoreWork, restoreBtn)

        btnBoxSizer.Add(enterCreateModeBtn, 0, wx.ALL)
        btnBoxSizer.Add(enterDemoModeBtn, 0, wx.ALL)
        btnBoxSizer.Add(saveBtn,0, wx.ALL)
        btnBoxSizer.Add(restoreBtn,0, wx.ALL)

        vboxLayout = wx.BoxSizer(wx.VERTICAL)
        vboxLayout.Add(topPanel, 1, wx.EXPAND|wx.ALL, 5)
        vboxLayout.Add(btnBoxSizer, 1, wx.EXPAND|wx.ALL, 5)
        ctrlPanel.SetSizer(vboxLayout)

        self.Show(True)

        # show demo
        self.displayDemoTimer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.displayDemoGraph, self.displayDemoTimer)
        self.createDemoForUsage()
        self.displayDemoInTimer()


    def enterCreateMode(self, event):
        self.mainpanel.SetFocus()   # 使键盘事件获得响应
        self.isCreateMode = True
        if self.displayDemoTimer:
            self.displayDemoTimer.Stop()
        self.createNewDottedGraph()
        self.history.clear()
        self.currWork = []


    def enterDemoMode(self, event):
        self.mainpanel.SetFocus()
        self.isCreateMode = False
        self.displayDemoTimer.Start(100, oneShot=True)


    def createNewDottedGraph(self):
        '''
            清空屏幕， 重新绘制点阵图
        '''
        if self.dc:
            self.dc.Clear()
        self.dc = wx.ClientDC(self.mainpanel)
        self.dc.SetPen(wx.Pen('GREEN'))
        self.dc.SetBrush(wx.Brush('GREEN'))
        for xcoord in range(self.origin, self.mainPanelSize[0] + self.intervalBetweenPoints, self.intervalBetweenPoints):
            for ycoord in range(self.origin, self.mainPanelSize[1] + self.intervalBetweenPoints, self.intervalBetweenPoints):
                self.dc.DrawPoint(xcoord, ycoord)
                self.dc.DrawCircle(xcoord,ycoord, self.pointRadius)


    def createDemoForUsage(self):
        '''
            展示创建图案的接口用法
        '''
        self.createNewDottedGraph()
        linkpointsStrategy = LinkPointStrategy(self.dotSize)
        allLines = linkpointsStrategy.obtainAllLinesByLinkPoints()
        self.drawGraph(allLines)

        ### demo for registering user-defined strategy
        def myStrategy(allPoints, size):
            return [(point, (point[0]+1, point[1]+1)) for point in allPoints if (point[0] == point[1] and point[0]<size-1)]

        LinkPointStrategy.registerStrategy("my", myStrategy)
        LinkPointStrategy.setStrategy("my")
        self.createNewDottedGraph()
        self.drawGraph(linkpointsStrategy.obtainAllLinesByLinkPoints())


    def displayDemoGraph(self, event):
        linkpointsStrategy = LinkPointStrategy(self.dotSize)
        allStrategies = linkpointsStrategy.getAllStrategies()
        for strategyName in allStrategies:
            self.createNewDottedGraph()
            linkpointsStrategy.setStrategy(strategyName)
            self.drawGraph(linkpointsStrategy.obtainAllLinesByLinkPoints())
            time.sleep(2)


    def displayDemoInTimer(self):
        '''
            欣赏模式下使用定时器自动展示已创建的图案
        '''
        self.displayDemoTimer.Start(100, oneShot=True)


    def drawGraphForRealCoords(self, allLines):
        '''
           根据已生成的所有线的设置绘制图案
           一条线是一个元组: ((x1,y1), (x2, y2)) xi, yi 是实际坐标
        '''
        for line in allLines:
            self.dc.DrawLine(line[0][0], line[0][1], line[1][0], line[1][1])

    def drawGraph(self, allLines):
        '''
           根据已生成的所有线的设置绘制图案
           一条线是一个元组: ((x1,y1), (x2, y2)) xi, yi 是逻辑坐标
        '''
        #print '***************************************'
        for line in allLines:
            #print line[0][0], ' ', line[0][1], ' ', line[1][0], ' ', line[1][1]
            x1 = self.obtainRealCoords(line[0][0])
            y1 = self.obtainRealCoords(line[0][1])
            x2 = self.obtainRealCoords(line[1][0])
            y2 = self.obtainRealCoords(line[1][1])
            self.dc.DrawLine(x1, y1, x2, y2)


    def mouseLeftPressHandler(self, event):
        '''
           拖拽时鼠标按下时的动作
        '''
        if self.isCreateMode:
            pos = event.GetPosition()
            nearestPoint = self.nearestPoint(pos)
            if nearestPoint:
                self.mousePostion.pushPressPos(nearestPoint[0], nearestPoint[1])
            else:
                showMsgDialog('请将鼠标放于点的位置进行拖拽!', '提示')


    def mouseMoveHandler(self, event):
        '''
           拖拽时鼠标移动的动作
        '''
        pass
        # if event.Dragging() and event.LeftIsDown():
        #     pressPos = self.mousePostion.getPressPos()
        #     lastPos = self.mousePostion.getLastMovePos()
        #     moveNowPos = event.GetPosition()
        #     self.mousePostion.pushMovePos(moveNowPos[0], moveNowPos[1])
        #     #self.dc.DrawLine(pressPos[0], pressPos[1], moveNowPos[0], moveNowPos[1])
        # event.Skip()


    def mouseLeftReleaseHandler(self, event):
        '''
           拖拽时鼠标释放时的动作
        '''
        if self.isCreateMode:
            nearestStart = self.mousePostion.getPressPos()
            releasePos = event.GetPosition()
            nearestEnd = self.nearestPoint(releasePos)
            if nearestEnd:
                self.dc.DrawLine(nearestStart[0], nearestStart[1], nearestEnd[0], nearestEnd[1])
                self.currWork.append((nearestStart, nearestEnd))
                self.history.push(copy.copy(self.currWork))
            else:
                showMsgDialog('请将鼠标放于点的位置进行拖拽!', '提示')


    def onKeyDown(self, event):
        #self.history.show()
        kc=event.GetKeyCode()
        if kc == wx.WXK_ESCAPE:
            ret = wx.MessageBox(decodeUTF8("确定要退出程序吗？"), decodeUTF8("询问"),
                                wx.YES_NO|wx.NO_DEFAULT,self)
            if ret == wx.YES:
                self.Close()

        if kc == 90:  # press z
            lastWork = self.history.back()
            if lastWork is None:
                showMsgDialog('已经位于最开始的地方，无法回退！', '提示')
                return
            self.createNewDottedGraph()
            self.drawGraphForRealCoords(lastWork)
            self.currWork = copy.copy(lastWork)
        elif kc == 88:  # press x
            nextWork = self.history.forward()
            if nextWork is None:
                showMsgDialog('已经位于最后的状态，无法向前！', '提示')
                return
            self.createNewDottedGraph()
            self.drawGraphForRealCoords(nextWork)
            self.currWork = copy.copy(nextWork)
        #self.history.show()


    def obtainRealCoordsOfDottedPoints(self):
        '''
           获取点阵图中所有点的实际坐标
        '''
        validPointsRange = set()
        for localXCoord in range(self.dotSize):
            for localYCoord in range(self.dotSize):
                validPointsRange.add((self.obtainRealCoords(localXCoord), self.obtainRealCoords(localYCoord)))
        return validPointsRange


    def nearestPoint(self, point):
        '''
            鼠标按下或释放时判断鼠标位置是否处于有效点的范围，并获取最近的有效点用于连线
             如果鼠标位置未处于有效点的位置，则返回 None
        '''
        if point in self.validPointsRange:
            return point
        tolerance = self.intervalBetweenPoints/4  ### 允许用户点击离有效点范围很近的地方
        for validPoint in self.validPointsRange:
            if self.distance(point, validPoint) <= self.pointRadius + tolerance:
                return validPoint
        return None

    def distance(self, point1, point2):
        return math.hypot(point1[0]-point2[0], point1[1]-point2[1])

    def obtainRealCoords(self, localCoord):
        '''
            将逻辑坐标 (x,y) 转换为 实际坐标 (real_x, real_y).
            eg. 假设原点坐标是 (15,15), 点间隔为 (30, 30), 则 (1,1) -> (45,45)
            这样在绘图时就可以专注于以逻辑坐标来思考，摒弃实际坐标的细节干扰
        '''
        return self.origin+localCoord*self.intervalBetweenPoints

    def saveWork(self, event):
        self.mainpanel.SetFocus()
        file_wildcard = "files(*.lp)|*.lp|All files(*.*)|*.*"
        dlg = wx.FileDialog(self, "Save as ...", os.getcwd(), "default.lp",
                            style = wx.SAVE | wx.OVERWRITE_PROMPT, wildcard = file_wildcard)
        f_work = None
        if dlg.ShowModal() != wx.ID_OK:
            dlg.Destroy()
            return
        filename = dlg.GetPath()
        if not os.path.splitext(filename)[1]: #如果没有文件名后缀
            filename = filename + '.lp'
        f_work = open(filename, 'w')
        dlg.Destroy()

        f_work.write("LINK POINTS FILE.\n")
        for (startPoint , endPoint) in self.currWork:
            f_work.write(str(startPoint[0]) + ' ' + str(startPoint[1]) + ' ' + str(endPoint[0]) + ' ' + str(endPoint[1]) + '\n')
        f_work.close()
        showMsgDialog('工作保存成功！^_^', '提示')

    def restoreWork(self, event):
        self.mainpanel.SetFocus()
        file_wildcard = "files(*.lp)|*.lp|All files(*.*)|*.*"
        dlg = wx.FileDialog(self, "Open file...", os.getcwd(), style = wx.OPEN, wildcard = file_wildcard)
        if dlg.ShowModal() != wx.ID_OK:
            dlg.Destroy()
            return

        filename = dlg.GetPath()
        f_work = open(filename)
        lines = f_work.readlines()
        f_work.close()
        dlg.Destroy()

        self.history.clear()
        if lines[0].strip() != 'LINK POINTS FILE.':
            showMsgDialog('文件类型无效，请打开后缀为.lp的文件!', '提示')
        else:
            self.createNewDottedGraph()
            self.currWork = []
            for line in lines[1:]:
                pointCoords = line.strip().split(' ')
                if len(pointCoords) != 4:
                    showMsgDialog('文件内容已损坏!', '提示')
                    return
                startPointX = pointCoords[0]
                startPointY = pointCoords[1]
                endPointX = pointCoords[2]
                endPointY = pointCoords[3]
                try:
                    self.dc.DrawLine(int(startPointX), int(startPointY), int(endPointX), int(endPointY))
                    self.currWork.append( ((int(startPointX), int(startPointY)), (int(endPointX), int(endPointY))) )
                except:
                    showMsgDialog('文件内容已损坏!', '提示')
                    return
            self.history.push(self.currWork)
            showMsgDialog('成功恢复工作，自动进入创作模式！^_^ ', '提示')
            self.isCreateMode = True


class MousePositionEachPressAndRelease(object):
    '''
        mousePosition: [(xpress, ypress), (xlastMove, ylastMove)]
    '''
    def __init__(self):
        self.mousePosition = []

    def pushPressPos(self, xcoord, ycoord):
        self.mousePosition.insert(0, (xcoord, ycoord))

    def pushMovePos(self, xcoord, ycoord):
        self.mousePosition.insert(1, (xcoord, ycoord))

    def getPressPos(self):
        return self.mousePosition[0]

    def getLastMovePos(self):
        return  self.mousePosition[1]

class WorkHistory(object):
    '''
        保存工作快照列表，实现回退功能
    '''
    def __init__(self):
        self.worksnapshots = [[]]
        self.currPoint = 0

    def push(self, currWork):
        ### 如果在回退操作之后立即 push ， 则回退之前从回退点之后的动作都将清空
        self.currPoint+=1
        self.worksnapshots = self.worksnapshots[0: self.currPoint]
        self.worksnapshots.append(currWork)


    def back(self):
        if self.currPoint <= 0:
            return None
        else:
            self.currPoint-=1
            return self.worksnapshots[self.currPoint]

    def forward(self):
        if self.currPoint >= len(self.worksnapshots)-1:
            return None
        else:
            self.currPoint+=1
            return self.worksnapshots[self.currPoint]

    def clear(self):
        self.worksnapshots = [[]]
        self.currPoint = 0

    def show(self):
        print "curr point: ", self.currPoint
        for snapshot in self.worksnapshots:
            print snapshot

# utils
def decodeUTF8(msg):
    return msg.decode('utf8')

def showMsgDialog(msg, title):
    dialog = wx.MessageDialog(None, decodeUTF8(msg), decodeUTF8(title), wx.YES_DEFAULT)
    dialog.ShowModal()
    dialog.Destroy()

def main():

    app = wx.App(False)
    frame = LinkPointsFrame(None, decodeUTF8('连点成图: 享受创建图形的乐趣'))
    app.MainLoop()


if __name__ == '__main__':
    main()
