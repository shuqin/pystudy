#-------------------------------------------------------------------------------
# Name:        wordstat_threading.py
# Purpose:     statistic words in java files of given directory by threading
#
# Author:      qin.shuq
#
# Created:     09/10/2014
#-------------------------------------------------------------------------------

import re
import os
import time
import threading, Queue

from basic.logUtil import (errlog, infolog)

timeoutInSecs = 0.05

class FileObtainer(threading.Thread):

    def __init__(self, dirpath, qOut, threadID, fileFilterFunc=None):
        threading.Thread.__init__(self)
        self.dirpath = dirpath
        self.fileFilterFunc = fileFilterFunc
        self.qOut = qOut
        self.threadID = threadID
        infolog.info('FileObtainer Initialized')

    def obtainFile(self, path):
        fileOrDirs = os.listdir(path)
        if len(fileOrDirs) == 0:
            return

        for name in fileOrDirs:
            fullPath = path + '/' + name
            if os.path.isfile(fullPath):
                if self.fileFilterFunc is None:
                    self.qOut.put(fullPath)
                elif self.fileFilterFunc(fullPath):
                    self.qOut.put(fullPath)
            elif os.path.isdir(fullPath):
                self.obtainFile(fullPath)

    def run(self):
        print threading.currentThread()
        starttime = time.time()
        self.obtainFile(self.dirpath)
        endtime = time.time()
        print 'ObtainFile cost: ', (endtime-starttime)*1000 , 'ms'

class WordReading(threading.Thread):

    def __init__(self, qIn, qOut, threadID):
        threading.Thread.__init__(self)
        self.qIn = qIn
        self.qOut = qOut
        self.threadID = threadID
        infolog.info('WordReading Initialized')

    def readFileInternal(self):
        lines = []
        try:
            filename = self.qIn.get(True, timeoutInSecs)
            #print filename
        except Queue.Empty, emp:
            errlog.error('In WordReading:' + str(emp))
            return None

        try:
            f = open(filename, 'r')
            lines = f.readlines()
            infolog.info('[successful read file %s]\n' % filename)
            f.close()
        except IOError, err:
            errorInfo = 'file %s Not found \n' % filename
            errlog.error(errorInfo)
        return lines

    def run(self):
        print threading.currentThread()
        starttime = time.time()
        while True:
            lines = self.readFileInternal()
            if lines is None:
                break
            self.qOut.put(lines)
        endtime = time.time()
        print 'WordReading cost: ', (endtime-starttime)*1000 , 'ms'

class WordAnalyzing(threading.Thread):
    '''
     return Map<Word, count>  the occurrence times of each word
    '''
    wordRegex = re.compile("[\w]+")

    def __init__(self, qIn, threadID):
        threading.Thread.__init__(self)
        self.qIn = qIn
        self.threadID = threadID
        self.result = {}
        infolog.info('WordAnalyzing Initialized')

    def run(self):
        print threading.currentThread()
        starttime = time.time()
        lines = []
        while True:
            try:
                start = time.time()
                lines = self.qIn.get(True, timeoutInSecs)
            except Queue.Empty, emp:
                errlog.error('In WordReading:' + str(emp))
                break

            linesContent = ''.join(lines)
            matches = WordAnalyzing.wordRegex.findall(linesContent)
            if matches:
                for word in matches:
                    if self.result.get(word) is None:
                        self.result[word] = 0
                    self.result[word] += 1


        endtime = time.time()
        print 'WordAnalyzing analyze cost: ', (endtime-starttime)*1000 , 'ms'

    def obtainResult(self):
        return self.result;


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

    dirpath = "E:\\workspace\\java\\javastudy\\src"
    if not os.path.exists(dirpath):
        print 'dir %s not found.' % dirpath
        exit(1)

    qFile = Queue.Queue()
    qLines = Queue.Queue()

    fileObtainer = FileObtainer(dirpath, qFile, "Thread-FileObtainer", lambda f: f.endswith('.java'))
    wr = WordReading(qFile, qLines, "Thread-WordReading")
    wa = WordAnalyzing(qLines, "Thread-WordAnalyzing")

    fileObtainer.start()
    wr.start()
    wa.start()

    wa.join()

    starttime = time.time()
    postproc = PostProcessing(wa.obtainResult())
    postproc.obtainTopN(30)
    endtime = time.time()
    print 'PostProcessing cost: ', (endtime-starttime)*1000 , 'ms'

    print 'exit the program.'

