#!/usr/bin/env python
# coding:UTF-8

from basicresult import CBasicResult
from commfunc import SetMultiDict

def GetFields(sdb, dbname, tbname, fields_array, keys_array, exclude_fields_set = set([]), exclude_keyfield_set = set([])):
    sql = "desc %s.%s"%(dbname, tbname)
    rst = sdb.execute(sql)
    if 0 != rst._resultcode:
        return rst
    
    for l in rst._rst:
        if l['Key'] == 'PRI':
            if l['Field'] in exclude_fields_set:
                return CBasicResult(-1, "GetFields key field:%s shold not be in exclude_fields_set"%l['Field'])
            if l['Field'] in exclude_keyfield_set:#filter key
                if not l['Field'] in exclude_fields_set:
                    fields_array.append(l['Field'])
                continue
            keys_array.append(l['Field'])
            
        #exclude field should not in fields_array
        if l['Field'] in exclude_fields_set:
            continue
        fields_array.append(l['Field'])
        
    if len(fields_array) == 0:
        return CBasicResult(-1, "GetFields fields_array null")
    if len(keys_array) == 0:
        return CBasicResult(-1, "GetFields keys_array null")
    
    return CBasicResult()

def MakeSqlKeyFields(fields_array):
    fields_str = ""
    for field in fields_array:
        fields_str += '%s,'%field
    
    #cut the last ","
    return fields_str[:-1]

def MakeSqlValueFields(fields_array):
    fields_str = ""
    for field in fields_array:
        #for better performance, we need treat str type and the others in different ways
        if type(field) is str:
            fields_str += '"%s",'%field
        else:
            fields_str += '%s,'%field
    
    #cut the last ","  
    return fields_str[:-1]

def MakeKey(line, keys_array, keysep = "-"):
    key_str = ""
    for k in keys_array:
        key_str += str(line[k])
        key_str += keysep
    
    return key_str[:-1] 


def GetDBRecord(sdb, dbname, tbname, records_dict, keys_array = [], exclude_fields_set = set([]),\
                 where_condition = "", keysep="-", exclude_keyfield_set = set([]), log = None):
    '''GetDBRecord is suitable for complex db field extract'''
    fields_array = []
    keys_array = []
    rst = GetFields(sdb, dbname, tbname, fields_array, keys_array, exclude_fields_set, exclude_keyfield_set)
    if 0 != rst._resultcode:
        return rst
    
    fields_str = MakeSqlKeyFields(fields_array)
    
    sql = "select %s from %s.%s %s;"%(fields_str, dbname, tbname, where_condition)
    
    if not log == None:
        log.info("GetDBRecord sql:%s"%sql)
        
    rst = sdb.execute(sql)
    if 0 != rst._resultcode:
        return rst
    
    for l in rst._rst:
        key = MakeKey(l, keys_array, keysep)
        records_dict[key] = l
        
    return CBasicResult() 

def GetSqlRecords(sdb, sql, keys_mutiarray, records_dict, keysep="-", log = None):
    '''get sql records and add record to dict, this can have multi level dicts(each level have the same struct), 
    such as {key1:{sub_key1:value1, sub_key2:value2}, key2:value2}
    keys_mutiarray : [[field1, field2], [field2,]]'''
    
    rst = sdb.execute(sql)
    if 0 != rst._resultcode:
        return rst  
    for line in rst._rst:
        keys_array = []
        for fields in keys_mutiarray:
            keys_array.append(MakeKey(line, fields, keysep))
        
        SetMultiDict(keys_array, line, records_dict)
    return CBasicResult()


def CommitDBRecord(sdb, dbname, tbname, records_dict, fields_map = {}, exclude_fields_set = set([]), log = None):
    '''Commit dict records to db, the dict key name must be the same to the db table's field name'''
    fields_array = []
    keys_array = []
    rst = GetFields(sdb, dbname, tbname, fields_array, keys_array)
    if 0 != rst._resultcode:
        return rst 
    
    fields_set = set(fields_array)
    for record in records_dict.values():
        fields_key_array = []
        fields_value_array = []
        for field_key, field_value in record.items():
            #the fields in exclude_fields_set not need to insert to db
            if field_key in exclude_fields_set:
                continue
            
            #need map record field to table field
            if field_key in fields_map.keys():
                field_key = fields_map[field_key]
                
            #dict value's key must be in table fields
            if not field_key in fields_set:
                errinfo = "dict value field:%s not in %s.%s table fields"%(field_key, dbname, tbname)
                if not None == log:
                    log.error("CommitDBRecord failed:%s"%errinfo)
                    return CBasicResult(-1, errinfo)
            
            fields_key_array.append(field_key)
            fields_value_array.append(field_value)
        
        if len(fields_key_array) == 0:
            continue
        
        key_sql = MakeSqlKeyFields(fields_key_array)
        value_sql = MakeSqlValueFields(fields_value_array)
        sql = '''insert into %s.%s(%s) values(%s)'''%(dbname, tbname, key_sql, value_sql)
        
        if not None == log:
            log.info("CommitDBRecord commitsql:%s"%sql)
            rst = sdb.execute(sql)
            if 0 != rst._resultcode:
                if not None == log:
                    log.error("CommitDBRecord db execute failed,sql:%s, err:%s"%(sql, rst))
                return rst
         
    return CBasicResult()


def EnforceCommitDBRecord(sdb, dbname, tbname, records_dict, fields_map = {}, \
                          where_conditon="", exclude_fields_set = set([]), log = None):
    
    delsql = '''delete from %s.%s %s;'''%(dbname, tbname, where_conditon)
    if not None == log:
        log.info("EnforceCommitDBRecord del sql:%s"%delsql)
    
    rst = sdb.execute(delsql)
    if 0 != rst._resultcode:
        if not None == log:
            log.error("EnforceCommitDBRecord db execute failed,sql:%s, err:%s"%(delsql, rst))
            return rst
        
    return CommitDBRecord(sdb, dbname, tbname, records_dict, fields_map, exclude_fields_set, log)