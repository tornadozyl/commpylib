#!/usr/bin/env python
# coding:utf-8
"""自定义日志 Handler 模块。

提供自然时间轮转的 FileHandler，解决时区问题。
"""

from logging.handlers import TimedRotatingFileHandler
import time
from typing import Optional

# 时区修正（UTC+8，单位：秒）
TIMEZONE_MODIFY = 60 * 60 * 8


class NatureTimedRotatingFileHandler(TimedRotatingFileHandler):
    """自然时间轮转的文件 Handler。

    使用本地时间的自然边界进行轮转，而非 UTC 时间。
    解决了标准 TimedRotatingFileHandler 在中国的时区问题。
    """

    def __init__(
        self,
        filename: str,
        when: str = "H",
        interval: int = 1,
        backupCount: int = 0,
        encoding: Optional[str] = None,
        delay: bool = False,
        utc: bool = False,
    ):
        super(NatureTimedRotatingFileHandler, self).__init__(
            filename, when.upper(), interval, backupCount, encoding, delay, utc
        )
        last_nature_time = self._get_last_nature_time()
        self.rolloverAt = self.compute_rollover(last_nature_time)

    def _get_last_nature_time(self) -> int:
        """获取上一个自然时间边界点。

        Returns:
            Unix 时间戳
        """
        now_unixtime = int(time.time())

        if self.when == "S":
            return now_unixtime
        elif self.when == "M":
            return now_unixtime - (now_unixtime % 60)
        elif self.when == "H":
            return now_unixtime - (now_unixtime % (60 * 60))
        elif self.when in ("D", "MIDNIGHT"):
            # 使用本地时间的午夜边界
            return now_unixtime - (now_unixtime % (60 * 60 * 24)) - TIMEZONE_MODIFY
        else:
            raise ValueError(f"Invalid rollover interval specified: {self.when}")

    def compute_rollover(self, current_time: int) -> int:
        """计算下次轮转时间。

        Args:
            current_time: 当前时间戳

        Returns:
            下次轮转的时间戳
        """
        return super(NatureTimedRotatingFileHandler, self).computeRollover(current_time)
