#
# This is a procedure for extracting transfer rules from parallel mrs
# corpora
#
# The program requires that the LOGON system is installed:
# http://moin.delph-in.net/LogonInstallation
#
# You need a parallel corpus in two files. You can execute this script
# with the following command, where SOURCE is the file with the source
# language items, TARGET is the file with the target language items,
# CORPUS is the name of your corpus, and TRANSDIR refers to a
# subdirectory with language specific data:
#
# bash rule-extr.bash SOURCE TARGET CORPUS TRANSDIR
# 
# bash extr-rule.bash corpora/mini.ja corpora/mini.en mini jaen
#

infile=$1
outfile=$2

corpus=$3
transdir=$4/

# Part-of-speech tag the Japanese corpus with MeCab:
#
# To install MeCab, do:
#
# sudo apt-get install python-yaml
# sudo apt-get install mecab-ipadic-utf8 python-mecab
#
# Comment the next three lines out if the source language is not
# Japanese
echo "Part-of-speech tagging the Japanese corpus"
python ${transdir}ja2yy.py $infile > $infile.pos
infile=$infile.pos

# Divide the corpus into profiles of 1500 items each
echo "Dividing the corpus into profiles in '"$transdir$corpus"-profiles/'"
v=$(python divide-corpus.py 1500 $corpus $infile $outfile $transdir)

# Batch parse the Japanese corpus with Jacy
echo "Batch parsing the Japanese corpus"
i="0"
while [ $i -lt $v ]
do
    i=$[$i+1]
    mkdir -p $transdir$corpus-profiles/$corpus${i}/source/
    cheap -comment-passthrough -mrs -nsolutions=1 -results=1 -packing=15 -timeout=10 -yy -default-les -tsdbdum=$transdir$corpus-profiles/$corpus${i}/source -inputfile=$transdir$corpus-profiles/$corpus${i}/bitext/original ~/logon/dfki/jacy/japanese &> $transdir$corpus-profiles/$corpus${i}/source/log
done 

# Batch parse the English corpus with the ERG
echo "Batch parsing the English corpus"
i="0"
while [ $i -lt $v ]
do
    i=$[$i+1]
    mkdir -p $transdir$corpus-profiles/$corpus${i}/target/
    cheap -repp -tagger -default-les=all -cm -packing -mrs -nsolutions=1 -results=1 -packing=15 -timeout=10 -inputfile=$transdir$corpus-profiles/$corpus${i}/bitext/object -tsdbdump $transdir$corpus-profiles/$corpus${i}/target  ~/logon/lingo/erg/english.grm &> $transdir$corpus-profiles/$corpus${i}/target/log
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
python anymalign2.5/anymalign.py $transdir${corpus}_mrs_source.txt $transdir${corpus}_mrs_target.txt > $transdir$corpus-anymalign.mrs

# Choosing the most probable phrase alignments

echo "Choosing the most probable phrase alignments"
python phrtab-thin.py $transdir$corpus

# Reading the existing transfer rule files
echo "Finding exisiting transfer rules"
python hand-rules.py $LOGONROOT $transdir >  $transdir/hand-rules

# Representing the lexicons of the parsing grammar and generating
# grammar as tables
python lex.py ${LOGONROOT}/lingo/erg/lexicon.tdl > $transdir/target-lex.tab
python lex.py ${LOGONROOT}/dfki/jacy/lexicon.tdl > $transdir/source-lex.tab

# Reading the processed phrase table and matching with templates. If
# your source language is not Japanese you need to change the
# src_prefix in the top of the file to ''. The script calls a function
# in 'jaen/templates.py' with language specific templates. You may
# need to modify the templates in this file.
echo "Writing transfer rules"
python thin2mtr.py $LOGONROOT $corpus $transdir
