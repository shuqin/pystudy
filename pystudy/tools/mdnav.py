#!/usr/bin/python                                                           
#_*_encoding:utf-8_*_

import re

mdTitleRegex = r'\s*(#{2,6})\s*(.*?)\s*(?:\1)\s+'
mdTitlePatt = re.compile(mdTitleRegex)

def parseLineByRegex(line, regex_patt):
    m = regex_patt.match(line)
    return m.groups() if m else ()

def outputAnchor(titleTuple):
    if len(titleTuple) == 2:
        intents = '&emsp;' * (len(titleTuple[0])-2)
        print intents,transToAnchor(titleTuple[1].decode('utf-8'))

def procLine(line):
    outputAnchor(parseLineByRegex(line, mdTitlePatt))

def transToAnchor(title):
    return '[%s](#%s)' % (title, title)

if __name__ == '__main__':
    with open('gaiyao.txt') as mdtext:
        mdTitles = map(procLine, mdtext.readlines())

