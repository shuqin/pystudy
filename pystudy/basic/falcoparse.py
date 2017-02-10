#!/usr/bin/python
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
            part = part.strip()
            field = part.split(" ")[0] 
            if len(field) != 0 and field.isspace() == False:
                field = parse_field(field)
                pattern.add(field)
    return " + ".join(list(pattern))


if __name__ == "__main__":

    rule = parse_rule_pattern('process_create.pname = \"echo.exe\" and process_create.path = \"C:\\Program Files\\Git\\usr\\bin\\echo.exe\" and  process_create.cmd = \"echo.exe  all_value_test\" and process_create.ppname = \"cmd.exe\"')
    print(rule)

    with open("alarm_types.txt", "r") as alarm_f:
        alarm_dict = json.load(alarm_f)
        alarm_type_map = {}
        for alarm in alarm_dict:
            alarm_type_map[alarm["uuid"]] = alarm["alarm_name"]    

    with open("rules_falco2.txt", 'r') as rule_f:
        load_dict = json.load(rule_f)
        alarm_type_pattern_map = {}
        for item in load_dict:
            if item['data_type'] == 2:
                continue
            alarm_types = set()
            alarm_type = item.get('alarm_type')
            displays = item['displays']
            content = item['detail']['content']
            
            if alarm_type:
               alarm_types.add(alarm_type)
            
            if displays:
               for dis in displays:
                   alarm_types.add(dis['alarm_type'])
 
            rule_pattern = parse_rule_pattern(content)

            for at in alarm_types:
                if not alarm_type_pattern_map.get(at):
                    alarm_type_pattern_map[at] = set()
                alarm_type_pattern_map[at].add(rule_pattern) 

        print("alarm_type => rule_patterns\n") 
               
        for alarm_type, rule_patterns in alarm_type_pattern_map.items():
             print("%s %s %s\n" % (alarm_type, alarm_type_map.get(alarm_type), rule_patterns))     
 
