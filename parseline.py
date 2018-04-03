#!/usr/bin/env python
# coding:UTF-8

import sys
import os

import commfunc


def ParseTitle(title_line, sep=""):
    index = 0
    field_map = {}
    # cut the last '\n'
    if title_line.endswith(os.linesep):
        title_array = title_line[:-1].split("%s" % sep)
    else:
        title_array = title_line.split("%s" % sep)
    for field in title_array:
        field_map[field] = index
        index += 1

    if 0 == len(field_map):
        return None

    return field_map


def ParseTitleFile(titlefile):
    if not os.path.exists(titlefile):
        return None

    f = open(titlefile, 'r')
    fields_map = {}
    index = 0
    for l in f:
        l = l.strip()
        fields_map[l] = index
        index += 1

    f.close()

    if 0 == len(fields_map):
        return None

    return fields_map


def ParseLine(line, fields_map={}, sep=""):
    if len(line) == 0:
        return None
    if line[-1] == os.linesep:
        line_array = line[:-1].split(sep)
    else:
        line_array = line.split(sep)

    array_len = len(line_array)
    if len(line_array) == 0:
        commfunc.printerr("line:%s, sep:%s split failed" % (line, sep))
        return None

    if len(fields_map) == 0:
        commfunc.printerr("field_map empty")
        return None

    line_dict = {}
    for k, v in fields_map.items():
        if v >= array_len:
            commfunc.printerr('index out of range: line:%s, field:%s field index:%d' % (line, k, v))
            return None
        line_dict[k] = line_array[v]

    return line_dict


def ParseKVLine(line, fields_sep="&", kv_sep="="):
    fields_array = line.split(fields_sep)
    kv_dict = {}
    if line.endswith('&'):
        line = line[:-1]

    for field in fields_array:
        kv = field.split(kv_sep)
        k = kv[0]
        v = kv[1]
        kv_dict[k] = v
    return kv_dict


def demo(filename, sep):
    f = open(filename, 'r')
    title = f.readline()

    fields_map = ParseTitle(title, sep)
    if None == fields_map:
        commfunc.printerr("parsetitle failed")
        sys.exit(-1)

    for l in f:
        fields = ParseLine(l, fields_map, sep)
        if None == fields:
            commfunc.printerr("parseline fields failed")
            sys.exit(-1)

        print fields

    sys.exit(0)


if "__main__" == __name__:
    if len(sys.argv) != 2:
        commfunc.printerr("please use like %s full_filepath" % sys.argv[0])
        sys.exit(-1)
    filename = sys.argv[1]
    demo(filename, '\t')
