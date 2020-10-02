#!/usr/bin/python3
#_*_encoding:utf-8_*_

import re
import sys
import json

import argparse
from bs4 import BeautifulSoup
from common.net import *
from common.multitasks import *

def parseArgs():
    description = '''This program is used to batch download resources from specified urls.
                     eg python dw.py -u http://xxx.html -r '[{"img":["jpg"]}, {"class":["resLink"]}, {"id": ["HidenDataArea"]}]'
                     will search and download resources from network urls http://xxx.html  by specified rulePath
                  '''
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('-u','--url', nargs='+', help='At least one html urls are required', required=True)
    parser.add_argument('-r','--rulepath',nargs=1,help='rule path to search restures. if not given, search restures in given urls', required=False)
    args = parser.parse_args()
    init_urls = args.url
    rulepath = args.rulepath
    return (init_urls, rulepath)

def getAbsLink(serverDomain, link):

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

    # print("body==="+htmlcontent)
    soup = BeautifulSoup(htmlcontent, "lxml")
    alinks = []
    reslinks = []

    for (key, values) in rule.items():
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
                    print("\nLLL======".join(links))
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
    dwResPool.execAsync(download, resOriginAddresses)

def batchGetLinks(urls, rules):
    htmlcontentList = map(getHTMLContent, urls)
    allLinks = batchGetLinksByRule(htmlcontentList, rules)
    with open('/Users/qinshu/joy/reslinks.txt','w') as f:
        for link in allLinks:
            print(link)
            f.write(link + "\n")

def parseRulePathParam(rulepathjson):
    rulepath = [{'img': ['jpg']}]
    if rulepathjson:
        try:
        	rulepath = json.loads(rulepathjson[0])
        except ValueError as e:
            print('Param Error: invalid rulepath %s %s' % (rulepathjson, e))
            sys.exit(1) 
    return rulepath

def parseServerDomain(url):
    parts = url.split('/',3)
    return parts[0] + '//' + parts[2]

def testBatchGetLinks():
    urls = ['http://dp.pconline.com.cn/list/all_t145.html']
    rules = {"img":["jpg"],"video":["mp4"]}
    
    batchGetLinks(urls, rules)

if __name__ == '__main__':

    # testBatchGetLinks()

    (init_urls, rulepathjson) = parseArgs()
    print('init urls: %s' % "\n".join(init_urls))

    rulepath = parseRulePathParam(rulepathjson)
    serverDomain = parseServerDomain(init_urls[0])
    print('rulepath: %s\n serverDomain:%s' % (rulepath, serverDomain))

    batchGetLinks(init_urls, rulepath)

    # dwResPool = IoTaskThreadPool(20)

    # downloadFromUrls(init_urls, rulepath)
    # dwResPool.close()
    # dwResPool.join()



