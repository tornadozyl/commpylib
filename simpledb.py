#!/usr/bin/env python
# coding:utf-8
import MySQLdb
from basicresult import CBasicResult

import time


# this is a db config object, use the checkConfig function can
# make sure if the necessary config is completed and valid
class SimpleDBConfig(object):
    '''this class is used for control db config and check them'''

    def __init__(self, host='', port=3306, user='root', passwd='', connect_timeout=5, dbname='', tbname=''):
        self._host = host
        self._port = port
        self._user = user
        self._passwd = passwd
        self._connect_timeout = connect_timeout
        self._dbname = dbname
        self._tbname = tbname

    def __str__(self):
        return "host:%s, port:%d, user:%s, passwd:%s, connect_timeout:%d, dbname:%s, tbname:%s" % (self._host,
                                                                                                   self._port,
                                                                                                   self._user,
                                                                                                   self._passwd,
                                                                                                   self._connect_timeout,
                                                                                                   self._dbname,
                                                                                                   self._tbname)

    def checkConfig(self):
        if self._host == '' or self._port <= 0 or self._user == '' or self._connect_timeout <= 0:
            return CBasicResult(-1, "config not valid [%s]" % self.__str__())

        return CBasicResult()


class SimpleDBRst(CBasicResult):
    '''this claas contain the result of db execution'''

    def __init__(self):
        super(SimpleDBRst, self).__init__()


class SimpleDB(object):
    '''class of db object, the object is assembled with db config and base function'''

    def __init__(self, config):
        self._config = config
        self._useable = False

    def initDB(self):
        '''connect db and create cursor obj'''
        if not isinstance(self._config, SimpleDBConfig):
            return CBasicResult(-1, "config is not instance of SimpleDBConfig buf %s" % type(self._config))

        checkrst = self._config.checkConfig()
        if checkrst._resultcode != 0:
            return checkrst

        try:
            self._connect = MySQLdb.connect(host=self._config._host, port=self._config._port,
                                            user=self._config._user, passwd=self._config._passwd,
                                            connect_timeout=self._config._connect_timeout)

            self._connect.autocommit(True)

            if self._config._dbname != '':
                self._connect.select_db(self._config._dbname)

            # use dictCursor way to get result
            self._cursor = self._connect.cursor(MySQLdb.cursors.DictCursor)

            self._useable = True
            return CBasicResult()

        except MySQLdb.Error, e:
            self._useable = False
            return CBasicResult(-1, "SimpleDB init failed", -1, e)

    def reInitDB(self):
        '''some time the connection is flash crash, so we need to rebuild connection,
        this function first close old connect then build a new one'''
        try:
            if self._useable:
                self._cursor.close()
                self._connect.close()

            return self.initDB()

        except MySQLdb.Error, e:
            return CBasicResult(-1, "SimpleDB reInitDB failed", -1, e)

    def execute(self, sql, again=False):
        try:
            sdbrst = SimpleDBRst()
            sdbrst._affect_rows = self._cursor.execute(sql)
            sdbrst._rst = self._cursor.fetchall()
            return sdbrst
        except MySQLdb.Error, e:
            if not again and ((not self._useable) or 2013 == e.args[0] or 2006 == e.args[0]):
                rst = self.reInitDB()
                if 0 != rst._resultcode:
                    # need to know the affect sql, so shadow the inner error
                    return CBasicResult(-1, "SimpleDB execute failed [%s]" % sql, rst._errorcode, rst._errorinfo)
                else:
                    return self.execute(sql, True)
            else:
                return CBasicResult(-1, "SimpleDB execute failed [%s]" % sql, -1, e)

    def Commit(self):
        self._connect.commit()

    def setAutoCommit(self):
        self._connect.autocommit(True)

    def resetAutoCommit(self):
        self._connect.autocommit(False)

    def __del__(self):
        try:
            if hasattr(self, '_cursor'):
                self._cursor.close()
            if hasattr(self, '_connect'):
                self._connect.close()
        except MySQLdb.Error, e:
            print CBasicResult(-1, "SimpleDB __del__ failed %s" % e)


# ----use demo----
def testSelect():
    # 1 create db config obj and add db config to it
    dbconfig = SimpleDBConfig(host='172.27.198.178', port=3306, user='root', dbname='scsa_center')
    print dbconfig

    # 2 create db obj and add db config obj to it
    sdb = SimpleDB(dbconfig)

    # 3 init db obj
    rst = sdb.initDB()
    # you need to check if db connection is successfully init
    if 0 != rst._resultcode:
        print rst
        return

    # 4 use db obj to use db
    while (1):
        time.sleep(1)
        value = sdb.execute('''select FAccttype, FRoutePolicy, FLoadCondition,\
                FLoadDescription, FTimeStamp from %s''' % 't_route_policy')

        if 0 != value._resultcode:
            print value
            continue
            # 5 get result by field name , e.g line['FAccttype'], FAccttype is a field name
        for line in value._rst:
            print "%d\t%s\t%s" % (value._affect_rows, line['FAccttype'], line['FRoutePolicy'])


def testInsert():
    dbconfig = SimpleDBConfig(host='172.27.198.178', port=3306, user='root', dbname='scsa_center')
    sdb = SimpleDB(dbconfig)
    rst = sdb.initDB()
    if 0 != rst._resultcode:
        print rst
        return

    sql = r'''insert into scsa_center.t_svr_config(FSetName) values('hello')'''

    ans = sdb.execute(sql)
    if 0 != ans._resultcode:
        print ans
        return

    print "affect rows %d" % ans._affect_rows


def testUpdate():
    dbconfig = SimpleDBConfig(host='172.27.198.178', port=3306, user='root', dbname='scsa_center')
    sdb = SimpleDB(dbconfig)
    rst = sdb.initDB()
    if 0 != rst._resultcode:
        print rst
        return

    sql = r'''update scsa_center.t_svr_config set FHost="1.1.1.1" where FSetName="hello"'''
    ans = sdb.execute(sql)
    if 0 != ans._resultcode:
        print ans
        return

    print "affect rows %d" % ans._affect_rows


def testDelete():
    dbconfig = SimpleDBConfig(host='172.27.198.178', port=3306, user='root', dbname='scsa_center')
    sdb = SimpleDB(dbconfig)
    rst = sdb.initDB()
    if 0 != rst._resultcode:
        print rst

    sql = r'''delete from scsa_center.t_svr_config where FSetName="hello"'''
    ans = sdb.execute(sql)
    if 0 != ans._resultcode:
        print ans
        return

    print "affect rows %d" % ans._affect_rows


# ----use demo end----

if '__main__' == __name__:
    testSelect()
