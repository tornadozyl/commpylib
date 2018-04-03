#!/usr/bin/env python
# coding:utf-8

import sys


def printerr(errstr):
    print>> sys.stderr, errstr


def SetMultiDict(keys_array, value, retdict):
    deep = len(keys_array)
    key = keys_array[0]
    # print key, deep
    if deep > 1:
        if key in retdict.keys():
            SetMultiDict(keys_array[1:], value, retdict[key])
        else:
            retdict[key] = {}
            SetMultiDict(keys_array[1:], value, retdict[key])
    else:
        retdict[key] = value


def GetMultiDict(keys_array, retdict):
    deep = len(keys_array)
    key = keys_array[0]
    if deep > 1:
        if key in retdict.keys():
            return GetMultiDict(keys_array[1:], retdict[key])
        else:
            return None
    else:
        if key in retdict.keys():
            return retdict[key]
        else:
            return None


def demo():
    key1 = ['a', 'b', 'c']
    value1 = "value1"
    key2 = ['b', 'c']
    value2 = "value2"
    retdict = {}
    SetMultiDict(key1, value1, retdict)
    SetMultiDict(key2, value2, retdict)
    print retdict
    SetMultiDict(key1, "changed value1", retdict)
    print retdict
    print GetMultiDict(key1, retdict)
    print GetMultiDict(['a', 'b'], retdict)


if "__main__" == __name__:
    demo()
