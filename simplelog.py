#!/usr/bin/env python
# coding:utf-8
"""简单日志模块。

提供基础的日志初始化功能。
"""

import logging
from logging.handlers import RotatingFileHandler
from typing import Optional, Set

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

_HANDLER_TYPE = frozenset(["file", "stream"])


class CLogConfig(object):
    """日志配置类。

    Attributes:
        level: 日志级别
        formatter: 日志格式
        path: 日志文件路径
        handler: handler 类型（file 或 stream）
    """

    def __init__(
        self,
        level: str = "debug",
        formatter: str = "simple",
        path: str = DEFAULT_PATH,
        handler: str = "file",
    ):
        self._level = LEVELS.get(level, logging.DEBUG)
        self._formatter = LOGFORMATTER.get(formatter, LOGFORMATTER["simple"])
        self._path = path
        self._handler = handler

    def __del__(self) -> None:
        pass

    def checkConfig(self) -> bool:
        """检查配置是否有效。

        Returns:
            True 表示配置有效，False 表示无效
        """
        if self._level not in LEVELS.values():
            return False
        if self._formatter not in LOGFORMATTER.values():
            return False
        if self._handler not in _HANDLER_TYPE:
            return False
        return True

    @property
    def level(self) -> int:
        """获取日志级别。"""
        return self._level

    @property
    def formatter(self) -> str:
        """获取日志格式。"""
        return self._formatter

    @property
    def path(self) -> str:
        """获取日志路径。"""
        return self._path

    @property
    def handler(self) -> str:
        """获取 handler 类型。"""
        return self._handler


def initLog(config: CLogConfig, logmodule: str = "sys") -> Optional[logging.Logger]:
    """初始化日志。

    Args:
        config: CLogConfig 配置对象
        logmodule: 日志模块名称

    Returns:
        Logger 对象，失败返回 None
    """
    if not isinstance(config, CLogConfig):
        printerr(
            f"InitLog Invalid parameter, need CLogConfig but got {type(config)}"
        )
        return None

    if not config.checkConfig():
        printerr("config.checkConfig() failed")
        return None

    logger = logging.getLogger(logmodule)
    logger.setLevel(config._level)

    if config._handler == "file":
        handler = RotatingFileHandler(
            config._path, maxBytes=4 * 1024 * 1024 * 1024, backupCount=100
        )
    else:
        handler = logging.StreamHandler()

    handler.setLevel(logging.DEBUG)
    handler.setFormatter(logging.Formatter(config._formatter))

    logger.addHandler(handler)

    return logger


# --------------------------------------------------- use demo -----------------------------------
def testLog() -> None:
    """测试日志功能。"""
    config1 = CLogConfig()
    logger = initLog(config1)
    if logger is None:
        return

    logger.debug("hello %s", ("world"))


def testLog2() -> None:
    """测试获取已有 logger。"""
    logger = logging.getLogger("sys")
    logger.debug("hello in testLog2")


# -----------------------------------------------use demo end ------------------------------------

if "__main__" == "__main__":
    testLog()
    testLog2()
