#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
import json
import sys
import math
import time

env = 'qa'
if len(sys.argv) == 2 and sys.argv[1] == 'prod':
    env = 'prod'

print "env: ", env

searchUrlMap = {'qa': 'xxx.qa.s.yyy-inc.com:80', 'prod': 'xxx.s.yyy-inc.com:80'}
searchUrl = searchUrlMap[env]
orderIndex = 'trade_order'
orderType = 'data'
size = 100

url = "http://%s/sync/scan/%s?scroll=600000&size=%d" % (searchUrl, orderIndex, size)

def fetch(url, query):

    r = requests.post(url, data=query)
    jsonobj = r.json()
    #print jsonobj

    if jsonobj['code'] != 0:
        return []

    data = jsonobj['data']
    total = data['hits']['totalHits']
    left = data['leftNumber']
    scrollId = data['scrollId']

    print "total: ", total, "scroll_id: ", scrollId

    allData = []
    first = data['hits']['hits']
    allData.extend(first)
    fetched = len(first)

    while left > 0:
        dataUrl = 'http://%s/sync/scan/%s?scroll=60000&scroll_id=%s&size=%d' % (searchUrl, orderIndex, scrollId, size)
        dr = requests.post(dataUrl, data={})
        # print "data result: " , dr.json()

        listResult = dr.json()
        if listResult['code'] != 0:
            break

        data = listResult['data']

        scroll_id = data['scrollId']
        left = data['leftNumber']
        hits = data['hits']['hits']
        allData.extend(hits)

        fetched += len(hits)
        print "fetched: ", fetched
        time.sleep(0.1)

    return allData

#print es data
def output(rec,fw):
    data = rec['source']
    fields = ["order_no", 'goods_id']
    line = " ".join(map(lambda f: str(data[f]) if str(data[f]) != '' else '-' , fields))
    fw.write(line + '\n')


if __name__ == '__main__':

    fw = open('/tmp/goods_info.txt', 'w')
    for line in open('goods.txt'):
        (kdtId, goodsId) = line.strip().split(",")
        query = '{"query":{"bool":{"must":[{"term":{"head_kdt_id":"%s"}},{"term":{"goods_id":"%s"}}],"should":[],"must_not":[]}},"from":0,"size":"10"}' % (kdtId, goodsId)

        allDatas = fetch(url, query)
        # print allDatas

        # pass user-defined data handler
        handle = output

        for rec in allDatas:
            handle(rec,fw)

    fw.close()
