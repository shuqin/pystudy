#_*_encoding:utf-8_*_
#!/usr/bin/python

import os
import re
import sys
from multiprocessing import (cpu_count, Pool)
from multiprocessing.dummy import Pool as ThreadPool

import requests
from bs4 import BeautifulSoup

ncpus = cpu_count()
saveDir = os.environ['HOME'] + '/joy/pic/pconline'
dwpicPool = ThreadPool(20)
getUrlPool = ThreadPool(20)

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


@catchExc
def batchGetSoups(urls):
    '''
       get the html content of url and transform into soup object 
           in order to parse what i want later
    '''

    urlnum = len(urls)
    if urlnum == 0:
        return []

    results = getUrlPool.map(requests.get, urls)

    soups = []
    for res in results:
        #r = res.get(timeout=1) 
        r = res
        status = r.status_code

        if status != 200:
            continue
        resp = r.text
        soup = BeautifulSoup(resp, "lxml")
        soups.append(soup)
    return soups

@catchExc 
def parseTotal(soup):
    '''
      parse total number of pics in html tag <span class="totPic"> (1/total)</span>
    '''
    totalNode = soup.find('span', class_='totPics')
    total = int(totalNode.text.split('/')[1].replace(')',''))
    return total

@catchExc 
def buildSubUrl(href, ind):
    '''
    if href is http://dp.pconline.com.cn/photo/3687736.html, total is 10
    then suburl is
        http://dp.pconline.com.cn/photo/3687736_[1-10].html
    which contain the origin href of picture
    '''
    return href.rsplit('.', 1)[0] + "_" + str(ind) + '.html' 

@catchExc 
def downloadPic(piclink):
    '''
       download pic from pic href such as 
            http://img.pconline.com.cn/images/upload/upc/tx/photoblog/1610/21/c9/28691979_1477032141707.jpg
    '''

    picsrc = piclink.attrs['src']
    picname = picsrc.rsplit('/',1)[1]
    saveFile = saveDir + '/' + picname

    picr = requests.get(piclink.attrs['src'], stream=True)
    with open(saveFile, 'wb') as f:
        for chunk in picr.iter_content(chunk_size=1024):  
            if chunk:
                f.write(chunk)
                f.flush() 
    f.close()

@catchExc
def getOriginPicLink(subsoup):
    hdlink = subsoup.find('a', class_='aView aViewHD')
    return hdlink.attrs['href']

@catchExc 
def downloadForASerial(serialHref):
    '''
       download a serial of pics  
    '''

    href = serialHref
    subsoups = batchGetSoups([href])
    total = parseTotal(subsoups[0])
    print 'href: %s *** total: %s' % (href, total)
   
    suburls = [buildSubUrl(href, ind) for ind in range(1, total+1)]
    subsoups = batchGetSoups(suburls)
    picUrls = map(getOriginPicLink, subsoups)
    picSoups = batchGetSoups(picUrls)
    piclinks = map(lambda picsoup: picsoup.find('img', src=re.compile(".jpg")), picSoups)
    dwpicPool.map_async(downloadPic, piclinks) 

def downloadAllForAPage(entryurl):
    '''
       download serial pics in a page
    '''

    print 'entryurl: ', entryurl
    soups = batchGetSoups([entryurl])
    if len(soups) == 0:
        return

    soup = soups[0] 
    #print soup.prettify()
    picLinks = soup.find_all('a', class_='picLink')
    if len(picLinks) == 0:
        return
    hrefs = map(lambda link: link.attrs['href'], picLinks)

    for serialHref in hrefs: 
        downloadForASerial(serialHref)

def downloadAll(serial_num, start, end, taskPool=None):
    entryUrl = 'http://dp.pconline.com.cn/list/all_t%d_p%d.html'
    entryUrls = [ (entryUrl % (serial_num, ind)) for ind in range(start, end+1)]
    execDownloadTask(entryUrls, taskPool)

def execDownloadTask(entryUrls, taskPool=None):
    if taskPool:
        taskPool.addDownloadTask(entryUrls)
    else:
        for entryurl in entryUrls:
            downloadAllForAPage(entryurl)

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

class TaskProcessPool():
    def __init__(self):
        self.taskPool = Pool(processes=ncpus)

    def addDownloadTask(self, entryUrls):
        self.taskPool.map_async(downloadAllForAPage, entryUrls)

    def close(self):
        self.taskPool.close()

    def join(self):
        self.taskPool.join()

if __name__ == '__main__':
    createDir(saveDir)
    taskPool = TaskProcessPool()

    serial_num = 601
    offset = 20
    end = 10
    nparts = divideNParts(end, 5)
    npartsWithOffset = [(t[0]+offset, t[1]+offset) for t in nparts]

    for part in npartsWithOffset:
        start = part[0]+1
        end = part[1]
        downloadAll(serial_num, start, end, taskPool=None)
    taskPool.close()
    taskPool.join()
