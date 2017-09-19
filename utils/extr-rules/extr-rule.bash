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
source "${1:-$cwd/parameters.bash}"

## Validation

[ -d "$source_grammar_dir" ] || { echo "Source grammar directory not found: $source_grammar_dir" >&2 ; exit 1; }
[ -f "$source_grammar_lexicon" ] || { echo "Source grammar lexicon not found: $source_grammar_lexicon" >&2 ; exit 1; }
[ -f "$source_grammar_image" ] || { echo "Source grammar image not found: $source_grammar_image" >&2 ; exit 1; }
[ -d "$transfer_grammar_dir" ] || { echo "Transfer grammar directory not found: $transfer_grammar_dir" >&2 ; exit 1; }
[ -d "$target_grammar_dir" ] || { echo "Target grammar directory not found: $target_grammar_dir" >&2 ; exit 1; }
[ -f "$target_grammar_lexicon" ] || { echo "Target grammar lexicon not found: $target_grammar_lexicon" >&2 ; exit 1; }
[ -f "$target_grammar_image" ] || { echo "Target grammar image not found: $target_grammar_image" >&2 ; exit 1; }
[ -f "$source_sentences" ] || { echo "Source sentences not found: $source_sentences" >&2 ; exit 1; }
[ -f "$target_sentences" ] || { echo "Target sentences not found: $target_sentences" >&2 ; exit 1; }
[ -f "$relations" ] || { echo "Relations file not found: $relations" >&2 ; exit 1; }
[ -x "$anymalign" ] || { echo "Anymalign script is not found or is not executable: $anymalign" >&2 ; exit 1; }
python -c 'import delphin' &>/dev/null || { echo "PyDelphin is not importable by Python." >&2 ; exit 1; }
type -p mecab &>/dev/null || { echo "MeCab is not found; perhaps it's not installed?" >&2 ; exit 1; }

##
## RULE EXTRACTION PROCEDURE
##

mkdir -p "$transdir/$corpus"

echo "Preparing source corpus"
source_sentences=$( preprocess_source "$source_sentences" )
echo "Preparing target corpus"
target_sentences=$( preprocess_target "$target_sentences" )

# Divide the corpus into profiles of 1500 items each
echo "Dividing the corpus into profiles in '$transdir/$corpus/'"
v=$(
	python divide-corpus.py 1500 \
		$corpus $source_sentences $target_sentences $transdir
)

# Batch parse the source corpus
echo "Batch parsing the source corpus..."
i="0"
while [ $i -lt $v ]
do
	i=$[$i+1]
	cdir="$transdir/$corpus/$corpus${i}"
	echo -e "  $i/$v\t$cdir/source"
	mkprof -r "$relations" -i "$cdir/bitext/original" "$cdir/source" \
		&> "$cdir/source-mkprof.log"
	art -a "$source_ace_command" $source_art_options "$cdir/source" \
		&> "$cdir/source/log"
done 

# Batch parse the target corpus
echo "Batch parsing the target corpus..."
i="0"
while [ $i -lt $v ]
do
	i=$[$i+1]
	cdir="$transdir/$corpus/$corpus${i}"
	echo -e "  $i/$v\t$cdir/target"
	mkprof -r "$relations" -i "$cdir/bitext/object" "$cdir/target" \
		&> "$cdir/target-mkprof.log"
	art -a "$target_ace_command" $target_art_options "$cdir/target" \
		&> "$cdir/target/log"
done 

# Create a parallel corpus of MRSs:
#  * indicating valency of verbs with suffixes to the relations
#  * marking nominalized verb relations with an 'nmz_' prefix
#  * marking proper name predicates with an 'nmd_' prefix
echo "Creating a parallel corpus of MRSs"
python profiles2mrsparcorp.py $transdir $corpus $v

# Use the Anymalign phrase aligner to produce a phrase table from the parallel
# corpus of MRSs. The program runs until it is stopped with Ctrl-C

# Can be downloaded from:
# wget http://perso.limsi.fr/Individu/alardill/anymalign/latest/anymalign2.5.zip
# unzip anymalign2.5.zip 

echo "Running Anymalign on the parallel MRS corpus"
python "$anymalign" $anymalign_options \
	"$transdir/$corpus/mrs_source.txt" \
	"$transdir/$corpus/mrs_target.txt" \
	> "$transdir/$corpus/anymalign.mrs"

# Choosing the most probable phrase alignments


echo "Choosing the most probable phrase alignments"
python phrtab-thin.py "$transdir/$corpus"


# Reading the existing transfer rule files
echo "Finding exisiting transfer rules"
python hand-rules.py "$transfer_grammar_dir" "$transdir" \
	>  "$transdir/$corpus/hand-rules"

# Representing the lexicons of the parsing grammar and generating
# grammar as tables
echo "Extracting source lexical table"
python lex.py ${source_grammar_lexicon} > $transdir/$corpus/source-lex.tab
echo "Extracting target lexical table"
python lex.py ${target_grammar_lexicon} > $transdir/$corpus/target-lex.tab


# Reading the processed phrase table and matching with templates. If
# your source language is not Japanese you need to change the
# src_prefix in the top of the file to ''. The script calls a function
# in 'jaen/templates.py' with language specific templates. You may
# need to modify the templates in this file.

echo "Writing transfer rules"
python thin2mtr.py $corpus $transdir
