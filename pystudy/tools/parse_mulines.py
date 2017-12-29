#!/usr/bin/python
#_*_encoding:utf-8_*_

import re

# config line keywords to seperate lines.
ksconf = [['S'], ['# User@Host:','Id:'] , ['# Schema:', 'Last_errno:', 'Killed:'], ['# Query_time:','Lock_time:', 'Rows_sent:', 'Rows_examined:', 'Rows_affected:'], ['# Bytes_sent:'], ['SET timestamp=']]
files = ['slow_sqls.txt']

#ksconf = [['id:'], ['name:'], ['able:']]
#files = ['stu.txt']

globalConf = {'ksconf': ksconf, 'files': files}


#linesConf=['id:', 'name:', 'able:']

def produceRegex(keywordlistInOneLine):
    ''' build the regex to match keywords in the list of keywordlistInOneLine '''
    oneLineRegex = "^\s*"
    oneLineRegex += "(.*?)".join(keywordlistInOneLine)
    oneLineRegex += "(.*?)\s*$"
    return oneLineRegex

def readFile(filename):
    f = open(filename)
    ftext = ''
    for line in f:
        ftext += line
    f.close()
    return ftext

def readAllFiles(files):
    return ''.join(map(readFile, files))

def findInText(regex, text, linesConf):
    '''
       return a list of maps, each map is a match to multilines,
              in a map, key is the line keyword
                         and value is the content corresponding to the key
    '''
    matched = regex.findall(text)
    if empty(matched):
        return []

    allMatched = []
    linePatternMap = buildLinePatternMap(linesConf)
    for onematch in matched:
        oneMatchedMap = buildOneMatchMap(linesConf, onematch, linePatternMap)
        allMatched.append(oneMatchedMap)
    return allMatched

def buildOneMatchMap(linesConf, onematch, linePatternMap):
    sepLines = map(lambda ks:ks[0], linesConf)
    lenOflinesInOneMatch = len(sepLines)
    lineMatchedMap = {}
    for i in range(lenOflinesInOneMatch):
        lineContent = sepLines[i] + onematch[i].strip()
        linekey = getLineKey(linesConf[i])
        lineMatchedMap.update(matchOneLine(linesConf[i], lineContent, linePatternMap))
    
    return lineMatchedMap    

def matchOneLine(keywordlistOneLine, lineContent, patternMap):
    '''
       match lineContent with a list of keywords , and return a map 
       in which key is the keyword and value is the content matched the key.
       eg. 
       keywordlistOneLine = ["host:", "ip:"] , lineContent = "host: qinhost ip: 1.1.1.1"
       return {"host:": "qinhost", "ip": "1.1.1.1"}
    '''
    
    ksmatchedResult = {}
    if len(keywordlistOneLine) == 0 or lineContent.strip() == "":
        return {}
    linekey = getLineKey(keywordlistOneLine)
    
    if empty(patternMap):
        linePattern = getLinePattern(keywordlistOneLine)
    else:
        linePattern = patternMap.get(linekey)
    
    lineMatched = linePattern.findall(lineContent)
    if empty(lineMatched):
        return {}
    kslen = len(keywordlistOneLine)
    if kslen == 1:
        ksmatchedResult[cleankey(keywordlistOneLine[0])] = lineMatched[0].strip()
    else:
        for i in range(kslen):                            
            ksmatchedResult[cleankey(keywordlistOneLine[i])] = lineMatched[0][i].strip()
    
    return ksmatchedResult

def empty(obj):
    return obj is None or len(obj) == 0

def cleankey(dirtykey):
    ''' clean unused characters in key '''
    return re.sub(r"[# :]", "", dirtykey)

def printMatched(allMatched, linesConf):
    allks = []
    for kslist in linesConf:
        allks.extend(kslist)
    for matched in allMatched:
        for k in allks:
            print cleankey(k) , "=>", matched.get(cleankey(k))
        print '\n'    

def buildLinePatternMap(linesConf):
    linePatternMap = {}
    for keywordlistOneLine in linesConf:
        linekey = getLineKey(keywordlistOneLine)
        linePatternMap[linekey] = getLinePattern(keywordlistOneLine)
    return linePatternMap    

def getLineKey(keywordlistForOneLine):
    return "_".join(keywordlistForOneLine)

def getLinePattern(keywordlistForOneLine):
    return re.compile(produceRegex(keywordlistForOneLine))

def testMatchOneLine():
    assert len(matchOneLine([], "haha", {})) == 0
    assert len(matchOneLine(["host"], "", {})) == 0
    assert len(matchOneLine("", "haha", {})) == 0 
    assert len(matchOneLine(["host", "ip"], "host:qqq addr: 1.1.1.1", {})) == 0

    lineMatchMap1 = matchOneLine(["id:"], "id: 123456", {"id:": re.compile(produceRegex(["id:"]))})
    assert lineMatchMap1.get("id") == "123456"

    lineMatchMap2 = matchOneLine(["host:", "ip:"], "host: qinhost  ip: 1.1.1.1  ", {"host:_ip:": re.compile(produceRegex(["host:", "ip:"]))})
    assert lineMatchMap2.get("host") == "qinhost"
    assert lineMatchMap2.get("ip") == "1.1.1.1"
    print 'testMatchOneLine passed.'


if __name__ == '__main__':

    testMatchOneLine()

    files = globalConf['files']
    linesConf = globalConf['ksconf']
    sepLines = map(lambda ks:ks[0], linesConf)

    text = readAllFiles(files)
    wholeRegex = produceRegex(sepLines)
    print 'wholeRegex: ', wholeRegex

    compiledPattern = re.compile(wholeRegex, flags=re.DOTALL+re.MULTILINE)
    allMatched = findInText(compiledPattern, text, linesConf)
    printMatched(allMatched, linesConf)

