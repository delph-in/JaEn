#!/usr/bin/env python
#-*- coding: utf-8 -*-

###
### Script for representing a lexicon as a table
###

import sys, os

lex = open(sys.argv[1])

for line in lex:
    if ':=' in line:
        items = line.split()
        t = items[2]
    if 'ORTH' in line or 'STEM' in line:
        items = line.split()
        expr = ''
        for item in items:
            if item[-1] == ',':
                item = item[:-1]
            if '"' in item:
                item = item.replace('"','')
                expr = expr + item + ' '
        o = expr[:-1]
    if 'KEYREL.PRED' in line:
        items = line.split()
        for item in items:
            if '_rel' in item:
                if item[-1] == ',':
                    item = item[:-1]
                p = item
                print o + '\t' + p + '\t' + t

