#!/usr/bin/env python
# coding:utf-8
"""告警消息发送模块。

提供发送告警消息的功能（依赖外部命令 sendAlarmMsg）。
"""

import os
import shutil
from typing import Optional
from basicresult import CBasicResult


def SendAlarmMsg(to: str, msg: str) -> CBasicResult:
    """发送告警消息。

    Args:
        to: 接收人
        msg: 消息内容

    Returns:
        CBasicResult 结果对象
    """
    # 检查命令是否存在
    cmd_path = shutil.which("sendAlarmMsg")
    if cmd_path is None:
        return CBasicResult(-1, "sendAlarmMsg command not found", -1, "command not exists")

    # 转义消息中的单引号
    safe_msg = msg.replace("'", "'\\''")
    cmd = f"sendAlarmMsg '{to}' '{safe_msg}'"

    try:
        ret = os.system(cmd)
        if ret != 0:
            return CBasicResult(-1, f"sendAlarmMsg failed with code {ret}", -1, cmd)
        return CBasicResult()
    except Exception as e:
        return CBasicResult(-1, "sendAlarmMsg execution failed", -1, str(e))


if "__main__" == "__main__":
    rst = SendAlarmMsg("hillzhang", "test")
    print(rst)
