# -*- coding: utf-8 -*-
# -------------------------------------------------------------------------------
# Name:          db_tables_descs.py
# Purpose:       generate the tables that describe the meanings of fields in db
#
# Author:       qin.shuq
#
# Created:      2014/11/17
# Output:       desc.txt
#               recording the tables that describe the meanings of fields in db
#-------------------------------------------------------------------------------
#!/usr/bin/env python

import db

globalFieldDescs = ('Field', 'Type', 'Null', 'Key', 'Default', 'Extra')

globalDescFile = '../data/desc.txt'

conflictedWithMysqlKeywords = set(['group'])

fieldDescMapping = {
    'id':         '唯一标识',
    'is_deleted': '是否逻辑删除',
    'status':     '实体状态',
    'type':       '实体类型',
    'priority':   '优先级',
    'password':   '密码',
    'ip':         'ip 地址',
    'mac':        'mac 地址',
    'protocol':   '访问协议',
    'user_id':    '用户唯一标识'
}

def formatCols(fieldDesc):
    return  "%-16s %-24s %-5s %-8s %-8s %-30s" % fieldDesc

def withNewLine(astr):
    return astr + '\n'


def commonFieldsProcess(fieldDescList):
    fieldName = fieldDescList[0]
    fieldDesc = fieldDescMapping.get(fieldName)
    desclen =   len(fieldDescList)
    if fieldDesc is None:
        if fieldName.startswith('gmt_c'):
            fieldDesc = '创建时间'
        elif fieldName.startswith('gmt_m'):
            fieldDesc = '修改时间'
        else:
            fieldDesc = fieldDescList[desclen-1]
    fieldDescList[desclen-1] = fieldDesc

def formatF(fieldDescTuple):
    fieldDescList = list(fieldDescTuple)
    fieldLen = len(fieldDescList)
    for i in range(fieldLen):
        if fieldDescList[i] is None:
            fieldDescList[i] = 'NULL'
        else:
            fieldDescList[i] = str(fieldDescList[i])
    commonFieldsProcess(fieldDescList)
    return formatCols(tuple(fieldDescList))

def format(tableDesc):
    desc = ''
    for fieldDescTuple in tableDesc:
        desc += withNewLine(formatF(fieldDescTuple))
    return desc

def descDb(givenDb):
    tablesRet = givenDb.query("show tables;")
    print tablesRet
    tableNames = [table[0] for table in tablesRet]
    desc = ''
    for tablename in tableNames:
        if tablename in conflictedWithMysqlKeywords:
            tablename = '`' + tablename + '`'
        descSql = "desc " + tablename
        tableDesc = givenDb.query(descSql)
        desc += withNewLine(tablename)
        desc += withNewLine(formatCols(globalFieldDescs)).decode('utf-8')
        desc += withNewLine(format(tableDesc)).decode('utf-8')
        desc += withNewLine('').decode('utf-8')
    return desc


def main():

    descFile = open(globalDescFile, 'w')

    mydb = db.Systemdb()
    desc = descDb(mydb)
    descFile.write(desc.encode('utf-8'))


    descFile.close()


if __name__ == '__main__':
    main()
