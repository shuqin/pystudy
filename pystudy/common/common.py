import os

def createDir(dirName):
    if not os.path.exists(dirName):
        os.makedirs(dirName)

def catchExc(func):
    def _deco(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            print ("error catch exception for %s (%s, %s): %s" % (func.__name__, str(*args), str(**kwargs), e))
            return None
    return _deco

