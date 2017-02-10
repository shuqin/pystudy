#!/usr/bin/python3
#_*_encoding:utf-8_*_

import argparse
import traceback
import pymongo

IP = "10.106.109.10"
PORT = 27017

PASSWORD = "GJVA7FyiwaR1emJd12JaGJDJhRTKegLS"

DETECTION_ID_KEY = "detection_id"
DETECTION_CODE_KEY = "detection_code"


ELEMETN_ID_KEY = "element_id"
ELEMETN_IDS_KEY = "element_ids"

ACTIVITY_ID_KEY = "activity_id"
ACTIVITY_IDS_KEY = "activity_ids"

def usage():
    return
    '''
        this program is to print  db details of specified detections.
        eg.
        python3 detection.py -t 106ac0bfac24af567a05 -d 63aafd01f6b8451c82447da048048e11126

    '''

def parseArgs():
    try:
        description = '''This program is used to print db details of specified detections.
                      '''
        parser = argparse.ArgumentParser(description=description)
        parser.add_argument('-t','--tenant', help='one tenant is required', required=False)
        parser.add_argument('-d','--detections', nargs='+', help='one or more detectionId is required', required=True)
        parser.add_argument('-c','--compare', nargs='+', help='compare two detections', required=False)
        args = parser.parse_args()
        print(args)
        tenant = args.tenant
        detections = args.detections
        compare = args.compare
        return (tenant, detections, compare)
    except:
        usage()
        traceback.print_exc()
        exit(1)

def four_space():
    return '    '

def format_value(value):
    if type(value).__name__ == 'dict':
        return desc(value, 2)
    return str(value)

def format(key, value, n=1):
    return four_space() * n + str(key) + ": " + format_value(value) + "\n"

def desc(doc, n):
    str = '\n'
    for key, value in doc.items():
        str += format(key, value, n)
    return str

def print_d(doc):
    print(desc(doc, 1))

def get_connection():
    connection = ("mongodb://root:%s@%s:%s/?authSource=admin&authMechanism=SCRAM-SHA-256&readPreference=primary&directConnection=true&ssl=false" %(PASSWORD, IP, PORT))
    return connection

def get_client():
    connection = get_connection()
    return pymongo.MongoClient(connection)

def get_db(dbname):
    client = get_client()
    return client[dbname]

def get_all_dbs():
    client = get_client()
    return client.list_database_names()

def print_detection(detectionId, db):

    # 查询 app_ids_detection 表中指定 detectionId 的数据
    query_detection = { DETECTION_ID_KEY: detectionId}
    detection_data = db["app_ids_detection"].find_one(query_detection)
    if not detection_data:
        query_detection2 = { DETECTION_CODE_KEY: detectionId}
        detection_data = db["app_ids_detection"].find_one(query_detection2)
        if not detection_data:
            return False

    print("detection_id:" + detection_data['detection_id'])
    print_d(detection_data)

    # 查询 app_ids_activity 表中指定 activityIds 对应的数据
    if detection_data.get(ACTIVITY_IDS_KEY):
        query_activity = { ACTIVITY_ID_KEY: {"$in": detection_data[ACTIVITY_IDS_KEY]}}
        activity_data = list(db["app_ids_activity"].find(query_activity))
        print("activity_id: " + activity_data[ACTIVITY_ID_KEY])
        print_d(activity_data)

    # 查询 app_ids_element 表中指定 elementIds 对应的数据
    query_element = {ELEMETN_ID_KEY: {"$in": detection_data[ELEMETN_IDS_KEY]}}
    element_data = list(db["app_ids_element"].find(query_element))
    cmds = []
    paths = []
    fpath = ''
    fsha256 = ''
    for e in element_data:
        print("\nelement id: " + e[ELEMETN_ID_KEY])
        print_d(e)
        if e['element_type'] == 'PROCESS':
            cmds.append(e['detail']['cmd'])
            paths.append(e['detail']['path'])
        if e['element_type'] == 'FILE':
            fpath = e['detail']['fpath']
            fsha256 = e['detail']['sha256']

    print("cmds: %s" % cmds)
    print("paths: %s" % paths)
    print("File: fpath %s sha256 %s" % (fpath, fsha256))

    return True



if __name__ == '__main__':

    (tenant, detections, compare) = parseArgs()
    print("tenant: %s detections: %s" % (tenant, detections))

    if tenant:
        db = get_db('tenant_%s' % tenant)
        for d in detections:
            print_detection(d, db)

    all_db_names = get_all_dbs()
    hit_count = 0
    for db_name in all_db_names:
        for d in detections:
             if print_detection(d, get_db(db_name)):
                 hit_count += 1
                 if hit_count == len(detections):
                    break
