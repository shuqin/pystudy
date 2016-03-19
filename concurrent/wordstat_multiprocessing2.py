#-------------------------------------------------------------------------------
# Name:        wordstat_multiprocessing.py
# Purpose:     statistic words in java files of given directory by multiprocessing
#
# Author:      qin.shuq
#
# Created:     09/10/2014
# Copyright:   (c) qin.shuq 2014
# Licence:     <your licence>
#-------------------------------------------------------------------------------

import re
import os
import time
import threading
from Queue import Empty
from multiprocessing import Process, Manager, Pool, Pipe, cpu_count

from basic.logUtil import (errlog, infolog)

ncpu = cpu_count()

CompletedMsg = "EOF FINISHED"


class FileObtainer(object):

    def __init__(self, dirpath, fileFilterFunc=None):
        self.dirpath = dirpath
        self.fileFilterFunc = fileFilterFunc

    def findAllFilesInDir(self):
        files = []
        for path, dirs, filenames in os.walk(self.dirpath):
            if len(filenames) > 0:
                for filename in filenames:
                    files.append(path+'/'+filename)

        if self.fileFilterFunc is None:
            return files
        else:
            return filter(self.fileFilterFunc, files)

class MultiQueue(object):

    def __init__(self, qnum, CompletedMsg, timeout=0.01):
        manager = Manager()
        self.timeout = timeout
        self.qnum = qnum
        self.CompletedMsg = CompletedMsg
        self.queues = []
        self.pindex = 0
        self.endIndex = -1
        for i in range(self.qnum):
            qLines = manager.Queue()
            self.queues.append(qLines)

    def put(self, obj):
        self.queues[self.pindex].put(obj)
        self.pindex = (self.pindex+1) % self.qnum

    def get(self, timeout=0.01):
        for i in range(self.qnum):
            if i != self.endIndex:
                try:
                    obj = self.queues[i].get(True, timeout)
                    if obj == self.CompletedMsg:
                        self.endIndex = i   # this queue contains 'finsh flag' msg
                        self.queues[i].put(self.CompletedMsg)
                        continue
                    return obj
                except Empty, emp:
                    errlog.error('In WordReading:' + str(emp))
        if self.endIndex != -1:
            return self.CompletedMsg
        return None

def readFile(filename):
    try:
        f = open(filename, 'r')
        lines = f.readlines()
        infolog.info('[successful read file %s]\n' % filename)
        f.close()
        return lines
    except IOError, err:
        errorInfo = 'file %s Not found \n' % filename
        errlog.error(errorInfo)
        return []


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

def batchReadFiles(fileList):
    allLines = []
    for filename in fileList:
        allLines.extend(readFile(filename))
    return allLines

def putResult(futureResult, mq):
    for res in futureResult:
        mq.put(res.get())
    mq.put(CompletedMsg)

class WordReading(object):

    def __init__(self, allFiles, mq):
        self.allFiles = allFiles
        self.mq = mq
        self.ioPool = Pool(ncpu*3)
        infolog.info('WordReading Initialized')

    def run(self):

        parts = divideNParts(len(self.allFiles), ncpu*3)
        futureResult = []
        for (begin, end) in parts:
            futureResult.append(self.ioPool.apply_async(func=batchReadFiles, args=(self.allFiles[begin:end],)))

        t = threading.Thread(target=putResult, args=(futureResult, self.mq))
        t.start()

        print 'Now quit'

def processLines(lines):
    result = {}
    linesContent = ''.join(lines)
    matches = WordAnalyzing.wordRegex.findall(linesContent)
    if matches:
        for word in matches:
            if result.get(word) is None:
                result[word] = 0
            result[word] += 1
    return result

def mergeToSrcMap(srcMap, destMap):
    for key, value in destMap.iteritems():
        if srcMap.get(key):
            srcMap[key] = srcMap.get(key)+destMap.get(key)
        else:
            srcMap[key] = destMap.get(key)
    return srcMap

class WordAnalyzing(object):
    '''
     return Map<Word, count>  the occurrence times of each word
    '''
    wordRegex = re.compile("[\w]+")

    def __init__(self, mq, conn):
        self.mq = mq
        self.cpuPool = Pool(ncpu)
        self.conn = conn
        self.resultMap = {}

        infolog.info('WordAnalyzing Initialized')

    def run(self):
        starttime = time.time()
        lines = []
        futureResult = []
        while True:
            lines = self.mq.get()
            if lines == None:
                continue
            if lines == CompletedMsg:
                break
            futureResult.append(self.cpuPool.apply_async(processLines, args=(lines,)))

        resultMap = {}
        for res in futureResult:
            mergeToSrcMap(self.resultMap, res.get())
        endtime = time.time()
        print 'WordAnalyzing analyze cost: ', (endtime-starttime)*1000 , 'ms'

        self.conn.send('OK')
        self.conn.close()

    def obtainResult(self):
        return self.resultMap


class PostProcessing(object):

    def __init__(self, resultMap):
        self.resultMap = resultMap

    def sortByValue(self):
        return sorted(self.resultMap.items(),key=lambda e:e[1], reverse=True)

    def obtainTopN(self, topN):
        sortedResult = self.sortByValue()
        sortedNum = len(sortedResult)
        topN = sortedNum if topN > sortedNum else topN
        for i in range(topN):
            topi = sortedResult[i]
            print topi[0], ' counts: ', topi[1]

if __name__ == "__main__":

    #dirpath = "/home/lovesqcc/workspace/java/javastudy/src/"
    dirpath = "E:\\workspace\\java\\javastudy\\src"

    if not os.path.exists(dirpath):
        print 'dir %s not found.' % dirpath
        exit(1)

    fileObtainer = FileObtainer(dirpath, lambda f: f.endswith('.java'))
    allFiles = fileObtainer.findAllFilesInDir()

    mqTimeout = 0.01
    mqNum = 3

    mq = MultiQueue(mqNum, CompletedMsg, timeout=mqTimeout)
    p_conn, c_conn = Pipe()
    wr = WordReading(allFiles, mq)
    wa = WordAnalyzing(mq, c_conn)

    wr.run()
    wa.run()

    msg = p_conn.recv()
    if msg == 'OK':
        pass

    # taking less time, parallel not needed.
    postproc = PostProcessing(wa.obtainResult())
    postproc.obtainTopN(30)

    print 'exit the program.'
