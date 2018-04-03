#!/usr/bin/env python
# coding:utf-8
import datetime
import time
import calendar

def firstDayOfMonth(dt):
    return (dt+datetime.timedelta(days=-dt.day+1)).replace(hour=0,minute=0,second=0,microsecond=0)

def getcurrentmonth():
    return time.strftime('%Y-%m',time.localtime(time.time()))

def getcurrentdate():
    return time.strftime('%Y-%m-%d',time.localtime(time.time()))

def From_UnixTime(unix_timestamp):
    return time.strftime("%Y-%m-%d %X", time.localtime(unix_timestamp))

def FormatTime(year = 1900, month = 1, day = 1, hour = 0, miniute = 0, second = 0, timeformat = "%Y-%m-%d %X"):
    return datetime.datetime(year, month, day, hour, miniute, second).strftime(timeformat)

def getlastmonth(month):
    month_list = month.split('-')
    y = month_list[0]
    m = month_list[1]
    last_month = ""
    last_m = "%02d"%(int(m) - 1)
    
    if int(last_m) > 0:
        last_month  = "%s-%s"%(y,last_m)
    else:
        last_month = "%s-%s"%(int(y)-1,"12")
    return last_month

def getdaysofmonth(year,month):
    return calendar.monthrange(year,month)[1]

def getFirstDayOfMonth(month):
    '''month should be like 2013-01'''
    return "%s-01"%(month)

def getLastDayOfMonth(month):
    '''month should be like 2013-01'''
    fyear = int(month.split('-')[0])
    fmonth = int(month.split('-')[1])
    lastdayoflastmonth="%s-%d"%(month, getdaysofmonth(fyear, fmonth))
    return lastdayoflastmonth

def getdateyesterday(date):
    datelist = date.split('-')
    year = int(datelist[0])
    month = int(datelist[1])
    day = int(datelist[2])
    
    date_yesterday = datetime.datetime(year,month, day) - datetime.timedelta(1)
    str_date_yesterday=date_yesterday.strftime('%Y-%m-%d')
    return str_date_yesterday

def getdateyesterdayex(date):
    year = date[0:4]
    month = date[4:6]
    day = date[6:8] 
    
    date_yesterday = datetime.datetime(int(year),int(month), int(day)) - datetime.timedelta(1)
    str_date_yesterday=date_yesterday.strftime('%Y%m%d')
    return str_date_yesterday

def getdateafterday(date):
    datelist = date.split('-')
    year = int(datelist[0])
    month = int(datelist[1])
    day = int(datelist[2])

    date_yesterday = datetime.datetime(year,month, day) + datetime.timedelta(1)
    str_date_afterday =date_yesterday.strftime('%Y-%m-%d')
    return str_date_afterday

def getdaysbefore(diffdays):
    date = datetime.date.today() - datetime.timedelta(diffdays)
    return "%s"%date

def datefunc_demo():
    lastmonth = getlastmonth('2013-03')
    print lastmonth
    
    print getLastDayOfMonth('2012-02')
    
if "__main__" == __name__:
    datefunc_demo()
