#!/usr/bin/env python
#-*- coding: utf-8 -*-

###
### Script for choosing the most probable phrase alignments
###
#
# phrase tables should be in:
# corpus/moses.mrs
# corpus/anymalign.mrs
#
# and are written to
# corpus/mrs-thin

import sys, os

corpus = sys.argv[1]
#pt = open('/home/petterha/jaentools/parmrs/moses.mrs.2012-01-06')

try:
    # This is the Moses phrase table
    pt = open(os.path.join(corpus, 'moses.mrs'))
except:
    pt = []
ptt = open(os.path.join(corpus, 'mrs-thin'),'w')
thindict = {}
for line in pt:
    items = line.split(' ||| ')
    source = items[0]
    target = items[1]
    targetlen = len(target.split())
    sourcelen = len(source.split())
    probs = items[2].split()
    prob = probs[2]
    try:
        prob = float(prob)
    except:
        prob == 0
    if sourcelen < 6 and targetlen < 6 and prob > 0.01:
        thindict[source + '\t' + target + '\tmos'] = prob

# This is the Anymalign phrase table
pt = open(os.path.join(corpus, 'anymalign.mrs'))
for line in pt:
    items = line.split('\t')
    source = items[0]
    target = items[1]
    targetlen = len(target.split())
    sourcelen = len(source.split())
    probs = items[3]
    pitems = probs.split(' ')
    try:
        prob = float(pitems[0])
    except:
        prob = 0
    freq = int(items[4][:-1])
    if freq > 1 and sourcelen < 6 and targetlen < 6 and prob > 0.01:
        thindict[source + '\t' + target + '\tany'] = prob


def sortfunc(x,y):
	return cmp(x[1],y[1])
items=thindict.items()
items.sort(sortfunc)
items.reverse()

for item in items:
    thinitems = item[0].split('\t')
    source = thinitems[0]
    target = thinitems[1]
    table = thinitems[2]
    prob = item[1]
    ptt.write(source + '\t' + target + '\t' + str(prob) + '\t' + table + '\n')
