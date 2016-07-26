#!/usr/bin/env python

import logging
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
from myloghandlers import NatureTimedRotatingFileHandler
from commfunc import printerr

DEFAULT_PATH = './server.log'
LOGFORMATTER={'simple':'[%(asctime)s %(module)s] %(levelname)s %(message)s'}
LEVELS={'noset':logging.NOTSET, 'debug':logging.DEBUG, 'info':logging.INFO, 'warning':logging.WARNING,\
        'error':logging.ERROR, 'critical':logging.CRITICAL}

class CBaseHandlerConfig(object):
    def __init__(self, level = 'debug', formatter = 'simple'):
        self._level = LEVELS[level]
        self._formatter = LOGFORMATTER[formatter]
    
    def _checkConfig(self):
        if not self._level in LEVELS.values():
            printerr("level %s illegal"%self._level)
            return False
            
        if not self._formatter in LOGFORMATTER.values():
            printerr("log formatter:%s not support"%self._formatter)
            return False
        
        return True
    
    def __str__(self):
        return "level:%s, formatter:%s"%(self._level, self._formatter)
    
    def InitHandler(self):
        if not self._checkConfig():
            return None
        #pdb.set_trace() 
        handler = self._initHandler()
        if None == handler:
            return None
        handler.setLevel(self._level)
        handler.setFormatter(logging.Formatter(self._formatter))
        return handler
        
    def InitALog(self):
        if not self.checkConfig(self):
            return None
        
        logger = self._initLogger(self, self._module)
        if None == logger:
            return None
        
        handler = self._initHandler(self)
        if None == handler:
            return None
        
        logger.addHandler(handler)
        return logger
    
    
class CFileRotatHandlerConfig(CBaseHandlerConfig):
    def __init__(self, level = 'debug', formatter = 'simple',\
                 filename = DEFAULT_PATH, mode = 'a', encoding = None, delay = 0, backupCount = 0):
        super(CFileRotatHandlerConfig, self).__init__(level, formatter)
        self._filename = filename
        self._mode = mode
        self._encoding = encoding
        self._delay = delay
        self._backupcount = backupCount 
        
    def _checkConfig(self):
        if not super(CFileRotatHandlerConfig, self)._checkConfig():
            return False
        if len(self._filename) == 0:
            printerr("file name empty")
            return False
        return True
        
    def __str__(self):
        return "%s, filename:%s, mode:%s, encoding:%s, delay:%d, backupcount:%d"%(super(CFileRotatHandlerConfig, self).__str__(),\
        self._filename, self._mode, self._encoding, self._delay, self._backupcount)
    
class CRotatingFileHandlerConfig(CFileRotatHandlerConfig):
    def __init__(self, level = 'debug', formatter = 'simple',\
                 filename = DEFAULT_PATH, maxBytes = 4 * 1024 * 1024 * 1024, mode = 'a', encoding = None, delay = 0, backupCount = 0):
        super(CRotatingFileHandlerConfig, self).__init__(level, formatter, filename, mode, encoding, delay, backupCount)
        self._maxbytes = maxBytes
        
    def _checkConfig(self):
        if not super(CRotatingFileHandlerConfig, self)._checkConfig():
            return False
        if self._maxbytes <= 0:
            printerr("maxbytes should above zero")
            return False
        return True
        
    def __str__(self):
        return "%s, maxbytes:%d"%(super(CRotatingFileHandlerConfig, self).__str__(), self._maxbytes)
        
    def _initHandler(self):
        handler = RotatingFileHandler(filename = self._filename, mode = self._mode, maxBytes = self._maxbytes,\
                                      backupCount = self._backupcount, encoding = self._encoding,\
                                      delay = self._delay)
        return handler
        
class CTimedRotatingFileHandlerConfig(CFileRotatHandlerConfig):
    def __init__(self, level = 'debug', formatter = 'simple',\
                 filename = DEFAULT_PATH, when='h', interval=1, \
                 mode = 'a', backupCount = 10000, encoding = None, delay = False, utc = False):
        super(CTimedRotatingFileHandlerConfig, self).__init__(level, formatter, filename, mode, encoding, delay, backupCount)
        self._when = when
        self._interval = interval

    def _checkConfig(self):
        if not super(CTimedRotatingFileHandlerConfig, self)._checkConfig():
            return False
        if not self._when.upper() in set(['S', 'M', 'H', 'D', 'MIDNIGHT']):
            printerr("invalid rotat log param %s"%self._when)
            return False
        return True 

        if self._interval <= 0:
            printerr("invalid rotat inter val"%self._interval)
            return False

    def __str__(self):
        return "%s, when:%s, interval:%d"%(super(CTimedRotatingFileHandlerConfig, self).__str__(), self._when, self._interval)
    
    def _initHandler(self):
        handler = TimedRotatingFileHandler(filename = self._filename, when = self._when, interval = self._interval,\
                                           backupCount = self._backupcount, encoding = self._encoding, delay = self._delay)
        return handler
    
class CNatureTimedRotatingFileHandlerConfig(CTimedRotatingFileHandlerConfig):
    def __init__(self, level = 'debug', formatter = 'simple',\
                 filename = DEFAULT_PATH, when='h', interval=1, \
                 mode = 'a', backupCount = 10000, encoding = None, delay = False, utc = False):
        
        super(CNatureTimedRotatingFileHandlerConfig, self).__init__(level, formatter, filename, when, interval, mode, backupCount,\
                                                                    encoding, delay, utc)
        
    def _checkConfig(self):
        if not super(CNatureTimedRotatingFileHandlerConfig, self)._checkConfig():
            return False
        if not self._when.upper() in set(['S', 'M', 'H', 'D', 'MIDNIGHT']):
            printerr("invalid rotat log param %s"%self._when)
            return False
        return True

    def _initHandler(self):
        handler = NatureTimedRotatingFileHandler(filename = self._filename, when = self._when, interval = self._interval,\
                                                 backupCount = self._backupcount, encoding = self._encoding, \
                                                 delay = self._delay)
        return handler
    

def initLog(logmodule="sys", loglevel = "debug", handlerConfigs = []):
    #pdb.set_trace()
    logger = logging.getLogger(logmodule)
    logger.setLevel(LEVELS[loglevel])
    
    for i in range(len(handlerConfigs)):
        handler = handlerConfigs[i].InitHandler()
        if None != handler:
            logger.addHandler(handler)
        
    return logger
    
