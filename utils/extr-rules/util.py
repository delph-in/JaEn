
def n_in(inlist):
    rel = []
    x = 0
    for pred in inlist:
        if '_n_' in pred or '_s_' in pred:
            rel.append(x)
        x = x+1
    return rel

def a_in(inlist):
    rel = []
    x = 0
    for pred in inlist:
        if ('_a_' in pred and not '_a_' in pred[:4]) or '_x_deg' in pred:
            rel.append(x)
        x = x+1
    return rel

def p_in(inlist):
    rel = []
    x = 0
    for pred in inlist:
        if '_p_' in pred:
            rel.append(x)
        x = x+1
    return rel

def q_in(inlist):
    rel = []
    x = 0
    for pred in inlist:
        if '_q_' in pred:
            rel.append(x)
        x = x+1
    return rel

def v_in(inlist):
    rel = []
    x = 0
    for pred in inlist:
        if '_v_' in pred:
            rel.append(x)
        x = x+1
    return rel

def striprel(inrel):            
    intype = inrel.replace('"','')
    if intype[0] == '_':
        intype = intype[1:]
    if intype.endswith('_rel'):
        intype = intype[:-4]
    intype = intype.replace('(','')
    intype = intype.replace(')','')
    intype = intype.replace('|','-')
    return intype

def rule_write(inlist,outlist,opt,supertype,translation,phrtab,src_prefix,alltrans,rulecheck,ruledict,transdict):
    blocktrans = 0
    if supertype[:-1] in set(['n+n_n']):
        srcs = inlist
        target = outlist[0]
        try:
            testrule = '"' + srcrel2lem[srcs[0]] + '" "' + srcrel2lem[srcs[1]] + '"\t' + '"' + tgtrel2lem[target] + '"'
            if transdir == 'jaen/':
                if not testrule in fulltrans:
                    blocktrans = 1
        except:
            blocktrans = 1
    trans = ''
    inlen = len(inlist)
    incopy = inlist
    outcopy = outlist
    sourcestr = ''
    for intrans in incopy:
        sourcestr = sourcestr + intrans + ' '
        intrans = '"' + src_prefix + intrans[1:]
        trans = trans + intrans + '&'
    trans = trans[:-1] + '\t'
    sourcestr = sourcestr[:-1]
    for outtrans in outcopy:
        trans = trans + outtrans + '&'
    trans = trans[:-1]
    rule_name = ''
    for pred in inlist:
        pred = striprel(pred)
        rule_name = rule_name + pred + '+'
    rule_name = rule_name[:-1] + '--'
    rule_name = rule_name.replace('_xxx','')
    for pred in outlist:
        pred = striprel(pred)
        pred = pred.replace('.','')
        rule_name = rule_name + pred + '+'
    if supertype == 'n+n_n-compound_':
        rule_name = rule_name[:-1] + '-2+'
    check = rule_name
    rule_name = rule_name[:-1] + '--'+phrtab+'-' + opt + 'mtr'
    rule_name = rule_name.replace('!','')
    inline = '[ INPUT.RELS < [ PRED '
    for pred in inlist:
        if pred[:1] == '"':
            pred = '"' + src_prefix + pred[1:]
            if 'xxx' in pred:
                pred = pred.replace('"' + src_prefix,'"~ja:')
                pred = pred.replace('_xxx_rel"','_"')
        inline = inline + pred + ' ] , [ PRED '
    inline = inline[:-7] + '... >,\n'
    outlist2 = outlist[:]
    if supertype == 'arg12+np_arg12+np_' and not '_make_v_1_rel' in outlist2[0]:
        outlist2[1] = outlist2[1] + ', ARG0 x & [ NUM sg ]'
    outline = '  OUTPUT.RELS < [ PRED '
    for pred in outlist2:
        outline = outline + pred + ' ] , [ PRED '
    outline = outline[:-12] + ' ] , ... > ].\n\n'
    if supertype == 'n_named_':
        inline = '[ INPUT.RELS < [ CARG ' + inlist[0] + ' ] , ... >,\n'
        outline = '  OUTPUT.RELS < [ CARG ' + outlist[0] + ' ] , ... > ].\n\n'
    line1 = rule_name + ' := ' + supertype + '' + opt + 'mtr &\n' 
    rule = line1 + inline + outline
    if not trans in alltrans and not 'NUM' in line1 and not check in rulecheck and blocktrans == 0: # and supertype in types
        ruledict[rule_name] = [rule,inlen]
        transdict[rule_name] = transdict.get( rule_name , [] ) + [ translation ]
        rulecheck.add(check)
    return [ruledict,transdict,rulecheck]
