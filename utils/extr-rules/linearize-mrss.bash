#!/bin/bash

# usage: linearize-mrss.bash DIR [PARAM]
#
# Find all bilingual profile pairs, extract the MRSs, and linearize
# them to produce a bilingual predicate corpus. DIR is the workspace
# directory, under which the paired profiles will be found. PARAM is
# the parameter file specific to this run; if not given, then
# parameters.bash is used.

[ -d "$1" ] || { echo "usage: linearize-mrss.bash DIR [PARAM]"; exit 1; }
workspace="$1"
pdir="$workspace/profiles"
ldir="$workspace/bipreds"
mkdir -p "$ldir"

cwd=$( cd `dirname $0` && pwd)
source "${2:-$cwd/parameters.bash}"

# clear any existing linearizations
echo -n > "$workspace/mrs_source.txt"
echo -n > "$workspace/mrs_target.txt"

# source and target profiles must be linearized at the same time to
# ensure the resulting files are in the same order
for bitext in ${bitexts[@]}; do
	# unpack name:src:tgt:div:src_pre:tgt_pre strings into variables
	read -d: name <<< "$bitext"  # get just name field from bitext array

	for src in `find "$pdir" -name "$name*.$source_suffix" | sort -V`; do
		tgt="${src%.$source_suffix}.$target_suffix"
		if [ -d "$tgt" ]; then
			lsrc="$ldir"/`basename "$src"`
			ltgt="$ldir"/`basename "$tgt"`
			python profiles2mrsparcorp.py "$src" "$tgt" "$lsrc" "$ltgt"
			# append to singular bipred file
			cat "$lsrc" >> "$workspace/mrs_source.txt"
			cat "$ltgt" >> "$workspace/mrs_target.txt"
		else
			echo "Warning: no corresponding target profile for source: $src"
		fi
	done
done
