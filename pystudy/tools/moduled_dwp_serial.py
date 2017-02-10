#!/usr/bin/python
#_*_encoding:utf-8_*_

import os
import re
import sys

from common import (createDir, catchExc)
from net import (getSoup, download)

saveDir = os.environ['HOME'] + '/joy/pic/pconline/nature'

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

@catchExc 
def downloadForASerial(serialHref):
    '''
       download a serial of pics  
    '''

    href = serialHref
    subsoup = getSoup(href)
    total = parseTotal(href)
    print 'href: %s *** total: %s' % (href, total)
    
    for ind in range(1, total+1):
        suburl = buildSubUrl(href, ind)
        print "suburl: ", suburl
        subsoup = getSoup(suburl)

        hdlink = subsoup.find('a', class_='aView aViewHD')
        picurl = hdlink.attrs['ourl']

        picsoup = getSoup(picurl)
        piclink = picsoup.find('img', src=re.compile(".jpg"))
        download(piclink, saveDir)
      

@catchExc 
def downloadAllForAPage(entryurl):
    '''
       download serial pics in a page
    '''

    soup = getSoup(entryurl)
    if soup is None:
        return
    #print soup.prettify()
    picLinks = soup.find_all('a', class_='picLink')
    if len(picLinks) == 0:
        return
    hrefs = map(lambda link: link.attrs['href'], picLinks)
    print 'serials in a page: ', len(hrefs)

    for serialHref in hrefs: 
        downloadForASerial(serialHref)

def downloadEntryUrl(serial_num, index):
    entryUrl = 'http://dp.pconline.com.cn/list/all_t%d_p%d.html' % (serial_num, index)
    print "entryUrl: ", entryUrl
    downloadAllForAPage(entryUrl)
    return 0

def downloadAll(serial_num):
    start = 1     
    end = 2
    return [downloadEntryUrl(serial_num, index) for index in range(start, end+1)] 

serial_num = 145

if __name__ == '__main__':

    createDir(saveDir)
    downloadAll(serial_num)
