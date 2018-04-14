#_*_encoding:utf-8_*_
#!/usr/bin/python

import os
import re
import sys

from common import createDir, catchExc
from net import getSoup, batchGetSoups, download, downloadForSinleParam
from multitasks import *

saveDir = os.environ['HOME'] + '/joy/pic/pconline'
dwpicPool = ThreadPool(5)
getUrlPool = ThreadPool(2)

@catchExc 
def parseTotal(href):
    '''
      total number of pics is obtained from a data request , not static html.
    '''
    photoId = href.rsplit('/',1)[1].split('.')[0]
    url = "http://dp.pconline.com.cn/public/photo/include/2016/pic_photo/intf/loadPicAmount.jsp?photoId=%s" % photoId
    soup = getSoup("http://dp.pconline.com.cn/public/photo/include/2016/pic_photo/intf/loadPicAmount.jsp?photoId=%s" % photoId)
    totalNode = soup.find('p')
    total = int(totalNode.text)
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

def getOriginPicLink(subsoup):
    hdlink = subsoup.find('a', class_='aView aViewHD')
    return hdlink.attrs['ourl']

def findPicLink(picsoup):
    return picsoup.find('img', src=re.compile(".jpg"))

def downloadForASerial(serialHref):
    '''
       download a serial of pics  
    '''

    href = serialHref
    total = getUrlPool.map(parseTotal, [href])[0]
    print 'href: %s *** total: %s' % (href, total)
   
    suburls = [buildSubUrl(href, ind) for ind in range(1, total+1)]
    subsoups = batchGetSoups(getUrlPool, suburls)    

    picUrls = map(getOriginPicLink, subsoups)
    picSoups = batchGetSoups(getUrlPool,picUrls)
    piclinks = map(findPicLink, picSoups)
    downloadParams = map(lambda picLink: (picLink, saveDir), piclinks)
    dwpicPool.map_async(downloadForSinleParam, downloadParams) 

def downloadAllForAPage(entryurl):
    '''
       download serial pics in a page
    '''

    print 'entryurl: ', entryurl
    soups = batchGetSoups(getUrlPool,[entryurl])
    if len(soups) == 0:
        return

    soup = soups[0] 
    #print soup.prettify()
    picLinks = soup.find_all('a', class_='picLink')
    if len(picLinks) == 0:
        return
    hrefs = map(lambda link: link.attrs['href'], picLinks)
    map(downloadForASerial, hrefs)

def downloadAll(serial_num, start, end, taskPool=None):
    entryUrl = 'http://dp.pconline.com.cn/list/all_t%d_p%d.html'
    entryUrls = [ (entryUrl % (serial_num, ind)) for ind in range(start, end+1)]
    execDownloadTask(entryUrls, taskPool)

def execDownloadTask(entryUrls, taskPool=None):
    if taskPool:
        print 'using pool to download ...'
        taskPool.map(downloadAllForAPage, entryUrls)
    else:
        map(downloadAllForAPage, entryUrls)

if __name__ == '__main__':
    createDir(saveDir)
    taskPool = Pool(processes=ncpus)

    serial_num = 145
    total = 4
    nparts = divideNParts(total, 2)
    for part in nparts:
        start = part[0]+1
        end = part[1]
        downloadAll(serial_num, start, end, taskPool=None)
    taskPool.close()
    taskPool.join()
