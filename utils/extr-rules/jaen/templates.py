from util import *

#################
### TEMPLATES ###
#################

def templates(source, target, prob, threshold, opt, trans, phrtab,src_prefix,alltrans,rulecheck,ruledict,transdict,mwe_thresh):
    lightverbs = set(['"_use_v_1_rel"','"_make_v_1_rel"','"_take_v_1_rel"'])    
    src = source[0].split('@')[0]
    tgt = target[0].split('@')[0]
    printrule = False
    if len(source) == 1 and len(target) == 1 and float(prob) > threshold:
        if n_in(source) == [0] and n_in(target) == [0] and not '@' in source[0] and not 'nmd' in target[0]:
            supertype = 'noun_'
            printrule = True
            
        elif a_in(source) == [0] and a_in(target) == [0]:
            supertype = 'adjective_'
            printrule = True

        elif 'nmd_' in target[0] and 'nmd_' in source[0]:
            target[0] = target[0].replace('nmd_','')
            source[0] = source[0].replace('nmd_','')
            supertype = 'n_named_'
            printrule = True

        elif p_in(source) == [0] and p_in(target) == [0] and not '@' in source[0] and not 'nmd' in target[0] and not '_no_p' in source[0]:
            supertype = 'preposition_'
            printrule = True

        elif a_in(source) == [0] and v_in(target) == [0] and not src[:3] == 'nmz' and not tgt[:3] == 'nmz' and target[0].split('@')[1] == '1x':
            supertype = 'adj_v_'
            source = [src]
            target = [tgt]
            printrule = True

        elif v_in(source) == [0] and v_in(target) == [0] and not src[:3] == 'nmz' and not tgt[:3] == 'nmz':
            srcvalence = source[0].split('@')[1]
            evalence = target[0].split('@')[1]
            trans = src + ' >> ' + tgt
            source = [src]
            target = [tgt]
            if srcvalence == evalence and '1' in srcvalence and '2' in srcvalence and '3' in srcvalence:
                supertype = 'arg123_v_'
                printrule = True

            elif srcvalence == evalence and '1' in srcvalence and '2' in srcvalence:
                supertype = 'arg12_v_'
                printrule = True

            elif srcvalence == evalence and '1' in srcvalence:
                supertype = 'arg1_v_'
                printrule = True

    if len(source) == 2 and len(target) == 1 and float(prob) > mwe_thresh:
        if n_in(source) == [0,1] and n_in(target) == [0] and not '@' in source[0] and not 'nmd' in target[0]:
            supertype = 'n+n_n_'
            printrule = True

    if len(source) == 1 and len(target) == 2:
        if n_in(source) == [0] and n_in(target) == [0,1] and not '@' in source[0] and not 'nmd' in target[0] and float(prob) > 0.16:
            supertype = 'n_n+n_'
            printrule = True

        if n_in(source) == [0] and a_in(target) == [0] and n_in(target) == [1] and not '@' in source[0] and not 'nmd' in target[1] and float(prob) > 0.13:
            supertype = 'n_adj+n_'
            printrule = True

    if len(source) == 2 and len(target) == 2 and float(prob) > mwe_thresh:
        if n_in(source) == [0,1] and n_in(target) == [0,1]:
            supertype = 'n+n_n+n_'
            printrule = True

        if n_in(source) == [0,1] and a_in(target) == [0] and n_in(target) == [1]:
            supertype = 'n+n_adj+n_'
            printrule = True

        if a_in(source) == [0] and n_in(source) == [1] and a_in(target) == [0] and n_in(target) == [1]:
            supertype = 'adj+n_adj+n_'
            printrule = True

    if len(source) == 4 and len(target) == 4:
        if n_in(source) == [1] and p_in(source) == [2] and source[3][-3:] == '@1x' and target[0][-3:] == '@1x' and p_in(target) == [1] and n_in(target) == [3] and not 'naru_v' in source[3] and not '_lie_v_2' in target[0]:
            if '_in_p' in target[1] or '_on_p' in target[1] or '_at_p' in target[1]:
                target[1] = 'unspec_loc_rel'
            supertype = 'arg1+pp_arg1+pp_'
            source = [source[3][:-3],source[2]]
            target = [target[0][:-3],target[1]]
            printrule = True

    if len(source) == 3 and len(target) == 3 and float(prob) > 0.01:
        if q_in(source) == [0] and n_in(source) == [1] and p_in(source) == [2] and p_in(target) == [0] and q_in(target) == [1] and n_in(target) == [2] and not 'NN_u' in target[2]:# and target[0] == '_by_p_means_rel' and source[2] == '"_de_p_rel"':
            supertype = 'pp_pp_'
            if '_no_p' in source[2]:
                target[0] = 'compound_or_prep_rel'
            source = [source[2],source[0],source[1]]
            printrule = True

    if len(source) == 5 and len(target) == 5 and q_in(source) == [0,3] and n_in(source) == [1,4] and p_in(source) == [2] and q_in(target) == [0,3] and n_in(target) == [1,4] and p_in(target) == [2]:
        if source[2] == '"_no_p_rel"' and target[2] == '_of_p_rel':
            supertype = 'pp+np_np+pp_'
            printrule = True

    if len(source) == 3 and len(target) == 1 and float(prob) > mwe_thresh:
        if q_in(source) == [0] and n_in(source) == [1] and p_in(source)==[2] and a_in(target) == [0]:
            supertype = 'pp-adj_'
            source = [source[2],source[0],source[1]]
            printrule = True
        
    if len(source) == 1 and len(target) == 3 and float(prob) > threshold:
        if  a_in(source) == [0] and p_in(target)==[0] and q_in(target) == [1] and n_in(target) == [2]:
            supertype = 'adj_pp_'
            printrule = True
        
    if len(source) == 2 and len(target) == 1 and float(prob) > mwe_thresh:
        if n_in(source) == [0] and a_in(source) == [1] and a_in(target) == [0]:
            supertype = 'n+adj-adj-'
            printrule = True
        
    if len(source) == 3 and len(target) == 3 and float(prob) > mwe_thresh:
        if q_in(source) == [0] and n_in(source) == [1] and v_in(source) == [2] and v_in(target) == [0] and q_in(target) == [1] and n_in(target) == [2]:
            srcvalence = source[2].split('@')[1]
            evalence = target[0].split('@')[1]
            src = source[2].split('@')[0]
            tgt = target[0].split('@')[0]
            if srcvalence == evalence and '1' in srcvalence and '2' in srcvalence and not '3' in srcvalence:
                supertype = 'arg12+np_arg12+np_'
                source = [src, source[0], source[1]]
                target = [tgt,target[1],target[2]]
                printrule = True
        
    if len(source) == 3 and len(target) == 1 and float(prob) > mwe_thresh:
        if q_in(source) == [0] and n_in(source) == [1] and v_in(source) == [2] and v_in(target) == [0]:
            srcvalence = source[2].split('@')[1]
            evalence = target[0].split('@')[1]
            src = source[2].split('@')[0]
            tgt = target[0].split('@')[0]
            if '1' in srcvalence and '2' in srcvalence and '1' in evalence and not '2' in evalence:
                supertype = 'arg12+np_arg1_'
                source = [src, source[1], source[0]]
                target = [tgt]
                printrule = True
        
    if len(source) == 4 and len(target) == 1 and float(prob) > mwe_thresh:
        if q_in(source) == [1] and n_in(source) == [2] and v_in(source) == [3] and v_in(target) == [0] and not source[3] in lightverbs and not 'nmz' in source[3]:
            evalence = target[0].split('@')[1]
            src = source[3].split('@')[0]
            tgt = target[0].split('@')[0]
            if '1' in evalence and '2' in evalence and not '3' in evalence:
                if source[0] == '"_no_p_rel"':
                    supertype = 'p+n+arg12_arg12_'
                    source = ['"_no_p_rel"', source[2], '"udef_q_rel"', src]
                    target = [tgt]
                    printrule = True

                if source[0] == '"_ni_p_rel"':
                    supertype = 'pp+arg12_arg12_'
                    source = ['"_ni_p_rel"', source[2], '"udef_q_rel"', src]
                    target = [tgt]
                    printrule = True
        
    if len(source) == 3 and len(target) == 1 and float(prob) > mwe_thresh:
        if n_in(source) == [0,2] and "_no_p_" in source[1] and n_in(target) == [0]:
            supertype = 'n+no+n_n_'
            printrule = True

    if printrule:
        ruleout = rule_write(source,target,opt,supertype,trans,phrtab,src_prefix,alltrans,rulecheck,ruledict,transdict)
        ruledict = ruleout[0]
        transdict = ruleout[1]
        rulecheck = ruleout[2]
