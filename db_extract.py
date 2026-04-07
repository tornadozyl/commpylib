#!/usr/bin/env python
# coding:utf-8
"""数据库数据抽取模块。

提供从数据库表结构自动获取字段、批量插入/更新等功能。
"""

from typing import Any, Dict, List, Optional, Set, Tuple
from basicresult import CBasicResult
from commfunc import SetMultiDict

try:
    from simpledb import SimpleDB
except ImportError:
    SimpleDB = Any  # type: ignore


def GetFields(
    sdb: SimpleDB,
    dbname: str,
    tbname: str,
    fields_array: List[str],
    keys_array: List[str],
    exclude_fields_set: Optional[Set[str]] = None,
    exclude_keyfield_set: Optional[Set[str]] = None,
) -> CBasicResult:
    """获取表的字段结构，区分主键和普通字段。

    Args:
        sdb: 数据库连接对象
        dbname: 数据库名
        tbname: 表名
        fields_array: 输出参数，存储所有字段名
        keys_array: 输出参数，存储主键字段名
        exclude_fields_set: 需要排除的字段集合
        exclude_keyfield_set: 不作为主键的字段集合

    Returns:
        CBasicResult 结果对象
    """
    if exclude_fields_set is None:
        exclude_fields_set = set()
    if exclude_keyfield_set is None:
        exclude_keyfield_set = set()

    sql = f"DESC `{dbname}`.`{tbname}`"
    rst = sdb.execute(sql)
    if rst.resultcode != 0:
        return rst

    for row in rst._rst:
        field_name = row["Field"]
        is_primary_key = row["Key"] == "PRI"

        if is_primary_key:
            if field_name in exclude_fields_set:
                return CBasicResult(
                    -1,
                    f"GetFields: key field '{field_name}' should not be in exclude_fields_set",
                )
            if field_name in exclude_keyfield_set:
                # 过滤掉，不作为主键
                if field_name not in exclude_fields_set:
                    fields_array.append(field_name)
                continue
            keys_array.append(field_name)

        # 排除的字段不加入 fields_array
        if field_name in exclude_fields_set:
            continue
        fields_array.append(field_name)

    if len(fields_array) == 0:
        return CBasicResult(-1, "GetFields: fields_array is empty")
    if len(keys_array) == 0:
        return CBasicResult(-1, "GetFields: keys_array is empty")

    return CBasicResult()


def MakeSqlKeyFields(fields_array: List[str]) -> str:
    """生成 SQL 字段列表字符串（用于 SELECT/INSERT 的字段部分）。

    Args:
        fields_array: 字段名列表

    Returns:
        逗号分隔的字段字符串
    """
    if not fields_array:
        return ""
    return ",".join(f"`{field}`" for field in fields_array)


def MakeSqlValueFields(fields_array: List[Any]) -> str:
    """生成 SQL 值占位符字符串（用于 INSERT 的值部分）。

    Args:
        fields_array: 值列表

    Returns:
        逗号分隔的值字符串（字符串类型加引号）
    """
    if not fields_array:
        return ""

    values = []
    for field in fields_array:
        if isinstance(field, str):
            # 转义单引号
            escaped = field.replace("'", "''")
            values.append(f"'{escaped}'")
        elif field is None:
            values.append("NULL")
        else:
            values.append(str(field))

    return ",".join(values)


def MakeKey(
    line: Dict[str, Any], keys_array: List[str], keysep: str = "-"
) -> str:
    """根据键字段生成记录的唯一键。

    Args:
        line: 数据行字典
        keys_array: 键字段列表
        keysep: 键分隔符

    Returns:
        组合键字符串
    """
    key_parts = [str(line[k]) for k in keys_array if k in line]
    return keysep.join(key_parts)


def GetDBRecord(
    sdb: SimpleDB,
    dbname: str,
    tbname: str,
    records_dict: Dict[str, Dict[str, Any]],
    keys_array: Optional[List[str]] = None,
    exclude_fields_set: Optional[Set[str]] = None,
    where_condition: str = "",
    keysep: str = "-",
    exclude_keyfield_set: Optional[Set[str]] = None,
    log: Optional[Any] = None,
) -> CBasicResult:
    """获取数据库表记录，适合复杂的字段抽取场景。

    Args:
        sdb: 数据库连接对象
        dbname: 数据库名
        tbname: 表名
        records_dict: 输出参数，存储结果记录（以组合键为键）
        keys_array: 输出参数，主键字段列表
        exclude_fields_set: 需要排除的字段集合
        where_condition: WHERE 条件（不含 WHERE 关键字）
        keysep: 组合键分隔符
        exclude_keyfield_set: 不作为主键的字段集合
        log: 日志对象

    Returns:
        CBasicResult 结果对象
    """
    if keys_array is None:
        keys_array = []
    fields_array: List[str] = []

    rst = GetFields(
        sdb, dbname, tbname, fields_array, keys_array,
        exclude_fields_set or set(), exclude_keyfield_set or set()
    )
    if rst.resultcode != 0:
        return rst

    fields_str = MakeSqlKeyFields(fields_array)

    where_clause = ""
    if where_condition:
        if not where_condition.strip().upper().startswith("WHERE"):
            where_clause = f"WHERE {where_condition}"
        else:
            where_clause = where_condition

    sql = f"SELECT {fields_str} FROM `{dbname}`.`{tbname}` {where_clause}"

    if log is not None:
        log.info(f"GetDBRecord sql: {sql}")

    rst = sdb.execute(sql)
    if rst.resultcode != 0:
        return rst

    for row in rst._rst:
        key = MakeKey(row, keys_array, keysep)
        records_dict[key] = row

    return CBasicResult()


def GetSqlRecords(
    sdb: SimpleDB,
    sql: str,
    keys_multi_array: List[List[str]],
    records_dict: Dict[str, Any],
    keysep: str = "-",
    log: Optional[Any] = None,
) -> CBasicResult:
    """执行 SQL 并将结果存储为嵌套字典。

    支持多级嵌套字典，例如：
    {key1: {sub_key1: value1, sub_key2: value2}, key2: value2}

    Args:
        sdb: 数据库连接对象
        sql: SQL 语句
        keys_multi_array: 多级键字段列表，如 [[field1, field2], [field2]]
        records_dict: 输出参数，存储结果
        keysep: 组合键分隔符
        log: 日志对象

    Returns:
        CBasicResult 结果对象
    """
    rst = sdb.execute(sql)
    if rst.resultcode != 0:
        return rst

    for row in rst._rst:
        keys_array = []
        for fields in keys_multi_array:
            keys_array.append(MakeKey(row, fields, keysep))

        SetMultiDict(keys_array, row, records_dict)

    return CBasicResult()


def CommitDBRecord(
    sdb: SimpleDB,
    dbname: str,
    tbname: str,
    records_dict: Dict[str, Dict[str, Any]],
    fields_map: Optional[Dict[str, str]] = None,
    exclude_fields_set: Optional[Set[str]] = None,
    log: Optional[Any] = None,
) -> CBasicResult:
    """提交记录到数据库。

    Args:
        sdb: 数据库连接对象
        dbname: 数据库名
        tbname: 表名
        records_dict: 记录字典（值中的字段名需与表字段对应）
        fields_map: 字段映射，将记录字段映射到表字段
        exclude_fields_set: 需要排除的字段集合
        log: 日志对象

    Returns:
        CBasicResult 结果对象
    """
    if fields_map is None:
        fields_map = {}
    if exclude_fields_set is None:
        exclude_fields_set = set()

    fields_array: List[str] = []
    keys_array: List[str] = []

    rst = GetFields(sdb, dbname, tbname, fields_array, keys_array)
    if rst.resultcode != 0:
        return rst

    fields_set = set(fields_array)

    for record in records_dict.values():
        fields_key_array: List[str] = []
        fields_value_array: List[Any] = []

        for field_key, field_value in record.items():
            # 排除指定字段
            if field_key in exclude_fields_set:
                continue

            # 字段映射
            actual_key = fields_map.get(field_key, field_key)

            # 验证字段是否在表中存在
            if actual_key not in fields_set:
                errinfo = f"field '{actual_key}' not in table `{dbname}`.`{tbname}`"
                if log is not None:
                    log.error(f"CommitDBRecord failed: {errinfo}")
                return CBasicResult(-1, errinfo)

            fields_key_array.append(actual_key)
            fields_value_array.append(field_value)

        if len(fields_key_array) == 0:
            continue

        key_sql = MakeSqlKeyFields(fields_key_array)
        value_sql = MakeSqlValueFields(fields_value_array)
        sql = f"INSERT INTO `{dbname}`.`{tbname}`({key_sql}) VALUES({value_sql})"

        if log is not None:
            log.info(f"CommitDBRecord: {sql}")

        rst = sdb.execute(sql)
        if rst.resultcode != 0:
            if log is not None:
                log.error(f"CommitDBRecord failed, sql: {sql}, err: {rst}")
            return rst

    return CBasicResult()


def EnforceCommitDBRecord(
    sdb: SimpleDB,
    dbname: str,
    tbname: str,
    records_dict: Dict[str, Dict[str, Any]],
    fields_map: Optional[Dict[str, str]] = None,
    where_condition: str = "",
    exclude_fields_set: Optional[Set[str]] = None,
    log: Optional[Any] = None,
) -> CBasicResult:
    """强制提交记录（先删除后插入）。

    Args:
        sdb: 数据库连接对象
        dbname: 数据库名
        tbname: 表名
        records_dict: 记录字典
        fields_map: 字段映射
        where_condition: 删除条件（不含 WHERE）
        exclude_fields_set: 需要排除的字段集合
        log: 日志对象

    Returns:
        CBasicResult 结果对象
    """
    if where_condition:
        if not where_condition.strip().upper().startswith("WHERE"):
            where_clause = f"WHERE {where_condition}"
        else:
            where_clause = where_condition
        delsql = f"DELETE FROM `{dbname}`.`{tbname}` {where_clause}"
    else:
        delsql = f"DELETE FROM `{dbname}`.`{tbname}`"

    if log is not None:
        log.info(f"EnforceCommitDBRecord delete sql: {delsql}")

    rst = sdb.execute(delsql)
    if rst.resultcode != 0:
        if log is not None:
            log.error(f"EnforceCommitDBRecord delete failed, sql: {delsql}, err: {rst}")
        return rst

    return CommitDBRecord(
        sdb, dbname, tbname, records_dict, fields_map, exclude_fields_set, log
    )
