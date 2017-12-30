#!/usr/bin/python
#_*_encoding:utf-8_*_

import os
import requests

from multiprocessing import (cpu_count, Pool)
from multiprocessing.dummy import Pool as ThreadPool

ncpus = cpu_count()
saveDir = os.environ['HOME'] + '/joy/res/test'

def createDir(dirName):
    if not os.path.exists(dirName):
        os.makedirs(dirName)

def catchExc(func):
    def _deco(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            print "error catch exception for %s (%s, %s): %s" % (func.__name__, str(*args), str(**kwargs), e)
            return None
    return _deco

class IoTaskThreadPool(object):
    '''
       thread pool for io operations
    '''
    def __init__(self, poolsize):
        self.ioPool = ThreadPool(poolsize)

    def execTasks(self, ioFunc, ioParams):
        if not ioParams or len(ioParams) == 0:
            return []
        return self.ioPool.map(ioFunc, ioParams)

    def execTasksAsync(self, ioFunc, ioParams):
        if not ioParams or len(ioParams) == 0:
            return []
        self.ioPool.map_async(ioFunc, ioParams)

    def close(self):
        self.ioPool.close()

    def join(self):
        self.ioPool.join()

class TaskProcessPool():
    '''
       process pool for cpu operations or task assignment
    '''
    def __init__(self):
        self.taskPool = Pool(processes=ncpus)

    def addDownloadTask(self, entryUrls):
        self.taskPool.map_async(downloadAllForAPage, entryUrls)

    def close(self):
        self.taskPool.close()

    def join(self):
        self.taskPool.join()

def getHTMLContentFromUrl(url):
    '''
       get html content from html url
    '''
    r = requests.get(url)
    status = r.status_code
    if status != 200:
        return ''
    return r.text

grapHtmlPool = IoTaskThreadPool(20)

def batchGrapHtmlContents(urls):
    '''
       batch get the html contents of urls
    '''
    global grapHtmlPool
    return grapHtmlPool.execTasks(getHTMLContentFromUrl, urls)


@catchExc
def download(ressrc):
    '''
       download res from res href
    '''

    resname = ressrc.rsplit('/',1)[1]
    saveFile = saveDir + '/' + resname

    resr = requests.get(ressrc, stream=True)
    with open(saveFile, 'wb') as f:
        for chunk in resr.iter_content(chunk_size=1024):
            if chunk:
                f.write(chunk)
                f.flush()
    f.close()

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

