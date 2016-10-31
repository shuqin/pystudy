#!/usr/bin/python

import os
#_*_encoding:utf-8_*_
import re
import sys
import json
from multiprocessing import (cpu_count, Pool)
from multiprocessing.dummy import Pool as ThreadPool

import argparse
import requests
from bs4 import BeautifulSoup

ncpus = cpu_count()
saveDir = os.environ['HOME'] + '/joy/pic/test'

def parseArgs():
    description = '''This program is used to batch download pictures from specified urls.
                     eg python dwloadpics_general.py -u http://xxx.html -g 1 10 _p -r '[{"img":["jpg"]}, {"class":["picLink"]}, {"id": ["HidenDataArea"]}]'
                     will search and download pictures from network urls http://xxx_p[1-10].html  by specified rulePath
                  '''
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('-u','--url', nargs='+', help='At least one html urls are required', required=True)
    parser.add_argument('-g','--generate',nargs=3, help='Given range containing (start end suffix) to generate more htmls if not empty ', required=False)
    parser.add_argument('-r','--rulepath',nargs=1,help='rule path to search pictures. if not given, search pictures in given urls', required=False)
    args = parser.parse_args()
    init_urls = args.url
    gene = args.generate
    rulepath = args.rulepath
    return (init_urls, gene, rulepath)

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
        if href.startswith('/'):
            return serverDomain + href
        else:
            return href
    except:
        return ''

def findWantedLinks(htmlcontent, rule):
    '''
       find html links or pic links from html by rule.
       sub rules such as:
          (1) a link with id=[value1,value2,...]
          (2) a link with class=[value1,value2,...]
          (3) img with src=xxx.jpg|png|...
       a rule is map containing sub rule such as:
          { 'id': [id1, id2, ..., idn] } or
          { 'class': [c1, c2, ..., cn] } or
          { 'img': ['jpg', 'png', ... ]}

    '''

    soup = BeautifulSoup(htmlcontent, "lxml")
    alinks = []
    imglinks = []

    for (key, values) in rule.iteritems():
        if key == 'id':
            for id in values:
                links = soup.find_all('a', id=id)
                links = map(getAbsLink, links)
                links = filter(lambda x: x !='', links)
                alinks.extend(links)
        elif key == 'class':
            for cls in values:
                if cls == '*':
                    links = soup.find_all('a')
                else:    
                    links = soup.find_all('a', class_=cls)
                links = map(getAbsLink, links)
                links = filter(lambda x: x !='', links)
                alinks.extend(links)        
        elif key == 'img':
            for picSuffix in values:
                imglinks.extend(soup.find_all('img', src=re.compile(picSuffix)))

    allLinks = []
    allLinks.extend(alinks)
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
        result = filter(lambda link: link.startswith('http://'),result)    
    print result
    return result

def downloadFromUrls(initUrls, rulePath):
    global dwPicPool
    picOriginAddresses = findOriginAddressesByRulePath(initUrls, rulePath)
    dwPicPool.execTasksAsync(downloadPic, picOriginAddresses)

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

def testBatchGetLinks():
    urls = ['http://dp.pconline.com.cn/list/all_t145.html', 'http://dp.pconline.com.cn/list/all_t292.html']
    htmlcontentList = map(getHTMLContentFromUrl, urls)
    rules = {'class':['picLink'], 'id': ['HidenDataArea'], 'img':['jpg']}
    allLinks = batchGetLinksByRule(htmlcontentList, rules)
    for link in allLinks:
        print link

def generateMoreInitUrls(init_urls, gene):
    '''
       two ways to generate urls:
           a.  http://xxx.html -> http://xxx_suffix[start-end].html
           b.  http://xxx.yyy?k1=v1&k2=v2 -> http://xxx.yyy?k1=v1&k2=v2suffix[start-end]
    '''

    if not gene:
        return init_urls

    start = int(gene[0])
    end = int(gene[1])
    suffix = gene[2]
    truerange = map(lambda x: x+start, range(end-start+1))
    if init_urls[0].endswith('.html'):
        urlNames = map(lambda url: url.rsplit('.', 1)[0] , init_urls)
        return [ urlName + suffix + str(ind) + '.html' for urlName in urlNames for ind in truerange ]
    else:
        return [ url + suffix + str(ind) for url in init_urls for ind in truerange ]

def parseRulePathParam(rulepathjson):
    rulepath = [{'img': ['jpg', 'png']}]
    if rulepathjson:
        try:
            rulepath = json.loads(rulepathjson[0])   
        except ValueError as e:
            print 'Param Error: invalid rulepath %s %s' % (rulepathjson, e)
            sys.exit(1) 
    return rulepath

def parseServerDomain(url):
    parts = url.split('/',3)
    return parts[0] + '//' + parts[2]


if __name__ == '__main__':

    #testBatchGetLinks()

    (init_urls, gene, rulepathjson) = parseArgs()
    moreInitUrls = generateMoreInitUrls(init_urls, gene)
    rulepath = parseRulePathParam(rulepathjson)
    serverDomain = parseServerDomain(init_urls[0])

    createDir(saveDir)

    grapHtmlPool = IoTaskThreadPool(20)
    dwPicPool = IoTaskThreadPool(20)

    downloadFromUrls(moreInitUrls, rulepath)
    dwPicPool.close()
    dwPicPool.join()
