#!/bin/bash

# usage: parse-profiles.bash DIR (source|target) [PARAM]
#
# parse profiles found under DIR/*/(source|target), e.g.:
#     parse-profiles.bash jaen/tc source
#     parse-profiles.bash jaen/tc target
# PARAM is the parameter file specific to this run; if not given, then
# parameters.bash is used

usage() { echo "usage: parse-profiles.bash DIR (source|target) [PARAM]"; }

[ -d "$1" ] || { usage; exit 1; }
pdir="$1/profiles"

cwd=$( cd `dirname $0` && pwd)
source "${3:-$cwd/parameters.bash}"

case "$2" in
	source)
		sfx="$source_suffix"
		cmd="$source_ace_command"
		opt="$source_art_options"
		;;
	target)
		sfx="$target_suffix"
		cmd="$target_ace_command"
		opt="$target_art_options"
		;;
	*)
		usage
		exit 1
		;;
esac

for bitext in ${bitexts[@]}; do
	read -d: name <<< "$bitext"  # get just name field from bitext array

	for d in `find "$pdir" -name "$name*.$sfx" -type d | sort -V`; do
		"$art" -a "$cmd" $opt "$d" &> "$d/log"
	done
done
