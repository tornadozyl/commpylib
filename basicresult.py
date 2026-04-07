#!/usr/bin/env python
# coding:utf-8
"""统一结果返回类模块。

提供 CBasicResult 基类，用于统一函数返回结果的格式。
"""

from typing import Any, Optional


class CBasicResult(object):
    """基础结果类，每个函数返回结果都应实现此类。

    Attributes:
        resultcode: 结果码，0 表示成功，非 0 表示失败
        resultinfo: 结果描述信息
        errorcode: 错误码
        errorinfo: 错误详细信息
        ref: 引用计数
    """

    def __init__(
        self,
        resultcode: int = 0,
        resultinfo: str = "ok",
        errorcode: int = 0,
        errorinfo: Any = "ok",
        ref: int = 1,
    ):
        self._resultcode = resultcode
        self._resultinfo = resultinfo
        self._errorcode = errorcode
        self._errorinfo = errorinfo
        self._ref = ref

    def setErr(
        self,
        resultcode: int = 0,
        resultinfo: str = "ok",
        errorcode: int = 0,
        errorinfo: Any = "ok",
    ) -> None:
        """添加错误信息。

        Args:
            resultcode: 结果码
            resultinfo: 结果描述
            errorcode: 错误码
            errorinfo: 错误详情
        """
        self._resultcode = resultcode
        self._resultinfo = resultinfo
        self._errorcode = errorcode
        self._errorinfo = errorinfo

    def incRef(self) -> None:
        """增加引用计数。"""
        self._ref += 1

    def decRef(self) -> None:
        """减少引用计数。"""
        self._ref -= 1

    @property
    def resultcode(self) -> int:
        """获取结果码。"""
        return self._resultcode

    @property
    def resultinfo(self) -> str:
        """获取结果信息。"""
        return self._resultinfo

    @property
    def errorcode(self) -> int:
        """获取错误码。"""
        return self._errorcode

    @property
    def errorinfo(self) -> Any:
        """获取错误信息。"""
        return self._errorinfo

    @property
    def ref(self) -> int:
        """获取引用计数。"""
        return self._ref

    def __str__(self) -> str:
        return (
            f"resultcode={self._resultcode}, "
            f"resultinfo={self._resultinfo}, "
            f"errorcode={self._errorcode}, "
            f"errorinfo={self._errorinfo}, "
            f"ref={self._ref}"
        )

    def is_ok(self) -> bool:
        """检查结果是否成功。

        Returns:
            True 表示成功，False 表示失败
        """
        return self._resultcode == 0


# ---- use demo ----
class CTestBasicResult(CBasicResult):
    """测试类，用于演示 CBasicResult 的继承使用。"""

    def __init__(self, value: str):
        super(CTestBasicResult, self).__init__()
        self._value = value

    def __str__(self) -> str:
        return f"value={self._value}, {super(CTestBasicResult, self).__str__()}"


def _TestBasicResult() -> CTestBasicResult:
    rst = CTestBasicResult("hello")
    rst.setErr(resultcode=-1, resultinfo="nonono")
    return rst


def _AddError(err: CBasicResult) -> CBasicResult:
    if not isinstance(err, CBasicResult):
        generr = CBasicResult()
        generr.setErr(-1, "not ok")
        return generr
    err.setErr(-1, "not ok")
    return err


def TestBasicResult() -> None:
    rst = _TestBasicResult()
    print(rst)
    err = CBasicResult()
    _AddError(err)
    print(err)


# ---- use demo end ----

if "__main__" == __name__:
    TestBasicResult()
