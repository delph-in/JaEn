#!/bin/bash

# usage: prepare-corpora.bash DIR [PARAM]
#
# Prepare corpus directories for data specified in the parameters
# file. This includes splitting large bitexts into subcorpora, making
# corpus directories, copying in the files, and creating [incr tsdb()]
# instances. DIR is the workspace directory, under which the resulting
# corpus directories will be placed. PARAM is the parameter file
# specific to this run; if not given, then parameters.bash is used.

[ -n "$1" ] || { echo "usage: prepare-corpora.bash DIR [PARAM]"; exit 1; }
bdir="$1/bitexts"
pdir="$1/profiles"
mkdir -p "$bdir" "$pdir"

cwd=$( cd `dirname $0` && pwd)
source "${2:-$cwd/parameters.bash}"


for bitext in ${bitexts[@]}; do
	# unpack name:src:tgt:div:src_pre:tgt_pre strings into variables
	IFS=: read -r name src tgt div src_pre tgt_pre <<< "$bitext"

	# figure out splits
	# numlines-1 and result+1 so (0 <= numlines <= div) is 1 subcorpus
	numlines=`awk 'END {print NR}' "$src"`  # like wc -l, but just the count
	div=${div:-$numlines}  # no div; just one subcorpus
	n=$(( (numlines-1)/div + 1 ))

	# preprocessors default to nothing
	src_pre=${src_pre:-cat}
	tgt_pre=${tgt_pre:-cat}

	echo "...creating $n subcorpora"
	"$src_pre" < "$src" | split -a ${#n} -d -l $div \
		--additional-suffix=".$source_suffix" - "$bdir/$name-"
	"$tgt_pre" < "$tgt" | split -a ${#n} -d -l $div \
		--additional-suffix=".$target_suffix" - "$bdir/$name-"
	
	# create profile instances
	for f in `find "$bdir/" -type f`; do
		bn=`basename "$f"`
		mkprof -r "$relations" -i "$f" "$pdir/$bn" &> /dev/null
	done
done
