#!/usr/bin/env python
# coding:utf-8
"""dynimport 模块单元测试。"""

import unittest
import sys
import os
import tempfile
import shutil

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dynimport import dimport, SingleDImport


class TestDynImport(unittest.TestCase):
    """动态导入测试类。"""

    def setUp(self):
        """设置测试环境。"""
        self.test_dir = tempfile.mkdtemp()
        self.module_path = os.path.join(self.test_dir, "testmod.py")
        with open(self.module_path, "w") as f:
            f.write("value = 1\n")
        self.original_cwd = os.getcwd()
        os.chdir(self.test_dir)

    def tearDown(self):
        """清理测试环境。"""
        os.chdir(self.original_cwd)
        shutil.rmtree(self.test_dir)
        SingleDImport._dynimport_dict.clear()

    def test_import_module(self):
        """测试导入模块。"""
        rst, mod = dimport("testmod")
        self.assertEqual(rst.resultcode, 0)
        self.assertIsNotNone(mod)
        self.assertEqual(mod.value, 1)

    def test_import_not_exist(self):
        """测试导入不存在的模块。"""
        rst, mod = dimport("nonexistent")
        self.assertNotEqual(rst.resultcode, 0)
        self.assertIsNone(mod)

    def test_is_imported(self):
        """测试 is_imported 方法。"""
        self.assertFalse(SingleDImport.is_imported("testmod"))
        dimport("testmod")
        self.assertTrue(SingleDImport.is_imported("testmod"))

    def test_cache_usage(self):
        """测试缓存使用。"""
        rst1, mod1 = dimport("testmod")
        rst2, mod2 = dimport("testmod")
        self.assertIs(mod1, mod2)


if __name__ == "__main__":
    unittest.main()
