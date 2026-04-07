# commpylib

通用 Python 工具库

## 安装依赖

```bash
pip install -r requirements.txt
```

## 运行测试

```bash
pip install pytest
pytest tests/ -v
```

## 模块列表

| 模块 | 功能 |
|------|------|
| basicresult | 统一结果返回类 |
| commfunc | 通用函数（嵌套字典） |
| datefunc | 日期时间处理 |
| daemonize | 守护进程创建 |
| dynimport | 动态模块导入 |
| globalins | 全局单例（配置/日志/DB） |
| simplelog | 简单日志 |
| simplelogex | 扩展日志（支持轮转） |
| myloghandlers | 自定义日志 Handler |
| simpledb | MySQL 数据库封装 |
| db_extract | 数据库数据抽取 |
| parseline | 文本行解析 |
| oss_utils_alarm | 告警消息发送 |
| oss_utils_mail | 邮件发送 |
| oss_utils_rsync | rsync 文件同步 |

## Python 版本

需要 Python 3.7+
