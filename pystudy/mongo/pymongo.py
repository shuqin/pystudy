#!/usr/bin/python3
#_*_encoding:utf-8_*_
 
import json
import pymongo
 
mogoclient = pymongo.MongoClient("mongodb://qingteng:PASSWD@172.16.17.51:27017/")
 
dblist = mogoclient.list_database_names()
 
wisteriadblist = filter(lambda s: s.startswith("wisteria"), dblist)
 
for db in wisteriadblist:
 
    print('dbname: %s' % db)
 
    dbconn = mogoclient[db]
    collection_names = dbconn.list_collection_names()
    for col in collection_names:
        print("collection name: %s" % col)
        one_doc = dbconn[col].find_one()
        if not one_doc:
            print("Empty Set\n")
            continue
 
        for k,v in one_doc.items():
            if type(v) not in ['int', 'float', 'bool', 'str', 'list', 'dict']:
                one_doc[k] = str(v)
         
 
        docstr = json.dumps(one_doc, indent=4)
        print("document example: %s" % docstr)
 
        print("\n")
