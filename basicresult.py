#!/usr/bin/env python
# coding:utf-8

class CBasicResult(object):
    '''This is a basic result class, every function returning result should implement this class'''

    def __init__(self, resultcode=0, resultinfo="ok", errorcode=0, errorinfo="ok", ref=1):
        self._resultcode = resultcode
        self._resultinfo = resultinfo
        self._errorcode = errorcode
        self._errorinfo = errorinfo
        self._ref = ref

    def setErr(self, resultcode=0, resultinfo="ok", errorcode=0, errorinfo="ok"):
        "use this function to add err info, if the result is ok, you may not use this function but the default value"
        self._resultcode = resultcode
        self._resultinfo = resultinfo
        self._errorcode = errorcode
        self._errorinfo = errorinfo

    def incRef(self):
        self._ref = self._ref + 1

    def decRef(self):
        self._ref = self._ref - 1

    def __str__(self):
        return "resultcode:%d, resultinfo:%s, errorcode:%d, errorinfo:%s, ref:%d" % (self._resultcode,
                                                                                     self._resultinfo, self._errorcode,
                                                                                     self._errorinfo, self._ref)


# ---- use demo ----
class CTestBasicResult(CBasicResult):
    '''this is a test class'''

    def __init__(self, value):
        super(CTestBasicResult, self).__init__()
        self._value = value

    def __str__(self):
        return "value:%s, %s" % (self._value, super(CTestBasicResult, self).__str__())


def _TestBasicResult():
    rst = CTestBasicResult("hello")
    rst.setErr(resultcode=-1, resultinfo="%s" % "nonono")

    return rst


def _AddError(err):
    if not isinstance(err, CBasicResult):
        generr = CBasicResult()
        generr.setErr(-1, "not ok")
        return err

    return err.setErr(-1, "not ok")


def TestBasicResult():
    rst = _TestBasicResult()
    print rst
    err = CBasicResult()
    _AddError(err)
    print err


# ---- use demo end ----

if '__main__' == __name__:
    TestBasicResult()
