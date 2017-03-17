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

bitextpath = transdir + corpus + '-profiles/'

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
    path = bitextpath + corpus + '1'
    os.mkdir( path, 0775 ) ;
    os.mkdir( path + '/bitext', 0775 );
except:
    pass
orig = open(bitextpath + corpus + '1/bitext/original','w')
obje = open(bitextpath + corpus + '1/bitext/object','w')
#print len(endict.keys())
wordnr = 0
for key in outdictkeys:
    z = len(key)
    myid = '1'
    while z < 7:
        myid = myid + '0'
        z = z+1
    myid = myid + key + '0'
    wordnr = wordnr + len(outdict[key].split())
    if wordnr > average:
       #print y
       wordnr = 0
    if x < profilelength:
#        orig.write('[' + myid + '] ' + indict[key] + ';;MYID=' + key + '\n')
        orig.write(indict[key] + '\n')
#        obje.write('[' + myid + '] ' + outdict[key] + ';;MYID=' + key + '\n')
        obje.write(outdict[key] + '\n')
        x = x + 1
    if x == profilelength:
        y = y+1
        try:
            path = bitextpath + corpus + str(y)
            os.mkdir( path, 0775 ) ;
            os.mkdir( path + '/bitext', 0775 );
        except:
            pass
        orig = open(bitextpath + corpus + str(y) + '/bitext/original','w')
        obje = open(bitextpath + corpus + str(y) + '/bitext/object','w')
        x = 0

print y
