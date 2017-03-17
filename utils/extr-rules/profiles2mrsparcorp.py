#!/usr/bin/env python
#-*- coding: utf-8 -*-

###
### Script for creating a parallel corpus of MRSs:
###  * indicating valency of verbs with suffixes to the relations
###  * marking nominalized verb relations with an 'nmz_' prefix
###  * marking proper name predicates with an 'nmd_' prefix
###

import sys

transdir = sys.argv[1]
corpus = sys.argv[2]
profilenr = int(sys.argv[3])

def sortfunc(x,y):
	return cmp(x[0],y[0])

def premrs(inlist,trigger,prefix,cat):
    trigged = 0
    for item in inlist:
        if trigger in item:
            trigger_charpos = item.split('<')[1][:-1]
            trigged = 1
    outlist = []
    if trigged == 1:
        for item in inlist:
            if '_rel' in item:
                charpos = item.split('<')[1][:-1]
            else:
                charpos = ''
            if charpos == trigger_charpos and not trigger in item and cat in item:
                item = prefix + item
            if not trigger in item:
                outlist.append(item)
    else:
        outlist = inlist
    return outlist

def readfile(infile,profnr):
    id2mrs = {}
#    infile = infile.split('\n')
    for line in infile:
        items = line.split('@')
	if len(items) > 1:
          if items[1] == '0':
            myid = str((profnr * 1500) + int(items[0]))
            #myid = items[0]
            mrs = items[13]
            mrsitems = mrs.split()
            cpos2rel = {}
            previtem = ''
            mrsstring = ''
            mrsitems = premrs(mrsitems,'nominalization_rel','nmz_','_v_')
#            for mrsitem in mrsitems:
	    copyitems = mrsitems[:]
	    while len(mrsitems) > 0:
                mrsitem = mrsitems.pop(0)
                if '_rel' in mrsitem and not 'unknown_rel' in mrsitem:
                    relitems = mrsitem.split('<')
                    rel = relitems[0]
                    if not rel == 'named_rel':
                        mrsstring = mrsstring + rel + ' '
		    if '_v_' in rel:
			    restitems = mrsitems[:]
			    mrsstring = mrsstring[:-1] + '@'
			    prevrest = rel
			    depth = 2
			    while depth > 1 and len(restitems) > 0:
				    rest = restitems.pop(0)
				    if rest == ']':
					    depth = depth - 1
				    if rest == '[':
					    depth = depth + 1
				    if not rest[0] in ['p','u','i'] and copyitems.count(rest) > 1:
					    if prevrest == 'ARG1:':
						    mrsstring = mrsstring+'1'+rest[0]
					    if prevrest == 'ARG2:':
						    mrsstring = mrsstring+'2'+rest[0]
					    if prevrest == 'ARG3:':
						    mrsstring = mrsstring+'3'+rest[0]
					    if prevrest == 'ARG4:':
						    mrsstring = mrsstring+'4'+rest[0]
				    prevrest = rest
			    mrsstring = mrsstring + ' '
                if previtem == 'CARG:':
                    if rel == 'named_rel':
                        mrsstring = mrsstring + 'nmd_' + mrsitem + ' '
                    else:
                        mrsstring = mrsstring + mrsitem + ' '
                previtem = mrsitem
            id2mrs[myid] = mrsstring[:-1]
    return id2mrs

source_mrsfile = open(transdir + corpus + '_mrs_source.txt','w')
target_mrsfile = open(transdir + corpus + '_mrs_target.txt','w')



targetmrs = {}
sourcemrs = {}

import tarfile
x = 0
while x < profilenr:
	x = x+1
	myint = ''
	y = 3 - len(str(x))
	while y > 0:
		myint = myint + '0'
		y = y-1
	source_result = open(transdir + corpus+'-profiles/' + corpus + str(x) + '/source/result')
	source_profile = readfile(source_result,x)
	sourcemrs.update(source_profile)


	target_result = open(transdir + corpus+'-profiles/' + corpus + str(x) + '/target/result')
	target_profile = readfile(target_result,x)
	targetmrs.update(target_profile)


sourcekeys = set(sourcemrs.keys())

for myid in targetmrs.keys():
    if myid in sourcekeys:
        target_mrsfile.write(targetmrs[myid] + '\n')
        source_mrsfile.write(sourcemrs[myid] + '\n')
