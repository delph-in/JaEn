#!/bin/bash

#
# This is a procedure for extracting transfer rules from parallel mrs
# corpora
#
# The program requires that ACE and art are installed:
#     http://sweaglesw.com/linguistics/ace/
#     http://sweaglesw.com/linguistics/libtsdb/art
#
# For Japanese tokenization, Mecab is also required:
#     sudo apt-get install mecab-ipadic-utf8 python-mecab
#
# To configure this script for your experiment, you will need to
# modify the parameters to suit your experiment and your environment.
# I suggest copying the parameters.bash file (e.g.,
# `cp parameters.bash jaen-parameters.bashextr-rule-jaen.bash`), then
# modify the copy and give its path as an argument to this script.
# That way you have a backup copy of the original file. If no argument
# is given to this script, it uses parameters.bash by default.
#
# When you're ready to run, call this script with either no arguments
# (to use the default parameters.bash) or with the path of the
# parameter file as an argument:
#
#     bash extr-rule.bash jaen-parameters.bash
#
# or just
#
#     bash extr-rule.bash

cwd=$( cd `dirname $0` && pwd)
param="${1:-$cwd/parameters.bash}"
source "$param"

##
## RULE EXTRACTION PROCEDURE
##

workspace="$transdir/$corpus"

# Prepare corpora

echo "Preparing bitext corpora"
bash prepare-corpora.bash "$workspace" "$param"

# Batch parsing

echo "Batch parsing the source corpus..."
bash parse-profiles.bash "$workspace" "source" "$param"

echo "Batch parsing the target corpus..."
bash parse-profiles.bash "$workspace" "target" "$param"

# Create a parallel corpus of MRSs:
#  * indicating valency of verbs with suffixes to the relations
#  * marking nominalized verb relations with an 'nmz_' prefix
#  * marking proper name predicates with an 'nmd_' prefix
echo "Creating a parallel corpus of MRSs"
bash linearize-mrss.bash "$workspace" "$param"

# Use the Anymalign phrase aligner to produce a phrase table from the parallel
# corpus of MRSs. The program runs until it is stopped with Ctrl-C

# Can be downloaded from:
# wget http://perso.limsi.fr/Individu/alardill/anymalign/latest/anymalign2.5.zip
# unzip anymalign2.5.zip 

echo "Running Anymalign on the parallel MRS corpus"
python "$anymalign" $anymalign_options \
	"$workspace/mrs_source.txt" \
	"$workspace/mrs_target.txt" \
	> "$workspace/anymalign.mrs"

# Choosing the most probable phrase alignments


echo "Choosing the most probable phrase alignments"
python phrtab-thin.py "$workspace"


# Reading the existing transfer rule files
echo "Finding exisiting transfer rules"
python hand-rules.py "$transfer_grammar_dir" "$transdir" \
	>  "$workspace/hand-rules"

# Representing the lexicons of the parsing grammar and generating
# grammar as tables
echo "Extracting source lexical table"
python lex.py ${source_grammar_lexicon} > $workspace/source-lex.tab
echo "Extracting target lexical table"
python lex.py ${target_grammar_lexicon} > $workspace/target-lex.tab


# Reading the processed phrase table and matching with templates. If
# your source language is not Japanese you need to change the
# src_prefix in the top of the file to ''. The script calls a function
# in 'jaen/templates.py' with language specific templates. You may
# need to modify the templates in this file.

echo "Writing transfer rules"
python thin2mtr.py $corpus $transdir
