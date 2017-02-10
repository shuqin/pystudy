#!/usr/bin/python3
#_*_encoding:utf-8_*_

import argparse
import traceback
import json
import time
import os
import random
import urllib.parse
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities


def usage():

    usage_info = '''
        This program is used to batch download pictures or videos from specified url.
        search and download pictures or videos from network url by specified rules.

        options:
              -k --keyword a keyword to specify which to search
              -g --generate generate more paged htmls based on url specified by url. eg.  url = https://search.bilibili.com/all?keyword=%E5%8F%A4%E5%85%B8%E8%88%9E&from_source=webtop_search&spm_id_from=333.1007&search_source=5 generate = 2-5 produces url list contains  https://search.bilibili.com/all?keyword=%E5%8F%A4%E5%85%B8%E8%88%9E&from_source=webtop_search&spm_id_from=333.1007&search_source=5&page=[2-5]

        eg.
            python3 bs.py -k '古典舞'
            python3 bs.py -k '何晴' -g 2-34

    '''

    print(usage_info)

def parseArgs():
    try:
        description = '''This program is used to batch download pictures or videos from specified urls.
                                will search and download pictures or videos from network url by specified rules.
                      '''
        parser = argparse.ArgumentParser(description=description)
        parser.add_argument('-k','--keyword', help='a keyword to specify which to search', required=True)
        parser.add_argument('-g','--generate', help='generate more paged htmls based on url specified by url', required=False)
        args = parser.parse_args()
        print(args)
        keyword = args.keyword
        generate = args.generate
        print("%s %s" % (keyword, generate))
        return  (keyword, generate)
    except:
        usage()
        traceback.print_exc()
        exit(1)


def generate_urls(url, generate):
    urls = []
    if not generate:
        return [url]

    start = int(generate.split("-")[0])
    end = int(generate.split("-")[1])
    urls = [ url + "&page=" + str(i) for i in range(start,end+1)]
    urls.append(url)
    return urls

def get_driver():

    # ChromeOptions 配置相关
    options = webdriver.ChromeOptions()
    options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')
    options.add_argument('--accept-language=zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7')
    options.add_argument('--ignore-certificate-errors')
    options.add_experimental_option('useAutomationExtension', False)
    options.add_experimental_option('excludeSwitches', ['enable-automation'])
    options.add_argument('--ignore-certificate-errors-spki-list')
    options.add_argument('--no-sandbox')
    options.add_argument('--headless')

    options.add_experimental_option('perfLoggingPrefs', {'enableNetwork': True})

    caps = DesiredCapabilities.CHROME
    caps['goog:loggingPrefs'] = {
         'browser': 'ALL',
         'driver': 'ALL',
         'performance': 'ALL'
    }

    headers = {

          'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36 Edg/116.0.0.0',
          'cookie': "innersign=0; buvid3=7D53C2F7-EA61-4A41-03E0-56AE18DA779B36333infoc; i-wanna-go-back=-1; b_ut=7; b_lsid=F478CE1C_188E0BFA7C4; _uuid=55EC7D21-81AD-B19F-ED25-7DC49B272D9B36750infoc; FEED_LIVE_VERSION=V8; header_theme_version=undefined; buvid_fp=db285454bd945781814b536ac93028f1; home_feed_column=4; buvid4=1383EBA3-8267-1CE5-3FC3-4085B84E5DAB37512-023062209-Gr0m3iB%2FfbeQ%2FgP6UQMOKg%3D%3D; b_nut=1687397837; browser_resolution=529-760; PVID=1"
    }


    driver = webdriver.Chrome(options=options, desired_capabilities=caps)

    driver.execute_cdp_cmd("Network.setExtraHTTPHeaders", {"headers" : headers})
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": """
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            })
        """
    })
    return driver

def encode(keyword):
    return urllib.parse.quote(keyword)

def get_all_urls(urls, driver):
    all_urls = []
    for url in urls:
        time.sleep(random.uniform(0.1, 0.5))
        all_urls.extend(get_url_response(url, driver))
    return all_urls

def get_url_response(url, driver):

    print("get_url_response %s" % url)

    driver.get(url)

    logs = driver.get_log("performance")

    for log in logs:
        logjson = json.loads(log["message"]).get("message")
        if logjson['method'] == 'Network.responseReceived':
            params = logjson['params']
            try:
                if 'api.bilibili.com/x/web-interface/wbi/search/type' in params['response']['url']:
                    requestId = params['requestId']
                    print(" requestId: %s" % requestId)

                    content = driver.execute_cdp_cmd('Network.getResponseBody', {'requestId': requestId})
                    response_body = content['body']
                    resp = json.loads(response_body)
                    #print(resp)
                    results = resp['data']['result']
                    bvlist = list(map(lambda r: 'https://www.bilibili.com/video/' + r['bvid'], results))
                    return bvlist

            except:
                print("没找到requestUrl")
                continue
        else:
            continue

    return []

def download_bibi(url):
    cmd = "y " + url
    os.system(cmd)

def download_all(urls):
    for url in urls:
        time.sleep(1 + random.uniform(0.1, 0.5))
        download_bibi(url)

if __name__ == "__main__":

    (keyword, generate) = parseArgs()

    base_url = "https://api.bilibili.com/x/web-interface/wbi/search/type?__refresh__=true&page_size=42&from_source=&from_spmid=333.337&platform=pc&highlight=1&single_column=0&qv_id=NCdP8YoL7figzkAn52lJqpQGPZFMgaKc&ad_resource=5654&source_tag=3&gaia_vtoken=&category_id=&search_type=video"

    if keyword :
        url = base_url + '&keyword=' + encode(keyword)

    if url:
        urls = generate_urls(url, generate)
        print("urls: %s" % urls)

    driver = get_driver()

    all_urls = get_all_urls(urls, driver)
    all_urls_undup = set(all_urls)
    print(all_urls_undup)
    print('total size: %s' % len(all_urls_undup))
    download_all(all_urls_undup)






