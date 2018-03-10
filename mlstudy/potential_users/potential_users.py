# -*- coding: utf-8 -*-
# -------------------------------------------------------------------------------
# Name:          potiential_users.py
# Purpose:       recognise potiential renewal users using kNN algorithm
#
# Author:       qin.shuq
#
# Created:      2018/03/10
#-------------------------------------------------------------------------------
#!/usr/bin/env python

import random
import matplotlib
import matplotlib.pyplot as plot
from numpy import *
import operator

indicatorNumber = 3
k = 5

def createMoreSamplesFrom(filename, n):
    datar = open(filename)
    lines = datar.readlines()
    datar.close()

    lineNum = len(lines)
    totalLines = lineNum * n
    dataw = open('sample.txt', 'w')
    for i in range(totalLines):
        data = map (lambda x: int(x), lines[random.randint(0,lineNum)].strip().split())
        (orderNumber, actualDeal, fans, classifierResult) = (data[0] + random.randint(0, 500), data[1] + random.randint(0, 500000), data[2] + random.randint(0, 100000), data[3])
        dataw.write('%d %d %d %d\n' % (orderNumber, actualDeal, fans, classifierResult))  
    dataw.close()
 
def file2matrix(filename):
    dataf = open(filename)
    lines = dataf.readlines()
    dataf.close()

    numOfLines = len(lines)
    dataMatrix = zeros((numOfLines, indicatorNumber))
    classLabelVector = []
    index = 0
    for line in lines:
        line = line.strip()
        listFromLine = line.split()
        dataMatrix[index, :] = listFromLine[0:indicatorNumber]
        classLabelVector.append(int(listFromLine[-1]))
        index += 1
    return (dataMatrix, classLabelVector)

def autoNorm(dataset):
    minVals = dataset.min(0)
    maxVals = dataset.max(0)
    ranges = maxVals - minVals
    normDataset = zeros(shape(dataset))
    rows = dataset.shape[0]
    normDataset = dataset - tile(minVals, (rows,1))
    normDataset = normDataset / tile(ranges, (rows,1))
    return normDataset, ranges, minVals

def classify(inX, dataset, labels, k):
    datasetrows = dataset.shape[0]
    diffMat = tile(inX, (datasetrows, 1)) - dataset
    sqDiffMat = diffMat ** 2
    sqDistances = sqDiffMat.sum(axis=1)
    distances = sqDistances ** 0.5
    sortedDistIndicies = distances.argsort()
    classCount = {}
    for i in range(k):
        voteLabel = labels[sortedDistIndicies[i]]
        classCount[voteLabel] = classCount.get(voteLabel, 0) + 1
    sortedClassCount = sorted(classCount.iteritems(), key=operator.itemgetter(1), reverse=True)
    return sortedClassCount[0][0]

def draw(data):
    fig = plot.figure()
    ax = fig.add_subplot(111)
    ax.scatter(data[:, 0], data[:,1])
    #ax.scatter(data[:, 0], data[:,1], 20.0*array(classLabelVector), 20.0*array(classLabelVector))
    plot.title('potiential renewal users figure')
    plot.xlabel('daily order number')
    plot.ylabel('daily actual deal')
    #plot.show()

def computeErrorRatio(dataMatrix, classLabelVector):
    testRatio = 0.10
    totalRows = dataMatrix.shape[0]
    testRows = int(totalRows*testRatio)
    errorCount = 0
    for i in range(testRows):
        classifierResult = classify(dataMatrix[i,:], dataMatrix[testRows:totalRows, :], classLabelVector[testRows:totalRows], k)
        print 'classify result: %d, the real result is %d' % (classifierResult, classLabelVector[i])
        if classifierResult != classLabelVector[i]:
            errorCount += 1.0
    print 'total error rate is %f' % (errorCount / float(testRows))

def classifyInstance(dataMatrix,classLabelVector, ranges, minVals):
    dataf = open('data.txt')
    for line in dataf:
        line = line.strip()
        (kid, orderNumber, actualDeal, fans) = map(lambda x: int(x), line.split())
        input = array([orderNumber, actualDeal, fans])
        classifierResult = classify((input-minVals)/ranges, dataMatrix, classLabelVector, k)
        print '%d [orderNumber=%d actualDeal=%d fans=%d] is %s potiential renewal user' % (kid, orderNumber, actualDeal, fans, "not" if classifierResult != 1 else "" )

if __name__ == '__main__':
    createMoreSamplesFrom('origin.txt', 10)
    (dataMatrix,classLabelVector) = file2matrix('sample.txt')
    (dataMatrix,ranges, minVals) = autoNorm(dataMatrix)
    
    print 'dataset: ', (dataMatrix,classLabelVector)
    draw(dataMatrix)

    computeErrorRatio(dataMatrix, classLabelVector)
    classifyInstance(dataMatrix,classLabelVector, ranges, minVals)

