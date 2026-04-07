#!/usr/bin/env python
# coding:utf-8
"""简单数据库模块。

提供 MySQL 数据库的简单封装，支持自动重连。
"""

from typing import Any, Dict, List, Optional, Tuple
from basicresult import CBasicResult

# 尝试导入 pymysql，如果不存在则使用 MySQLdb
try:
    import pymysql

    MYSQL_LIB = "pymysql"
except ImportError:
    try:
        import MySQLdb

        MYSQL_LIB = "MySQLdb"
    except ImportError:
        MYSQL_LIB = None
        pymysql = None  # type: ignore
        MySQLdb = None  # type: ignore


import time


class SimpleDBConfig(object):
    """数据库配置类。

    Attributes:
        host: 数据库主机
        port: 数据库端口
        user: 用户名
        passwd: 密码
        connect_timeout: 连接超时时间
        dbname: 数据库名
        tbname: 表名
    """

    def __init__(
        self,
        host: str = "",
        port: int = 3306,
        user: str = "root",
        passwd: str = "",
        connect_timeout: int = 5,
        dbname: str = "",
        tbname: str = "",
    ):
        self._host = host
        self._port = port
        self._user = user
        self._passwd = passwd
        self._connect_timeout = connect_timeout
        self._dbname = dbname
        self._tbname = tbname

    def __str__(self) -> str:
        return (
            f"host={self._host}, port={self._port}, user={self._user}, "
            f"passwd={'*' * len(self._passwd) if self._passwd else ''}, "
            f"connect_timeout={self._connect_timeout}, dbname={self._dbname}, "
            f"tbname={self._tbname}"
        )

    def checkConfig(self) -> CBasicResult:
        """检查配置是否有效。

        Returns:
            CBasicResult 结果对象
        """
        if (
            not self._host
            or self._port <= 0
            or not self._user
            or self._connect_timeout <= 0
        ):
            return CBasicResult(-1, f"config not valid [{self}]")
        return CBasicResult()

    @property
    def host(self) -> str:
        return self._host

    @property
    def port(self) -> int:
        return self._port

    @property
    def user(self) -> str:
        return self._user

    @property
    def passwd(self) -> str:
        return self._passwd

    @property
    def connect_timeout(self) -> int:
        return self._connect_timeout

    @property
    def dbname(self) -> str:
        return self._dbname

    @property
    def tbname(self) -> str:
        return self._tbname


class SimpleDBRst(CBasicResult):
    """数据库执行结果类。

    Attributes:
        _affect_rows: 影响的行数
        _rst: 查询结果
    """

    def __init__(self) -> None:
        super(SimpleDBRst, self).__init__()
        self._affect_rows: int = 0
        self._rst: List[Dict[str, Any]] = []

    @property
    def affect_rows(self) -> int:
        return self._affect_rows

    @property
    def rst(self) -> List[Dict[str, Any]]:
        return self._rst


class SimpleDB(object):
    """数据库操作类。

    提供简单的数据库操作接口，支持自动重连。
    """

    def __init__(self, config: SimpleDBConfig):
        self._config = config
        self._useable = False
        self._connect: Optional[Any] = None
        self._cursor: Optional[Any] = None

    def initDB(self) -> CBasicResult:
        """初始化数据库连接。

        Returns:
            CBasicResult 结果对象
        """
        if not isinstance(self._config, SimpleDBConfig):
            return CBasicResult(
                -1, f"config is not instance of SimpleDBConfig but {type(self._config)}"
            )

        checkrst = self._config.checkConfig()
        if checkrst.resultcode != 0:
            return checkrst

        if MYSQL_LIB is None:
            return CBasicResult(-1, "No MySQL library found (pymysql or MySQLdb)")

        try:
            if MYSQL_LIB == "pymysql":
                self._connect = pymysql.connect(
                    host=self._config._host,
                    port=self._config._port,
                    user=self._config._user,
                    password=self._config._passwd,
                    connect_timeout=self._config._connect_timeout,
                    cursorclass=pymysql.cursors.DictCursor,
                )
            else:
                self._connect = MySQLdb.connect(
                    host=self._config._host,
                    port=self._config._port,
                    user=self._config._user,
                    passwd=self._config._passwd,
                    connect_timeout=self._config._connect_timeout,
                )
                # 使用 DictCursor 方式获取结果
                self._cursor = self._connect.cursor(MySQLdb.cursors.DictCursor)

            if MYSQL_LIB == "pymysql":
                self._connect.autocommit(True)

                if self._config._dbname != "":
                    self._connect.select_db(self._config._dbname)

                # pymysql cursor 已在创建连接时指定
                self._cursor = self._connect.cursor()
            else:
                self._connect.autocommit(True)

                if self._config._dbname != "":
                    self._connect.select_db(self._config._dbname)

            self._useable = True
            return CBasicResult()

        except Exception as e:
            self._useable = False
            return CBasicResult(-1, "SimpleDB init failed", -1, str(e))

    def reInitDB(self) -> CBasicResult:
        """重新初始化数据库连接。

        Returns:
            CBasicResult 结果对象
        """
        try:
            if self._useable and self._cursor is not None:
                self._cursor.close()
            if self._connect is not None:
                self._connect.close()

            return self.initDB()

        except Exception as e:
            return CBasicResult(-1, "SimpleDB reInitDB failed", -1, str(e))

    def execute(
        self, sql: str, again: bool = False
    ) -> CBasicResult:
        """执行 SQL 语句。

        Args:
            sql: SQL 语句
            again: 是否是重试执行

        Returns:
            CBasicResult 结果对象，包含查询结果
        """
        if self._cursor is None:
            return CBasicResult(-1, "Cursor is None", -1, "DB not initialized")

        try:
            sdbrst = SimpleDBRst()
            sdbrst._affect_rows = self._cursor.execute(sql)
            sdbrst._rst = self._cursor.fetchall()
            return sdbrst

        except Exception as e:
            # 获取错误码
            errno = getattr(e, "args", [0])[0] if hasattr(e, "args") else 0

            if not again and (
                (not self._useable) or errno == 2013 or errno == 2006
            ):
                rst = self.reInitDB()
                if rst.resultcode != 0:
                    return CBasicResult(
                        -1, f"SimpleDB execute failed [{sql}]", rst.errorcode, rst.errorinfo
                    )
                else:
                    return self.execute(sql, True)
            else:
                return CBasicResult(
                    -1, f"SimpleDB execute failed [{sql}]", -1, str(e)
                )

    def Commit(self) -> None:
        """提交事务。"""
        if self._connect is not None:
            self._connect.commit()

    def setAutoCommit(self) -> None:
        """设置自动提交。"""
        if self._connect is not None:
            if MYSQL_LIB == "pymysql":
                self._connect.autocommit(True)
            else:
                self._connect.autocommit(True)

    def resetAutoCommit(self) -> None:
        """重置自动提交。"""
        if self._connect is not None:
            if MYSQL_LIB == "pymysql":
                self._connect.autocommit(False)
            else:
                self._connect.autocommit(False)

    def __del__(self) -> None:
        """析构函数，关闭连接。"""
        try:
            if hasattr(self, "_cursor") and self._cursor is not None:
                self._cursor.close()
            if hasattr(self, "_connect") and self._connect is not None:
                self._connect.close()
        except Exception as e:
            print(f"SimpleDB __del__ failed: {e}")


# ============================================================================
# Test / Demo
# ============================================================================
def _create_test_db() -> SimpleDB:
    """创建测试数据库连接。"""
    dbconfig = SimpleDBConfig(
        host="172.27.198.178", port=3306, user="root", dbname="scsa_center"
    )
    return SimpleDB(dbconfig)


def testSelect() -> None:
    """测试查询操作。"""
    sdb = _create_test_db()
    rst = sdb.initDB()
    if rst.resultcode != 0:
        print(rst)
        return

    while True:
        time.sleep(1)
        value = sdb.execute(
            "select FAccttype, FRoutePolicy, FLoadCondition, "
            "FLoadDescription, FTimeStamp from t_route_policy"
        )

        if rst.resultcode != 0:
            print(value)
            continue

        for line in value._rst:
            print(f"{value._affect_rows}\t{line['FAccttype']}\t{line['FRoutePolicy']}")


def testInsert() -> None:
    """测试插入操作。"""
    sdb = _create_test_db()
    rst = sdb.initDB()
    if rst.resultcode != 0:
        print(rst)
        return

    sql = "insert into scsa_center.t_svr_config(FSetName) values('hello')"
    ans = sdb.execute(sql)
    if ans.resultcode != 0:
        print(ans)
        return

    print(f"affect rows {ans._affect_rows}")


def testUpdate() -> None:
    """测试更新操作。"""
    sdb = _create_test_db()
    rst = sdb.initDB()
    if rst.resultcode != 0:
        print(rst)
        return

    sql = "update scsa_center.t_svr_config set FHost='1.1.1.1' where FSetName='hello'"
    ans = sdb.execute(sql)
    if ans.resultcode != 0:
        print(ans)
        return

    print(f"affect rows {ans._affect_rows}")


def testDelete() -> None:
    """测试删除操作。"""
    sdb = _create_test_db()
    rst = sdb.initDB()
    if rst.resultcode != 0:
        print(rst)
        return

    sql = "delete from scsa_center.t_svr_config where FSetName='hello'"
    ans = sdb.execute(sql)
    if ans.resultcode != 0:
        print(ans)
        return

    print(f"affect rows {ans._affect_rows}")


if "__main__" == "__main__":
    # 默认执行查询测试
    print(f"Using MySQL library: {MYSQL_LIB}")
    testSelect()
