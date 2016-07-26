#!/usr/bin/env python
import sys
import os
import copy
import ConfigParser
import simplelog
import simplelogex
import simpledb
import datetime
from basicresult import CBasicResult

#import pdb

INSTANCE_TEMP = {'config':None, 'IsInited':False, 'obj':None}

class GlobalIns(object):
    '''init one config, one sdb, one log'''
    __config_fullpath = "../conf/conf.ini"
    __cfg = copy.deepcopy(INSTANCE_TEMP)
    __sdb = {}
    __log = {}
    __logex = {}
    def __init__(self):
        pass
    
    @staticmethod
    def setConfigPath(config_fullpath):
        try:
            if os.path.exists(config_fullpath):
                GlobalIns.__config_fullpath = config_fullpath
                return CBasicResult()
            else:
                errinfo="%s not exists"%GlobalIns.__config_fullpath
                return CBasicResult(-1, errinfo, -1, errinfo)
            
        except Exception, e:
            return CBasicResult(-1, "setConfigPath failed", -1, e)
        
    @staticmethod
    def getCfgInstance(needreparse = False):
        try:
            if GlobalIns.__cfg['IsInited'] and not needreparse:
                return CBasicResult(), GlobalIns.__cfg['obj']
        
            if not os.path.exists(GlobalIns.__config_fullpath):
                errinfo = "%s not exists"%GlobalIns.__config_fullpath
                return CBasicResult(-1, errinfo, -1, errinfo), None
        
        
            GlobalIns.__cfg['obj'] = ConfigParser.ConfigParser()
            l = GlobalIns.__cfg['obj'].read(GlobalIns.__config_fullpath)
            if len(l) == 0:
                return CBasicResult(-1, 'read config [%s] failed'%GlobalIns.__config_fullpath,\
                                    -1, 'read config [%s] failed'%GlobalIns.__config_fullpath), None
                                    
            return CBasicResult(), GlobalIns.__cfg['obj']
        
        except ConfigParser.Error, e:
            return CBasicResult(-1, "getCfgInstance failed", -1, e), None
        except Exception, e:
            return CBasicResult(-1, "getCfgInstance failed", -1, e), None
        
    @staticmethod
    def getLogInstance(name):
        try:
            if GlobalIns.__log.has_key(name) and GlobalIns.__log[name]['IsInited']:
                return CBasicResult(), GlobalIns.__log[name]['obj']
            
            rst, cfg = GlobalIns.getCfgInstance()
            if 0 != rst._resultcode or None == cfg:
                errinfo = "getLogInstance: getCfgInstance failed"
                return CBasicResult(-1, errinfo, -1, rst), None
            
            if not GlobalIns.__log.has_key(name):
                GlobalIns.__log[name] = copy.deepcopy(INSTANCE_TEMP)
            
            loglevel = cfg.get(name, 'level')
            logpath = "%s.%s.log"%(cfg.get(name, 'logname'), datetime.datetime.today().strftime("%Y%m%d"))
            logconfig = simplelog.CLogConfig(level = loglevel, path = logpath)
            GlobalIns.__log[name]['obj'] = simplelog.initLog(logconfig, name)
            if GlobalIns.__log[name]['obj'] == None:
                errinfo = "getLogInstance create log with [%s] failed"%name
                return CBasicResult(-1, errinfo, -1, errinfo), None
            else:
                GlobalIns.__log[name]['IsInited'] = True
            
            return CBasicResult(), GlobalIns.__log[name]['obj']
        
        except ConfigParser.Error, e:
            return CBasicResult(-1, "getLogInstance failed", -1, e), None
        except Exception, e:
            return CBasicResult(-1, "getLogInstance failed", -1, e), None
        
    @staticmethod
    def _initSizeRotatedHandlerConfig(cfg, sectionname, logconfig):             
        if cfg.has_option(sectionname, 'rotatesize'):
            logconfig['rotatesize'] = cfg.getint(sectionname, 'rotatesize') * 1024 * 1024
        else:
            logconfig['rotatesize'] = 4 * 1024 * 1024 * 1024
            
        if cfg.has_option(sectionname, 'openmode'):
            logconfig['openmode'] = cfg.get(sectionname, 'openmode')
        else:
            logconfig['openmode'] = 'a'
            
        if cfg.has_option(sectionname, 'encoding'):
            #logconfig['encoding'] = cfg.get(sectionname, 'encoding')
            logconfig['encoding'] = None
        else:
            logconfig['encoding'] = None
            
        if cfg.has_option(sectionname, 'backupcount'):
            logconfig['backupcount'] = cfg.getint(sectionname, 'backupcount')
        else:
            logconfig['backupcount'] = 10000
        
        handlerconfig = simplelogex.CRotatingFileHandlerConfig(level = logconfig['loglevel'], formatter = logconfig['formatter'],\
filename = "%s.log.%s"%(logconfig['logpath'], datetime.datetime.today().strftime("%Y-%m-%d")), \
maxBytes = logconfig['rotatesize'], mode = logconfig['openmode'], \
                        encoding = logconfig['encoding'], backupCount = logconfig['backupcount'])
        
        return CBasicResult(), handlerconfig
        
    @staticmethod
    def _initNatureTimeRotateLog(cfg, sectionname, logconfig):
        #handlerconfig = []
        
        when_map = {'day':'D', 'hour':'H', 'minute':'M', 'second':'S'}
        
        if cfg.has_option(sectionname, 'when'):
            when = cfg.get(sectionname, 'when')
            if when not in when_map.keys():
                logconfig['when'] = when_map['day']
            else:
                logconfig['when'] = when_map[when]
        else:
            logconfig['when'] = when_map['day']
            
        if cfg.has_option(sectionname, 'interval'):
            logconfig['interval'] = cfg.getint(sectionname, 'interval')
        else:
            logconfig['interval'] = 1
            
        if cfg.has_option(sectionname, 'openmode'):
            logconfig['openmode'] = cfg.get(sectionname, 'openmode')
        else:
            logconfig['openmode'] = 'a'
            
        if cfg.has_option(sectionname, 'encoding'):
            #logconfig['encoding'] = cfg.get(sectionname, 'encoding')
            logconfig['encoding'] = None
        else:
            logconfig['encoding'] = None
            
        if cfg.has_option(sectionname, 'backupcount'):
            logconfig['backupcount'] = cfg.getint(sectionname, 'backupcount')
        else:
            logconfig['backupcount'] = 10000
            
        handlerconfig = simplelogex.CNatureTimedRotatingFileHandlerConfig(level = logconfig['loglevel'], \
formatter = logconfig['formatter'], filename = logconfig['logpath'], when = logconfig['when'], interval = logconfig['interval'],\
mode = logconfig['openmode'], backupCount = logconfig['backupcount'], encoding=logconfig['encoding'])	
        
        return CBasicResult(), handlerconfig
    
    @staticmethod
    def getLogExInstance(name):
        try:
            if GlobalIns.__logex.has_key(name) and GlobalIns.__logex[name]['IsInited']:
                return CBasicResult(), GlobalIns.__logex[name]['obj']
            
            rst, cfg = GlobalIns.getCfgInstance()
            if 0 != rst._resultcode or None == cfg:
                return CBasicResult(-1, "getCfgInstance failed", -1, rst), None

            if not GlobalIns.__logex.has_key(name):
                GlobalIns.__logex[name] = copy.deepcopy(INSTANCE_TEMP)


            logconfig = {}
            logconfig['loglevel'] = cfg.get(name, 'level')
            logconfig['logpath'] = cfg.get(name, 'logname')
            logconfig['logtype'] = cfg.get(name, 'logtype')
            
            if cfg.has_option(name, 'formatter'):
                logconfig['formatter'] = cfg.get(name, 'formatter')
            else:
                logconfig['formatter'] = 'simple'
            
            handlerconfig_array = []
            
            if logconfig['logtype'].lower() == 'size':
                rst, handlerconfig = GlobalIns._initSizeRotatedHandlerConfig(cfg, name, logconfig)
                if 0 != rst._resultcode:
                    return rst, None
                
                print handlerconfig
                handlerconfig_array.append(handlerconfig)
            elif logconfig['logtype'].lower() == 'naturetime':
                rst, handlerconfig = GlobalIns._initNatureTimeRotateLog(cfg, name, logconfig)
                if 0 != rst._resultcode:
                    return rst, None
                
                print handlerconfig 
                handlerconfig_array.append(handlerconfig)
            else:
                return CBasicResult(-1, "logtype %s invalid"%logconfig['logtype'], \
                                    -1, "logtype %s invalid"%logconfig['logtype']), None

            GlobalIns.__logex[name]['obj'] = simplelogex.initLog(logmodule = name, \
                                                                 loglevel = logconfig['loglevel'], \
                                                                 handlerConfigs = handlerconfig_array)
            GlobalIns.__logex[name]['IsInited'] = True
            return CBasicResult(), GlobalIns.__logex[name]['obj']
            
        except Exception, e:
            return CBasicResult(-1, "getLogExInstance failed", -1 ,e), None
    @staticmethod
    def getSDBInstance(name):
        try:
            if GlobalIns.__sdb.has_key(name) and GlobalIns.__sdb[name]['IsInited']:
                return GlobalIns.__sdb[name]['obj']
            
            rst, cfg = GlobalIns.getCfgInstance()
            if 0 != rst._resultcode or  None == cfg:
                return CBasicResult(-1, "getSDBInstance failed", -1, "getCfgInstance None"), None
            
            if not GlobalIns.__sdb.has_key(name):
                GlobalIns.__sdb[name] = copy.deepcopy(INSTANCE_TEMP)
            db_host = cfg.get(name, 'ip')
            db_port = int(cfg.get(name, 'port'))
            db_user = cfg.get(name, 'user')
            db_passwd = cfg.get(name, 'passwd')
            db_timeout =  5
            if cfg.has_option(name, 'timeout'):
                db_timeout = int(cfg.get(name, 'timeout'))
            db_dbname = ''
            if cfg.has_option(name, 'dbname'):
                db_dbname = cfg.get(name, 'dbname')
                
            db_tbname = ''
            if cfg.has_option(name, 'tablename'):
                db_tbname = cfg.get(name, 'tablename')
            
            sdbconfig = simpledb.SimpleDBConfig(db_host, db_port, db_user, db_passwd, db_timeout, db_dbname, db_tbname)
            GlobalIns.__sdb[name]['obj'] = simpledb.SimpleDB(sdbconfig)
            
            rst = GlobalIns.__sdb[name]['obj'].initDB()
            if 0 != rst._resultcode:
                return CBasicResult(-1, "getSDBInstance failed", -1, rst), None
            
            GlobalIns.__sdb[name]['IsInited'] = True
            return CBasicResult(), GlobalIns.__sdb[name]['obj']
        except ConfigParser.Error, e:
            return CBasicResult(-1, "getSDBInstance failed", -1, e), None
        except Exception, e:
            return CBasicResult(-1, "getSDBInstance failed", -1, e), None
        
        
#demo below------------------------------------------------------------------------------------------------------------------------
def GlobalIns_Demo():
    rst =  GlobalIns.setConfigPath('./globalins_demo_config.ini')
    if 0 != rst._resultcode:
        print rst
        sys.exit(-1)
        
    rst ,cfg = GlobalIns.getCfgInstance()
    if 0 != rst._resultcode or None == cfg:
        print rst
        sys.exit(-1)
    
    #the getlogInstance param should be the same with globalins_demo_config.ini section
    rst ,log_demo1 = GlobalIns.getLogExInstance('log_demo1')
    if 0 != rst._resultcode or None == log_demo1:
        print rst
        sys.exit(-1)
        
    rst, log_demo2 = GlobalIns.getLogExInstance('log_demo2')
    if 0 != rst._resultcode or None == log_demo2:
        print rst
        sys.exit(-1)
    
    #the getSDBInstance param should be the same with globalins_demo_config.ini section
    rst, db_demo1 = GlobalIns.getSDBInstance('db_demo1')
    if 0 != rst._resultcode or None == db_demo1:
        print rst
        sys.exit(-1)
        
    rst, db_demo2 = GlobalIns.getSDBInstance('db_demo2')
    if 0 != rst._resultcode or None == db_demo2:
        print rst
        sys.exit(-1)
    
if '__main__' == __name__:
    GlobalIns_Demo()
