#!/usr/bin/env python
# coding:utf-8
from basicresult import CBasicResult
import os


def SendAlarmMsg(to, msg):
    os.system("sendAlarmMsg %s '%s'" % (to, msg))


if "__main__" == __name__:
    SendAlarmMsg("hillzhang", "test")
