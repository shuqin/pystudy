import requests
from bs4 import BeautifulSoup
from common import catchExc

@catchExc
def getSoup(url):
    '''
       get the html content of url and transform into soup object
           in order to parse what i want later
    '''
    result = requests.get(url)
    status = result.status_code
    if status != 200:
        return None
    resp = result.text
    soup = BeautifulSoup(resp, "lxml")
    return soup

@catchExc
def batchGetSoups(urls):
    '''
       get the html content of url and transform into soup object
           in order to parse what i want later
    '''

    urlnum = len(urls)
    if urlnum == 0:
        return []

    return getUrlPool.map(getSoup, urls)


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
