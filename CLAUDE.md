# CLAUDE.md

## 项目概述

commpylib 是一个通用 Python 工具库，提供数据库、日志、文件解析等常用功能。

## 运行测试

```bash
cd /Users/zhangyunlong/MyProj/commpylib
pip install pytest
pytest tests/ -v
```

## 模块结构

- `basicresult.py` - 统一结果返回类
- `commfunc.py` - 通用工具函数
- `datefunc.py` - 日期时间函数
- `daemonize.py` - 守护进程
- `dynimport.py` - 动态导入
- `globalins.py` - 全局单例
- `simplelog.py` / `simplelogex.py` / `myloghandlers.py` - 日志系统
- `simpledb.py` - 数据库封装
- `db_extract.py` - 数据抽取
- `parseline.py` - 文本解析
- `oss_utils_*.py` - OSS 工具（告警/邮件/rsync）

## 依赖

- pymysql (或 MySQLdb)
- pytest (测试)
