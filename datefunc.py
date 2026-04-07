#!/usr/bin/env python
# coding:utf-8
"""日期时间处理函数模块。

提供日期计算、格式化等常用功能。
"""

import calendar
import time
from datetime import datetime, timedelta, date
from typing import Optional


def first_day_of_month(dt: datetime) -> datetime:
    """获取指定日期所在月的第一天。

    Args:
        dt: 输入日期时间

    Returns:
        当月第一天的 datetime 对象（0 点 0 分 0 秒）
    """
    return (dt + timedelta(days=-dt.day + 1)).replace(
        hour=0, minute=0, second=0, microsecond=0
    )


def get_current_month() -> str:
    """获取当前月份字符串。

    Returns:
        格式为 'YYYY-MM' 的当前月份字符串
    """
    return time.strftime("%Y-%m", time.localtime(time.time()))


def get_current_date() -> str:
    """获取当前日期字符串。

    Returns:
        格式为 'YYYY-MM-DD' 的当前日期字符串
    """
    return time.strftime("%Y-%m-%d", time.localtime(time.time()))


def from_unixtime(unix_timestamp: int) -> str:
    """将 Unix 时间戳转换为格式化的日期字符串。

    Args:
        unix_timestamp: Unix 时间戳

    Returns:
        格式为 'YYYY-MM-DD HH:MM:SS' 的日期字符串
    """
    return time.strftime("%Y-%m-%d %X", time.localtime(unix_timestamp))


def format_time(
    year: int = 1900,
    month: int = 1,
    day: int = 1,
    hour: int = 0,
    minute: int = 0,
    second: int = 0,
    timeformat: str = "%Y-%m-%d %X",
) -> str:
    """格式化时间为字符串。

    Args:
        year: 年
        month: 月
        day: 日
        hour: 时
        minute: 分
        second: 秒
        timeformat: 输出格式

    Returns:
        格式化后的时间字符串
    """
    return datetime(year, month, day, hour, minute, second).strftime(timeformat)


def get_last_month(month: str) -> str:
    """获取上一个月。

    Args:
        month: 月份字符串，格式为 'YYYY-MM'

    Returns:
        上一个月的字符串，格式为 'YYYY-MM'
    """
    year, mon = month.split("-")
    y, m = int(year), int(mon)

    if m > 1:
        return f"{y}-{m - 1:02d}"
    else:
        return f"{y - 1}-12"


def get_days_of_month(year: int, month: int) -> int:
    """获取指定月份的天数。

    Args:
        year: 年
        month: 月

    Returns:
        该月的天数
    """
    return calendar.monthrange(year, month)[1]


def get_first_day_of_month(month: str) -> str:
    """获取指定月份的第一天。

    Args:
        month: 月份字符串，格式为 'YYYY-MM'

    Returns:
        格式为 'YYYY-MM-01' 的字符串
    """
    return f"{month}-01"


def get_last_day_of_month(month: str) -> str:
    """获取指定月份的最后一天。

    Args:
        month: 月份字符串，格式为 'YYYY-MM'

    Returns:
        格式为 'YYYY-MM-DD' 的月末日期字符串
    """
    year, mon = month.split("-")
    fyear, fmonth = int(year), int(mon)
    last_day = get_days_of_month(fyear, fmonth)
    return f"{month}-{last_day:02d}"


def get_date_yesterday(date_str: str) -> str:
    """获取昨天的日期（YYYY-MM-DD 格式）。

    Args:
        date_str: 日期字符串，格式为 'YYYY-MM-DD'

    Returns:
        昨天的日期字符串
    """
    datelist = date_str.split("-")
    year, month, day = int(datelist[0]), int(datelist[1]), int(datelist[2])
    date_yesterday = datetime(year, month, day) - timedelta(days=1)
    return date_yesterday.strftime("%Y-%m-%d")


def get_date_yesterday_ex(date_str: str) -> str:
    """获取昨天的日期（YYYYMMDD 格式）。

    Args:
        date_str: 日期字符串，格式为 'YYYYMMDD'

    Returns:
        昨天的日期字符串，格式为 'YYYYMMDD'
    """
    year = int(date_str[0:4])
    month = int(date_str[4:6])
    day = int(date_str[6:8])
    date_yesterday = datetime(year, month, day) - timedelta(days=1)
    return date_yesterday.strftime("%Y%m%d")


def get_date_after_day(date_str: str) -> str:
    """获取后一天的日期。

    Args:
        date_str: 日期字符串，格式为 'YYYY-MM-DD'

    Returns:
        后一天的日期字符串
    """
    datelist = date_str.split("-")
    year, month, day = int(datelist[0]), int(datelist[1]), int(datelist[2])
    date_after = datetime(year, month, day) + timedelta(days=1)
    return date_after.strftime("%Y-%m-%d")


def get_days_before(diff_days: int) -> str:
    """获取 N 天前的日期。

    Args:
        diff_days: 与今天相差的天数

    Returns:
        N 天前的日期字符串，格式为 'YYYY-MM-DD'
    """
    return (date.today() - timedelta(days=diff_days)).strftime("%Y-%m-%d")


def get_days_after(diff_days: int) -> str:
    """获取 N 天后的日期。

    Args:
        diff_days: 与今天相差的天数

    Returns:
        N 天后的日期字符串，格式为 'YYYY-MM-DD'
    """
    return (date.today() + timedelta(days=diff_days)).strftime("%Y-%m-%d")


def datefunc_demo() -> None:
    """演示日期函数的使用。"""
    last_month = get_last_month("2013-03")
    print(last_month)

    print(get_last_day_of_month("2012-02"))


if "__main__" == __name__:
    datefunc_demo()
