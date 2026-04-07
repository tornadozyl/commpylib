#!/usr/bin/env python
# coding:utf-8
"""simpledb 模块单元测试。"""

import unittest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from simpledb import SimpleDBConfig, SimpleDBRst


class TestSimpleDBConfig(unittest.TestCase):
    """SimpleDBConfig 测试类。"""

    def test_default_init(self):
        """测试默认初始化。"""
        config = SimpleDBConfig()
        self.assertEqual(config.port, 3306)
        self.assertEqual(config.connect_timeout, 5)

    def test_custom_init(self):
        """测试自定义初始化。"""
        config = SimpleDBConfig(
            host="localhost",
            port=3307,
            user="test",
            passwd="password",
            connect_timeout=10,
            dbname="testdb",
        )
        self.assertEqual(config.host, "localhost")
        self.assertEqual(config.port, 3307)
        self.assertEqual(config.user, "test")

    def test_checkConfig_valid(self):
        """测试有效配置。"""
        config = SimpleDBConfig(host="localhost", port=3306, user="root")
        rst = config.checkConfig()
        self.assertEqual(rst.resultcode, 0)

    def test_checkConfig_invalid_no_host(self):
        """测试无效配置（无主机）。"""
        config = SimpleDBConfig(host="", port=3306, user="root")
        rst = config.checkConfig()
        self.assertNotEqual(rst.resultcode, 0)

    def test_checkConfig_invalid_port(self):
        """测试无效配置（无效端口）。"""
        config = SimpleDBConfig(host="localhost", port=0, user="root")
        rst = config.checkConfig()
        self.assertNotEqual(rst.resultcode, 0)

    def test_checkConfig_invalid_timeout(self):
        """测试无效配置（无效超时）。"""
        config = SimpleDBConfig(host="localhost", port=3306, user="root", connect_timeout=0)
        rst = config.checkConfig()
        self.assertNotEqual(rst.resultcode, 0)

    def test_str(self):
        """测试字符串表示。"""
        config = SimpleDBConfig(host="localhost", passwd="secret")
        config_str = str(config)
        self.assertIn("localhost", config_str)
        self.assertNotIn("secret", config_str)  # 密码应该被隐藏


class TestSimpleDBRst(unittest.TestCase):
    """SimpleDBRst 测试类。"""

    def test_init(self):
        """测试初始化。"""
        rst = SimpleDBRst()
        self.assertEqual(rst.resultcode, 0)
        self.assertEqual(rst.affect_rows, 0)
        self.assertEqual(rst.rst, [])


if __name__ == "__main__":
    unittest.main()
