#!/usr/bin/env python
#-*- coding: utf-8 -*-

###
### Script for creating a parallel corpus of MRSs:
###  * indicating valency of verbs with suffixes to the relations
###  * marking nominalized verb relations with an 'nmz_' prefix
###  * marking proper name predicates with an 'nmd_' prefix
###

from __future__ import print_function

import os
import argparse

from delphin import itsdb
from delphin.mrs import simplemrs
from delphin.mrs.components import (
    var_re,
    Pred,
    ElementaryPredication as EP
)

parser = argparse.ArgumentParser(
    description='Create a parallel corpus of MRSs from profiles'
)
parser.add_argument(
    'source_profile', help='input source profile from which to extract'
)
parser.add_argument(
    'target_profile', help='input target profile from which to extract'
)
parser.add_argument(
    'source_preds', help='output file for linearized source predicates'
)
parser.add_argument(
    'target_preds', help='output file for linearized target predicates'
)
args = parser.parse_args()


def extract_valency(ep):
    valencies = []
    for role in ('ARG1', 'ARG2', 'ARG3', 'ARG4'):
        v = ep.args.get(role)
        if v is not None:
            m = var_re.match(v)
            if m is not None:
                n = role[-1]
                vs = m.group(1)
                if vs not in ('u', 'i', 'p'):
                    valencies.append(n + vs)
    return ''.join(valencies)


def pred_strings(prof):
    # need to join parse and result to get i-id to mrs mapping
    rows = prof.join('parse', 'result')
    cols = ('parse:i-id', 'result:result-id', 'result:mrs')
    for i_id, r_id, mrs in itsdb.select_rows(cols, rows):
        if r_id != '0':
            continue

        mrs = simplemrs.loads_one(mrs)

        preds = []
        valency = {}
        nmz_locs = set()

        # pre-scan
        for ep in mrs.eps():
            if ep.pred.short_form() == 'nominalization' and ep.cfrom != -1:
                nmz_locs.add(ep.lnk)
            valency[ep.nodeid] = extract_valency(ep)

        # extract and simplify predicates
        for ep in mrs.eps():
            pred = ep.pred.short_form()
            # skip omitted preds
            if pred == 'nominalization' or pred.endswith('unknown'):
                continue
            # combine named with CARG value
            if pred == 'named':
                pred = 'nmd_' + str(ep.carg or '')
            # normalize verbs
            if ep.pred.pos == 'v':
                # mark if nominalized
                if ep.lnk in nmz_locs:
                    pred = 'nmz_' + pred
                # add argument info
                pred += '@' + valency[ep.nodeid]
            preds.append(pred)

        yield (int(i_id), ' '.join(preds))


with open(args.source_preds, 'w') as src, \
     open(args.target_preds, 'w') as tgt:
    source_profile = itsdb.ItsdbProfile(args.source_profile)
    target_profile = itsdb.ItsdbProfile(args.target_profile)

    sourcemrs = dict(pred_strings(source_profile))
    targetmrs = dict(pred_strings(target_profile))

    # only print pred strings where they exist in both sides
    for id_ in set(sourcemrs).intersection(targetmrs):
        print(sourcemrs[id_], file=src)
        print(targetmrs[id_], file=tgt)
