# -*- coding: utf-8 -*-

from xml.dom.minidom import parse
def readXML():
    domTree = parse("/Users/qinshu/Downloads/cnblogs_backup.xml")
    rootNode = domTree.documentElement

    # 所有文章
    posts = rootNode.getElementsByTagName("entry")
    print("****所有文章****")
    for post in posts:
        # title 元素
        # title = post.getElementsByTagName("title")[0]
        # print("title: %s", title.childNodes[0].data)
        # link 元素
        link = post.getElementsByTagName("link")[0]
        print(link.getAttribute("href"))

if __name__ == '__main__':
    readXML()

