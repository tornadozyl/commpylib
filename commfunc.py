#!/usr/bin/env python
# coding:utf-8
"""通用工具函数模块。

提供嵌套字典操作等通用工具函数。
"""

import sys
from typing import Any, Dict, List, Optional


def printerr(errstr: str) -> None:
    """打印错误信息到标准错误。

    Args:
        errstr: 错误信息字符串
    """
    print(errstr, file=sys.stderr)


def SetMultiDict(
    keys_array: List[str], value: Any, retdict: Dict[str, Any]
) -> None:
    """设置嵌套字典的值。

    Args:
        keys_array: 键路径数组，如 ['a', 'b', 'c'] 表示 retdict['a']['b']['c']
        value: 要设置的值
        retdict: 目标字典
    """
    deep = len(keys_array)
    key = keys_array[0]

    if deep > 1:
        if key not in retdict:
            retdict[key] = {}
        SetMultiDict(keys_array[1:], value, retdict[key])
    else:
        retdict[key] = value


def GetMultiDict(
    keys_array: List[str], retdict: Dict[str, Any]
) -> Optional[Any]:
    """获取嵌套字典的值。

    Args:
        keys_array: 键路径数组
        retdict: 源字典

    Returns:
        如果路径存在则返回对应的值，否则返回 None
    """
    deep = len(keys_array)
    key = keys_array[0]

    if deep > 1:
        if key not in retdict:
            return None
        return GetMultiDict(keys_array[1:], retdict[key])
    else:
        return retdict.get(key)


def demo() -> None:
    """演示 SetMultiDict 和 GetMultiDict 的用法。"""
    key1 = ["a", "b", "c"]
    value1 = "value1"
    key2 = ["b", "c"]
    value2 = "value2"
    retdict: Dict[str, Any] = {}

    SetMultiDict(key1, value1, retdict)
    SetMultiDict(key2, value2, retdict)
    print(retdict)

    SetMultiDict(key1, "changed value1", retdict)
    print(retdict)

    print(GetMultiDict(key1, retdict))
    print(GetMultiDict(["a", "b"], retdict))


if "__main__" == "__main__":
    demo()
