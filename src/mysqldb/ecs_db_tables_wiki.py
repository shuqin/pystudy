# -*- coding: utf-8 -*-
# -------------------------------------------------------------------------------
# Name:          ecs_db_tables.py
# Purpose:       generate the tables that describe the meanings of fields in ecs db
#
# Author:       qin.shuq
#
# Created:      2014/11/17
# Output:       ecs_db_tables.txt
#               recording the tables that describe the meanings of fields in ecs db
#-------------------------------------------------------------------------------
#!/usr/bin/env python


from pypet.houyi import db

globalFieldDescs = ('Field', 'Type', 'Null', 'Key', 'Default', 'Extra')

globalDescFile = 'desc.txt'

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
    'user_id':    '用户唯一标识',
    'zone_id':    'Zone域唯一标识',
    'cluster_id': '小集群唯一标识',
    'region_no':  '小集群唯一标识'
}

def formatCols(fieldDesc, sep=''):
    midstr = sep.join(fieldDesc)
    return (sep+midstr)[1:]

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
    return formatCols(tuple(fieldDescList), '||')

def format(tableDesc):
    contents = []
    for fieldDescTuple in tableDesc:
        contents.append(withNewLine(formatF(fieldDescTuple)))
    desc = '|-\n'.join(contents)
    return desc

def descDb(givenDb):
    tablesRet = givenDb.query("show tables;")
    tableNames = [table[0] for table in tablesRet]
    desc = ''
    for tablename in tableNames:
        if tablename in conflictedWithMysqlKeywords:
            tablename = '`' + tablename + '`'
        descSql = "desc " + tablename
        tableDesc = givenDb.query(descSql)
        desc += withNewLine(tablename)
        desc += '{| class="wikitable"\n|-\n'
        desc += withNewLine(formatCols(globalFieldDescs, '!!')).decode('utf-8')
        desc += withNewLine('|-').decode('utf-8')
        desc += withNewLine(format(tableDesc)).decode('utf-8')
        desc += '|}\n'.decode('utf-8')
        desc += withNewLine('').decode('utf-8')
    return desc


def main():

    descFile = open(globalDescFile, 'w')

    regiondb = db.Houyiregiondb()
    desc = descDb(regiondb)
    descFile.write(desc.encode('utf-8'))

    houyi = db.Houyi()
    descFile.write(descDb(houyi).encode('utf-8'))

    descFile.close()


if __name__ == '__main__':
    main()