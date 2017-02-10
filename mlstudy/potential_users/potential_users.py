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
import math
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
        newdata = []
        for j in range(indicatorNumber):
            newdata.append(str(data[j] + random.randint(0, math.pow(8, j)*10)))
            classifierResult = data[-1]
        dataw.write('%s %d\n' % (' '.join(newdata), classifierResult))  
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
    normDataset = true_divide(normDataset, tile(ranges, (rows,1)))
    return normDataset, ranges, minVals

def computeDistance(inX, dataset):
    datasetrows = dataset.shape[0]
    diffMat = tile(inX, (datasetrows, 1)) - dataset
    sqDiffMat = diffMat ** 2
    sqDistances = sqDiffMat.sum(axis=1)
    distances = sqDistances ** 0.5
    return distances

def divideNParts(total, N):
    '''
       divide [0, total) into N parts:
        return [(0, total/N), (total/N, 2M/N), ((N-1)*total/N, total)]
    '''

    each = total / N
    parts = []
    for index in range(N):
        begin = index*each
        if index == N-1:
            end = total
        else:
            end = begin + each
        parts.append((begin, end))
    return parts

def fastComputeDistance(inX, dataset, n):
    totalrows = dataset.shape[0]
    parts = divideNParts(totalrows, n)
    partsResult = getPartResults(inX, dataset, parts)
    return array(flatten(partsResult))

def flatten(multiDimenList):
    return [item for sublist in multiDimenList for item in sublist]   

def getPartResults(inX, dataset, parts):
    # should use concurrent implementation
    partsResult = []
    for part in parts:
        partsResult.append(computeDistance(inX, dataset[part[0]:part[1], :]))
    return partsResult

def classify(inX, dataset, labels, k):
    distances = fastComputeDistance(inX, dataset, 4)
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
        print('classify result: %d, the real result is %d' % (classifierResult, classLabelVector[i]))
        if classifierResult != classLabelVector[i]:
            errorCount += 1.0
    print ('total error rate is %f' % (errorCount / float(testRows)))

def classifyInstance(dataMatrix,classLabelVector, ranges, minVals):
    dataf = open('data.txt')
    for line in dataf:
        line = line.strip()
        # the first line is id of data, should not be used for distance computation
        data = map(lambda x: int(x), line.split())
        input = array(list(data[1:len(data)]))
        classifierResult = classify((input-minVals)/ranges, dataMatrix, classLabelVector, k)
        features = " ".join(map(lambda x: str(x), data[1:]))
        print('%d (%s) is %s potiential renewal user' % (data[0], features, "not" if classifierResult != 1 else "" ))

def test():
    x = array([[16,4,9], [3,15,27], [12,1,18], [20, 7, 15], [7,9,15], [23,8,11], [5,17,26], [3,10,6]])
    xNorm = autoNorm(x)
    print('x: %s \nnorm(x): %s' % (x, xNorm))

    inX = array([0.1,0.5,0.8])
    slowComputeDistances = computeDistance(inX, xNorm[0])
    print('slow distances: %s' % slowComputeDistances)

    for npart in [1,2,3,4]:
        fastComputeDistances = fastComputeDistance(inX, xNorm[0],npart)
        print('fast distances: %s' % fastComputeDistances)
        
        for ind in range(slowComputeDistances.shape[0]):
            slowComputeDistances[ind] == fastComputeDistances[ind]
              

if __name__ == '__main__':

    test()

    createMoreSamplesFrom('origin.txt', 10)
    (dataMatrix,classLabelVector) = file2matrix('sample.txt')
    (dataMatrix,ranges, minVals) = autoNorm(dataMatrix)
    
    #print 'dataset: ', (dataMatrix,classLabelVector)
    draw(dataMatrix)

    computeErrorRatio(dataMatrix, classLabelVector)
    classifyInstance(dataMatrix,classLabelVector, ranges, minVals)

