import requests
import time
from bs4 import BeautifulSoup
from common.common import catchExc
from common.multitasks import IoTaskThreadPool
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

delayForHttpReq = 0.5 # 500ms

class HTMLGrasper(object):

    def __init__(self, conf):
        '''
        抓取 HTML 网页内容时的配置项
          _async: 是否异步加载网页。 _async = 1 当网页内容是动态生成时，异步加载网页; 
          targetIdWhenAsync: 当 _async = 1 指定。
             由于此时会加载到很多噪音内容，需要指定 ID 来精确获取所需的内容部分
          sleepWhenAsync:  当 _async = 1 指定。
             异步加载网页时需要等待的秒数  
        '''
        self._async = conf.get('async', 0)
        self.targetIdWhenAsync = conf.get('targetIdWhenAsync', '')
        self.sleepWhenAsync = conf.get('sleepWhenAsync', 10)

    def batchGrapHtmlContents(self, urls):
        '''
           batch get the html contents of urls
        '''
        grapHtmlPool = IoTaskThreadPool(20)
        return grapHtmlPool.exec(self.getHTMLContent, urls)

    def getHTMLContent(self, url):
        if self._async == 1:
            htmlContent = self.getHTMLContentAsync(url)

            if htmlContent is not None and htmlContent != '':
                html = '<html><head></head><body>' + htmlContent + '</body></html>'
                return html

        return self.getHTMLContentFromUrl(url)

    def getHTMLContentAsync(self, url):
        '''
           get html content from dynamic loaed html url
        '''

        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--disable-gpu')
        driver = webdriver.Chrome(chrome_options=chrome_options)
        driver.get(url)
        time.sleep(self.sleepWhenAsync)

        try:
            elem = driver.find_element_by_id(self.targetIdWhenAsync)
        except:
            elem = driver.find_element(By.XPATH, '/html/body')

        return elem.get_attribute('innerHTML')       

    def getHTMLContentFromUrl(self, url):
        '''
           get html content from html url
        '''
        r = requests.get(url)
        status = r.status_code
        if status != 200:
            return ''
        return r.text


'''
    # 利用property装饰器将获取name方法转换为获取对象的属性
    @property
    def async(self):
        return self._async

    # 利用property装饰器将设置name方法转换为获取对象的属性
    @async.setter
    def async(self,async):
        self._async = async 
'''       

@catchExc
def download(piclink, saveDir):
    '''
       #download pic from pic href such as
       #     http://img.pconline.com.cn/images/upload/upc/tx/photoblog/1610/21/c9/28691979_1477032141707.jpg
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

