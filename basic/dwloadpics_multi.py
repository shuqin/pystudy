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
saveDir = os.environ['HOME'] + '/joy/pic/test'

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

def findWantedLinks(htmlcontent, rules):
    '''
       find html links or pic links from html by rules.
       rules such as:
          (1) a link with id=[value1,value2,...]
          (2) a link with class=[value1,value2,...]
          (3) img with src=xxx.jpg|png|...
          rules is map containing rule such as:
              {
                 'id': [id1, id2, ..., idn],
                 'class': [c1, c2, ..., cn],
                 'img': ['jpg', 'png', ... ]
              }
                 
    '''
    soup = BeautifulSoup(htmlcontent, "lxml")
    alinks = []
    imglinks = []
    for (key, values) in rules.iteritems():
        if key == 'id':
            for id in values:
                alinks.extend(soup.find_all('a', id=id))
        elif key == 'class':
            for cls in values:
                alinks.extend(soup.find_all('a', class_=cls))
        elif key == 'img':
                imglinks.extend(soup.find_all('img', src=re.compile(".jpg")))
    
    allLinks = []
    allLinks.extend(map(lambda link: link.attrs['href'], alinks))
    allLinks.extend(map(lambda img: img.attrs['src'], imglinks))
    return allLinks

def batchGetLinksByRules(htmlcontentList, rules):
    '''
       find all html links or pic links from html content list by rules 
    '''
    links = []
    for htmlcontent in htmlcontentList:
        links.extend(findWantedLinks(htmlcontent, rules))
    return links

@catchExc
def batchGetSoups(urls):
    '''
       batch transform list of html content into list of soup object 
           in order to parse what i want later
    '''
    return map(lambda resp: BeautifulSoup(resp, "lxml"), batchGrapHtmlContents(urls))

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

    global dwPicPool
    dwPicPool.execTasksAsync(downloadPic, piclinks) 

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

def testBatch():
    urls = ['http://dp.pconline.com.cn/list/all_t145.html', 'http://dp.pconline.com.cn/list/all_t292.html']
    htmlcontentList = map(getHTMLContentFromUrl, urls)
    rules = {'img':['jpg'], 'class':['picLink'], 'id': ['HidenDataArea']}
    allLinks = batchGetLinksByRules(htmlcontentList, rules)
    for link in allLinks:                                  
        print link

if __name__ == '__main__':

    testBatch()

    createDir(saveDir)
    taskPool = TaskProcessPool()
    
    global grapHtmlPool
    grapHtmlPool = IoTaskThreadPool(20)

    global dwPicPool
    dwPicPool = IoTaskThreadPool(20)

    serial_num = 601
    offset = 30
    end = 4
    nparts = divideNParts(end, 1)
    npartsWithOffset = [(t[0]+offset, t[1]+offset) for t in nparts]

    for part in npartsWithOffset:
        start = part[0]+1
        end = part[1]
        downloadAll(serial_num, start, end, taskPool=None)
    taskPool.close()
    taskPool.join()
