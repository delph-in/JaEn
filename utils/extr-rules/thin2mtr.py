#!/usr/bin/env python
#-*- coding: utf-8 -*-

###
### Script for extracting transfer rules from mrs phrase tables
###

from __future__ import print_function

import sys
import os

corpus = sys.argv[1]
transdir = sys.argv[2]
pathbase = os.path.join(transdir, corpus)  # e.g. jaen/mini
singlepath = os.path.join(transdir, corpus, corpus + '.single.mtr')
mwepath = os.path.join(transdir, corpus, corpus + '.mwe.mtr')

# Prefix added to source language predicates in order to avoid loops
# in the tranfer grammar. Change the value to '' if the source
# language is not Japanese
src_prefix = 'ja:'

# All template types
types = set(['adjective_','noun_','adj_v_','arg1_v_','arg12_v_','arg123_v_','n+n_adj+n_','n+n_n+n_','n_named_','pp-adj_','pp_pp_','arg12+np_arg12+np_','n+adj-adj-','p+n+arg12_arg12_','pp+arg12_arg12_','pp+np_np+pp_','arg1+pp_arg1+pp_','n_n+n_','n_adj+n_','n+n_n_','preposition_','adj_pp_'])

threshold = 0.1
mwe_thresh = 0.01

# Reading the source language lexicon
srclex = open(os.path.join(transdir, corpus, 'source-lex.tab'))
srcrel2lem = {}
for line in srclex:
    items = line.split('\t')
    lemma = items[0]
    rel = items[1]
    srcrel2lem[rel] = lemma

# Reading the target language lexicon
tgtlex = open(os.path.join(transdir, corpus, 'target-lex.tab'))
tgtrel2lem = {}
for line in tgtlex:
    items = line.split('\t')
    lemma = items[0]
    rel = items[1]
    tgtrel2lem[rel] = lemma

# Reading the existing transfer rules
transfer = open(os.path.join(transdir, corpus, 'hand-rules'))
transferset = set([])
enset = set([])
alltrans = set([])
allsource = set([])
for line in transfer:
    alltrans.add(line[:-1])
    items = line.split('\t')
    source = items[0]
    target = items[1][:-1]
    source = source.replace(src_prefix,'')
    sourcestr = source.replace('&',' ')
    transferset.add(sourcestr)
    enset.add(target)

# Function for looping through alignment files and checking the
# alignments for matches against templates. The function that contains
# the templates, is given in 'jaen/templates.py'
rulecheck = set([])
transdict = {}
ruledict = {}
freqs = {}
trans2freq = {}
trans2prob = {}
def readfile(phrtab):
    infile = open(os.path.join(pathbase, 'mrs-thin'))
    for line in infile:
        items = line.split('\t')
        sourcestr = items[0]
        targetstr = items[1]
        prob = float(items[2])
        freq = 1
        newtargetstr = ''
        for string in targetstr.split():
            newstr = string.split('@')[0]
            newtargetstr = newtargetstr + newstr + ' '
        newsourcestr = sourcestr.split('@')[0]
        newtargetstr = newtargetstr[:-1]
        trans = newsourcestr + ' >> ' + newtargetstr
        trans = trans.replace('nmd_','')
        if phrtab == 'any':
            transferset.add(sourcestr)
        trans2freq[trans] = freq
        trans2prob[trans] = trans2prob.get(trans, []) + [prob]
        source = sourcestr.split()
        newsource = []
        for s in source:
            if '_q_' in s and not s[-1]=='"':
                s = '"' + s + '"'
            newsource.append(s)
        source = newsource
        target = targetstr.split()
        opt = ''
        if phrtab == items[3][:-1]:
            from jaen.templates import templates
            templates(source, target, prob, threshold, opt, trans, phrtab, src_prefix, alltrans,rulecheck,ruledict,transdict,mwe_thresh)

readfile('any')
readfile('mos') 

def sortfunc(x,y):
	return cmp(x[1][1],y[1][1])
items=ruledict.items()
items.sort(sortfunc)
items.reverse()

rulekeys = []
for item in items:
    rulekeys.append(item[0])


source_count = {}
for trans in ruledict.keys():
    source = trans.split(' := ')[0].split('--')[0]
    source_count[source] = source_count.get( source , 0 ) + 1

transset = set([])
evaldict = {}

# Printing the transfer rules
a = open(singlepath, 'w')
b = open(mwepath, 'w')
newtrans2prob = {}
x = 0
y = 0
for key in rulekeys:
    rulevalue = ruledict[key]
    rule = rulevalue[0]
    inlen = rulevalue[1]
    sourcerule = rule.split('--')[0]
    opt = ''
    if source_count[sourcerule] > 1:
        opt = 'o'
        source_count[sourcerule] = source_count[sourcerule] - 1
    if opt == 'o':
        rule = rule.replace('_mtr','_omtr')
    supertype = rule.split('\n')[0].split()[2]
    prob = 0
    freq = 0
    for translation in set(transdict[key]):
      try:
        if trans2freq[translation] > freq:
            freq = trans2freq[translation]
            if float(freq) == 0.1:
                freq = 0.5
        if max(trans2prob[translation]) > prob:
            prob = max(trans2prob[translation])
        if inlen == 1:
            a.write('; ' + translation)
            a.write('\t' + str(trans2freq[translation]) + '\t' + str(max(trans2prob[translation])) +'\n')
        elif inlen > 1:
            b.write('; ' + translation)
            b.write('\t' + str(trans2freq[translation]) + '\t' + str(max(trans2prob[translation])) +'\n')
        newtrans2prob[translation] = max(trans2prob[translation])
        transset.add(translation)
        evaldict[translation] = evaldict.get(translation, []) + [key]
      except:
          print(translation)
      if inlen == 1:
          a.write(rule)
          x = x+1
      elif inlen > 1:
          b.write(rule)
          y = y+1

print('Wrote {} rule(s) in \'{}\''.format(str(x), singlepath))
print('Wrote {} rule(s) in \'{}\''.format(str(y), mwepath))
