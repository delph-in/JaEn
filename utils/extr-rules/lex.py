#!/usr/bin/env python
#-*- coding: utf-8 -*-

###
### Script for representing a lexicon as a table
###

import argparse

from delphin import tdl

parser = argparse.ArgumentParser(
    description='Convert a lexicon to a tab-separated table'
)
parser.add_argument('lexicon', type=open, help='path to a lexicon tdl file')

args = parser.parse_args()

for entry in tdl.parse(args.lexicon):

    if len(entry.supertypes) != 1:
        continue  # lexical entries should have only 1 supertype
    supertype = entry.supertypes[0]

    try:
        if 'ORTH' in entry:
            orth = ' '.join(o.strip('"') for o in entry['ORTH'].values())
        elif 'STEM' in entry:
            orth = ' '.join(o.strip('"') for o in entry['STEM'].values())
        else:
            continue  # no orth/stem value
    except AttributeError:
        continue

    if 'SYNSEM.LKEYS.KEYREL.PRED' in entry:
        pred = entry['SYNSEM.LKEYS.KEYREL.PRED']
        if hasattr(pred, 'supertypes'):
            pred = pred.supertypes[0]
    elif 'SYNSEM.LKEYS.ALTKEYREL.PRED' in entry:
        pred = entry['SYNSEM.LKEYS.ALTKEYREL.PRED']
        if hasattr(pred, 'supertypes'):
            pred = pred.supertypes[0]
    else:
        continue
    if not pred.strip('"').endswith('_rel'):
        continue

    print('\t'.join([orth, pred, supertype]))
