#!/usr/bin/env python
# coding:utf-8

import os
import sys
import signal
import time
from commfunc import printerr


def Daemonize(pidfile=".pid"):
    '''use this function to shield signal and create a daemon proc'''
    try:
        pid = os.fork()
        if pid > 0:
            sys.exit(0)
    except OSError, e:
        sys.stderr.write("fork #1 failed: (%d) %s\n" % (e.errno, e.strerror))
        sys.exit(-1)

    # os.chdir("/")
    os.umask(0)
    os.setsid()
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
    except OSError, e:
        sys.stderr.write("fork #2 failed: (%d) %s\n" % (e.errno, e.strerror))
        sys.exit(-1)

    f = open(pidfile, 'w')
    f.write(str(os.getpid()))
    f.close()

    sys.stdout.flush()
    sys.stderr.flush()


if '__main__' == __name__:
    Daemonize()
