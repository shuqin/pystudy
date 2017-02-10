#!/usr/bin/python
#_*_encoding:utf-8_*_

import re
import sys
import json

import argparse
from bs4 import BeautifulSoup
from common import *

def parseArgs():
    description = '''This program is used to batch download resources from specified urls.
                     eg python dw.py -u http://xxx.html -g 1 10 _p -r '[{"img":["jpg"]}, {"class":["resLink"]}, {"id": ["HidenDataArea"]}]'
                     will search and download resources from network urls http://xxx_p[1-10].html  by specified rulePath
                  '''
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('-u','--url', nargs='+', help='At least one html urls are required', required=True)
    parser.add_argument('-g','--generate',nargs=2, help='Given range containing two number (start end) to generate more htmls if not empty ', required=False)
    parser.add_argument('-r','--rulepath',nargs=1,help='rule path to search restures. if not given, search restures in given urls', required=False)
    args = parser.parse_args()
    init_urls = args.url
    gene = args.generate
    rulepath = args.rulepath
    return (init_urls, gene, rulepath)

def getAbsLink(link):
    global serverDomain

    try:
        href = link.attrs['href']
        if href.startswith('//'):
            return 'http:' + href
        if href.startswith('/'):
            return serverDomain + href
        else:
            return href
    except:
        return ''

def getTrueResLink(reslink):
    global serverDomain
    try:
        href = reslink.attrs['src']
        if href.startswith('//'):
            return 'http:' + href 
        if href.startswith('/'):
            href = serverDomain + href
            return href
        pos = href.find('jpg@')
        if pos == -1:
            return href
        return href[0: pos+3] 
    except:
        return ''

def batchGetResTrueLink(resLinks):
    hrefs = map(getTrueResLink, resLinks)
    return filter(lambda x: x!='', hrefs)

resTags = set(['img', 'video'])

def findWantedLinks(htmlcontent, rule):
    '''
       find html links or res links from html by rule.
       sub rules such as:
          (1) a link with id=[value1,value2,...]
          (2) a link with class=[value1,value2,...]
          (3) res with src=xxx.jpg|png|mp4|...
       a rule is map containing sub rule such as:
          { 'id': [id1, id2, ..., idn] } or
          { 'class': [c1, c2, ..., cn] } or
          { 'img': ['jpg', 'png', ... ]} or
          { 'video': ['mp4', ...]}

    '''
  
    soup = BeautifulSoup(htmlcontent, "lxml")
    alinks = []
    reslinks = []

    for (key, values) in rule.iteritems():
        if key == 'id':
            for id in values:
                links = soup.find_all('a', id=id)
                links = map(getTrueResLink, links)
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
        elif key in resTags:
            for resSuffix in values:
                reslinks.extend(soup.find_all(key, src=re.compile(resSuffix)))

    allLinks = []
    allLinks.extend(alinks)
    allLinks.extend(batchGetResTrueLink(reslinks))
    return allLinks

def batchGetLinksByRule(htmlcontentList, rule):
    '''
       find all html links or res links from html content list by rule
    '''

    links = []
    for htmlcontent in htmlcontentList:
        links.extend(findWantedLinks(htmlcontent, rule))
    return links

def defineResRulePath():
    '''
        return the rule path from init htmls to the origin addresses of ress
        if we find the origin addresses of ress by
        init htmls --> grap htmlcontents --> rules1 --> intermediate htmls
           --> grap htmlcontents --> rules2 --> intermediate htmls
           --> grap htmlcontents --> rules3 --> origin addresses of ress
        we say the rulepath is [rules1, rules2, rules3]
    '''
    return []

def findOriginAddressesByRulePath(initUrls, rulePath):
    '''
       find Origin Addresses of ress by rulePath started from initUrls
    '''
    result = initUrls[:]
    for rule in rulePath:
        htmlContents = batchGrapHtmlContents(result)
        links = batchGetLinksByRule(htmlContents, rule)
        result = []
        result.extend(links)
    return result

def downloadFromUrls(initUrls, rulePath):
    global dwResPool
    resOriginAddresses = findOriginAddressesByRulePath(initUrls, rulePath)
    dwResPool.execTasksAsync(download, resOriginAddresses)

def testBatchGetLinks():
    urls = ['http://dp.pconline.com.cn/list/all_t145.html']
    urls = ['https://guzhifs.tmall.com/%22//detail.tmall.com/item.htm?id=537430822422&rn=4e22a3b274803229822fd796d2e51387\%22']
    urls = ['https://detail.tmall.com/item.htm?spm=a1z10.1-b-s.w5003-17392175825.5.12894e47kzQ4x5&id=559610585063&scene=taobao_shop'] 
    rules = {"img":["jpg"],"video":["mp4"]}
    #rules = {"class":["zui"]}
    
    htmlcontentList = map(getHTMLContentFromUrl, urls)
    allLinks = batchGetLinksByRule(htmlcontentList, rules)
    print ('Test BatchGetLinks:')
    for link in allLinks:
        print (link)

def generateMoreInitUrls(init_urls, gene):
    '''
      Generate more initial urls using init_urls and a range specified by gene
      to generate urls, we give a base url containing a placeholder, then replace placeholder with number.
       eg. 
       base url:  http://xxx.yyy?k1=v1&k2=v2&page=placeholder -> http://xxx.yyy?k1=v1&k2=v2&page=[start-end]
       base url is specified by -u option if -g is given.
    '''

    if not gene:
        return init_urls

    start = int(gene[0])
    end = int(gene[1])
    truerange = map(lambda x: x+start, range(end-start+1))
    resultUrls = []
    for ind in truerange:
        for url in init_urls:
            resultUrls.append(url.replace('placeholder', str(ind)))
    return resultUrls

def parseRulePathParam(rulepathjson):
    rulepath = [{'img': ['jpg']}]
    if rulepathjson:
        try:
            rulepath = json.loads(rulepathjson[0])   
        except ValueError as e:
            print ('Param Error: invalid rulepath %s %s' % (rulepathjson, e))
            sys.exit(1) 
    return rulepath

def parseServerDomain(url):
    parts = url.split('/',3)
    return parts[0] + '//' + parts[2]


if __name__ == '__main__':

    testBatchGetLinks()

    (init_urls, gene, rulepathjson) = parseArgs()
    moreInitUrls = generateMoreInitUrls(init_urls, gene)
    print 'Generated init urls:', moreInitUrls
    
    rulepath = parseRulePathParam(rulepathjson)
    serverDomain = parseServerDomain(init_urls[0])
    print 'rulepath: %s, serverDomain:%s' % (rulepath, serverDomain)

    createDir(saveDir)

    dwResPool = IoTaskThreadPool(20)

    downloadFromUrls(moreInitUrls, rulepath)
    dwResPool.close()
    dwResPool.join()
