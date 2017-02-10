# -*- coding: utf-8 -*-

import markdownify
import sys
from bs4 import BeautifulSoup

inputfname_withext = sys.argv[1]
inputfname = inputfname_withext[:inputfname_withext.index(".")]

with open(inputfname + ".html") as fr:
    html = fr.read()

soup = BeautifulSoup(html, "lxml")
post_body = soup.find('div', id="cnblogs_post_body")

md = markdownify.markdownify(str(post_body), heading_style="ATX")

with open(inputfname + ".md", "w") as fw:
    fw.write(md)

