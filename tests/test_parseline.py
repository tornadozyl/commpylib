#!/usr/bin/env python
# coding:utf-8
"""parseline 模块单元测试。"""

import unittest
import sys
import os
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from parseline import (
    ParseTitle,
    ParseTitleFile,
    ParseLine,
    ParseKVLine,
    ParseFile,
)


class TestParseTitle(unittest.TestCase):
    """ParseTitle 测试类。"""

    def test_parse_title_tab_sep(self):
        """测试制表符分隔。"""
        result = ParseTitle("name\tage\tcity", sep="\t")
        self.assertEqual(result, {"name": 0, "age": 1, "city": 2})

    def test_parse_title_comma_sep(self):
        """测试逗号分隔。"""
        result = ParseTitle("name,age,city", sep=",")
        self.assertEqual(result, {"name": 0, "age": 1, "city": 2})

    def test_parse_title_with_newline(self):
        """测试带换行符。"""
        result = ParseTitle("name\tage\n", sep="\t")
        self.assertEqual(result, {"name": 0, "age": 1})

    def test_parse_title_empty(self):
        """测试空行。"""
        result = ParseTitle("", sep="\t")
        # 空字符串分割后得到 ['']，所以返回 {'': 0}
        self.assertEqual(result, {"": 0})


class TestParseLine(unittest.TestCase):
    """ParseLine 测试类。"""

    def test_parse_line(self):
        """测试解析行。"""
        fields_map = {"name": 0, "age": 1, "city": 2}
        result = ParseLine("Alice\t25\tBeijing", fields_map, sep="\t")
        self.assertEqual(result, {"name": "Alice", "age": "25", "city": "Beijing"})

    def test_parse_line_not_enough_fields(self):
        """测试字段不足。"""
        fields_map = {"name": 0, "age": 1, "city": 2}
        result = ParseLine("Alice\t25", fields_map, sep="\t")
        self.assertIsNone(result)

    def test_parse_line_empty_fields_map(self):
        """测试空字段映射。"""
        result = ParseLine("Alice\t25", {}, sep="\t")
        self.assertIsNone(result)

    def test_parse_line_empty_line(self):
        """测试空行。"""
        result = ParseLine("", {"name": 0}, sep="\t")
        self.assertIsNone(result)


class TestParseKVLine(unittest.TestCase):
    """ParseKVLine 测试类。"""

    def test_parse_kv_line(self):
        """测试解析 KV 行。"""
        result = ParseKVLine("name=Alice&age=25&city=Beijing")
        self.assertEqual(result, {"name": "Alice", "age": "25", "city": "Beijing"})

    def test_parse_kv_line_with_trailing_sep(self):
        """测试带尾部分隔符。"""
        result = ParseKVLine("name=Alice&age=25&")
        self.assertEqual(result, {"name": "Alice", "age": "25"})

    def test_parse_kv_line_empty(self):
        """测试空行。"""
        result = ParseKVLine("")
        self.assertEqual(result, {})


class TestParseFile(unittest.TestCase):
    """ParseFile 测试类。"""

    def setUp(self):
        """设置测试环境。"""
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        """清理测试环境。"""
        import shutil
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_parse_file(self):
        """测试解析文件。"""
        filepath = os.path.join(self.test_dir, "test.tsv")
        with open(filepath, "w") as f:
            f.write("name\tage\n")
            f.write("Alice\t25\n")
            f.write("Bob\t30\n")

        result = ParseFile(filepath, sep="\t")
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["name"], "Alice")
        self.assertEqual(result[1]["age"], "30")


if __name__ == "__main__":
    unittest.main()
