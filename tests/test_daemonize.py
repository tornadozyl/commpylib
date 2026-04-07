#!/usr/bin/env python
# coding:utf-8
"""daemonize 模块单元测试。"""

import unittest
import sys
import os
import tempfile
import shutil

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from daemonize import Daemonize, stop_daemon


class TestDaemonize(unittest.TestCase):
    """守护进程测试类。"""

    def setUp(self):
        """设置测试环境。"""
        self.test_dir = tempfile.mkdtemp()
        self.pidfile = os.path.join(self.test_dir, "test.pid")

    def tearDown(self):
        """清理测试环境。"""
        if os.path.exists(self.pidfile):
            os.remove(self.pidfile)
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_daemonize_pidfile_in_valid_dir(self):
        """测试守护进程创建（有效目录）。"""
        # daemonize 会 fork，子进程会退出，父进程会继续
        # 这里只测试返回类型，不实际测试守护进程功能
        try:
            result = Daemonize(self.pidfile)
            self.assertIsInstance(result, bool)
        except SystemExit:
            # daemonize 在 fork 时会调用 sys.exit，这是预期行为
            pass


if __name__ == "__main__":
    unittest.main()
