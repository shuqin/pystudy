#-------------------------------------------------------------------------------
# Name:        wordstat_threading_improved.py
# Purpose:     statistic words in java files of given directory by threading
#              improved
#
# Author:      qin.shuq
#
# Created:     09/10/2014
#-------------------------------------------------------------------------------

import re
import os
import time
import threading, Queue
from multiprocessing import Process, Pool, cpu_count

from basic.logUtil import (errlog, infolog)

timeoutInSecs = 0.1

class FileObtainer(threading.Thread):

    def __init__(self, dirpath, qOut, threadID, fileFilterFunc=None):
        threading.Thread.__init__(self)
        self.dirpath = dirpath
        self.fileFilterFunc = fileFilterFunc
        self.qOut = qOut
        self.threadID = threadID
        infolog.info('FileObtainer Initialized')


    def run(self):
        print threading.currentThread()
        starttime = time.time()

        for path, dirs, filenames in os.walk(self.dirpath):
            if len(filenames) > 0:
                files = []
                for filename in filenames:
                    start = time.time()
                    fullPath = path+'/'+filename
                    files.append(fullPath)
                    end = time.time()

                if self.fileFilterFunc is None:
                    self.qOut.put_nowait(files)
                else:
                    fileterFiles = filter(self.fileFilterFunc, files)
                    if len(fileterFiles) > 0:
                        self.qOut.put_nowait(fileterFiles)

        endtime = time.time()
        print 'ObtainFile cost: ', (endtime-starttime)*1000 , 'ms'


def readFile(filename, qOut):
    try:
        f = open(filename, 'r')
        lines = f.readlines()
        infolog.info('[successful read file %s]\n' % filename)
        f.close()
    except IOError, err:
        errorInfo = 'file %s Not found \n' % filename
        errlog.error(errorInfo)
    qOut.put(lines)

class WordReading(threading.Thread):

    def __init__(self, qIn, qOut, threadID):
        threading.Thread.__init__(self)
        self.qIn = qIn
        self.qOut = qOut
        self.threadID = threadID
        self.threads = []
        infolog.info('WordReading Initialized')

    def readFileInternal(self):
        try:
            filelist = self.qIn.get(True, timeoutInSecs)
            for filename in filelist:
                t = threading.Thread(target=readFile, args=(filename, self.qOut), name=self.threadID+'-'+filename)
                t.start()
                self.threads.append(t)
            return []
        except Queue.Empty, emp:
            errlog.error('In WordReading:' + str(emp))
            return None

    def run(self):
        print threading.currentThread()
        starttime = time.time()
        while True:
            lines = self.readFileInternal()
            if lines is None:
                break

        for t in self.threads:
            t.join()

        endtime = time.time()
        print 'WordReading cost: ', (endtime-starttime)*1000 , 'ms'


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

class WordAnalyzing(threading.Thread):
    '''
     return Map<Word, count>  the occurrence times of each word
    '''
    wordRegex = re.compile("[\w]+")

    def __init__(self, qIn, threadID):
        threading.Thread.__init__(self)
        self.qIn = qIn
        self.threadID = threadID
        self.resultMap = {}
        self.pool = Pool(cpu_count())
        infolog.info('WordAnalyzing Initialized')

    def run(self):
        print threading.currentThread()
        starttime = time.time()
        lines = []
        futureResult = []
        while True:
            try:
                lines = self.qIn.get(True, timeoutInSecs)
                futureResult.append(self.pool.apply_async(processLines, args=(lines,)))
            except Queue.Empty, emp:
                errlog.error('In WordReading:' + str(emp))
                break

        self.pool.close()
        self.pool.join()

        resultMap = {}
        for res in futureResult:
            mergeToSrcMap(self.resultMap, res.get())
        endtime = time.time()
        print 'WordAnalyzing analyze cost: ', (endtime-starttime)*1000 , 'ms'

    def obtainResult(self):
        #print len(self.resultMap)
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

