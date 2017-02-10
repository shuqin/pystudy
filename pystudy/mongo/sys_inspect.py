#!/usr/bin/python3
#_*_encoding:utf-8_*_

import datetime
import json
import traceback
import socket
import subprocess
import pymongo
from bson.objectid import ObjectId

PORT = 27017

ONE_DAY_MILLISECONDS = 86400000

LOG_DIR = "/var/log/pods/"

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

def convert_to_timestamp(time_str):

    from datetime import datetime, timedelta

    time_format = '%Y-%m-%dT%H:%M:%S.%fZ'
    utc_time = datetime.strptime(time_str, time_format)
    utc_time = utc_time - timedelta(hours=8)
    local_offset = timedelta(hours=8)
    local_time = utc_time + local_offset
    timestamp = local_time.timestamp()
    return local_time.timestamp() * 1000

def get_command_output(cmd):
    output = subprocess.check_output(cmd, shell=True)
    return output.decode()

def get_log_file(keyword):
    output = get_command_output('ls %s | grep %s' % (LOG_DIR, keyword))
    return LOG_DIR + output.strip() + "/main/0.log"


def parse_log(log_file, time_range, log_handler):

    with open(log_file, 'r') as f:
        count = 0
        for line in f:
            parts = line.split(" ")
            log = " ".join(parts[3:])
            try:
                json_obj = json.loads(log)
                time = convert_to_timestamp(json_obj['time'])
                if time >= time_range[0] and time <= time_range[1]:
                    if log_handler(json_obj):
                        count += 1
            except:
                print("exception. log: %s" % log)
                traceback.print_exc()

    return count



def severity_map():
    return { 0: 'Low', 1: 'Medium', 2: 'High',  3: 'Critical' }

def format_time(timestamp):
    dt = datetime.datetime.fromtimestamp(timestamp / 1000)
    return dt.strftime('%Y-%m-%d %H:%M:%S')

def day_range(dayago):

    now = datetime.datetime.now()
    beforeday = now - datetime.timedelta(days=dayago)
    start_of_day = datetime.datetime(beforeday.year, beforeday.month, beforeday.day, 0, 0, 0, 0)
    timestamp = int(start_of_day.timestamp())
    return (timestamp * 1000 ,  timestamp * 1000 + ONE_DAY_MILLISECONDS - 1)

def get_ip():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.connect(("8.8.8.8", 80))
    ip_address = sock.getsockname()[0]
    sock.close()
    return ip_address


def get_connection():

    ip = get_ip()
    password = get_command_output('kubectl -n infra-system get secret mongo-mongodb -o jsonpath="{.data.mongodb-root-password}" | base64 -d')

    #print(ip + " " + password)

    connection = ("mongodb://root:%s@%s:%s/?authSource=admin&authMechanism=SCRAM-SHA-256&readPreference=primary&directConnection=true&ssl=false" %(password, ip, PORT))
    return connection

def get_tenant_dbs():
    connection = get_connection()
    client = pymongo.MongoClient(connection)
    database_names = client.list_database_names()
    print(database_names)
    return list(filter(lambda s: s.startswith('tenant_') , database_names))

def get_db(dbname):
    connection = get_connection()
    client = pymongo.MongoClient(connection)
    return client[dbname]

def get_alert_type_map(app_ids):
    alert_type_map = {}
    alert_types = app_ids.app_ids_info_alert_types.find({})
    for at in alert_types:
        alert_type_map[at['alert_uuid']] = at['alert_name']
    return alert_type_map

def sort_by_value_reverse(detection_type_code_group_result):
    def sort_by_value(item):
        return item[1] * -1

    return sorted(detection_type_code_group_result.items(), key=sort_by_value)


def group_detections(collection, group_field, time_field, time_range):
    pipeline = [
        {
            '$match': {
               time_field: {
                    '$gt': time_range[0],
                    '$lt': time_range[1]
                }
            }
        },
        {
            '$group': {
                '_id': { group_field: '$' + group_field},
                'count': {'$sum': 1}
            }
        }
    ]

    final_result = {}
    result = collection.aggregate(pipeline)
    for res in result:
        final_result[res['_id'][group_field]] = res['count']
    return final_result

def stat_detections_groupby(group_field, tenant_db, time_range, code_map=None):
    print ("count | %s" % group_field)
    sum = 0
    detection_type_code_group_result = group_detections( tenant_db.app_ids_detection, group_field, 'detection_time', time_range)
    detection_type_code_group_result_sorted = sort_by_value_reverse(detection_type_code_group_result)
    if code_map:
        for gr in detection_type_code_group_result_sorted:
            sum += gr[1]
            print("%s     %s(%s)     " % (str(gr[1]), str(code_map.get(gr[0])), gr[0]))
    else:
        for gr in detection_type_code_group_result_sorted:
            sum += gr[1]
            print("%s     %s    " % (str(gr[1]), gr[0]))
    print('detection total number : %s\n' %sum)


def stat_whiterule_effections(tenant_db, time_range):
    print("TOP3 of white rules that effect detections: ")
    detection_white_rule_group_result = group_detections(tenant_db.app_ids_whiterule_hit_detection, 'white_rule_id', 'detection_time', time_range)
    detection_white_rule_group_result_sorted = sort_by_value_reverse(detection_white_rule_group_result)
    top3_white_rule_group_result = detection_white_rule_group_result_sorted[:3]
    top3_white_rule_ids = []
    for res in top3_white_rule_group_result:
        print(res[0], res[1])
        top3_white_rule_ids.append(ObjectId(res[0]))

    top3_white_rules = tenant_db.app_ids_white_rule.find({"_id": { '$in':  top3_white_rule_ids }})
    for wr in top3_white_rules:
        print("top3 white rule id: " + str(wr['_id']) + " " + desc(wr, 1))


def stat_custome_rule_effections(tenant_db, time_range):
    print("TOP3 of custom rules that effect detections: ")
    detection_custom_rule_group_result = group_detections(tenant_db.app_ids_rule_related_detection, 'rule_id', 'create_time', time_range)
    detection_custom_rule_group_result_sorted = sort_by_value_reverse(detection_custom_rule_group_result)
    top3_custom_rule_group_result = detection_custom_rule_group_result_sorted[:3]
    top3_custom_rule_ids = []
    for res in top3_custom_rule_group_result:
        print(res[0], res[1])
        top3_custom_rule_ids.append(res[0])

    top3_custom_rules = tenant_db.app_ids_ioa.find({"rule_id": { '$in':  top3_custom_rule_ids }})
    for wr in top3_custom_rules:
        print("top3 custom rule id: " + str(wr['_id']) + " " + desc(wr, 1))


def cdc_unfinish(app_ids, time_range):
    cdc_check_task = app_ids.app_ids_detect_cdc_check_task
    count = cdc_check_task.count_documents({"create_time": {'$gt': time_range[0], '$lt': time_range[1]}, 'status': { "$in": [0, 6, 80, 90]} })
    print("\ncdc unfinish task count: %s" % count)


def virus_unfinish(app_ids, time_range):
    virus_check_task = app_ids.app_ids_detect_virus_check_task_info
    count = virus_check_task.count_documents({"create_time": {'$gt': time_range[0], '$lt': time_range[1]}, 'status': { "$in": [0, 1, 2, 5]} })
    print("\nvirus unfinish task count: %s" % count)

def scan_running(app_ids, time_range):
    scan_result = app_ids.app_ids_scan_result
    count = scan_result.count_documents({"start_time": {'$gt': time_range[0], '$lt': time_range[1]}, 'status': { "$in": ["running"]} })
    print("\nscan running task count: %s" % count)

def scan_failed(app_ids, time_range):
    scan_result = app_ids.app_ids_scan_result
    count = scan_result.count_documents({"start_time": {'$gt': time_range[0], '$lt': time_range[1]}, 'status': { "$in": ["FAILED"]} })
    print("\nscan failed task count: %s" % count)

def yesterday_stat_all():

    time_range = day_range(1)
    print("system inspect: %s - %s" % (format_time(time_range[0]), format_time(time_range[1])))

    tenant_dbs = get_tenant_dbs()
    for tenant_db in tenant_dbs:
        yesterday_stat(tenant_db, time_range)
        print('\n')


def yesterday_stat(tenant_db_name, time_range):

    tenant_db = get_db(tenant_db_name)
    print("tenant_db_name: %s" % tenant_db_name)

    app_ids = get_db('app_ids')
    alert_type_map = get_alert_type_map(app_ids)

    stat_detections_groupby('detection_type_code', tenant_db,  time_range, alert_type_map)
    stat_detections_groupby('detection_method', tenant_db, time_range)
    stat_detections_groupby('severity', tenant_db, time_range, severity_map())

    stat_whiterule_effections(tenant_db, time_range)
    stat_custome_rule_effections(tenant_db, time_range)

    cdc_unfinish(app_ids, time_range)
    virus_unfinish(app_ids, time_range)
    scan_running(app_ids, time_range)
    scan_failed(app_ids, time_range)


def hit_denoise_count(time_range):
    hit_denoise_log_handle = lambda log:  'hit denoise model' in log['msg']
    count = parse_log(get_log_file('ids-detect'), time_range, hit_denoise_log_handle)
    print("\nhit denoise count: %s" % count)

def not_hit_denoise_count(time_range):
    hit_denoise_log_handle = lambda log:  'NO_DENOISE' in log['msg']
    count = parse_log(get_log_file('ids-detect'), time_range, hit_denoise_log_handle)
    print("\nnot hit denoise count: %s" % count)

def is_process_create_event(log):
    msg = log['msg']
    if 'detection msg' in msg and 'virus_process' in msg:
        detection_body = msg.split("detection msg:")[1]
        detection_obj = json.loads(detection_body)
        return detection_obj.get('details') and detection_obj.get('details').get('flowtype') == "virus_process"
    return false

def process_create_report_count(time_range):
    count = parse_log(get_log_file('ids-endpoint'), time_range, is_process_create_event)
    print("\nprocess_create event count: %s" % count)

def is_error_log(log):
    return log['level'] == 'ERROR'

def stat_exception(time_range):
    count = parse_log(get_log_file('ids-detect') ,time_range, is_error_log)
    print("\nerror total count: %s" % count)


def real_monitor():
    today_time_range = day_range(0)
    print(today_time_range)

    stat_exception(today_time_range)

    hit_denoise_count(today_time_range)
    not_hit_denoise_count(today_time_range)
    #process_create_report_count(today_time_range)

if __name__ == "__main__":

    yesterday_stat_all()
    real_monitor()





