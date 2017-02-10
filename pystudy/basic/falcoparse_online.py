#!/usr/bin/python3
#_*_encoding:utf-8_*_

import sys
import json

def parse_field(field):
    field_part = field.split(".")
    field_final = ""
    if len(field_part) == 1:
       field_final = field
    elif len(field_part) == 2:
       field_final = field.split(".")[1]
    field_final = field_final.replace("\t", "")
    for sep in ["=", ">", "<", "<=", ">="]:
        if sep in field_final:
            field_final = field_final.split(sep)[0]
    return field_final

def parse_rule_pattern(rulecontent):
    sub_parts = rulecontent.split(" and ")
    all_parts = []
    for part in sub_parts:
        small_parts = part.split(" or ")
        all_parts.extend(small_parts)
    pattern = set()
    for part in all_parts:
        if part.isspace() == False:
            part = part.strip().replace("not", "")
            field = part.split(" ")[0] 
            if len(field) != 0 and field.isspace() == False:
                field = parse_field(field)
                pattern.add(field)
    return " + ".join(list(pattern))


if __name__ == "__main__":

    with open("alarm_types.txt", "r") as alarm_f:
        alarm_dict = json.load(alarm_f)
        data = alarm_dict['data']
        alarm_type_map = {}
        for alarm in data:
            alarm_type_map[alarm["uuid"]] = alarm["name"]    

    alarm_type_pattern_map = {} 
    with open("rules_falco_online.txt", 'r') as rule_f:
        lines = rule_f.readlines()            
    count = 0
    for line in lines:
        line = line.strip()
        if len(line) == 0 or line.isspace() == True:
            continue
        jsonobj = json.loads(line)
        data = jsonobj['data'] 
        count += len(data)
        for item in data:
            if item['data_type'] == 2:
                continue
            alarm_types = set()
            alarm_type = item.get('alarm_type')
            displays = item['displays']
            content = item['rule_details']['content']
            
            if alarm_type:
               alarm_types.add(alarm_type)
            
            if displays:
               for dis in displays:
                   alarm_types.add(dis['alarm_type'])
 
            rule_pattern = parse_rule_pattern(content)

            #print("%s %s" %(alarm_types, rule_pattern))
            for at in alarm_types:
                if not alarm_type_pattern_map.get(at):
                    alarm_type_pattern_map[at] = set()
                alarm_type_pattern_map[at].add(rule_pattern) 

    #print(alarm_type_pattern_map)
    print("alarm_type => rule_patterns\n") 
               
    for alarm_type, rule_patterns in alarm_type_pattern_map.items():
        print("%s %s %s\n" % (alarm_type, alarm_type_map.get(alarm_type), rule_patterns))     

    print("rule count: %s" % count)
       
