# -*- coding: utf8 -*-
# -------------------------------------------------------------------------------
# Name:        LinkPointStrategy.py
# Purpose:     varieties of algorithms for linking points
#
# Author:      qin.shuq
#
# Created:     11/29/2014
# Copyright:   (c) qin.shuq 2014
# Licence:     ONLY BE USED FOR STUDY
# -------------------------------------------------------------------------------

def linesForDiamond(centerPoint, radius):
    '''
       centerPoint: (localXCoord, localYCoord)
       radius: the distance from points in diamond to centerpoint
    '''
    centerx = centerPoint[0]
    centery = centerPoint[1]
    leftPoint = (centerx-1, centery)
    rightPoint = (centerx+1, centery)
    topPoint = (centerx, centery-1)
    bottomPoint = (centerx, centery+1)
    return [(leftPoint, topPoint), (topPoint, rightPoint), (rightPoint, bottomPoint), (bottomPoint, leftPoint)]

def repeatedDiamondStrategy(allPoints, size):
    allLines = []
    radius = 2
    for point in allPoints:
        if not isOutOfBound(point, radius, size):
            allLines.extend(linesForDiamond(point, radius))
    return allLines

def isOutOfBound(centerPoint, radius, dotSize):
    if centerPoint[0] <= radius-1 or centerPoint[0] + radius >= dotSize:
        return True
    if centerPoint[1] <= radius-1 or centerPoint[1] + radius >= dotSize:
        return True
    return False

def simpleLoopStrategyOfLinkpoints(allPoints, size):
    pairs = []
    for i in range(size):
        if i*2 <= size-1:
            pairs.append((i, size-1-i))
    allLines = []
    for pair in pairs:
        allLines.append( ((pair[0], pair[0]), (pair[0], pair[1])) )
        allLines.append( ((pair[0], pair[0]), (pair[1], pair[0])) )
        allLines.append( ((pair[0], pair[1]), (pair[1], pair[1])) )
        allLines.append( ((pair[1], pair[0]), (pair[1], pair[1])) )
    return allLines


def loopStrategyOfLinkpoints(allPoints, size):
    pairs = []
    for i in range(size):
        if i*2 <= size-1:
            pairs.append((i, size-1-i))
    allLines = []
    for pair in pairs:
        begin = (pair[0], pair[0])
        end = (pair[1], pair[1])
        for localXCoord in range(pair[0], pair[1], 1):
            allLines.append(((pair[0], localXCoord), (pair[0], localXCoord+1)))
            allLines.append(((pair[1], localXCoord), (pair[1], localXCoord+1)))
        for localYCoord in range(pair[0], pair[1], 1):
            allLines.append(((localYCoord, pair[0]), (localYCoord+1, pair[0])))
            allLines.append(((localYCoord, pair[1]), (localYCoord+1, pair[1])))
    return allLines


def defaultStrategyOfLinkpoints(allPoints, size):
    return [( point, (point[0]+1, point[1]+1) )
                for point in allPoints if not isRightOrButtomBoundPoint(point, size)]


def isRightOrButtomBoundPoint(point, size):
    localXCoord = point[0]
    localYCoord = point[1]
    return localXCoord == size-1 or localYCoord == size-1


def singleton(cls):
    '''
       Implements Singleton pattern in python.
       From  http://blog.csdn.net/ghostfromheaven/article/details/7671853
    '''
    instances = {}
    def _singleton(*args, **kw):
        if cls not in instances:
            instances[cls] = cls(*args, **kw)
        return instances[cls]
    return _singleton

@singleton
class StrategyManager(object):

    def __init__(self):
        self.strategiesForlinkPoints = {
            'default': defaultStrategyOfLinkpoints,
            'loop': loopStrategyOfLinkpoints,
            'simpleLoop': simpleLoopStrategyOfLinkpoints,
            'diamond': repeatedDiamondStrategy
        }
        self.DEFAULT_STRATEGY = self.strategiesForlinkPoints['default']
        self.CURR_STRATEGY = self.DEFAULT_STRATEGY

    def getStrategy(self, strategyName):
        strategyForLinkPoints = self.strategiesForlinkPoints.get(strategyName)
        if strategyForLinkPoints is None:
            raise Exception('No stragegy named "%s". You can write one. ' % strategyName)
        return strategyForLinkPoints

    def registerStrategy(self, strategyName, strategyForLinkPoints):
        oldStrategy = self.strategiesForlinkPoints.get(strategyName)
        if oldStrategy:
            self.strategiesForlinkPoints['old_' + strategyName] = oldStrategy
        self.strategiesForlinkPoints[strategyName] = strategyForLinkPoints

    def setCurrStrategy(self, strategyName):
        self.CURR_STRATEGY = self.getStrategy(strategyName)

    def getCurrStratety(self):
        return self.CURR_STRATEGY

    def getAllStrategies(self):
        return self.strategiesForlinkPoints.keys()


class LinkPointStrategy(object):
    '''
       just think in a dotted graph of  (0,0) - (dotSize-1, dotSize-1) with interval of points = 1
       (0,0), (0,1), ... , (0, dotSize-1)
       (1,0), (1,1), ... , (1, dotSize-1)
        ... ,  ... , ... ,  ...
       (dotSize-1,0), (dotSize-1, 1), ..., (dotSize-1, dotSize-1)
       and output a set of [((x1,y1), (x2,y2)), ..., ((xm,ym), (xn,yn))]
    '''

    strategyManager = StrategyManager()

    def __init__(self, dotSize):
        self.dotSize = dotSize
        self.allPoints = []

        for localXCoord in range(dotSize):
            for localYCoord in range(dotSize):
                self.allPoints.append((localXCoord, localYCoord))


    @classmethod
    def setStrategy(cls, strategyName):
        cls.strategyManager.setCurrStrategy(strategyName)

    @classmethod
    def getStrategy(cls, strategyName):
        return cls.strategyManager.getStrategy(strategyName)

    @classmethod
    def registerStrategy(cls, strategyName, strategyFunc):
        cls.strategyManager.registerStrategy(strategyName, strategyFunc)

    @classmethod
    def getAllStrategies(cls):
        return cls.strategyManager.getAllStrategies()

    def obtainAllLinesByLinkPoints(self):
        '''
           generate all lines between points according to given strategy which is a algorithm of linking points
           line: a tuple of (x1, y1, x2, y2)
           note: (x1, y1, x2, y2) are local coordinates which will be converted into real coordinates upon drawing
        '''
        currStrategy = LinkPointStrategy.strategyManager.getCurrStratety()
        return currStrategy(self.allPoints, self.dotSize)

if __name__ == '__main__':
    strategyManager = StrategyManager()
    anoStrategyManager = StrategyManager()
    assert id(strategyManager) == id(anoStrategyManager)
