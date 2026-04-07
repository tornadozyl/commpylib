#!/usr/bin/env python
# coding:utf-8
"""文本行解析模块。

提供文件标题行解析、数据行解析、KV 格式解析等功能。
"""

import os
from typing import Dict, List, Optional


def ParseTitle(title_line: str, sep: str = "\t") -> Optional[Dict[str, int]]:
    """解析标题行，生成字段名到索引的映射。

    Args:
        title_line: 标题行字符串
        sep: 分隔符，默认为制表符

    Returns:
        字段名到索引的字典，失败返回 None
    """
    # 去除末尾换行符
    title_line = title_line.rstrip("\r\n")
    title_array = title_line.split(sep)

    if not title_array:
        return None

    field_map = {field: idx for idx, field in enumerate(title_array)}
    return field_map if field_map else None


def ParseTitleFile(titlefile: str) -> Optional[Dict[str, int]]:
    """从文件解析标题（每行一个字段名）。

    Args:
        titlefile: 标题文件路径

    Returns:
        字段名到索引的字典，失败返回 None
    """
    if not os.path.exists(titlefile):
        return None

    fields_map: Dict[str, int] = {}
    try:
        with open(titlefile, "r", encoding="utf-8") as f:
            for idx, line in enumerate(f):
                field = line.strip()
                if field:
                    fields_map[field] = idx
    except (IOError, OSError):
        return None

    return fields_map if fields_map else None


def ParseLine(
    line: str, fields_map: Dict[str, int], sep: str = "\t"
) -> Optional[Dict[str, str]]:
    """解析数据行，生成字段名到值的映射。

    Args:
        line: 数据行字符串
        fields_map: 字段名到索引的映射
        sep: 分隔符

    Returns:
        字段名到值的字典，失败返回 None
    """
    if not line:
        return None

    if not fields_map:
        return None

    # 去除末尾换行符
    line = line.rstrip("\r\n")
    line_array = line.split(sep)

    if not line_array:
        return None

    array_len = len(line_array)
    line_dict: Dict[str, str] = {}

    for field, idx in fields_map.items():
        if idx >= array_len:
            return None
        line_dict[field] = line_array[idx]

    return line_dict


def ParseKVLine(
    line: str, fields_sep: str = "&", kv_sep: str = "="
) -> Dict[str, str]:
    """解析 KV 格式行。

    Args:
        line: KV 格式字符串，如 "key1=value1&key2=value2"
        fields_sep: 字段分隔符
        kv_sep: KV 分隔符

    Returns:
        键值对字典
    """
    kv_dict: Dict[str, str] = {}

    if not line:
        return kv_dict

    # 去除末尾分隔符
    if line.endswith(fields_sep):
        line = line[:-1]

    fields_array = line.split(fields_sep)
    for field in fields_array:
        parts = field.split(kv_sep, 1)
        if len(parts) == 2:
            k, v = parts
            kv_dict[k] = v

    return kv_dict


def ParseFile(
    filename: str, sep: str = "\t", encoding: str = "utf-8"
) -> List[Dict[str, str]]:
    """解析整个文件（第一行为标题）。

    Args:
        filename: 文件路径
        sep: 分隔符
        encoding: 文件编码

    Returns:
        记录列表
    """
    records: List[Dict[str, str]] = []

    with open(filename, "r", encoding=encoding) as f:
        title_line = f.readline()
        fields_map = ParseTitle(title_line, sep)

        if fields_map is None:
            return records

        for line in f:
            record = ParseLine(line, fields_map, sep)
            if record is not None:
                records.append(record)

    return records


def demo(filename: str, sep: str = "\t") -> None:
    """演示文件解析功能。

    Args:
        filename: 文件路径
        sep: 分隔符
    """
    records = ParseFile(filename, sep)
    for record in records:
        print(record)


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <filename> [sep]")
        sys.exit(1)

    filename = sys.argv[1]
    sep = sys.argv[2] if len(sys.argv) > 2 else "\t"
    demo(filename, sep)
