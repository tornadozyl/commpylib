#!/usr/bin/env python
# coding:utf-8
"""扩展日志模块。

支持多种日志轮转方式（按大小、按时间、按自然时间）。
"""

import logging
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
from typing import List, Optional

from myloghandlers import NatureTimedRotatingFileHandler
from commfunc import printerr

DEFAULT_PATH = "./server.log"
LOGFORMATTER = {"simple": "[%(asctime)s %(module)s] %(levelname)s %(message)s"}
LEVELS = {
    "noset": logging.NOTSET,
    "debug": logging.DEBUG,
    "info": logging.INFO,
    "warning": logging.WARNING,
    "error": logging.ERROR,
    "critical": logging.CRITICAL,
}


class CBaseHandlerConfig(object):
    """Handler 配置基类。

    Attributes:
        _level: 日志级别
        _formatter: 日志格式
        _module: 模块名
    """

    def __init__(self, level: str = "debug", formatter: str = "simple"):
        self._level = LEVELS.get(level, logging.DEBUG)
        self._formatter = LOGFORMATTER.get(formatter, LOGFORMATTER["simple"])
        self._module = "sys"

    def _checkConfig(self) -> bool:
        """检查配置是否有效。

        Returns:
            True 表示配置有效，False 表示无效
        """
        if self._level not in LEVELS.values():
            printerr(f"level {self._level} illegal")
            return False

        if self._formatter not in LOGFORMATTER.values():
            printerr(f"log formatter:{self._formatter} not support")
            return False

        return True

    def __str__(self) -> str:
        return f"level={self._level}, formatter={self._formatter}"

    def InitHandler(self) -> Optional[logging.Handler]:
        """初始化 Handler。

        Returns:
            Handler 对象，失败返回 None
        """
        if not self._checkConfig():
            return None

        handler = self._initHandler()
        if handler is None:
            return None

        handler.setLevel(self._level)
        handler.setFormatter(logging.Formatter(self._formatter))
        return handler

    def _initHandler(self) -> Optional[logging.Handler]:
        """子类实现具体的 Handler 初始化。

        Returns:
            Handler 对象
        """
        raise NotImplementedError("_initHandler must be implemented by subclass")


class CFileRotateHandlerConfig(CBaseHandlerConfig):
    """文件轮转 Handler 配置基类。

    Attributes:
        _filename: 日志文件名
        _mode: 文件打开模式
        _encoding: 编码
        _delay: 是否延迟打开文件
        _backupcount: 备份文件数量
    """

    def __init__(
        self,
        level: str = "debug",
        formatter: str = "simple",
        filename: str = DEFAULT_PATH,
        mode: str = "a",
        encoding: Optional[str] = None,
        delay: bool = False,
        backupCount: int = 0,
    ):
        super(CFileRotateHandlerConfig, self).__init__(level, formatter)
        self._filename = filename
        self._mode = mode
        self._encoding = encoding
        self._delay = delay
        self._backupcount = backupCount

    def _checkConfig(self) -> bool:
        """检查配置是否有效。"""
        if not super(CFileRotateHandlerConfig, self)._checkConfig():
            return False
        if not self._filename:
            printerr("file name empty")
            return False
        return True

    def __str__(self) -> str:
        base = super(CFileRotateHandlerConfig, self).__str__()
        return (
            f"{base}, filename={self._filename}, mode={self._mode}, "
            f"encoding={self._encoding}, delay={self._delay}, backupcount={self._backupcount}"
        )


class CRotatingFileHandlerConfig(CFileRotateHandlerConfig):
    """按大小轮转的文件 Handler 配置。

    Attributes:
        _maxbytes: 单个文件最大字节数
    """

    def __init__(
        self,
        level: str = "debug",
        formatter: str = "simple",
        filename: str = DEFAULT_PATH,
        maxBytes: int = 4 * 1024 * 1024 * 1024,
        mode: str = "a",
        encoding: Optional[str] = None,
        delay: bool = False,
        backupCount: int = 0,
    ):
        super(CRotatingFileHandlerConfig, self).__init__(
            level, formatter, filename, mode, encoding, delay, backupCount
        )
        self._maxbytes = maxBytes

    def _checkConfig(self) -> bool:
        """检查配置是否有效。"""
        if not super(CRotatingFileHandlerConfig, self)._checkConfig():
            return False
        if self._maxbytes <= 0:
            printerr("maxbytes should be above zero")
            return False
        return True

    def __str__(self) -> str:
        base = super(CRotatingFileHandlerConfig, self).__str__()
        return f"{base}, maxbytes={self._maxbytes}"

    def _initHandler(self) -> Optional[logging.Handler]:
        """初始化 RotatingFileHandler。

        Returns:
            RotatingFileHandler 对象
        """
        try:
            handler = RotatingFileHandler(
                filename=self._filename,
                mode=self._mode,
                maxBytes=self._maxbytes,
                backupCount=self._backupcount,
                encoding=self._encoding,
                delay=self._delay,
            )
            return handler
        except Exception as e:
            printerr(f"Create RotatingFileHandler failed: {e}")
            return None


class CTimedRotatingFileHandlerConfig(CFileRotateHandlerConfig):
    """按时间轮转的 Handler 配置。

    Attributes:
        _when: 轮转周期（S/M/H/D/MIDNIGHT）
        _interval: 轮转间隔
    """

    VALID_WHEN = frozenset(["S", "M", "H", "D", "MIDNIGHT"])

    def __init__(
        self,
        level: str = "debug",
        formatter: str = "simple",
        filename: str = DEFAULT_PATH,
        when: str = "H",
        interval: int = 1,
        mode: str = "a",
        backupCount: int = 10000,
        encoding: Optional[str] = None,
        delay: bool = False,
        utc: bool = False,
    ):
        super(CTimedRotatingFileHandlerConfig, self).__init__(
            level, formatter, filename, mode, encoding, delay, backupCount
        )
        self._when = when.upper()
        self._interval = interval
        self._utc = utc

    def _checkConfig(self) -> bool:
        """检查配置是否有效。"""
        if not super(CTimedRotatingFileHandlerConfig, self)._checkConfig():
            return False
        if self._when not in self.VALID_WHEN:
            printerr(f"invalid rotate log param when={self._when}")
            return False
        if self._interval <= 0:
            printerr(f"invalid rotate interval {self._interval}")
            return False
        return True

    def __str__(self) -> str:
        base = super(CTimedRotatingFileHandlerConfig, self).__str__()
        return f"{base}, when={self._when}, interval={self._interval}"

    def _initHandler(self) -> Optional[logging.Handler]:
        """初始化 TimedRotatingFileHandler。

        Returns:
            TimedRotatingFileHandler 对象
        """
        try:
            handler = TimedRotatingFileHandler(
                filename=self._filename,
                when=self._when,
                interval=self._interval,
                backupCount=self._backupcount,
                encoding=self._encoding,
                delay=self._delay,
                utc=self._utc,
            )
            return handler
        except Exception as e:
            printerr(f"Create TimedRotatingFileHandler failed: {e}")
            return None


class CNatureTimedRotatingFileHandlerConfig(CTimedRotatingFileHandlerConfig):
    """按自然时间轮转的 Handler 配置（解决时区问题）。

    使用本地时间的自然边界进行轮转，而非 UTC 时间。
    """

    def __init__(
        self,
        level: str = "debug",
        formatter: str = "simple",
        filename: str = DEFAULT_PATH,
        when: str = "H",
        interval: int = 1,
        mode: str = "a",
        backupCount: int = 10000,
        encoding: Optional[str] = None,
        delay: bool = False,
        utc: bool = False,
    ):
        super(CNatureTimedRotatingFileHandlerConfig, self).__init__(
            level,
            formatter,
            filename,
            when,
            interval,
            mode,
            backupCount,
            encoding,
            delay,
            utc,
        )

    def _checkConfig(self) -> bool:
        """检查配置是否有效。"""
        if not super(CNatureTimedRotatingFileHandlerConfig, self)._checkConfig():
            return False
        return True

    def _initHandler(self) -> Optional[logging.Handler]:
        """初始化 NatureTimedRotatingFileHandler。

        Returns:
            NatureTimedRotatingFileHandler 对象
        """
        try:
            handler = NatureTimedRotatingFileHandler(
                filename=self._filename,
                when=self._when,
                interval=self._interval,
                backupCount=self._backupcount,
                encoding=self._encoding,
                delay=self._delay,
                utc=self._utc,
            )
            return handler
        except Exception as e:
            printerr(f"Create NatureTimedRotatingFileHandler failed: {e}")
            return None


def initLog(
    logmodule: str = "sys",
    loglevel: str = "debug",
    handlerConfigs: Optional[List[CBaseHandlerConfig]] = None,
) -> Optional[logging.Logger]:
    """初始化日志。

    Args:
        logmodule: 日志模块名
        loglevel: 日志级别
        handlerConfigs: Handler 配置列表

    Returns:
        Logger 对象，失败返回 None
    """
    logger = logging.getLogger(logmodule)
    logger.setLevel(LEVELS.get(loglevel, logging.DEBUG))

    if handlerConfigs is None:
        return logger

    for config in handlerConfigs:
        handler = config.InitHandler()
        if handler is not None:
            logger.addHandler(handler)

    return logger
