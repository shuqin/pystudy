#-------------------------------------------------------------------------------
# Name:        wordstat_serial.py
# Purpose:     statistic words in java files of given directory by serial
#
# Author:      qin.shuq
#
# Created:     08/10/2014
# Copyright:   (c) qin.shuq 2014
# Licence:     <your licence>
#-------------------------------------------------------------------------------

import re
import os
import time
from basic.logUtil import (errlog, infolog)



class WordReading(object):

    def __init__(self, fileList):
        self.fileList = fileList
        #TODO
        #FIXME

    def readFileInternal(self, filename):
        lines = []
        try:
            f = open(filename, 'r')
            lines = f.readlines()
            infolog.info('[successful read file %s]\n' % filename)
            f.close()
        except IOError, err:
            errorInfo = 'file %s Not found \n' % filename
            errlog.error(errorInfo)
        return lines

    def readFile(self):
        allLines = []
        for filename in self.fileList:
            allLines.extend(self.readFileInternal(filename))
        return allLines

class WordAnalyzing(object):
    '''
     return Map<Word, count>  the occurrence times of each word
    '''
    wordRegex = re.compile("[\w]+")
    def __init__(self, allLines):
        self.allLines = allLines

    def analyze(self):
        result = {}
        lineContent = ''.join(self.allLines)
        matches = WordAnalyzing.wordRegex.findall(lineContent)
        if matches:
            for word in matches:
                if result.get(word) is None:
                    result[word] = 0
                result[word] += 1
        return result

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

    starttime = time.time()
    fileObtainer = FileObtainer(dirpath, lambda f: f.endswith('.java'))
    fileList = fileObtainer.findAllFilesInDir()
    endtime = time.time()
    print 'ObtainFile cost: ', (endtime-starttime)*1000 , 'ms'

    starttime = time.time()
    wr = WordReading(fileList)
    allLines = wr.readFile()
    endtime = time.time()
    print 'WordReading cost: ', (endtime-starttime)*1000 , 'ms'

    starttime = time.time()
    wa = WordAnalyzing(allLines)
    resultMap = wa.analyze()
    endtime = time.time()
    print 'WordAnalyzing cost: ', (endtime-starttime)*1000 , 'ms'

    print len(resultMap)

    starttime = time.time()
    postproc = PostProcessing(resultMap)
    postproc.obtainTopN(30)
    endtime = time.time()
    print 'PostProcessing cost: ', (endtime-starttime)*1000 , 'ms'
