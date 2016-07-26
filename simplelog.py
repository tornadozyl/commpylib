#!/usr/bin/env python

import logging
from logging.handlers import RotatingFileHandler
from commfunc import printerr

DEFAULT_PATH='./server.log'
LOGFORMATTER={'simple':'[%(asctime)s %(module)s] %(levelname)s %(message)s'}
LEVELS={'noset':logging.NOTSET, 
    'debug':logging.DEBUG, 
    'info':logging.INFO, 
    'warning':logging.WARNING,
    'error':logging.ERROR, 
    'critical':logging.CRITICAL}

_handlerTYPE=set(['file', 'stream'])


class CLogConfig(object):
    def __init__(self, level='debug', formatter='simple', path=DEFAULT_PATH, handler='file'):
        self._level = LEVELS[level]
        self._formatter = LOGFORMATTER[formatter] 
        self._path  = path 
        self._handler = handler
                
    def __del__(self):
        pass

    def checkConfig(self):
        if self._level not in LEVELS.values()\
             or self._formatter not in LOGFORMATTER.values() \
             or self._handler not in _handlerTYPE:
            return False
        return True


def initLog(config, logmodule="sys"):
    "init a log for use"
    if not isinstance(config, CLogConfig):
        printerr("InitLog Invalid parameter, need parameter CLogConfig buf now %s"%type(config))
        return None

    if not config.checkConfig():
        printerr("config.checkConfig() failed") 
        return None

    logger = logging.getLogger(logmodule)
    logger.setLevel(config._level)

    handler = RotatingFileHandler(config._path, maxBytes=4 * 1024 * 1024 * 1024, backupCount=100)
    if 'file' != config._handler:
        handler = logging.StreamHandler()

    handler.setLevel(logging.DEBUG)
    handler.setFormatter(logging.Formatter(config._formatter))

    logger.addHandler(handler)    

    return logger



#--------------------------------------------------- use demo -----------------------------------
def testLog():
    config1 = CLogConfig()
    logger = initLog(config1)
    if None == logger:
        return

    logger.debug("hello %s"%("world"))

def testLog2():
    logger = logging.getLogger("sys")
    logger.debug("hello in testLog2")

#-----------------------------------------------use demo end ------------------------------------

if '__main__' == __name__: 
    testLog()
    testLog2()
