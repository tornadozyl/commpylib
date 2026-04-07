#!/usr/bin/env python
# coding:utf-8
"""oss_utils 模块单元测试。"""

import unittest
import sys
import os
import tempfile
import shutil

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from oss_utils_alarm import SendAlarmMsg
from oss_utils_mail import SendStringMail


class TestSendAlarmMsg(unittest.TestCase):
    """SendAlarmMsg 测试类。"""

    def test_command_not_found(self):
        """测试命令不存在。"""
        rst = SendAlarmMsg("test", "test message")
        # 在没有 sendAlarmMsg 命令的环境下应该返回错误
        self.assertNotEqual(rst.resultcode, 0)


class TestSendStringMail(unittest.TestCase):
    """SendStringMail 测试类。"""

    def setUp(self):
        """设置测试环境。"""
        self.test_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.test_dir)

    def tearDown(self):
        """清理测试环境。"""
        os.chdir(self.original_cwd)
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_command_not_found(self):
        """测试命令不存在。"""
        rst = SendStringMail(
            sender="sender@test.com",
            receivers="receiver@test.com",
            cc="",
            subject="Test",
            mailstring="Test content",
        )
        # 在没有 sendmail2 命令的环境下应该返回错误
        self.assertNotEqual(rst.resultcode, 0)


if __name__ == "__main__":
    unittest.main()
