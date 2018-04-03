#!/usr/bin/env python
# coding:utf-8
from logging.handlers import TimedRotatingFileHandler
import time

TIMEZONE_MODIFY = 60 * 60 * 8


class NatureTimedRotatingFileHandler(TimedRotatingFileHandler, object):
    def __init__(self, filename, when='h', interval=1, backupCount=0, encoding=None, delay=False, utc=False):
        super(NatureTimedRotatingFileHandler, self).__init__(filename, when, interval, backupCount, encoding, delay,
                                                             utc)
        lastnaturetime = self.getLastNatureTime()
        self.rolloverAt = self.computeRollover(lastnaturetime)
        # print "rollat %d, currtime %d, last naturetime %d"%(self.rolloverAt, int(time.time()), lastnaturetime)

    def getLastNatureTime(self):
        now_unixtime = int(time.time())

        if self.when == 'S':
            return now_unixtime
        elif self.when == 'M':
            return now_unixtime - now_unixtime % 60
        elif self.when == 'H':
            return now_unixtime - now_unixtime % (60 * 60)
        elif self.when == 'D' or self.when == 'MIDNIGHT':
            return now_unixtime - now_unixtime % (60 * 60 * 24) - TIMEZONE_MODIFY
        else:
            raise ValueError("Invalid rollover interval specified: %s" % self.when)

    def computeRollover(self, currentTime):
        currentTime = self.getLastNatureTime()
        return super(NatureTimedRotatingFileHandler, self).computeRollover(currentTime)
