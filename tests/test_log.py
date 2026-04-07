#!/usr/bin/env python
# coding:utf-8
"""日志模块单元测试。"""

import unittest
import sys
import os
import tempfile
import shutil
import logging

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from simplelog import CLogConfig, initLog
from simplelogex import (
    CRotatingFileHandlerConfig,
    CTimedRotatingFileHandlerConfig,
    CNatureTimedRotatingFileHandlerConfig,
    initLog as initLogEx,
)


class TestCLogConfig(unittest.TestCase):
    """CLogConfig 测试类。"""

    def test_default_init(self):
        """测试默认初始化。"""
        config = CLogConfig()
        self.assertEqual(config.level, logging.DEBUG)
        self.assertIn("%(asctime)s", config.formatter)

    def test_custom_init(self):
        """测试自定义初始化。"""
        config = CLogConfig(level="info", formatter="simple", path="/tmp/test.log")
        self.assertEqual(config.level, logging.INFO)

    def test_checkConfig_valid(self):
        """测试配置检查（有效）。"""
        config = CLogConfig()
        self.assertTrue(config.checkConfig())

    def test_checkConfig_invalid_handler(self):
        """测试配置检查（无效 handler）。"""
        config = CLogConfig()
        config._handler = "invalid"
        self.assertFalse(config.checkConfig())


class TestInitLog(unittest.TestCase):
    """initLog 测试类。"""

    def setUp(self):
        """设置测试环境。"""
        self.test_dir = tempfile.mkdtemp()
        self.log_file = os.path.join(self.test_dir, "test.log")

    def tearDown(self):
        """清理测试环境。"""
        shutil.rmtree(self.test_dir, ignore_errors=True)
        # 清理 logger
        for name in logging.root.manager.loggerDict:
            logger = logging.getLogger(name)
            logger.handlers = []

    def test_initLog_file_handler(self):
        """测试文件 handler 初始化。"""
        config = CLogConfig(path=self.log_file, handler="file")
        logger = initLog(config, "test")
        self.assertIsNotNone(logger)
        self.assertIsInstance(logger, logging.Logger)

    def test_initLog_stream_handler(self):
        """测试流 handler 初始化。"""
        config = CLogConfig(handler="stream")
        logger = initLog(config, "test_stream")
        self.assertIsNotNone(logger)

    def test_initLog_invalid_config(self):
        """测试无效配置。"""
        config = CLogConfig()
        config._handler = "invalid"
        logger = initLog(config, "test_invalid")
        self.assertIsNone(logger)


class TestRotatingFileHandlerConfig(unittest.TestCase):
    """CRotatingFileHandlerConfig 测试类。"""

    def test_init(self):
        """测试初始化。"""
        config = CRotatingFileHandlerConfig(
            level="debug",
            filename="/tmp/test.log",
            maxBytes=1024 * 1024,
            backupCount=5,
        )
        self.assertEqual(config._maxbytes, 1024 * 1024)

    def test_checkConfig_invalid_maxbytes(self):
        """测试无效 maxBytes。"""
        config = CRotatingFileHandlerConfig(maxBytes=-1)
        self.assertFalse(config._checkConfig())


class TestTimedRotatingFileHandlerConfig(unittest.TestCase):
    """CTimedRotatingFileHandlerConfig 测试类。"""

    def test_init(self):
        """测试初始化。"""
        config = CTimedRotatingFileHandlerConfig(
            level="info", when="H", interval=1
        )
        self.assertEqual(config._when, "H")

    def test_checkConfig_invalid_when(self):
        """测试无效 when 参数。"""
        config = CTimedRotatingFileHandlerConfig(when="X")
        self.assertFalse(config._checkConfig())


class TestNatureTimedRotatingFileHandlerConfig(unittest.TestCase):
    """CNatureTimedRotatingFileHandlerConfig 测试类。"""

    def test_init(self):
        """测试初始化。"""
        config = CNatureTimedRotatingFileHandlerConfig(
            level="debug", when="D", interval=1
        )
        self.assertEqual(config._when, "D")

    def test_initHandler(self):
        """测试 Handler 初始化。"""
        config = CNatureTimedRotatingFileHandlerConfig(
            filename="/tmp/nature_test.log",
            when="H",
            interval=1,
        )
        handler = config.InitHandler()
        self.assertIsNotNone(handler)


if __name__ == "__main__":
    unittest.main()
