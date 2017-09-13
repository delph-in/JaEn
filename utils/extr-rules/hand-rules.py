#!/usr/bin/env python
#-*- coding: utf-8 -*-

###
### Script for finding existing transfer rules
###

# python hand-rules.py $JAENDIR $LANGDIR > hand-rules
# where JAENDIR is the path to the JaEn transfer grammar (subdirectory
# `jaen/` at the top of this repository), and LANGDIR is the resources
# for extraction specific to this transfer grammar (subdirectory
# `jaen/` in this directory)

import sys, os

jaendir = sys.argv[1]
langdir = sys.argv[2]

trans_dict = {}

def findtrans(infile):
    inrel = 0
    outrel = 0
    inrels = []
    outrels = []
    difflist = []
    diff_dict = {}
    trans_in = []
    trans_out = []
    for line in infile:
        line = line.replace('[PRED','[ PRED')
        line = line.replace('"]','" ]')
        items = line.split(' ')
        if ':=' in line:
            trans_id = items[0]
            trans_id2 = trans_id
            trans_id2 = trans_id2.replace('--edict-omtr','')
            trans_id2 = trans_id2.replace('--edict-mtr','')
            trans_id2 = trans_id2.replace('--omtr','')
            trans_id2 = trans_id2.replace('-omtr','')
            trans_id2 = trans_id2.replace('--mtr','')
            trans_id2 = trans_id2.replace('-mtr','')

        if 'INPUT' in line or 'JA' in line:
            for item in items:
                item = item.replace(',','')
                item = item.replace('\n','')
                if item == '<':
                    inrel = 1
                if inrel == 1 and '_rel' in item:
                    inrels.append(item)
                if item == '>' or '>' in item:
                    inrel = 0
                    trans_in = inrels
        elif inrel == 1:
            for item in items:
                item = item.replace(',','')
                item = item.replace('\n','')
                if '_rel' in item:
                    inrels.append(item)
                if item == '>' or '>' in item:
                    inrel = 0
                    trans_in = inrels
        elif 'OUTPUT' in line or 'EN' in line:
            for item in items:
                item = item.replace(',','')
                item = item.replace('\n','')
                if item == '<':
                    outrel = 1
                if outrel == 1 and '_rel' in item:
                    outrels.append(item)
                if item == '>' or '>' in item:
                    outrel = 0
                    trans_out = outrels
                    trans_dict[trans_id] = [trans_in,trans_out]
                    diffstring = ''
                    mtrstring = ''
                    for rel in inrels:
                        diffstring = diffstring + rel + '@'
                        if "ja:" in rel:
                            mtrstring = mtrstring + rel + '&'
                    diffstring = diffstring + ' >>> '
                    if len(mtrstring) > 1:
                        mtrstring = mtrstring[:-1] + '--'
                    out_check = 0
                    for rel in outrels:
                        diffstring = diffstring + rel + '@'
                        if len(mtrstring) > 1:
                            mtrstring = mtrstring + rel + '&'
                            out_check = 1
                    difflist.append(diffstring)
                    if len(mtrstring) > 5 and out_check == 1:
                        diff_dict[trans_id] = mtrstring[:-1]
                    inrels = []
                    outrels = []
        elif outrel == 1:
            for item in items:
                item = item.replace(',','')
                item = item.replace('\n','')
                if '_rel' in item:
                    outrels.append(item)
                if item == '>' or '>' in item:
                    outrel = 0
                    trans_out = outrels
                    trans_dict[trans_id] = [trans_in,trans_out]
                    diffstring = ''
                    mtrstring = ''
                    for rel in inrels:
                        diffstring = diffstring + rel + '@'
                        if "ja:" in rel:
                            mtrstring = mtrstring + rel + '&'
                    diffstring = diffstring + ' >>> '
                    if len(mtrstring) > 0:
                        mtrstring = mtrstring[:-1] + '--'
                    out_check =0
                    for rel in outrels:
                        diffstring = diffstring + rel + '@'
                        if len(mtrstring) > 0:
                            mtrstring = mtrstring + rel + '&'
                            out_check = 1
                    difflist.append(diffstring)
                    if len(mtrstring) > 5 and out_check == 1:
                        diff_dict[trans_id] = mtrstring[:-1]
                    inrels = []
                    outrels = []
    return([difflist,diff_dict])

difflist = []
mtr_paths = open(os.path.join(langdir, 'mtr-file-paths'))
for line in mtr_paths:
    filepath = os.path.join(jaendir, line.rstrip('\n'))
    mtr_file = open(filepath)
    difflist.extend(findtrans(mtr_file)[0])

diffdict = {}

mtr_paths = open(os.path.join(langdir, 'mtr-file-paths'))
for line in mtr_paths:
    filepath = os.path.join(jaendir, line.rstrip('\n'))
    mtr_file = open(filepath)
    diffdict.update(findtrans(mtr_file)[1])

mtr_id_set = set(diffdict.keys())

def findpred(instr):
    if '&' in instr:
        items = instr.split('&')
        newstr = ''
        for item in items:
            pred_items = item.split('_')
            try:
                pred = pred_items[1]
                newstr = newstr + pred + '&'
            except:
                outstr = instr
        outstr = newstr[:-1]
    else:
        pred_items = instr.split('_')
        try:
            outstr = pred_items[1]
        except:
            outstr = instr
    return outstr

for key in diffdict.keys():
    trans = diffdict[key]
    items = trans.split('--')
    source = items[0]
    target = items[1]
    print source + '\t',
    print target
