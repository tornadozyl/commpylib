#!/usr/bin/env python
# coding:utf-8
import sys
import os
import copy
import ConfigParser
import simplelog
import simpledb
import datetime
from basicresult import CBasicResult


def printerr(errstr):
    print>> sys.stderr, errstr


INSTANCE_TEMP = {'config': None, 'IsInited': False, 'obj': None}


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
                return 0
            else:
                printerr("%s not exists" % GlobalIns.__config_fullpath)
                return -1
        except Exception, e:
            printerr(e)
            return -1

    @staticmethod
    def getCfgInstance():
        try:
            if GlobalIns.__cfg['IsInited']:
                return GlobalIns.__cfg['obj']

            if not os.path.exists(GlobalIns.__config_fullpath):
                printerr("%s not exists" % GlobalIns.__config_fullpath)
                return None

            GlobalIns.__cfg['obj'] = ConfigParser.ConfigParser()
            GlobalIns.__cfg['obj'].read(GlobalIns.__config_fullpath)
            return GlobalIns.__cfg['obj']
        except Exception, e:
            printerr(e)
            return None

    @staticmethod
    def getLogInstance(name):
        try:
            if GlobalIns.__log.has_key(name) and GlobalIns.__log[name]['IsInited']:
                return GlobalIns.__log[name]['obj']

            cfg = GlobalIns.getCfgInstance()
            if None == cfg:
                printerr("getLogInstance: getCfgInstance failed")
                return None

            if not GlobalIns.__log.has_key(name):
                GlobalIns.__log[name] = copy.deepcopy(INSTANCE_TEMP)

            loglevel = cfg.get(name, 'level')
            logpath = "%s.%s.log" % (cfg.get(name, 'logname'), datetime.datetime.today().strftime("%Y%m%d"))
            logconfig = simplelog.CLogConfig(level=loglevel, path=logpath)
            GlobalIns.__log[name]['obj'] = simplelog.initLog(logconfig, name)
            if GlobalIns.__log[name]['obj'] == None:
                printerr("getLogInstance create log with [%s] failed" % name)
            else:
                GlobalIns.__log[name]['IsInited'] = True

            return GlobalIns.__log[name]['obj']

        except Exception, e:
            printerr(e)
            return None

    @staticmethod
    def getLogExInstance(name):
        try:
            if GlobalIns.__logex.has_key(name) and GlobalIns.__logex[name]['IsInited']:
                return CBasicResult(), GlobalIns.__logex[name]['obj']

            cfg = GlobalIns.getCfgInstance()
            if None == cfg:
                return CBasicResult(-1, "getCfgInstance failed", -1, "getCfgInstance failed")


        except Exception, e:
            printerr(e)
            return CBasicResult(-1, "getLogExInstance failed", -1, e), None

    @staticmethod
    def getSDBInstance(name):
        try:
            if GlobalIns.__sdb.has_key(name) and GlobalIns.__sdb[name]['IsInited']:
                return GlobalIns.__sdb[name]['obj']

            cfg = GlobalIns.getCfgInstance()
            if None == cfg:
                printerr("getSDBInstance: getCfgInstance failed")
                return None

            if not GlobalIns.__sdb.has_key(name):
                GlobalIns.__sdb[name] = copy.deepcopy(INSTANCE_TEMP)
            db_host = cfg.get(name, 'ip')
            db_port = int(cfg.get(name, 'port'))
            db_user = cfg.get(name, 'user')
            db_passwd = cfg.get(name, 'passwd')
            db_timeout = 5
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
                printerr(rst)
                return None

            GlobalIns.__sdb[name]['IsInited'] = True
            return GlobalIns.__sdb[name]['obj']

        except Exception, e:
            printerr(e)
            return None


# demo below------------------------------------------------------------------------------------------------------------------------
def GlobalIns_Demo():
    if 0 != GlobalIns.setConfigPath('./globalins_demo_config.ini'):
        printerr("setConfigPath failed")
        sys.exit(-1)

    config = GlobalIns.getCfgInstance()
    if None == config:
        printerr("getCfgInstance failed")
        sys.exit(-1)

    # the getlogInstance param should be the same with globalins_demo_config.ini section
    log_demo1 = GlobalIns.getLogInstance('log_demo1')
    if None == log_demo1:
        sys.exit(-1)

    log_demo2 = GlobalIns.getLogInstance('log_demo2')
    if None == log_demo2:
        sys.exit(-1)

    # the getSDBInstance param should be the same with globalins_demo_config.ini section
    db_demo1 = GlobalIns.getSDBInstance('db_demo1')
    if None == db_demo1:
        sys.exit(-1)

    db_demo2 = GlobalIns.getSDBInstance('db_demo2')
    if None == db_demo2:
        sys.exit(-1)


if '__main__' == __name__:
    GlobalIns_Demo()
