#!/usr/bin/env python
#-*- coding: utf-8 -*-

###
### Script for dividing a corpus consisting of two big files into
### profiles of 1500 items each
###

import os, sys

profilelength = int(sys.argv[1])
corpus = sys.argv[2]
infile = open(sys.argv[3])
outfile = open(sys.argv[4])
transdir = sys.argv[5]

bitextpath = os.path.join(transdir, corpus)  # e.g. jaen/mini
pathbase = os.path.join(bitextpath, corpus)  # e.g. jaen/mini/mini{1,2,...}

if not os.path.exists(bitextpath):
   os.makedirs(bitextpath)


indict = {}
x = 1
for line in infile:
   indict[str(x)] = line[:-1]
   x = x+1

outdictkeys = []
outdict = {}
x = 1
wordnr = 0
for line in outfile:
   if not line[:4] == 'EntL':
      outdict[str(x)] = line[:-1]
      outdictkeys.append(str(x))
      wordnr = wordnr + len(line.split())
   x= x+1

average = wordnr/6

x = 0
y = 1
try:
    os.mkdir( pathbase + '1', 0775 ) ;
    os.mkdir( os.path.join(pathbase + '1', 'bitext'), 0775 );
except:
    pass

orig = open(os.path.join(pathbase + '1', 'bitext', 'original'), 'w')
obje = open(os.path.join(pathbase + '1', 'bitext', 'object'), 'w')
#print len(endict.keys())
wordnr = 0
for key in outdictkeys:
    wordnr = wordnr + len(outdict[key].split())
    if wordnr > average:
       wordnr = 0
    if x < profilelength:
        orig.write(indict[key] + '\n')
        obje.write(outdict[key] + '\n')
        x = x + 1
    if x == profilelength:
        y = y+1
        try:
            path = pathbase + str(y)
            os.mkdir( path, 0775 ) ;
            os.mkdir( os.path.join(path, 'bitext'), 0775 );
        except:
            pass
        orig = open(os.path.join(path, 'bitext', 'original'), 'w')
        obje = open(os.path.join(path, 'bitext', 'object'), 'w')
        x = 0

print y
