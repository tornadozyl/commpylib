#!/usr/bin/env python
# coding:utf-8
"""commfunc 模块单元测试。"""

import unittest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from commfunc import SetMultiDict, GetMultiDict


class TestSetMultiDict(unittest.TestCase):
    """SetMultiDict 测试类。"""

    def test_set_single_level(self):
        """测试单层嵌套。"""
        d = {}
        SetMultiDict(["a"], "value1", d)
        self.assertEqual(d, {"a": "value1"})

    def test_set_multi_level(self):
        """测试多层嵌套。"""
        d = {}
        SetMultiDict(["a", "b", "c"], "value1", d)
        self.assertEqual(d, {"a": {"b": {"c": "value1"}}})

    def test_set_existing_key(self):
        """测试已存在的键。"""
        d = {"a": {"b": {"c": "old"}}}
        SetMultiDict(["a", "b", "d"], "new", d)
        self.assertEqual(d["a"]["b"]["d"], "new")
        self.assertEqual(d["a"]["b"]["c"], "old")


class TestGetMultiDict(unittest.TestCase):
    """GetMultiDict 测试类。"""

    def test_get_existing(self):
        """测试获取已存在的值。"""
        d = {"a": {"b": {"c": "value1"}}}
        result = GetMultiDict(["a", "b", "c"], d)
        self.assertEqual(result, "value1")

    def test_get_not_exist(self):
        """测试获取不存在的值。"""
        d = {"a": {"b": {"c": "value1"}}}
        result = GetMultiDict(["a", "x"], d)
        self.assertIsNone(result)

    def test_get_single_level(self):
        """测试单层获取。"""
        d = {"a": "value1"}
        result = GetMultiDict(["a"], d)
        self.assertEqual(result, "value1")


if __name__ == "__main__":
    unittest.main()
