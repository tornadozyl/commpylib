#!/usr/bin/env python
# coding:utf-8
"""守护进程创建模块。

提供将当前进程转换为守护进程的功能。
"""

import os
import sys
import signal
import time
from typing import Optional


def Daemonize(pidfile: str = ".pid", logger: Optional[object] = None) -> bool:
    """将当前进程转换为守护进程。

    使用双 fork 方式创建守护进程，屏蔽常见信号，并写入 PID 文件。

    Args:
        pidfile: PID 文件路径
        logger: 可选的日志对象

    Returns:
        True 表示成功，False 表示失败
    """

    def log_info(msg: str) -> None:
        if logger is not None:
            logger.info(msg)
        else:
            print(msg)

    def log_error(msg: str) -> None:
        if logger is not None:
            logger.error(msg)
        else:
            print(msg, file=sys.stderr)

    try:
        pid = os.fork()
        if pid > 0:
            sys.exit(0)
    except OSError as e:
        log_error(f"fork #1 failed: ({e.errno}) {e.strerror}")
        return False

    # 创建新会话
    os.chdir("/")
    os.umask(0)
    os.setsid()

    # 屏蔽信号
    signal.signal(signal.SIGINT, signal.SIG_IGN)
    signal.signal(signal.SIGHUP, signal.SIG_IGN)
    signal.signal(signal.SIGQUIT, signal.SIG_IGN)
    signal.signal(signal.SIGPIPE, signal.SIG_IGN)
    signal.signal(signal.SIGTTOU, signal.SIG_IGN)
    signal.signal(signal.SIGTTIN, signal.SIG_IGN)
    signal.signal(signal.SIGCHLD, signal.SIG_IGN)
    signal.signal(signal.SIGTERM, signal.SIG_IGN)

    try:
        pid = os.fork()
        if pid > 0:
            sys.exit(0)
    except OSError as e:
        log_error(f"fork #2 failed: ({e.errno}) {e.strerror}")
        return False

    # 写入 PID 文件
    try:
        with open(pidfile, "w") as f:
            f.write(str(os.getpid()))
        log_info(f"Daemon started with pid={os.getpid()}, pidfile={pidfile}")
    except IOError as e:
        log_error(f"Failed to write pidfile: {e}")
        return False

    # 刷新标准输出
    sys.stdout.flush()
    sys.stderr.flush()

    return True


def stop_daemon(pidfile: str) -> bool:
    """停止守护进程。

    Args:
        pidfile: PID 文件路径

    Returns:
        True 表示成功停止，False 表示失败
    """
    if not os.path.exists(pidfile):
        print(f"PID file {pidfile} not found", file=sys.stderr)
        return False

    try:
        with open(pidfile, "r") as f:
            pid = int(f.read().strip())
        os.kill(pid, signal.SIGTERM)
        os.remove(pidfile)
        return True
    except (IOError, ValueError, OSError) as e:
        print(f"Failed to stop daemon: {e}", file=sys.stderr)
        return False


if __name__ == "__main__":
    # 示例：创建守护进程
    if Daemonize("/tmp/test.pid"):
        while True:
            time.sleep(1)
