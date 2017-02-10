#!/usr/bin/python
#_*_encoding:utf-8_*_

import os
import re
import sys
import json
from multiprocessing import (cpu_count, Pool)
from multiprocessing.dummy import Pool as ThreadPool

import argparse
import requests
from bs4 import BeautifulSoup
import Image

ncpus = cpu_count()
saveDir = os.environ['HOME'] + '/joy/pic/test'
whitelist = ['pconline', 'zcool', 'huaban', 'taobao', 'voc']

DEFAULT_LOOPS = 3
DEFAULT_WIDTH = 800
DEFAULT_HEIGHT = 600

def isInWhiteList(url):
    for d in whitelist:
        if d in url:
            return True
    return False    


def parseArgs():
    description = '''This program is used to batch download pictures from specified initial url.
                     eg python dwloadpics_killer.py -u init_url
                  '''   
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('-u','--url', help='One initial url is required', required=True)
    parser.add_argument('-l','--loop', help='download url depth')
    parser.add_argument('-s','--size', nargs=2, help='specify expected size that should be at least, (with,height) ')
    args = parser.parse_args()
    init_url = args.url
    size = args.size
    loops = int(args.loop)
    if loops is None:
        loops = DEFAULT_LOOPS
    if size is None:
        size = [DEFAULT_WIDTH, DEFAULT_HEIGHT]
    return (init_url,loops, size)

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

def batchGrapHtmlContents(urls):
    '''
       batch get the html contents of urls
    '''
    global grapHtmlPool
    return grapHtmlPool.execTasks(getHTMLContentFromUrl, urls)

def getAbsLink(link):
    global serverDomain

    try:
        href = link.attrs['href']
        if href.startswith('//'):
            return 'http:' + href
        if href.startswith('/'):
            return serverDomain + href
        if href.startswith('http://'):
            return href
        return ''
    except:
        return ''

def filterLink(link):
    '''
       only search for pictures in websites specified in the whitelist 
    '''
    if link == '':
        return False
    if not link.startswith('http://'):
        return False
    serverDomain = parseServerDomain(link)
    if not isInWhiteList(serverDomain):
        return False
    return True

def filterImgLink(imgLink):
    '''
       The true imge addresses always ends with .jpg
    '''
    commonFilterPassed = filterLink(imgLink)
    if commonFilterPassed:
        return imgLink.endswith('.jpg')

def getTrueImgLink(imglink):
    '''
    get the true address of image link:
        (1) the image link is http://img.zcool.cn/community/01a07057d1c2a40000018c1b5b0ae6.jpg@900w_1l_2o_100sh.jpg
            but the better link is http://img.zcool.cn/community/01a07057d1c2a40000018c1b5b0ae6.jpg (removing what after @) 
        (2) the image link is relative path /path/to/xxx.jpg
            then the true link is serverDomain/path/to/xxx.jpg serverDomain is http://somedomain
    '''

    global serverDomain
    try:
        href = imglink.attrs['src']
        if href.startswith('/'):
            href = serverDomain + href
        pos = href.find('jpg@')
        if pos == -1:
            return href
        return href[0: pos+3] 
    except:
        return ''

def findAllLinks(htmlcontent, linktag):
    '''
       find html links or pic links from html by rule.
    '''
    soup = BeautifulSoup(htmlcontent, "lxml")
    if linktag == 'a':
        applylink = getAbsLink
    else:
        applylink = getTrueImgLink
    alinks = soup.find_all(linktag)
    allLinks = map(applylink, alinks)
    return filter(lambda x: x!='', allLinks)

def findAllALinks(htmlcontent):
    return findAllLinks(htmlcontent, 'a')

def findAllImgLinks(htmlcontent):
    return findAllLinks(htmlcontent, 'img')

def flat(listOfList):
    return [val for sublist in listOfList for val in sublist]

@catchExc
def downloadPic(picsrc):
    '''
       download pic from pic href such as
            http://img.pconline.com.cn/images/upload/upc/tx/photoblog/1610/21/c9/28691979_1477032141707.jpg
    '''

    picname = picsrc.rsplit('/',1)[1]
    saveFile = saveDir + '/' + picname

    picr = requests.get(picsrc, stream=True)
    with open(saveFile, 'wb') as f:
        for chunk in picr.iter_content(chunk_size=1024):
            if chunk:
                f.write(chunk)
                f.flush()
    f.close()
    return saveFile

@catchExc
def removeFileNotExpected(filename):
    global size

    expectedWidth = size[0]
    expectedHeight = size[1]
    img = Image.open(filename)
    imgsize = img.size
    if imgsize[0] < expectedWidth or imgsize[1] < expectedHeight: 
       os.remove(filename) 

def downloadAndCheckPic(picsrc):
    saveFile = downloadPic(picsrc)
    removeFileNotExpected(saveFile)

def batchDownloadPics(imgAddresses):
    global dwPicPool
    dwPicPool.execTasksAsync(downloadAndCheckPic, imgAddresses)

def downloadFromUrls(urls, loops):
    htmlcontents = batchGrapHtmlContents(urls)
    allALinks = flat(map(findAllALinks, htmlcontents))
    allALinks = filter(filterLink, allALinks)
    if loops == 1:
        allImgLinks = flat(map(findAllImgLinks, htmlcontents))
        validImgAddresses = filter(filterImgLink, allImgLinks)
        batchDownloadPics(validImgAddresses)
    return allALinks

def startDownload(init_url, loops=3):
    '''
       if init_url -> mid_1 url -> mid_2 url -> true image address
       then loops = 3 ; default loops = 3
    '''
    urls = [init_url]
    while True:
        urls = downloadFromUrls(urls, loops) 
        loops -= 1
        if loops == 0:
            break

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

def parseServerDomain(url):
    parts = url.split('/',3)
    return parts[0] + '//' + parts[2]

if __name__ == '__main__':

    (init_url,loops, size) = parseArgs()
    serverDomain = parseServerDomain(init_url)

    createDir(saveDir)

    grapHtmlPool = IoTaskThreadPool(20)
    dwPicPool = IoTaskThreadPool(20)

    startDownload(init_url, loops)
    dwPicPool.close()
    dwPicPool.join()

