#-*- coding: utf-8 -*-

# Script for selecting transfer rules relevant to batch files
# from the automatically derived transfer rules. The script reads the
# file(s) given as argument(s) and selects the transfer rules that could
# apply to the text in the batch file(s). To run the script, give the
# following command:
#
# $ python select-rule.py [OPTION...] WORKDIR ITEMFILE [ITEMFILE...]
#
# $ python select-rule.py ../ ~/logon/dfki/jacy/tsdb/skeletons/tanaka/tc-000/item ~/logon/dfki/jacy/tsdb/skeletons/tanaka/tc-001/item ~/logon/dfki/jacy/tsdb/skeletons/tanaka/tc-002/item
#
# WORKDIR is the working directory where the output files will be
# written to, and also where the default directories for data and Jacy
# are read from. You can create custom data sets by making a new working
# directory and copying or symlinking the relevant data to it.
#
# To install MeCab, try
#
# sudo apt-get install python-yaml
# sudo apt-get install mecab-ipadic-utf8 python-mecab
#
# pyDelphin must be installed or importable (see https://github.com/delph-in/pydelphin); try
#
# pip install pydelphin

import sys
import os; pjoin = os.path.join
from glob import glob
import re
import argparse

import MeCab
from delphin import tdl
from delphin.mrs.components import Pred
from collections import deque  # remove when pyDelphin issue #81 is resolved


# various constants (unlikely to change often)
JACY_ORTH_FEAT = 'STEM'
JACY_PRED_FEAT = 'SYNSEM.LKEYS.KEYREL.PRED'
ERG_ORTH_FEAT = 'ORTH'
ERG_PRED_FEAT = 'SYNSEM.LKEYS.KEYREL.PRED'

DEFAULT_PROB = 0.09

parser = argparse.ArgumentParser()

# parser.add_argument('logonroot', help='root path of the LOGON distribution')
parser.add_argument(
    'WORKDIR', metavar='DIR',
    help='working directory (e.g. for output files)'
)
parser.add_argument('items', nargs='+', help='[incr tsdb()] item files')
parser.add_argument('--threshold', type=float, default=0.1)
# parser.add_argument('--division', type=int, default=1)
parser.add_argument(
    '--data', metavar='DIR',
    help='data (mtr) file directory [default: $WORKDIR/data]'
)
parser.add_argument(
    '--jacy', metavar='DIR',
    help='Jacy grammar directory [default: $WORKDIR/jacy]')
# parser.add_argument(
#     '--erg', metavar='DIR',
#     help='ERG grammar directory [default: $WORKDIR/erg]'
# )

# parser.add_argument()

args = parser.parse_args()

workdir = args.WORKDIR
if not os.path.isdir(workdir):
    if os.path.isfile(workdir):
        sys.exit(
            'Working directory path is not a directory: {}'.format(workdir)
        )
    os.makedirs(workdir)

datadir = args.data if args.data else pjoin(workdir, 'data')
if not os.path.isdir(datadir):
    sys.exit('Data directory not found: {}'.format(datadir))

jacydir = args.jacy if args.jacy else pjoin(workdir, 'jacy')
if not os.path.isdir(datadir):
    sys.exit('Jacy directory not found: {}'.format(datadir))

# ergdir = args.erg if args.erg else pjoin(workdir, 'erg')
# if not os.path.isdir(datadir):
#     sys.exit('ERG directory not found: {}'.format(datadir))

threshold = args.threshold
# division = args.division

mecab = MeCab.Tagger('-Ochasen')


# Reading Edict

# MWG 2017-03-15 : removed as it seems unused
# unfulltrans = set([])
# for line in open(pjoin(datadir, 'edict.ja-en.txt')):
#     items = line.rstrip().split('\t')
#     ens = items[1].split()
#     if len(ens) == 2:
#         unfulltrans.add(items[0] + '\t' + ens[0])
#         unfulltrans.add(items[0] + '\t' + ens[1])


# Reading Jacy

jrel = {}
id2rel = {}
# rel2lem = {}

print >>sys.stderr, "Reading Jacy lexicon"
for entry in tdl.parse(open(pjoin(jacydir, 'lexicon.tdl'))):
    identifier = entry.identifier
    orths = [o.strip('"') for o in entry[JACY_ORTH_FEAT].values()]
    rel = entry.get(JACY_PRED_FEAT, default='')
    # rel2lem[rel] = ' '.join(orths)
    id2rel[identifier] = rel
    if rel:
        if isinstance(rel, tdl.TdlDefinition):
            rel = rel.supertypes[0]
        lemma = Pred.string_or_grammar_pred(rel).lemma
        for orth in orths:
            jrel[orth] = jrel.get(orth, []) + [lemma]

## FIXME
## Added 'saseru' to the dictonaries. The _saseru_v_cause_rel is not specified
## in the Jacy lexicon.
jrel['させる'] = jrel.get( 'させる' , [] ) + ["saseru"]
# rel2lem['"_saseru_v_cause_rel"'] = 'させる'
id2rel['saseru-intrans-end'] = '"_saseru_v_cause_rel"'
id2rel['saseru-trans-obj-end'] = '"_saseru_v_cause_rel"'
## End FIXME
jrelkeys = set(jrel.keys())

# Reading the ERG lexicon
# MWG 2017-03-15 : removed as it seems unused
# erel2lem = {}
# for entry in tdl.parse(open(pjoin(ergdir, 'lexicon.tdl'))):
#     # identifier = entry.identifier
#     orths = [o.strip('"') for o in entry[ERG_ORTH_FEAT].values()]
#     rel = entry.get(ERG_PRED_FEAT, default='')
#     if rel:
#         erel2lem[rel] = ' '.join(orths)

# Reading Jacy fullform
print >>sys.stderr, "Reading Jacy fullform"

fullform = open(pjoin(datadir, 'jacy-fullform.txt'))
for line in fullform:
    items = line.split()
    identifier = items[-2].lower()
    rulename = items[-1].upper()
    orths = items[:-2]
    if '-INFL-RULE' in rulename:
        try:
            rel = id2rel[identifier]
            lemma = Pred.string_or_grammar_pred(rel).lemma
            for orth in orths:
                jrel[orth] = jrel.get(orth, []) + [lemma]
        except KeyError:
            pass

jrelkeys = set(jrel.keys())

# Reading transfer rule files and writing three dictionaries:
#    ruledict[ruleid] = rule
#    r2l[ruleid] = lemmas
#    l2r[lemma] = ruleids
sgids = []
mweids = []
ruleset = set([])
r2l = {}
ruledict = {}
l2r = {}
ja2jaen = {}
jaen2rule = {}
jaen2prob = {}

def findrule(mtrfile):
    prob = 0.1
    rule = ''
    inrule = 0
    outrule = 0
    # MWG 2017-03-15 : div doesn't appear to be used; removing
    # div = division if mtrfile in ['lex-auto-jaen.single.phr-tab.mtr'] else 1
    for line in open(mtrfile):
        items = line.split(' ')
        if ';' in line:
            comment = line.lstrip('; ').split('\t')
            if len(comment) == 3:
                prob = float(comment[2]) # /div
            else:
                prob == DEFAULT_PROB

        if ':=' in line and len(items[0].split('--')) > 1:
            inrule = 1
            ruleid = items[0]
            ids = items[0].split('--')
            if len(ids) != 3:
                continue  # invalid entry?
            jpid, enid, _ = ids
            jaen = '%s--%s' % (jpid, enid)
            jps = jpid.split('+')
            jlist = []
            for jp in jpid.split('+'):
                j = re.sub(r'[0-9]', '', jp.split('_')[0])
                if j not in ['udef']:
                    jlist.append(j)
        if inrule == 1:
            rule = rule + line
        if '].' in line:
            ja2jaen[jpid] = ja2jaen.get(jpid,[]) + [jaen]
            inrule = 0
            r2l[jaen] = jlist
            ruledict[jaen] = rule
            jaen2prob[jaen] = jaen2prob.get(jaen,[]) + [prob]
            for lemma in jlist:
                l2r[lemma] = l2r.get(lemma , []) + [jaen]
            if '.mwe.' in mtrfile: # in ['lex-auto-jaen.mwe.mrs-tab.mtr','lex-auto-jaen.mwe.phr-tab.mtr']:
                mweids.append(jaen)
            else:
                sgids.append(jaen)
            rule = ''

# the following version won't work until pydelphin has a way to serialize
# TDL back to a string
#
# def findrule(mtrfile):
#     prob = 0.1
#     infile = open(pjoin(datadir, mtrfile))
#     rule = ''
#     inrule = 0
#     outrule = 0

#     div = division if mtrfile in ['lex-auto-jaen.single.phr-tab.mtr'] else 1

#     for line_no, event, data in tdl.lex(open(pjoin(datadir, mtrfile))):

#         if event == 'LINECOMMENT':
#             items = data.lstrip('; ').split('\t')
#             if len(items) == 3:
#                 prob = float(items[2])/div
#             else:
#                 prob == DEFAULT_PROB

#         elif event == 'TYPEDEF':
#             # see comment about deque at top
#             entry = tdl.parse_typedef(deque(data))
#             ids = entry.identifier.split('--')
#             if len(ids) != 3:
#                 continue  # invalid entry?
#             jpid, enid, _ = ids
#             jaen = '%s--%s' % (jpid, enid)
#             jlist = []
#             for jp in jpid.split('+'):
#                 j = re.sub(r'[0-9]', '', jp.split('_')[0])
#                 if j not in ['udef']:
#                     jlist.append(j)
#             ja2jaen[jpid] = ja2jaen.get(jpid, []) + [jaen]
#             r2l[jaen] = jlist
#             ruledict[jaen] = ...  # serialize rule here
#             jaen2prob[jaen] = jaen2prob.get(jaen, []) + [prob]
#             for lemma in jlist:
#                 l2r[lemma] = l2r.get(lemma, []) + [jaen]
#             if mtrfile in ['lex-auto-jaen.mwe.mrs-tab.mtr','lex-auto-jaen.mwe.phr-tab.mtr']:
#                 mweids.append(jaen)
#             else:
#                 sgids.append(jaen)

print >>sys.stderr, "Reading MTR files"

for mtrfile in glob(pjoin(datadir, '*.mtr')):
    findrule(mtrfile)

#findrule('enamdict.mtr')  # where is this file?

# Reading the batch file(s) and choosing rules that apply to the lemmas
# in each sentence

#print len(ja2jaen.keys())

# for ja in ja2jaen.keys():
#     ruleids = ja2jaen[ja]
#     for ruleid in set(ruleids):
#         print ruledict[ruleid]

print >>sys.stderr, "Select rules"

l2rkeys = set(l2r.keys())
for itemfile in args.items:
    print >>sys.stderr, ".. reading " + itemfile
    for line in open(itemfile):
        items = line.split('@')
        try:
            text = items[6]
        except:
            text = line
        relations = set([])
        for word in text.split():
            if word in jrelkeys:
                for reljap in jrel[word]:
                    relations.add(reljap)
            else:
                relations.add(word)
        node = mecab.parseToNode(text)
        while node:
            word = node.surface

            relations.add(word)
            lemma = node.feature.split(",")[6]
            if lemma in jrelkeys:
                for reljap in jrel[lemma]:
                    relations.add(reljap)
            else:
                relations.add(lemma)
            node = node.next
        relations_cp = relations
        for rel in relations:
            if rel in l2rkeys:
                for ruleid in l2r[rel]:
                    if not ruleid in ruleset and not '"sei_7' in ruleid:
                        writerule = 1
                        for lemma in r2l[ruleid]:
                            if not lemma in relations_cp:
                                writerule = 0
                        if writerule == 1:
                            ruleset.add(ruleid)


def sortfunc(x,y):
	return cmp(x[1],y[1])

jasgrels = set([])

def writerules(ids,outfilename):
    outfile = open(outfilename, 'w')
#    h = open(datadir + 'mwe.selected.mtr','w')
    x = 0
    idrest = {}
    rest = set([])
    ja2jaen = {}
    newids = set([])
    for key in set(ids):
        items = key.split('--')
        jap = items[0]
        if key in ruleset:
            ja2jaen[jap] = ja2jaen.get(jap,[]) + [[key,jaen2prob[key]]]
            newids.add(key)
    japs = ja2jaen.keys()
    newjaps = []
    jap2len = {}
    jap2translist = {}
    for jap in japs:
        japlen = len(jap.split('+'))
        jap2len[jap] = japlen
        trans2prob = {}
        for trans in ja2jaen[jap]:
            trans2prob[trans[0]] = trans[1][0]
        transprobs = trans2prob.items()
        transprobs.sort(sortfunc)
        transprobs.reverse()
        translist = []
        # Accepting rules with a probability of 0.1 and higher, and accepting rules of lower probability i) for single rules which is the most probable rule with the given japanese input, and ii) for the most probable mwe rule where at least one japanese predicate is not among the input predicates of the single rules (of probability higher than 0.1)
        if len(transprobs) == 1:
            if 'single' in outfilename:
                translist = [transprobs[0][0]]
                if float(transprobs[0][1]) > threshold:
                    jasgrels.add(transprobs[0][0].split('--')[0])
            if 'mwe' in outfilename:
                if float(transprobs[0][1]) < threshold:
                    jarels = transprobs[0][0].split('--')[0].split('+')
                    jablock = 1
                    for jarel in jarels:
                        if not jarel in jasgrels and not '_q' in jarel and not '_p' in jarel:
                            jablock = 0
                    if jablock == 0:
                        translist = [transprobs[0][0]]
                else:
                    translist = [transprobs[0][0]]
        else:
            translist = [transprobs[0][0]]
            topprob = float(transprobs[0][1])
            engcats = set([])
            if 'single' in outfilename:
                if float(transprobs[0][1]) > threshold:
                    jasgrels.add(transprobs[0][0].split('--')[0])
                engpred = transprobs[0][0].split('--')[1]
                if len(engpred.split('_')) > 1:
                    engcats = set([engpred.split('_')[1]])
            for transprob in transprobs[1:]:
                engpred = transprob[0].split('--')[1]
                if len(engpred.split('_')) > 1:
                    engcat = engpred.split('_')[1]
                else:
                    engcat = ''
                if float(transprob[1]) > threshold or float(transprob[1]) == topprob:
                    translist.append(transprob[0])
                    if 'single' in outfilename and float(transprob[1]) > threshold:
                        jasgrels.add(transprobs[0][0].split('--')[0])
                elif 'single' in outfilename and not engcat in engcats:
                    translist.append(transprob[0])
                    engcats.add(engcat)
        # for transprob in transprobs:
        #     translist.append(transprob[0])
        jap2translist[jap] = translist

    japlens=jap2len.items()
    japlens.sort(sortfunc)
    for item in japlens:
        jap = item[0]
        newjaps.append(jap)
    japs = newjaps
    japs.reverse()
    # Writing the rules
    for jap in japs:
        #print jap
        jaens = jap2translist[jap]
#        jaens = ja2jaen[jap]
        jaens2prob = {}
#        if len(jaens) > 4:
#            jaens = jaens[4:]
        for jaen in jaens:
            #print jaen
            problist = jaen2prob[jaen]
            problist.sort()
            problist.reverse()
            jaens2prob[jaen] = problist[0]
        jaenprobs=jaens2prob.items()
        jaenprobs.sort(sortfunc)
#        jaenprobs.reverse()
        y = 0
        # Selecting the 3 most probable transfer rules
#        if len(jaenprobs) > 3:
#            jaenprobs = jaenprobs[-3:]
        while len(jaenprobs) > 1:
            jaenprob = jaenprobs.pop()
            jaen = jaenprob[0]
            rule = ruledict[jaen]
            rule = rule.replace('_mtr','_omtr')
            rule = rule.replace('-mtr','-omtr')
            prob = jaenprob[1]
            outfile.write('; ' + str(prob) + '\n')
            outfile.write(rule + '\n')
            x = x+1
            y = x+1
        if len(jaenprobs) > 0:
#        try:

            rule = ruledict[jaenprobs[0][0]]
            ruleitems = rule.split()
            ruletype = ruleitems[2]
            ruleid = ruleitems[0]
            # MWG 2017-03-15 : removed as it seems unused
            # if ruletype in set(['n+n_n_mtr','n+n_n_omtr']):
            #     iditems = ruleid.split('--')
            #     jas = iditems[0].split('+')
            #     eng = iditems[1]
            #     try:
            #         testrule = '"' + rel2lem['"_' + jas[0] + '_rel"'] + '" "' + rel2lem['"_'+jas[1] +'_rel"'] + '"\t' + '"' + erel2lem['"_' + eng +'_rel"'] + '"'
            #         # print testrule
            #         if testrule in unfulltrans:
            #             pass
            #     except:
            #     #pass
            #         print rule
            # jap = items[0]
            # eng = items[1]
            # japs = jap.split('+')
            # engs = eng.split('+')

            rule = rule.replace('_omtr','_mtr')
            rule = rule.replace('-omtr','-mtr')
            prob = jaenprobs[0][1]
            outfile.write('; ' + str(prob) + '\n')
            outfile.write(rule + '\n')
            x = x+1
 #       except:
 #           print jaenprobs
    return x

# Opening output files

# Writing the rules

print >>sys.stderr, "Write files"

single_path = pjoin(workdir, 'single.selected.mtr')
single_count = writerules(sgids, single_path)
print 'Wrote %d rules into %s' % (single_count, single_path)

mwe_path =  pjoin(workdir, 'mwe.selected.mtr')
mwe_count = writerules(mweids, mwe_path)
print 'Wrote %d rules into %s' % (mwe_count, mwe_path)
