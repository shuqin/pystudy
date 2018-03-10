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

def file2matrix(filename):
    dataf = open(filename)
    lines = dataf.readlines()
    numOfLines = len(lines)
    returnMat = zeros((numOfLines, 2))
    classLabelVector = []
    index = 0
    for line in lines:
        line = line.strip()
        listFromLine = line.split()
        returnMat[index, :] = listFromLine[0:2]
        classLabelVector.append(int(listFromLine[-1]))
        index += 1
    return (returnMat, classLabelVector)

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

if __name__ == '__main__':
    (returnMat,classLabelVector) = file2matrix('data.txt')
    (returnMat,ranges, minVals) = autoNorm(returnMat)
    print 'dataset: ', (returnMat,classLabelVector)

    fig = plot.figure()
    ax = fig.add_subplot(111)
    ax.scatter(returnMat[:, 0], returnMat[:,1])
    #ax.scatter(returnMat[:, 0], returnMat[:,1], 20.0*array(classLabelVector), 20.0*array(classLabelVector))
    plot.title('potiential renewal users figure')
    plot.xlabel('daily order number')
    plot.ylabel('daily actual deal')
    #plot.show()

    ratio = 0.20
    totalRows = returnMat.shape[0]
    testRows = int(totalRows*ratio)
    errorCount = 0
    for i in range(testRows):
        classifierResult = classify(returnMat[i,:], returnMat[testRows:totalRows, :], classLabelVector[testRows:totalRows], 2)
        print 'classify result: %d, the real result is %d' % (classifierResult, classLabelVector[i])
        if classifierResult != classLabelVector[i]:
            errorCount += 1.0
    print 'total error rate is %f' % (errorCount / float(testRows)) 

       
