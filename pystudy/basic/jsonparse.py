#!/usr/bin/python
#_*_encoding:utf-8_*_

import sys
import json

argslen = len(sys.argv)
if argslen != 2:
    print('Usage: python jsonparse.py filename')
    exit(1)

f = sys.argv[1]

with open(f, 'r') as load_f:
    load_dict = json.load(load_f)
    medias = load_dict['data']['medias']
    videolinks = map(lambda x: "https://www.bilibili.com/video/" + x['bv_id'], medias)
    for link in videolinks:
        print(link) 
