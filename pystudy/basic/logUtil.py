#-------------------------------------------------------------------------------
# Name:        logging
# Purpose:     common for logging
#
# Author:      Administrator
#
# Created:     30/09/2014
#-------------------------------------------------------------------------------

import logging

LOG_LEVELS = {
            'DEBUG': logging.DEBUG, 'INFO': logging.INFO,
            'WARN': logging.WARNING, 'ERROR': logging.ERROR,
	        'CRITICAL': logging.CRITICAL
}

def initlog(filename) :

    logger = logging.getLogger()
    hdlr = logging.FileHandler(filename)
    formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
    hdlr.setFormatter(formatter)
    logger.addHandler(hdlr)
    logger.setLevel(LOG_LEVELS['ERROR'])

    return logger

errlog = initlog("../log/error.log")
infolog = initlog("../log/info.log")

def fname():
    """docstring for fname"""
    pass

if  __name__ == '__main__' :

    errlog.info('this is an ordinary info')
    errlog.warn('this is a warning')
    errlog.error('this is an error that should be handled')
    errlog.critical('this is an severe error')

