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



