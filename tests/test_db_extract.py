#!/usr/bin/env python
# coding:utf-8
"""db_extract 模块单元测试。"""

import unittest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db_extract import (
    MakeSqlKeyFields,
    MakeSqlValueFields,
    MakeKey,
)


class TestMakeSqlKeyFields(unittest.TestCase):
    """MakeSqlKeyFields 测试类。"""

    def test_empty_list(self):
        """测试空列表。"""
        result = MakeSqlKeyFields([])
        self.assertEqual(result, "")

    def test_single_field(self):
        """测试单个字段。"""
        result = MakeSqlKeyFields(["name"])
        self.assertEqual(result, "`name`")

    def test_multiple_fields(self):
        """测试多个字段。"""
        result = MakeSqlKeyFields(["name", "age", "city"])
        self.assertEqual(result, "`name`,`age`,`city`")


class TestMakeSqlValueFields(unittest.TestCase):
    """MakeSqlValueFields 测试类。"""

    def test_empty_list(self):
        """测试空列表。"""
        result = MakeSqlValueFields([])
        self.assertEqual(result, "")

    def test_string_values(self):
        """测试字符串值。"""
        result = MakeSqlValueFields(["Alice", "Beijing"])
        self.assertEqual(result, "'Alice','Beijing'")

    def test_numeric_values(self):
        """测试数值。"""
        result = MakeSqlValueFields([25, 30])
        self.assertEqual(result, "25,30")

    def test_none_value(self):
        """测试 None 值。"""
        result = MakeSqlValueFields([None])
        self.assertEqual(result, "NULL")

    def test_mixed_values(self):
        """测试混合值。"""
        result = MakeSqlValueFields(["Alice", 25, None])
        self.assertEqual(result, "'Alice',25,NULL")


class TestMakeKey(unittest.TestCase):
    """MakeKey 测试类。"""

    def test_single_key(self):
        """测试单个键。"""
        line = {"id": "1", "name": "Alice"}
        result = MakeKey(line, ["id"])
        self.assertEqual(result, "1")

    def test_multiple_keys(self):
        """测试多个键。"""
        line = {"id": "1", "type": "A", "name": "Alice"}
        result = MakeKey(line, ["id", "type"])
        self.assertEqual(result, "1-A")

    def test_custom_sep(self):
        """测试自定义分隔符。"""
        line = {"id": "1", "type": "A"}
        result = MakeKey(line, ["id", "type"], keysep="_")
        self.assertEqual(result, "1_A")

    def test_missing_key(self):
        """测试缺失键。"""
        line = {"id": "1", "name": "Alice"}
        result = MakeKey(line, ["id", "missing"])
        self.assertEqual(result, "1")


if __name__ == "__main__":
    unittest.main()
