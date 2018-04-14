#!/usr/bin/python
#_*_encoding:utf-8_*_

import os
import re
import sys
import requests
from bs4 import BeautifulSoup

saveDir = os.environ['HOME'] + '/joy/pic/pconline/nature'

def createDir(dirName):
    if not os.path.exists(dirName):
        os.makedirs(dirName)

def catchExc(func):
    def _deco(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            print "error catch exception for %s (%s, %s)." % (func.__name__, str(*args), str(**kwargs))
            print e
            return None
    return _deco


@catchExc
def getSoup(url):
    '''
       get the html content of url and transform into soup object 
           in order to parse what i want later
    '''
    result = requests.get(url)
    status = result.status_code
    if status != 200:
        return None
    resp = result.text
    soup = BeautifulSoup(resp, "lxml")
    return soup

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
def download(piclink):
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
        download(piclink)
      

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
