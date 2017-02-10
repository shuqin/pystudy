#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import os
import sys
import configparser

def readFile(htmlfilepath):

    content = ""
    with open(htmlfilepath) as hf:
         for line in hf:
              content += line.strip() + " "
    return content          


def escapeStr(text):
    return text.replace('\"', '\\"')

def generate(htmlfilepath, configs):
    
    filenamepath = os.path.basename(htmlfilepath)

    config = configs.get(filenamepath, configs['default'])
    htmlstr = readFile(htmlfilepath)

    return [{"update":"service_notification_event","updates":[{"q":{"id":config['title']},"u":{"$set":{"name":config['zn'],"type":"NOTICE_TYPE_INTRUSION","subtype":config['title'],"display_name":{"zh-cn":config['zn']}},"$currentDate":{"created_at":True,"updated_at":True}},"upsert":True}]},{"update":"service_notification_template","updates":[{"q":{"id":config['title']+"_WEB"},"u":{"$set":{"name":config['zn']+"-站内信","event_id":config['title'],"send_method":"WEB","default_text":{"subject":"{% for agentEvent in aggregateAgentEvents %} {% if agentEvent.params.containerId %} [{{ agentEvent.params.detectionSeverity }}]容器{{ agentEvent.params.containerName }}于{{ agentEvent.params.detectionTime }}检测到{{ agentEvent.params.detectionType }}告警:{{ agentEvent.params.content }} {% else %}  [{{ agentEvent.params.detectionSeverity }}]主机{{ agentEvent.params.hostname }}({{ agentEvent.params.displayIp }})于{{ agentEvent.params.detectionTime }}检测到{{ agentEvent.params.detectionType }}告警:{{ agentEvent.params.content }} {% endif %}  {{showOneRecord(aggregateAgentEvent)}} {% endfor %}","body":escapeStr(htmlstr),"language":"zh-CN"}},"$currentDate":{"created_at":True,"updated_at":True}},"upsert":True}]},{"update":"service_notification_template","updates":[{"q":{"id":config['title']+"_EMAIL"},"u":{"$set":{"name":config['zn']+"-邮件","event_id":config['title'],"send_method":"EMAIL","default_text":{"subject":"{% for agentEvent in aggregateAgentEvents %} {% if agentEvent.params.containerId %} [{{ agentEvent.params.detectionSeverity }}]容器{{ agentEvent.params.containerName }}于{{ agentEvent.params.detectionTime }}检测到{{ agentEvent.params.detectionType }}告警:{{ agentEvent.params.content }} {% else %}  [{{ agentEvent.params.detectionSeverity }}]主机{{ agentEvent.params.hostname }}({{ agentEvent.params.displayIp }})于{{ agentEvent.params.detectionTime }}检测到{{ agentEvent.params.detectionType }}告警:{{ agentEvent.params.content }} {% endif %}  {{showOneRecord(aggregateAgentEvent)}} {% endfor %}","body":escapeStr(htmlstr),"language":"zh-CN"}},"$currentDate":{"created_at":True,"updated_at":True}},"upsert":True}]},{"update":"service_notification_template","updates":[{"q":{"id":config['title']+"_SMS"},"u":{"$set":{"name":config['zn']+"-短信","event_id":config['title'],"send_method":"SMS","default_text":{"subject":"入侵告警通知，建议立即处理","body":"{% for agentEvent in aggregateAgentEvents %} {% if agentEvent.params.containerId %}  [{{ agentEvent.params.detectionSeverity }}]容器{{ agentEvent.params.containerName }}于{{ agentEvent.params.detectionTime }}检测到{{ agentEvent.params.detectionType }}告警:{{ agentEvent.params.content }} {% else %}     [{{ agentEvent.params.detectionSeverity }}]主机{{ agentEvent.params.hostname }}({{ agentEvent.params.displayIp }})于{{ agentEvent.params.detectionTime }}检测到{{ agentEvent.params.detectionType }}告警:{{ agentEvent.params.content }} {% endif %}  {{showOneRecord(aggregateAgentEvent)}} {% endfor %}","language":"zh-CN"}},"$currentDate":{"created_at":True,"updated_at":True}},"upsert":True}]}]
    

def parsePaths(args):
    files = []
    for arg in args[1:]:
        if os.path.isfile(arg):
            files.append(arg)
        elif os.path.isdir(arg):
             for parent,dirnames,filenames in os.walk(arg):
                 for filename in filenames:
                     files.append(os.path.join(parent,filename))                  
    return files          


def generateAll(htmlfilepaths, configs):

    result = list()
    for htmlfp in htmlfilepaths:
        result.extend(list(generate(htmlfp, configs)))
    return result    

if __name__ == '__main__':


    config = configparser.ConfigParser()
    config.read("template.ini")  

    configs = {"default": {"title":"", "zn":""}}
    for sec, value in config.items():
        configs[sec] = {}
        for key in config[sec].keys():
             section = config[sec]
             configs[sec][key] = section.get(key)   
    
    print(configs)

    filepaths = parsePaths(sys.argv)
    print(filepaths)

    jsonall = generateAll(filepaths, configs)

    print(json.dumps(jsonall).encode().decode("unicode_escape"))

    print(escapeStr('"abc"'))
