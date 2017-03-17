#!/bin/bash

i="0"
while [ $i -lt $1 ]
do
    i=$[$i+1]
    mkdir -p $2/ku${i}/jacy/
    cheap -comment-passthrough -mrs -nsolutions=1 -results=1 -packing=15 -timeout=10 -yy -default-les -tsdbdum=$2/ku${i}/jacy -inputfile=$2/ku${i}/bitext/original ~/logon/dfki/jacy/japanese &> $2/ku${i}/jacy/log
    mkdir -p $2/ku${i}/erg/
    cheap -repp -tagger -default-les=all -cm -packing -mrs -nsolutions=1 -results=1 -packing=15 -timeout=10 -inputfile=$2/ku${i}/bitext/object -tsdbdump $2/ku${i}/erg  ~/logon/lingo/erg/english.grm &> $2/ku${i}/erg/log


done 
