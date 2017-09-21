
##
## PARAMETERS - adjust as necessary
##

# Directory for created profiles
corpus=mini

# Directory with language-pair-specific code and data
transdir=jaen

# Binary locations
ace="ace"
art="art"

# Source grammar parameters
source_suffix=ja
source_grammar_dir=~/grammars/jacy
source_grammar_lexicon="$source_grammar_dir/lexicon.tdl"
source_grammar_image="$source_grammar_dir/jacy.dat"
source_ace_command="$ace -g $source_grammar_image -y -n1 --timeout=10"
source_art_options="-Y"  # yy mode
jpn2yy="$source_grammar_dir/utils/jpn2yy"  # used in bitexts below

# Transfer grammar parameters
transfer_grammar_dir=~/grammars/jaen

# Target grammar parameters
target_suffix=en
target_grammar_dir=~/grammars/erg
target_grammar_lexicon="$target_grammar_dir/lexicon.tdl"
target_grammar_image="$target_grammar_dir/erg.dat"
target_ace_command="$ace -g $target_grammar_image -n1 --timeout=10"
target_art_options=

# Relations file; used when creating [incr tsdb()] profiles from the
# bitext sentences
relations="$source_grammar_dir/tsdb/skeletons/Relations"

# Anymalign options (e.g. --timeout=86400 to stop after 24hrs)
anymalign="/opt/anymalign2.5/anymalign.py"
anymalign_options="--timeout=30"

# bitexts is an array of ':'-delimited 6-tuples with the following form:
#     name:source:target[:divisor[:src_pre[:tgt_pre]]]
# The fields are:
#     name    - unique basename of the resulting corpus directory
#     source  - path to the source side of the bitext
#     target  - path to the target side of the bitext
#     divisor - (optional) divide into subcorpora of $divisor lines
#     src_pre - (optional) command for source-side preprocessing
#     tgt_pre - (optional) command for target-side preprocessing
# For example:
#     mini:corpora/mini.ja:corpora/mini.en
#     mini:corpora/mini.ja:corpora/mini.en:1500:jpn2yy
#     mini:corpora/mini.ja:corpora/mini.en::jpn2yy:tokenizer.pl

bitexts=(
	mini:corpora/mini.ja:corpora/mini.en:10:$jpn2yy
)


## Validation

# use subshell so variables used for validation aren't leaked to outer scope
(
	# change $status instead of exiting immediately so we can get
	# reports for multiple errors
	status=0

	[ -d "$source_grammar_dir" ] || { echo "Source grammar directory not found: $source_grammar_dir" >&2 ; status=1; }
	[ -f "$source_grammar_lexicon" ] || { echo "Source grammar lexicon not found: $source_grammar_lexicon" >&2 ; status=1; }
	[ -f "$source_grammar_image" ] || { echo "Source grammar image not found: $source_grammar_image" >&2 ; status=1; }
	[ -d "$transfer_grammar_dir" ] || { echo "Transfer grammar directory not found: $transfer_grammar_dir" >&2 ; status=1; }
	[ -d "$target_grammar_dir" ] || { echo "Target grammar directory not found: $target_grammar_dir" >&2 ; status=1; }
	[ -f "$target_grammar_lexicon" ] || { echo "Target grammar lexicon not found: $target_grammar_lexicon" >&2 ; status=1; }
	[ -f "$target_grammar_image" ] || { echo "Target grammar image not found: $target_grammar_image" >&2 ; status=1; }
	[ -f "$relations" ] || { echo "Relations file not found: $relations" >&2 ; status=1; }
	[ -x "$anymalign" ] || { echo "Anymalign script is not found or is not executable: $anymalign" >&2 ; status=1; }
	python -c 'import delphin' &>/dev/null || { echo "PyDelphin is not importable by Python." >&2 ; status=1; }
	"$ace" -V &>/dev/null || { echo "$ace not found; perhaps it's not installed?" >&2 ; status=1; }
	"$art" -V &>/dev/null || { echo "$art not found; perhaps it's not installed?" >&2 ; status=1; }
	type -p mecab &>/dev/null || { echo "MeCab is not found; perhaps it's not installed?" >&2 ; status=1; }

	declare -A names
	for line in ${bitexts[@]}; do
		IFS=: read -r name src tgt div src_pre tgt_pre <<< "$line"
		[ -n "$name" ] || { echo "Bitext 'name' field is required." >&2; status=1; }
		[ -z "${names[$name]}" ] || { echo "Bitext name is already used: $name" >&2; status=1; }
		names[$name]="."
		[ -f "$src" ] || { echo "Bitext source not found: '$src'" >&2; status=1; }
		[ -f "$tgt" ] || { echo "Bitext target not found: '$tgt'" >&2; status=1; }
		grep -qP '^[0-9]*$' <<< "$div" || {	echo "divisor must be an integer: $xyz" >&2; status=1; }
	done
	exit $status
)
if [ $? -ne 0 ]; then
	echo "Aborting run" >&2
	exit 1
fi
