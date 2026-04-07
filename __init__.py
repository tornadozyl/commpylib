#!/usr/bin/env python
# coding:utf-8
"""commpylib - 通用 Python 工具库。

常用工具模块：
- basicresult: 统一结果返回类
- commfunc: 通用函数（嵌套字典）
- datefunc: 日期时间处理
- daemonize: 守护进程创建
- dynimport: 动态模块导入
- globalins: 全局单例（配置/日志/DB）
- simplelog / simplelogex: 日志系统
- simpledb: MySQL 数据库封装
- db_extract: 数据库数据抽取
- parseline: 文本行解析
- oss_utils_*: OSS 工具（告警/邮件/rsync）
"""

__version__ = "1.0.0"

__all__ = [
    "basicresult",
    "commfunc",
    "datefunc",
    "daemonize",
    "dynimport",
    "globalins",
    "simplelog",
    "simplelogex",
    "simpledb",
    "db_extract",
    "parseline",
    "oss_utils_alarm",
    "oss_utils_mail",
    "oss_utils_rsync",
]
