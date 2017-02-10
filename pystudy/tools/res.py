#!/usr/bin/python3
#_*_encoding:utf-8_*_

import re
import sys
import json

import argparse
from bs4 import BeautifulSoup
from common.net import *
from common.multitasks import *

SaveResLinksFile = '/Users/qinshu/joy/reslinks.txt'
serverDomain = ''

def parseArgs():
    description = '''This program is used to batch download resources from specified urls.
                     eg. python3 res.py -u http://xxx.html -r 'img=jpg,png;class=resLink;id=xyz'
                     will search resource links from network urls http://xxx.html  by specified rules
                     img = jpg or png OR class = resLink OR id = xyz [ multiple rules ]

                     python3 tools/res.py -u 'http://tu.heiguang.com/works/show_167480.html' -r 'img=jpg!c'
                     for <img src="xxx.jpg!c"/> 
                  '''
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('-u','--url', nargs='+', help='At least one html urls are required', required=True)
    parser.add_argument('-r','--rulepath', nargs=1, help='rules to search resources. if not given, search a hrefs or img resources in given urls', required=False)
    args = parser.parse_args()
    init_urls = args.url
    rulepath = args.rulepath
    return (init_urls, rulepath)

def getAbsLink(serverDomain, link):

    try:
        href = link.attrs['href']
        if href.startswith('//'):
            return 'https:' + href
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
    return filter(lambda x: x != '', hrefs)

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

    print("html===\n"+htmlcontent+"\n===End")
    print("rule===\n"+str(rule)+"\n===End")

    soup = BeautifulSoup(htmlcontent, "lxml")
    alinks = []
    reslinks = []

    for (key, values) in rule.items():
        if key == 'id':
            for id in values:
                links = soup.find_all('a', id=id)
                links = map(getTrueResLink, links)
                links = filter(lambda x: x != '', links)
                alinks.extend(links)
        elif key == 'class':
            for cls in values:
                if cls == '*':
                    links = soup.find_all('a')
                else:
                    links = soup.find_all('a', class_=cls)
                links = map(lambda link: getAbsLink(serverDomain, link), links)
                links = filter(lambda x: validate(x), links)
                alinks.extend(links)
        elif key in resTags:
            for resSuffix in values:
                reslinks.extend(soup.find_all(key, src=re.compile(resSuffix)))

    allLinks = []
    allLinks.extend(alinks)
    allLinks.extend(batchGetResTrueLink(reslinks))
    return allLinks

def validate(link):

    validSuffix = ['png', 'jpg', 'jpeg', 'mp4']

    for suf in validSuffix:
        if link.endswith(suf):
            return True
    if link == '':
        return False
    if link.endswith('html'):
        return False
    if 'javascript' in link:
        return False    
    return True    

def batchGetLinksByRule(htmlcontentList, rules):
    '''
       find all res links from html content list by rules
    '''

    links = []
    for htmlcontent in htmlcontentList:
        for rule in rules:
            links.extend(findWantedLinks(htmlcontent, rule))
    return links

def batchGetLinks(urls, rules):
    conf = {"async":1, "targetIdWhenAsync": "page-fav", "sleepWhenAsync": 10}
    grasper = HTMLGrasper(conf)
    htmlcontentList = grasper.batchGrapHtmlContents(urls)
    allLinks = batchGetLinksByRule(htmlcontentList, rules)
    with open(SaveResLinksFile, 'w') as f:
        for link in allLinks:
            print(link)
            f.write(link + "\n")

def parseRulesParam(rulesParam):
    '''
       parse rules params to rules json
       eg. img=jpg,png;class=resLink;id=xyz to
           [{"img":["jpg","png"], "class":["resLink"], "id":["xyz"]}]
    '''
    defaultRules = [{'img': ['jpg','png','jpeg']},{"class":"*"}]
    if rulesParam:
        try:
            rules = []
            rulesStrArr = rulesParam[0].split(";")
            for ruleStr in rulesStrArr:
                ruleArr = ruleStr.split("=")
                key = ruleArr[0]
                value = ruleArr[1].split(",")
                rules.append({key: value})
            return rules
        except ValueError as e:
            print('Param Error: invalid rulepath %s %s' % (rulepathjson, e))
            sys.exit(1)
    return defaultRules

def parseServerDomain(url):
    parts = url.split('/', 3)
    return parts[0] + '//' + parts[2]

def testBatchGetLinks():
    urls = ['http://dp.pconline.com.cn/list/all_t145.html']
    rules = [{"img":["jpg"], "video":["mp4"]}]

    batchGetLinks(urls, rules)

if __name__ == '__main__':

    #testBatchGetLinks()

    (init_urls, rulesParam) = parseArgs()
    print('init urls: %s' % "\n".join(init_urls))

    rulepath = parseRulesParam(rulesParam)
    serverDomain = parseServerDomain(init_urls[0])
    print('rulepath: %s\n serverDomain:%s' % (rulepath, serverDomain))

    batchGetLinks(init_urls, rulepath)



