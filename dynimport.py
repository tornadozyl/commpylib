#!/usr/bin/env python
# coding:utf-8
"""动态模块导入模块。

支持根据模块名字符串动态导入模块，并检测文件修改后重新加载。
"""

import os
import copy
from typing import Any, Dict, Optional, Tuple
from importlib import import_module, reload
import importlib.util

from basicresult import CBasicResult

TMP_MODULE_INFO = {
    "name": None,
    "module": None,
    "valid": False,
    "fstat": None,
}  # type: Dict[str, Any]


class SingleDImport(object):
    """单例动态导入类。

    维护已导入模块的缓存，支持文件修改检测。
    """

    _dynimport_dict: Dict[str, Dict[str, Any]] = {}

    def __init__(self) -> None:
        pass

    @staticmethod
    def is_imported(name: str) -> bool:
        """检查模块是否已导入。

        Args:
            name: 模块名

        Returns:
            True 表示已导入，False 表示未导入
        """
        return name in SingleDImport._dynimport_dict

    @staticmethod
    def is_modified(name: str) -> bool:
        """检查模块文件是否被修改。

        Args:
            name: 模块名

        Returns:
            True 表示已修改，False 表示未修改
        """
        filename = "%s.py" % name.replace(".", "/")
        if name not in SingleDImport._dynimport_dict:
            return True

        mfinfo = SingleDImport._dynimport_dict[name]["fstat"]
        try:
            statinfo = os.stat(filename)
            return (
                statinfo.st_ctime != mfinfo.st_ctime
                or statinfo.st_mtime != mfinfo.st_mtime
            )
        except OSError:
            return True

    @staticmethod
    def add_imported_module(
        modulename: str,
    ) -> Tuple[CBasicResult, Optional[Any]]:
        """添加已导入的模块到缓存。

        Args:
            modulename: 模块名（不含.py 后缀）

        Returns:
            (结果对象，模块对象) 元组
        """
        filename = "%s.py" % modulename.replace(".", "/")
        if not os.path.exists(filename):
            return (
                CBasicResult(-1, f"{filename} not exist", -1, f"{filename} not exist"),
                None,
            )

        try:
            statinfo = os.stat(filename)

            # 使用 importlib 动态导入
            spec = importlib.util.spec_from_file_location(modulename, filename)
            if spec is None or spec.loader is None:
                return (
                    CBasicResult(-1, f"Cannot load spec for {filename}", -1, "spec load failed"),
                    None,
                )

            m = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(m)

            minfo = copy.deepcopy(TMP_MODULE_INFO)
            minfo["name"] = modulename
            minfo["module"] = m
            minfo["valid"] = True
            minfo["fstat"] = statinfo
            SingleDImport._dynimport_dict[minfo["name"]] = minfo
            return CBasicResult(), m

        except Exception as e:
            return CBasicResult(-1, "add_imported_module failed", -1, str(e)), None

    @staticmethod
    def get_module(name: str) -> Tuple[CBasicResult, Optional[Any]]:
        """获取模块，如果已导入且未修改则使用缓存版本。

        Args:
            name: 模块名

        Returns:
            (结果对象，模块对象) 元组
        """
        if SingleDImport.is_imported(name) and not SingleDImport.is_modified(name):
            return CBasicResult(), SingleDImport._dynimport_dict[name]["module"]
        else:
            return SingleDImport.add_imported_module(name)


def dimport(modulename: str) -> Tuple[CBasicResult, Optional[Any]]:
    """动态导入模块的接口函数。

    Args:
        modulename: 模块名（不含.py 后缀）

    Returns:
        (结果对象，模块对象) 元组
    """
    return SingleDImport.get_module(modulename)


if __name__ == "__main__":
    for i in range(2):
        rst, m = dimport("dymodule.test")
        if rst.resultcode != 0:
            print(rst)
            import sys

            sys.exit(-1)
        m.test()
