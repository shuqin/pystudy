#!/usr/bin/python3
#_*_encoding:utf-8_*_

import os
import random
import string
import json
import time
import argparse
import traceback
import subprocess


from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver import ActionChains
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import requests
from bs4 import BeautifulSoup
from PIL import Image


# 下载目录设置
save_path = '/Users/qinshu/Downloads'
img_width_threshold = 500
img_height_threshold = 500

def usage():

    usage_info = '''
        This program is used to batch download pictures or videos from specified url.
        search and download pictures or videos from network url by specified rules.

        options:
              -u --url  one html url is required
              -f --file one file is specified
              -c --classname a class name selector to locate href link elements
              -s --css a css selector to locate href link elements
              -a --attr a custom attribute selector to locate href link elements
              -k --keyword a keyword to specify filter href links
              -t --type specify source type eg. img, video
              -g --generate generate more paged htmls based on url specified by url. eg.  url = https://search.bilibili.com/all?keyword=%E5%8F%A4%E5%85%B8%E8%88%9E&from_source=webtop_search&spm_id_from=333.1007&search_source=5 generate = 2-5 produces url list contains  https://search.bilibili.com/all?keyword=%E5%8F%A4%E5%85%B8%E8%88%9E&from_source=webtop_search&spm_id_from=333.1007&search_source=5&page=[2-5]

        eg.
            python3 dw.py -u https://dp.pconline.com.cn/list/all_t601.html -k photo
            python3 dw.py -u https://dp.pconline.com.cn/list/all_t601.html -c picLink
            python3 dw.py -f /Users/qinshu/workspace/pystudy/pystudy/tools/yijiu.html -c J_TGoldData
            python3 dw.py -f /Users/qinshu/workspace/pystudy/pystudy/tools/yijiu.html -s ".photo .J_TGoldData"
            python3 dw.py -f /Users/qinshu/workspace/pystudy/pystudy/tools/yijiu.html -s ".photo .J_TGoldData" -t video
            python3 dw.py -u https://dp.pconline.com.cn/list/all_t601.html -c picLink -t img
            python3 dw.py -u https://dp.pconline.com.cn/list/all_t601.html -c picLink -t img -s "#J-BigPic img"
            python3 dw.py -u https://www.yituyu.com/tag/65/p21/ -c ztitle -k gallery -t img -s ".lazy"
            python3 dw.py -u https://dp.pconline.com.cn/photo/5197753.html -s ".picTxtList .lWork"
            python3 dw.py -u https://space.bilibili.com/1995535864 -c cover  -t video
            python3 dw.py -u 'https://search.bilibili.com/all?keyword=%E5%8F%A4%E5%85%B8%E8%88%9E&from_source=webtop_search&spm_id_from=333.1007&search_source=5' -a 'data-mod=search-card' -k video -t video
            python3 dw.py -u 'https://search.bilibili.com/all?keyword=%E5%8F%A4%E5%85%B8%E8%88%9E&from_source=webtop_search&spm_id_from=333.1007&search_source=5' -a 'data-mod=search-card' -k video -t video -g 2-34

    '''

    print(usage_info)


def parseArgs():
    try:
        description = '''This program is used to batch download pictures or videos from specified urls.
                                will search and download pictures or videos from network url by specified rules.
                      '''
        parser = argparse.ArgumentParser(description=description)
        parser.add_argument('-u','--url', help='one html url is specified', required=False)
        parser.add_argument('-f','--file', help='one file is specified', required=False)
        parser.add_argument('-g','--generate', help='generate more paged htmls based on url specified by url', required=False)
        parser.add_argument('-c','--classname', help='a class name element selector to locate href link elements', required=False)
        parser.add_argument('-s','--css', help='a css selector to locate href link elements', required=False)
        parser.add_argument('-a','--attr', help='a custom attribute selector to locate href link elements', required=False)
        parser.add_argument('-k','--keyword', help='a keyword to specify filter href links', required=False)
        parser.add_argument('-t','--type', help='source type specified, eg. img, video', required=False)
        args = parser.parse_args()
        print(args)
        url = args.url
        file = args.file
        generate = args.generate
        clsname = args.classname
        css = args.css
        attr = args.attr
        keyword = args.keyword
        sourcetype = args.type
        print("%s %s %s %s %s %s %s %s" % (url, file, generate, clsname, css, attr, keyword, sourcetype))
        return (url, file, generate, clsname, css, attr, keyword, sourcetype)
    except:
        usage()
        traceback.print_exc()
        exit(1)

# 生成随机字符串
def generate_random_string(length):
    # 生成随机数字和字母组合的序列
    rand_seq = string.ascii_letters + string.digits
    return ''.join(random.choice(rand_seq) for _ in range(length))


def picsubffix():
    return ["png", "jpg", "jpeg", "tif", "webp"]


def end_with_pic_suffix(link):
    for s in picsubffix():
        if link.endswith(s):
            return True
    return False

def get_suffix(link):
    return link.rsplit(".", 1)[-1]

def complete(link):
    if link.startswith("//"):
        return "https:" + link
    return link

def build_soup(url):

    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')
    options.add_argument('--accept-language=zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7')

    # download corresponding version of chromedriver in https://chromedriver.chromium.org/downloads
    # unzip and cp chromedriver to /usr/local/bin/  then chmod +x /usr/local/bin/chromedriver
    with webdriver.Chrome(options=options) as driver:
        driver.get(url)

        try:
            # 将页面滚动到底部，确保所有内容都被加载和渲染
            driver.execute_script('window.scrollTo(0, document.body.scrollHeight);')
        except:
            print("not scroll to window bottom")

        driver.implicitly_wait(30)

        # 获取完整页面内容
        full_page_content = driver.page_source
        #print(full_page_content)

        # 关闭浏览器

        driver.quit()
        return BeautifulSoup(full_page_content, 'html.parser')

def build_soup_use_request(url):

    response = requests.get(url)
    #print(response.text)
    return BeautifulSoup(response.text, 'html.parser')

def read_file(filename):
    with open(filename, 'r') as f:
                content = f.read()
    return content

def getlinks_by_url(url, clsname, css_selectors, attr, filter_func=None):
    soup = build_soup(url)
    return getlinks(soup, clsname, css_selectors, attr, filter_func)


def getlinks_by_file(file, clsname, css_selectors, attr, filter_func=None):
    content = read_file(file)
    #print(content)
    soup = BeautifulSoup(content, 'html.parser')
    return getlinks(soup, clsname, css_selectors, attr, filter_func)


def getlinks(soup, clsname, css_selectors, attr, filter_func=None):

    all_links = set()
    if clsname:
        all_links.update(getlinks_by_class(soup, clsname, filter_func))

    if css_selectors:
        all_links.update(getlinks_by_css(soup, css_selectors, filter_func))

    if attr:
        all_links.update(getlinks_by_attr(soup, attr, filter_func))

    if len(all_links) != 0:
        return all_links

    return getlinks_all(soup, filter_func)


def get_links_from_elements(elements, filter_func=None):
    links = set()
    for element in elements:
        link = element.get('href')
        if link:
            if not filter_func:
                links.add(complete(link))
                #print(link)
            else:
                if filter_func(link):
                    #print("filtered:%s" % link)
                    links.add(complete(link))

    return links

def getlinks_by_css(soup, css_selectors, filter_func=None):

    elements = soup.select(css_selectors)
    return get_links_from_elements(elements, filter_func)

def getlinks_by_attr(soup, attr, filter_func=None):

    attr_parts = attr.split("=")
    key = attr_parts[0]
    value = attr_parts[1]

    elements = soup.find_all('a', attrs={ key: value })
    return get_links_from_elements(elements, filter_func)

def getlinks_all(soup, filter_func):

    elements = soup.find_all('a')
    return get_links_from_elements(elements, filter_func)

def getlinks_by_id_class(soup, pid, clsname, filter_func=None):

    my_div = soup.find(id=pid)
    elements = my_div.find_all('a', class_=clsname)
    return get_links_from_elements(elements, filter_func)

def getlinks_by_class(soup, clsname, filter_func=None):

    all_elements = []

    # a.className = clsname
    all_elements.extend(soup.find_all('a', {'class': clsname}))

    div_elements = soup.find_all("div", {'class': clsname})
    for div_e in div_elements:
        a_elements = soup.find_all("a")
        all_elements.extend(a_elements)

    return get_links_from_elements(all_elements, filter_func)

def range_secs(base):
    return base + random.random()

def download_from_links(key, links):
    print("url or file: %s links: %s" % (key, links))
    print("number of links: %s"  % len(links))

    if len(links) > 0:
        for link in links:
            if sourcetype:
                time.sleep(range_secs(1))
                download_source(link, sourcetype, css)

def download_source(url, sourcetype, css):

    print("url %s sourcetype %s" % (url, sourcetype))

    # use you-get to download bilibili videoes
    if "bilibili.com" in url and sourcetype == "video":
        download_bibi(url, sourcetype)
        return

    # common download
    if css:
        soup = build_soup(url)
        elements = soup.select(css)
    else:
        soup = build_soup(url)
        elements = soup.find_all(sourcetype)

    download_from_elements(elements)


def download_from_elements(elements):
    for e in elements:
        src = e.get("src")
        if src:
            c_src = complete(src)

            if sourcetype == 'img' and end_with_pic_suffix(src):
                response = requests.get(c_src)
                delete_flag = False

                pic_filename = save_path + "/" + generate_random_string(16)+ "." + get_suffix(src)
                print("%s %s" %(c_src, pic_filename))
                with open(pic_filename, "wb") as file:
                    file.write(response.content)
                with Image.open(pic_filename) as img:
                    width, height = img.size
                    #print("width: %s height:%s " % (width,height))
                    if width < img_width_threshold or height < img_height_threshold:
                        delete_flag = True
                if delete_flag:
                    os.remove(pic_filename)

            if sourcetype == 'video':
               cmd = "y " + c_src
               os.system(cmd)
               print('downloaded successfully! src: %s' % src)


def download_bibi(url, sourcetype):
    if sourcetype == 'video':
        cmd = "you-get " + url
        os.system(cmd)

def generate_urls(url, generate):
    urls = []
    if not generate:
        return [url]

    start = int(generate.split("-")[0])
    end = int(generate.split("-")[1])
    urls = [ url + "&page=" + str(i) + "&o=" + str((i-1)*30) for i in range(start,end+1)]
    urls.append(url)
    return urls

if __name__ == "__main__":

    (url, file, generate, clsname, css, attr, keyword, sourcetype) = parseArgs()

    filter_func = None
    if keyword:
        filter_func = lambda x : keyword in x

    if url:
        urls = generate_urls(url, generate)
        print("urls: %s" % urls)

        for url in urls:
            links = getlinks_by_url(url, clsname, css, attr, filter_func)
            download_from_links(url, links)


    if file:
        links = getlinks_by_file(file, clsname, css, attr, filter_func)
        download_from_links(file, ["https://detail.tmall.com/item.htm?spm=a1z10.5-b-s.w4011-16302054121.299.7d7763920w6zID&id=696932124488&rn=66a08459a64a9ad1e6763dabbcb87d6b&abbucket=3"])





