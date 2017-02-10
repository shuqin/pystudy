#!/usr/bin/python                                                           
#_*_encoding:utf-8_*_

##########################################################################
# mdnav.py: Generate nav anchors for given markdown files
# usage:  python mdnav.py md_filename1 md_filename2 ... md_filenameN
##########################################################################

import re
import sys

mdTitleRegex = r'\s*(#{2,6})\s*(.*?)\s*(?:\1)\s+'
mdTitlePatt = re.compile(mdTitleRegex)

def parseLineByRegex(line, regex_patt):
    m = regex_patt.match(line)
    return m.groups() if m else ()

def outputAnchor(titleTuple):
    if len(titleTuple) == 2:
        intents = '&emsp;' * (len(titleTuple[0])-2)
        title = titleTuple[1]
        anchor = '[%s](#%s)' % (title, title)
        print intents,anchor

def procLine(line):
    outputAnchor(parseLineByRegex(line, mdTitlePatt))

def help():
    print '%s usage: need at least one param as markdown filename' % sys.argv[0]
    print 'python %s filename1 filename2 ... filenameN' % sys.argv[0]

if __name__ == '__main__':
    if len(sys.argv) < 2:
        help()
        exit(1)
    for ind in range(1, len(sys.argv)):
        filename = sys.argv[ind]
        print 'file: ', filename
        with open(filename) as mdtext:
            map(procLine, mdtext.readlines())
