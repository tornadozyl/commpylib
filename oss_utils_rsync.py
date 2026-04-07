#!/usr/bin/env python
# coding:utf-8
"""Rsync 文件同步模块。

提供通过 rsync 进行文件拉取的功能。
"""

import os
from typing import Any, Dict, Optional, Tuple
from basicresult import CBasicResult

# 延迟导入避免循环依赖
# from globalins import GlobalIns


class CRsync(object):
    """Rsync 文件同步类。

    支持直接从配置拉取文件或使用配置节拉取文件。
    """

    _rsync_cfg: Dict[str, Dict[str, Any]] = {}

    def __init__(self) -> None:
        pass

    @staticmethod
    def Rsync_Pull(
        ip: str,
        port: int,
        username: str,
        src_path: str,
        src_name: str,
        dst_path: str,
        dst_name: str,
        force: bool = False,
        log: Optional[object] = None,
    ) -> Tuple[CBasicResult, Optional[str]]:
        """从远程 rsync 拉取文件。

        Args:
            ip: 远程主机 IP
            port: rsync 端口
            username: 用户名
            src_path: 源路径
            src_name: 源文件名
            dst_path: 目标路径
            dst_name: 目标文件名
            force: 是否强制覆盖
            log: 日志对象

        Returns:
            (结果对象，目标文件路径) 元组
        """
        srcfull = f"{src_path}/{src_name}"
        dstfull = f"{dst_path}/{dst_name}"

        # 检查目标文件是否已存在
        if os.path.exists(dstfull) and not force:
            return CBasicResult(), dstfull

        if os.path.exists(dstfull):
            os.remove(dstfull)

        cmd = f"rsync --port={port} {username}@{ip}::{srcfull} {dst_path}"

        if log is not None:
            log.info(cmd)

        print(cmd)

        try:
            ret = os.system(cmd)
            if ret != 0:
                return CBasicResult(-1, f"rsync failed with code {ret}", -1, cmd), dstfull

            # 检查源文件是否成功复制
            old_name = f"{dst_path}/{src_name}"
            if not os.path.exists(old_name):
                return CBasicResult(-1, "Source file not found after rsync", -1, cmd), dstfull

            # 如果源文件名和目标文件名不同，进行重命名
            if src_name != dst_name:
                os.rename(old_name, dstfull)

            return CBasicResult(), dstfull

        except Exception as e:
            return CBasicResult(-1, "rsync execution failed", -1, str(e)), dstfull

    @staticmethod
    def CfgRsync_Pull(
        sec_name: str,
        src_name: str,
        dst_name: str,
        force: bool = False,
        log: Optional[object] = None,
    ) -> Tuple[CBasicResult, Optional[str]]:
        """从配置节拉取文件。

        Args:
            sec_name: 配置文件节名称
            src_name: 源文件名
            dst_name: 目标文件名
            force: 是否强制覆盖
            log: 日志对象

        Returns:
            (结果对象，目标文件路径) 元组
        """
        # 需要首先初始化 GlobalIns
        from globalins import GlobalIns

        rst, cfg = GlobalIns.getCfgInstance()
        if rst.resultcode != 0:
            return rst, None

        if sec_name not in CRsync._rsync_cfg:
            rsync_cfg: Dict[str, Any] = {}
            try:
                rsync_cfg["ip"] = cfg.get(sec_name, "ip")
                rsync_cfg["port"] = cfg.get(sec_name, "port")
                rsync_cfg["user"] = cfg.get(sec_name, "user")
                rsync_cfg["src_path"] = cfg.get(sec_name, "src_path")
                rsync_cfg["dst_path"] = cfg.get(sec_name, "dst_path")

                CRsync._rsync_cfg[sec_name] = rsync_cfg

            except KeyError as e:
                return CBasicResult(-1, f"Config key not found: {e}", -1, str(e)), None

        rsync_cfg = CRsync._rsync_cfg[sec_name]

        return CRsync.Rsync_Pull(
            rsync_cfg["ip"],
            rsync_cfg["port"],
            rsync_cfg["user"],
            rsync_cfg["src_path"],
            src_name,
            rsync_cfg["dst_path"],
            dst_name,
            force,
            log,
        )


def demo() -> None:
    """演示 Rsync 功能。"""
    from globalins import GlobalIns

    GlobalIns.setConfigPath("globalins_demo_config.ini")

    rst, name = CRsync.CfgRsync_Pull(
        "rsync_demo", "t_acct_qqtest_20131218.01006", "qqtest", True
    )
    if rst.resultcode != 0:
        print(rst)
        return

    print(f"File synced to: {name}")


if "__main__" == "__main__":
    demo()
