import requests
from bs4 import BeautifulSoup
from common import catchExc

import time

delayForHttpReq = 0.5 # 500ms

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
    picname = picsrc.rsplit('/',1)[1]
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
