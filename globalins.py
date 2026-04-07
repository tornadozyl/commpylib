#!/usr/bin/env python
# coding:utf-8
"""全局单例模块。

提供配置、日志、数据库连接的单例管理。
统一接口版本，返回 (CBasicResult, 对象) 元组格式。
"""

import os
import sys
import copy
import datetime
from typing import Any, Dict, List, Optional, Tuple
import configparser

from basicresult import CBasicResult
from commfunc import printerr

# 引入日志和数据库模块（延迟导入避免循环依赖）


INSTANCE_TEMP = {"config": None, "IsInited": False, "obj": None}  # type: Dict[str, Any]


class GlobalIns(object):
    """全局单例类。

    管理配置、日志、数据库连接的单例实例。
    所有方法返回 (CBasicResult, 对象) 元组格式。
    """

    __config_fullpath = "../conf/conf.ini"
    __cfg = copy.deepcopy(INSTANCE_TEMP)
    __sdb: Dict[str, Dict[str, Any]] = {}
    __log: Dict[str, Dict[str, Any]] = {}
    __logex: Dict[str, Dict[str, Any]] = {}

    def __init__(self) -> None:
        pass

    @staticmethod
    def setConfigPath(config_fullpath: str) -> CBasicResult:
        """设置配置文件路径。

        Args:
            config_fullpath: 配置文件完整路径

        Returns:
            CBasicResult 结果对象
        """
        try:
            if os.path.exists(config_fullpath):
                GlobalIns.__config_fullpath = config_fullpath
                return CBasicResult()
            else:
                errinfo = f"{config_fullpath} not exists"
                return CBasicResult(-1, errinfo, -1, errinfo)

        except Exception as e:
            return CBasicResult(-1, "setConfigPath failed", -1, str(e))

    @staticmethod
    def getCfgInstance(needreparse: bool = False) -> Tuple[CBasicResult, Optional[configparser.ConfigParser]]:
        """获取配置解析器单例。

        Args:
            needreparse: 是否强制重新解析配置文件

        Returns:
            (CBasicResult, ConfigParser 对象) 元组
        """
        try:
            if GlobalIns.__cfg["IsInited"] and not needreparse:
                return CBasicResult(), GlobalIns.__cfg["obj"]

            if not os.path.exists(GlobalIns.__config_fullpath):
                errinfo = f"{GlobalIns.__config_fullpath} not exists"
                return CBasicResult(-1, errinfo, -1, errinfo), None

            GlobalIns.__cfg["obj"] = configparser.ConfigParser()
            parsed_files = GlobalIns.__cfg["obj"].read(GlobalIns.__config_fullpath)
            if len(parsed_files) == 0:
                errinfo = f"read config [{GlobalIns.__config_fullpath}] failed"
                return CBasicResult(-1, errinfo, -1, errinfo), None

            return CBasicResult(), GlobalIns.__cfg["obj"]

        except configparser.Error as e:
            return CBasicResult(-1, "getCfgInstance failed", -1, str(e)), None
        except Exception as e:
            return CBasicResult(-1, "getCfgInstance failed", -1, str(e)), None

    @staticmethod
    def getLogInstance(name: str) -> Tuple[CBasicResult, Optional[Any]]:
        """获取日志实例（简单版）。

        Args:
            name: 日志配置节名称

        Returns:
            (CBasicResult, logger 对象) 元组
        """
        try:
            if name in GlobalIns.__log and GlobalIns.__log[name]["IsInited"]:
                return CBasicResult(), GlobalIns.__log[name]["obj"]

            rst, cfg = GlobalIns.getCfgInstance()
            if rst.resultcode != 0 or cfg is None:
                errinfo = "getLogInstance: getCfgInstance failed"
                return CBasicResult(-1, errinfo, -1, rst), None

            if name not in GlobalIns.__log:
                GlobalIns.__log[name] = copy.deepcopy(INSTANCE_TEMP)

            loglevel = cfg.get(name, "level")
            logpath = "{}.{}.log".format(
                cfg.get(name, "logname"), datetime.datetime.today().strftime("%Y%m%d")
            )

            # 延迟导入避免循环依赖
            from simplelog import CLogConfig, initLog

            logconfig = CLogConfig(level=loglevel, path=logpath)
            GlobalIns.__log[name]["obj"] = initLog(logconfig, name)

            if GlobalIns.__log[name]["obj"] is None:
                errinfo = f"getLogInstance create log with [{name}] failed"
                return CBasicResult(-1, errinfo, -1, errinfo), None
            else:
                GlobalIns.__log[name]["IsInited"] = True

            return CBasicResult(), GlobalIns.__log[name]["obj"]

        except configparser.Error as e:
            return CBasicResult(-1, "getLogInstance failed", -1, str(e)), None
        except Exception as e:
            return CBasicResult(-1, "getLogInstance failed", -1, str(e)), None

    @staticmethod
    def _initSizeRotatedHandlerConfig(
        cfg: configparser.ConfigParser, sectionname: str, logconfig: Dict[str, Any]
    ) -> Tuple[CBasicResult, Optional[Any]]:
        """初始化按大小轮转的日志 Handler 配置。

        Args:
            cfg: ConfigParser 对象
            sectionname: 配置节名称
            logconfig: 日志配置字典

        Returns:
            (CBasicResult, HandlerConfig 对象) 元组
        """
        from simplelogex import CRotatingFileHandlerConfig

        if cfg.has_option(sectionname, "rotatesize"):
            logconfig["rotatesize"] = cfg.getint(sectionname, "rotatesize") * 1024 * 1024
        else:
            logconfig["rotatesize"] = 4 * 1024 * 1024 * 1024

        if cfg.has_option(sectionname, "openmode"):
            logconfig["openmode"] = cfg.get(sectionname, "openmode")
        else:
            logconfig["openmode"] = "a"

        logconfig["encoding"] = None

        if cfg.has_option(sectionname, "backupcount"):
            logconfig["backupcount"] = cfg.getint(sectionname, "backupcount")
        else:
            logconfig["backupcount"] = 10000

        handlerconfig = CRotatingFileHandlerConfig(
            level=logconfig["loglevel"],
            formatter=logconfig["formatter"],
            filename="{}.log.{}".format(
                logconfig["logpath"], datetime.datetime.today().strftime("%Y-%m-%d")
            ),
            maxBytes=logconfig["rotatesize"],
            mode=logconfig["openmode"],
            encoding=logconfig["encoding"],
            backupCount=logconfig["backupcount"],
        )

        return CBasicResult(), handlerconfig

    @staticmethod
    def _initNatureTimeRotateLog(
        cfg: configparser.ConfigParser, sectionname: str, logconfig: Dict[str, Any]
    ) -> Tuple[CBasicResult, Optional[Any]]:
        """初始化按自然时间轮转的日志 Handler 配置。

        Args:
            cfg: ConfigParser 对象
            sectionname: 配置节名称
            logconfig: 日志配置字典

        Returns:
            (CBasicResult, HandlerConfig 对象) 元组
        """
        from simplelogex import CNatureTimedRotatingFileHandlerConfig

        when_map = {"day": "D", "hour": "H", "minute": "M", "second": "S"}

        if cfg.has_option(sectionname, "when"):
            when = cfg.get(sectionname, "when")
            logconfig["when"] = when_map.get(when, "D")
        else:
            logconfig["when"] = "D"

        if cfg.has_option(sectionname, "interval"):
            logconfig["interval"] = cfg.getint(sectionname, "interval")
        else:
            logconfig["interval"] = 1

        if cfg.has_option(sectionname, "openmode"):
            logconfig["openmode"] = cfg.get(sectionname, "openmode")
        else:
            logconfig["openmode"] = "a"

        logconfig["encoding"] = None

        if cfg.has_option(sectionname, "backupcount"):
            logconfig["backupcount"] = cfg.getint(sectionname, "backupcount")
        else:
            logconfig["backupcount"] = 10000

        handlerconfig = CNatureTimedRotatingFileHandlerConfig(
            level=logconfig["loglevel"],
            formatter=logconfig["formatter"],
            filename=logconfig["logpath"],
            when=logconfig["when"],
            interval=logconfig["interval"],
            mode=logconfig["openmode"],
            backupCount=logconfig["backupcount"],
            encoding=logconfig["encoding"],
        )

        return CBasicResult(), handlerconfig

    @staticmethod
    def getLogExInstance(name: str) -> Tuple[CBasicResult, Optional[Any]]:
        """获取扩展日志实例（支持轮转）。

        Args:
            name: 日志配置节名称

        Returns:
            (CBasicResult, logger 对象) 元组
        """
        try:
            if name in GlobalIns.__logex and GlobalIns.__logex[name]["IsInited"]:
                return CBasicResult(), GlobalIns.__logex[name]["obj"]

            rst, cfg = GlobalIns.getCfgInstance()
            if rst.resultcode != 0 or cfg is None:
                return CBasicResult(-1, "getCfgInstance failed", -1, rst), None

            if name not in GlobalIns.__logex:
                GlobalIns.__logex[name] = copy.deepcopy(INSTANCE_TEMP)

            logconfig: Dict[str, Any] = {}
            logconfig["loglevel"] = cfg.get(name, "level")
            logconfig["logpath"] = cfg.get(name, "logname")
            logconfig["logtype"] = cfg.get(name, "logtype")

            if cfg.has_option(name, "formatter"):
                logconfig["formatter"] = cfg.get(name, "formatter")
            else:
                logconfig["formatter"] = "simple"

            handlerconfig_array: List[Any] = []

            if logconfig["logtype"].lower() == "size":
                rst, handlerconfig = GlobalIns._initSizeRotatedHandlerConfig(
                    cfg, name, logconfig
                )
                if rst.resultcode != 0:
                    return rst, None
                handlerconfig_array.append(handlerconfig)

            elif logconfig["logtype"].lower() == "naturetime":
                rst, handlerconfig = GlobalIns._initNatureTimeRotateLog(
                    cfg, name, logconfig
                )
                if rst.resultcode != 0:
                    return rst, None
                handlerconfig_array.append(handlerconfig)
            else:
                errinfo = f"logtype {logconfig['logtype']} invalid"
                return CBasicResult(-1, errinfo, -1, errinfo), None

            # 延迟导入
            from simplelogex import initLog

            GlobalIns.__logex[name]["obj"] = initLog(
                logmodule=name,
                loglevel=logconfig["loglevel"],
                handlerConfigs=handlerconfig_array,
            )
            GlobalIns.__logex[name]["IsInited"] = True

            return CBasicResult(), GlobalIns.__logex[name]["obj"]

        except Exception as e:
            return CBasicResult(-1, "getLogExInstance failed", -1, str(e)), None

    @staticmethod
    def getSDBInstance(name: str) -> Tuple[CBasicResult, Optional[Any]]:
        """获取数据库连接实例。

        Args:
            name: 数据库配置节名称

        Returns:
            (CBasicResult, SimpleDB 对象) 元组
        """
        try:
            if name in GlobalIns.__sdb and GlobalIns.__sdb[name]["IsInited"]:
                return CBasicResult(), GlobalIns.__sdb[name]["obj"]

            rst, cfg = GlobalIns.getCfgInstance()
            if rst.resultcode != 0 or cfg is None:
                return CBasicResult(-1, "getSDBInstance failed", -1, "getCfgInstance None"), None

            if name not in GlobalIns.__sdb:
                GlobalIns.__sdb[name] = copy.deepcopy(INSTANCE_TEMP)

            db_host = cfg.get(name, "ip")
            db_port = int(cfg.get(name, "port"))
            db_user = cfg.get(name, "user")
            db_passwd = cfg.get(name, "passwd")
            db_timeout = 5
            if cfg.has_option(name, "timeout"):
                db_timeout = int(cfg.get(name, "timeout"))

            db_dbname = ""
            if cfg.has_option(name, "dbname"):
                db_dbname = cfg.get(name, "dbname")

            db_tbname = ""
            if cfg.has_option(name, "tablename"):
                db_tbname = cfg.get(name, "tablename")

            # 延迟导入
            from simpledb import SimpleDBConfig, SimpleDB

            sdbconfig = SimpleDBConfig(
                db_host, db_port, db_user, db_passwd, db_timeout, db_dbname, db_tbname
            )
            GlobalIns.__sdb[name]["obj"] = SimpleDB(sdbconfig)

            rst = GlobalIns.__sdb[name]["obj"].initDB()
            if rst.resultcode != 0:
                return CBasicResult(-1, "getSDBInstance failed", -1, rst), None

            GlobalIns.__sdb[name]["IsInited"] = True
            return CBasicResult(), GlobalIns.__sdb[name]["obj"]

        except configparser.Error as e:
            return CBasicResult(-1, "getSDBInstance failed", -1, str(e)), None
        except Exception as e:
            return CBasicResult(-1, "getSDBInstance failed", -1, str(e)), None


# ============================================================================
# Demo / Test
# ============================================================================
def GlobalIns_Demo() -> None:
    """演示 GlobalIns 的使用方法。"""
    rst = GlobalIns.setConfigPath("./globalins_demo_config.ini")
    if rst.resultcode != 0:
        print(rst)
        sys.exit(-1)

    rst, cfg = GlobalIns.getCfgInstance()
    if rst.resultcode != 0 or cfg is None:
        print(rst)
        sys.exit(-1)

    # 获取简单日志实例
    rst, log_demo1 = GlobalIns.getLogInstance("log_demo1")
    if rst.resultcode != 0 or log_demo1 is None:
        print(rst)
        sys.exit(-1)

    # 获取扩展日志实例
    rst, log_demo2 = GlobalIns.getLogExInstance("logex_demo1")
    if rst.resultcode != 0 or log_demo2 is None:
        print(rst)
        sys.exit(-1)

    # 获取数据库实例
    rst, db_demo1 = GlobalIns.getSDBInstance("db_demo2")
    if rst.resultcode != 0 or db_demo1 is None:
        print(rst)
        # db 连接失败不退出，仅提示

    print("GlobalIns Demo passed!")


if __name__ == "__main__":
    GlobalIns_Demo()
