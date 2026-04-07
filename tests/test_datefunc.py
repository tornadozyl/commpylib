#!/usr/bin/env python
# coding:utf-8
"""datefunc 模块单元测试。"""

import unittest
import sys
import os
from datetime import datetime, date, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datefunc import (
    first_day_of_month,
    get_current_month,
    get_current_date,
    from_unixtime,
    format_time,
    get_last_month,
    get_days_of_month,
    get_first_day_of_month,
    get_last_day_of_month,
    get_date_yesterday,
    get_date_yesterday_ex,
    get_date_after_day,
    get_days_before,
    get_days_after,
)


class TestDateFunc(unittest.TestCase):
    """日期函数测试类。"""

    def test_first_day_of_month(self):
        """测试获取月初。"""
        dt = datetime(2023, 3, 15, 10, 30, 45)
        result = first_day_of_month(dt)
        self.assertEqual(result, datetime(2023, 3, 1, 0, 0, 0))

    def test_get_current_month(self):
        """测试获取当前月份。"""
        result = get_current_month()
        self.assertRegex(result, r"\d{4}-\d{2}")

    def test_get_current_date(self):
        """测试获取当前日期。"""
        result = get_current_date()
        self.assertRegex(result, r"\d{4}-\d{2}-\d{2}")

    def test_from_unixtime(self):
        """测试 Unix 时间戳转换。"""
        result = from_unixtime(1609459200)  # 2021-01-01 00:00:00 UTC+8
        self.assertIn("2021-01-01", result)

    def test_format_time(self):
        """测试时间格式化。"""
        result = format_time(2023, 3, 15, 10, 30, 0)
        self.assertIn("2023-03-15", result)

    def test_get_last_month(self):
        """测试获取上月。"""
        self.assertEqual(get_last_month("2023-03"), "2023-02")
        self.assertEqual(get_last_month("2023-01"), "2022-12")

    def test_get_days_of_month(self):
        """测试获取月份天数。"""
        self.assertEqual(get_days_of_month(2023, 2), 28)
        self.assertEqual(get_days_of_month(2024, 2), 29)  # 闰年
        self.assertEqual(get_days_of_month(2023, 1), 31)

    def test_get_first_day_of_month(self):
        """测试获取月初日期。"""
        self.assertEqual(get_first_day_of_month("2023-03"), "2023-03-01")

    def test_get_last_day_of_month(self):
        """测试获取月末日期。"""
        self.assertEqual(get_last_day_of_month("2023-02"), "2023-02-28")
        self.assertEqual(get_last_day_of_month("2024-02"), "2024-02-29")

    def test_get_date_yesterday(self):
        """测试获取昨天（YYYY-MM-DD）。"""
        self.assertEqual(get_date_yesterday("2023-03-15"), "2023-03-14")
        self.assertEqual(get_date_yesterday("2023-01-01"), "2022-12-31")

    def test_get_date_yesterday_ex(self):
        """测试获取昨天（YYYYMMDD）。"""
        self.assertEqual(get_date_yesterday_ex("20230315"), "20230314")
        self.assertEqual(get_date_yesterday_ex("20230101"), "20221231")

    def test_get_date_after_day(self):
        """测试获取后天。"""
        self.assertEqual(get_date_after_day("2023-03-15"), "2023-03-16")
        self.assertEqual(get_date_after_day("2023-12-31"), "2024-01-01")

    def test_get_days_before(self):
        """测试获取 N 天前。"""
        result = get_days_before(1)
        expected = (date.today() - timedelta(days=1)).strftime("%Y-%m-%d")
        self.assertEqual(result, expected)

    def test_get_days_after(self):
        """测试获取 N 天后。"""
        result = get_days_after(1)
        expected = (date.today() + timedelta(days=1)).strftime("%Y-%m-%d")
        self.assertEqual(result, expected)


if __name__ == "__main__":
    unittest.main()
