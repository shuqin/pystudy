#_*_encoding:utf-8_*_

import json
import sys

reload(sys)
sys.setdefaultencoding('utf-8')

def readFile(filename):
    content = ''
    f = open(filename)
    for line in f:
        content += line.strip("\n")
    f.close()
    return content


def cmpArray(jsonArr1, jsonArr2, f_res):
    for i in range(0, len(jsonArr1)):
        diffDict(jsonArr1[i], jsonArr2[i], f_res)

def cmpPrimitive(key, value1, value2, f_res):

    if isinstance(value1,list) or isinstance(value1, dict) \
       or isinstance(value2, list) or isinstance(value2, dict):
       return

    if value1 == value2:
       f_res.write(key + " " + str(value1) + " OK\n")
    else:
       f_res.write(key + " " + str(value1) + " " + str(value2) + " NotEqual\n") 


def diffDict(json1, json2, f_res):

    for (key, value) in json1.iteritems():
        json2Value = json2.get(key)
        #print "key: ", key, ", value: ", value, " , value2: ", json2Value
        if json2Value == None:
            f_res.write(key + " in json1, not in json2 " + "\n")

        if isinstance(value, dict) and isinstance(json2Value, dict):
            diffDict(value, json2Value, f_res)        
 
        if isinstance(value, list) and isinstance(json2Value, list):
            cmpArray(value, json2Value, f_res)   

        cmpPrimitive(key, value, json2Value, f_res)    
 

def diffJson(json1, json2, f_res):
    diffDict(json1, json2, f_res)
    f_res.close()


if __name__ == "__main__":
    content1 = readFile("/Users/shuqin/Data/order_list_data.txt")
    content2 = readFile("/Users/shuqin/Data/pf_list_data.txt")
    json1 = json.loads(content1)
    json2 = json.loads(content2)
    diffJson(json1, json2, open('diff_waptopf.txt', 'w'))
    diffJson(json2, json1, open('diff_pftowap.txt', 'w'))
