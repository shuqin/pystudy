import requests
import time
from bs4 import BeautifulSoup
from common.common import catchExc
from common.multitasks import IoTaskThreadPool
from selenium import webdriver

delayForHttpReq = 0.5 # 500ms

grapHtmlPool = IoTaskThreadPool(20)

asynLoading = 1  # 当网页内容是动态生成时，异步加载网页
targetIdWhenAsyncLoading = 'page-fav' # 异步加载网页时，根据 ID 获取内容（因此此时会加载到很多噪音内容） 

def getHTMLContent(url):
    if asynLoading == 1:
        htmlContent = getHTMLContentFromLoadedUrl(url)

        if htmlContent is not None and htmlContent != '':
            html = '<html><head></head><body>' + htmlContent + '</body></html>'
            return html

    return getHTMLContentFromUrl(url)

def getHTMLContentFromLoadedUrl(url):
    '''
       get html content from dynamic loaed html url
    '''
    driver = webdriver.PhantomJS()
    driver.get(url)
    time.sleep(10)

    try:
        elem = driver.find_element_by_id(targetIdWhenAsyncLoading)
    except:
        elem = driver.find_element_by_xpath('/html/body')

    return elem.get_attribute('innerHTML')       

def getHTMLContentFromUrl(url):
    '''
       get html content from html url
    '''
    r = requests.get(url)
    status = r.status_code
    if status != 200:
        return ''
    return r.text

def batchGrapHtmlContents(urls):
    '''
       batch get the html contents of urls
    '''
    global grapHtmlPool
    return grapHtmlPool.exec(getHTMLContent, urls)

@catchExc
def getSoup(url):
    '''
       get the html content of url and transform into soup object
           in order to parse what i want later
    '''
    time.sleep(delayForHttpReq)
    result = requests.get(url)
    status = result.status_code
    # print 'url: %s , status: %s' % (url, status)
    if status != 200:
        return None
    resp = result.text
    soup = BeautifulSoup(resp, "lxml")
    return soup

@catchExc
def batchGetSoups(pool, urls):
    '''
       get the html content of url and transform into soup object
           in order to parse what i want later
    '''

    urlnum = len(urls)
    if urlnum == 0:
        return []

    return pool.map(getSoup, urls)


@catchExc
def download(piclink, saveDir):
    '''
       download pic from pic href such as
            http://img.pconline.com.cn/images/upload/upc/tx/photoblog/1610/21/c9/28691979_1477032141707.jpg
    '''

    picsrc = piclink.attrs['src']
    picname = picsrc.rsplit('/', 1)[1]
    saveFile = saveDir + '/' + picname

    picr = requests.get(piclink.attrs['src'], stream=True)
    with open(saveFile, 'wb') as f:
        for chunk in picr.iter_content(chunk_size=1024):
            if chunk:
                f.write(chunk)
                f.flush()
    f.close()


@catchExc
def downloadForSinleParam(paramTuple):
    download(paramTuple[0], paramTuple[1])
