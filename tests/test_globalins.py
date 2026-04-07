#!/usr/bin/env python
# coding:utf-8
"""配置文件和全局单例测试。"""

import unittest
import sys
import os
import tempfile
import shutil

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestGlobalIns(unittest.TestCase):
    """GlobalIns 测试类。"""

    def setUp(self):
        """设置测试环境。"""
        self.test_dir = tempfile.mkdtemp()
        self.config_file = os.path.join(self.test_dir, "test.ini")

        # 创建测试配置文件
        with open(self.config_file, "w") as f:
            f.write("[log_demo1]\n")
            f.write("level=debug\n")
            f.write("logname=./logtest1\n")
            f.write("\n")
            f.write("[db_demo1]\n")
            f.write("ip=localhost\n")
            f.write("port=3306\n")
            f.write("user=test\n")
            f.write("passwd=test\n")

    def tearDown(self):
        """清理测试环境。"""
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_setConfigPath_valid(self):
        """测试设置有效配置路径。"""
        from globalins import GlobalIns
        rst = GlobalIns.setConfigPath(self.config_file)
        self.assertEqual(rst.resultcode, 0)

    def test_setConfigPath_invalid(self):
        """测试设置无效配置路径。"""
        from globalins import GlobalIns
        rst = GlobalIns.setConfigPath("/nonexistent/path.ini")
        self.assertNotEqual(rst.resultcode, 0)

    def test_getCfgInstance(self):
        """测试获取配置实例。"""
        from globalins import GlobalIns
        GlobalIns.setConfigPath(self.config_file)
        rst, cfg = GlobalIns.getCfgInstance()
        self.assertEqual(rst.resultcode, 0)
        self.assertIsNotNone(cfg)


if __name__ == "__main__":
    unittest.main()
