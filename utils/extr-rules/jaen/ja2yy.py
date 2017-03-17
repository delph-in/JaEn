#!/usr/bin/env python
#-*- coding: utf-8 -*-
#
# Script for producing input for cheap with the -yy -default-les
# turned on. It runs the text from the INPUT file through MeCab and
# represents it with tags in the following format:

# 南アフリカ産の茎のない多肉植物の属 >>
#
# (17, 0, 1, <0:15>, 1, "南アフリカ", 0, "null", "名詞-固有名詞-地域-国+n-n" 1.0000)
# (18, 1, 2, <16:19>, 1, "産", 0, "null", "名詞-接尾-地域+n-n" 1.0000)
# (19, 2, 3, <20:23>, 1, "の", 0, "null", "助詞-連体化+n-n" 1.0000) 
# (20, 3, 4, <24:27>, 1, "茎", 0, "null", "名詞-一般+n-n" 1.0000)
# (21, 4, 5, <28:31>, 1, "の", 0, "null", "助詞-格助詞-一般+n-n" 1.0000)
# (22, 5, 6, <32:38>, 1, "ない", 0, "null", "形容詞-自立+形容詞・アウオ段-基本形" 1.0000)
# (23, 6, 7, <39:51>, 1, "多肉植物", 0, "null", "名詞-一般+n-n" 1.0000)
# (24, 7, 8, <52:55>, 1, "の", 0, "null", "助詞-連体化+n-n" 1.0000)
# (25, 8, 9, <56:59>, 1, "属", 0, "null", "名詞-サ変接続+n-n" 1.0000) 
#
# To execute it, use:
#
# python INPUT > OUTPUT
#
# To install MeCab, try
#
# sudo apt-get install python-yaml
# sudo apt-get install mecab-ipadic-utf8 python-mecab
#
# The following cheap command will parse a file `INFILE' and output a
# profile in `OUTDIR':
#
# cheap -comment-passthrough -mrs -nsolutions=1 -results=1 -packing=15 -timeout=10 -yy -default-les -tsdbdum=OUTDIR -inputfile=INFILE ~/logon/dfki/jacy/japanese.grm &> log

import sys
import xml.etree.ElementTree as ET
import MeCab
import os

infile = open(sys.argv[1])

mecab = MeCab.Tagger('-Ochasen')
wordid = 0
for line in infile:
    charpos = 0
    wordpos = 0
    sent = ''
    node = mecab.parseToNode(line)
    while node:
        word = node.surface
        fields = node.feature.split(",")
        pos = fields[0]
        if not fields[1] == '*':
            pos = pos + '-' + fields[1]
        if not fields[2] == '*':
            pos = pos + '-' + fields[2]
        if not fields[3] == '*':
            pos = pos + '-' + fields[3]
        pos = pos + '+'
        if fields[4] == '*':
            pos = pos + 'n-' 
        else:
            pos = pos + fields[4] + '-'
        if fields[5] == '*':
            pos = pos + 'n'
        else:
            pos = pos + fields[5]
            
        sent = sent + word  + ' '
        node = node.next
        line = sent[1:-2]
        newwordpos = wordpos+1
        newcharpos = charpos + len(word)
        if not charpos == newcharpos and not word == '。':
            print '(' + str(wordid) +', ' + str(wordpos) + ', ' + str(newwordpos) + ', <' + str(charpos) + ':' + str(newcharpos) + '>, 1, "' + word + '", 0, "null", "' + pos + '" 1.0000)',
            wordid = wordid+1
            wordpos = newwordpos
            charpos = newcharpos + 1

    print '\n',
