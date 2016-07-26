#!/usr/bin/env python
#coding:UTF-8

from globalins_ex import GlobalIns
from basicresult import CBasicResult
from time import sleep
def test():
    rst = GlobalIns.setConfigPath("globalins_demo_config.ini")
    if 0 != rst._resultcode:
        return rst
    
    rst, logex = GlobalIns.getLogExInstance('logex_demo2')
    if 0 != rst._resultcode:
        return rst

    #test log rotate by size
    #for i in range(100):
    #	logex.debug("你好")

    #test log rotate by nature time
    while True:
        logex.info('你好')
        sleep(1)
        
        return CBasicResult()
    
if "__main__" == __name__:
    rst = test()
    print rst
