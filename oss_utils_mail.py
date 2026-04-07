#!/usr/bin/env python
# coding:utf-8
"""邮件发送模块。

提供发送邮件的功能（依赖外部命令 sendmail2）。
"""

import os
import shutil
from typing import Optional
from basicresult import CBasicResult


def SendFileMail(
    sender: str,
    receivers: str,
    cc: str,
    subject: str,
    mailfile: str,
    accessoryfile: str = "",
    htmloption: bool = False,
    passwd: Optional[str] = None,
    log: Optional[object] = None,
) -> CBasicResult:
    """发送文件邮件。

    Args:
        sender: 发件人
        receivers: 收件人
        cc: 抄送人
        subject: 邮件主题
        mailfile: 邮件内容文件
        accessoryfile: 附件文件
        htmloption: 是否为 HTML 邮件
        passwd: 密码
        log: 日志对象

    Returns:
        CBasicResult 结果对象
    """
    # 检查命令是否存在
    cmd_path = shutil.which("sendmail2")
    if cmd_path is None:
        return CBasicResult(-1, "sendmail2 command not found", -1, "command not exists")

    cmd = f"sendmail2 '{sender}' '{receivers}' '{cc}' '{subject}' {mailfile}"

    if accessoryfile:
        cmd = f"{cmd} {accessoryfile}"

    if htmloption:
        cmd = f"{cmd} --html"

    if passwd:
        cmd = f"{cmd} --pass={passwd}"

    if log is not None:
        log.info(cmd)
    else:
        print(cmd)

    try:
        ret = os.system(cmd)
        if ret != 0:
            return CBasicResult(-1, f"SendMail failed with code {ret}", -1, cmd)
        return CBasicResult()
    except Exception as e:
        return CBasicResult(-1, "SendMail execution failed", -1, str(e))


def SendStringMail(
    sender: str,
    receivers: str,
    cc: str,
    subject: str,
    mailstring: str,
    accessoryfile: str = "",
    htmloption: bool = False,
    passwd: Optional[str] = None,
    log: Optional[object] = None,
) -> CBasicResult:
    """发送字符串邮件。

    Args:
        sender: 发件人
        receivers: 收件人
        cc: 抄送人
        subject: 邮件主题
        mailstring: 邮件内容字符串
        accessoryfile: 附件文件
        htmloption: 是否为 HTML 邮件
        passwd: 密码
        log: 日志对象

    Returns:
        CBasicResult 结果对象
    """
    mailfile = ".CSendMail.tmpfile"
    try:
        with open(mailfile, "w", encoding="utf-8") as f:
            f.write(mailstring)
    except IOError as e:
        return CBasicResult(-1, "Write temp file failed", -1, str(e))

    return SendFileMail(
        sender, receivers, cc, subject, mailfile, accessoryfile, htmloption, passwd, log
    )


if "__main__" == "__main__":
    rst = SendStringMail(
        "sender@test.com", "receiver@test.com", "", "test", "this is a test"
    )
    print(rst)
