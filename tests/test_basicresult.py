#!/usr/bin/env python
# coding:utf-8
"""basicresult 模块单元测试。"""

import unittest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from basicresult import CBasicResult


class TestCBasicResult(unittest.TestCase):
    """CBasicResult 测试类。"""

    def test_default_init(self):
        """测试默认初始化。"""
        rst = CBasicResult()
        self.assertEqual(rst.resultcode, 0)
        self.assertEqual(rst.resultinfo, "ok")
        self.assertEqual(rst.errorcode, 0)
        self.assertEqual(rst.ref, 1)

    def test_custom_init(self):
        """测试自定义初始化。"""
        rst = CBasicResult(
            resultcode=-1,
            resultinfo="error",
            errorcode=100,
            errorinfo="detail error",
            ref=5,
        )
        self.assertEqual(rst.resultcode, -1)
        self.assertEqual(rst.resultinfo, "error")
        self.assertEqual(rst.errorcode, 100)
        self.assertEqual(rst.errorinfo, "detail error")
        self.assertEqual(rst.ref, 5)

    def test_setErr(self):
        """测试设置错误信息。"""
        rst = CBasicResult()
        rst.setErr(resultcode=-1, resultinfo="failed", errorcode=50, errorinfo="bad")
        self.assertEqual(rst.resultcode, -1)
        self.assertEqual(rst.resultinfo, "failed")
        self.assertEqual(rst.errorcode, 50)
        self.assertEqual(rst.errorinfo, "bad")

    def test_incRef(self):
        """测试增加引用计数。"""
        rst = CBasicResult()
        initial_ref = rst.ref
        rst.incRef()
        self.assertEqual(rst.ref, initial_ref + 1)

    def test_decRef(self):
        """测试减少引用计数。"""
        rst = CBasicResult()
        initial_ref = rst.ref
        rst.decRef()
        self.assertEqual(rst.ref, initial_ref - 1)

    def test_is_ok(self):
        """测试 is_ok 方法。"""
        rst_ok = CBasicResult()
        rst_err = CBasicResult(resultcode=-1)
        self.assertTrue(rst_ok.is_ok())
        self.assertFalse(rst_err.is_ok())

    def test_str(self):
        """测试字符串表示。"""
        rst = CBasicResult(resultcode=0, resultinfo="success")
        rst_str = str(rst)
        self.assertIn("resultcode=0", rst_str)
        self.assertIn("resultinfo=success", rst_str)


if __name__ == "__main__":
    unittest.main()
