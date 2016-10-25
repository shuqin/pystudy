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

def findWantedLinks(htmlcontent, rule):
    '''
       find html links or pic links from html by rule.
       sub rules such as:
          (1) a link with id=[value1,value2,...]
          (2) a link with class=[value1,value2,...]
          (3) img with src=xxx.jpg|png|...
       a rule is map containing sub rule such as:
          {
              'id': [id1, id2, ..., idn],
              'class': [c1, c2, ..., cn],
              'img': ['jpg', 'png', ... ]
          }
                 
    '''

    soup = BeautifulSoup(htmlcontent, "lxml")
    alinks = []
    imglinks = []
    for (key, values) in rule.iteritems():
        if key == 'id':
            for id in values:
                alinks.extend(soup.find_all('a', id=id))
        elif key == 'class':
            for cls in values:
                alinks.extend(soup.find_all('a', class_=cls))
        elif key == 'img':
            for picSuffix in values:
                imglinks.extend(soup.find_all('img', src=re.compile(picSuffix)))
    
    allLinks = []
    allLinks.extend(map(lambda link: link.attrs['href'], alinks))
    allLinks.extend(map(lambda img: img.attrs['src'], imglinks))
    return allLinks

def batchGetLinksByRule(htmlcontentList, rule):
    '''
       find all html links or pic links from html content list by rule
    '''

    links = []
    for htmlcontent in htmlcontentList:
        links.extend(findWantedLinks(htmlcontent, rule))
    return links

def defineResRulePath():
    '''
        return the rule path from init htmls to the origin addresses of pics
        if we find the origin addresses of pics by 
        init htmls --> grap htmlcontents --> rules1 --> intermediate htmls 
           --> grap htmlcontents --> rules2 --> intermediate htmls
           --> grap htmlcontents --> rules3 --> origin addresses of pics
        we say the rulepath is [rules1, rules2, rules3] 
    '''
    return []

def definePconlineResRulePath():
    return [{'class': ['picLink']}, {'class':['aView aViewHD']}, {'img': ['jpg']}]


def findOriginAddressesByRulePath(initUrls, rulePath):
    '''
       find Origin Addresses of pics by rulePath started from initUrls
    '''
    result = initUrls[:]
    for rule in rulePath:
        htmlContents = batchGrapHtmlContents(result)
        links = batchGetLinksByRule(htmlContents, rule)
        result = []
        result.extend(links)
    return result

def downloadFromPconline(serial_num, start, end):
    entryUrl = 'http://dp.pconline.com.cn/list/all_t%d_p%d.html'
    entryUrls = [ (entryUrl % (serial_num, ind)) for ind in range(start, end+1)]
    rulePath = definePconlineResRulePath()
    picOriginAddresses = findOriginAddressesByRulePath(entryUrls, rulePath)

    global dwPicPool
    dwPicPool.execTasksAsync(downloadPic, picOriginAddresses)

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
    allLinks = batchGetLinksByRule(htmlcontentList, rules)
    for link in allLinks:                                  
        print link

if __name__ == '__main__':

    #testBatch()

    createDir(saveDir)
    
    global grapHtmlPool
    grapHtmlPool = IoTaskThreadPool(20)

    global dwPicPool
    dwPicPool = IoTaskThreadPool(20)

    downloadFromPconline(145, 1, 2) 
