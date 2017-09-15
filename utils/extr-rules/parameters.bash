
##
## PARAMETERS - adjust as necessary
##

# Directory for created profiles
corpus=mini

# Directory with language-pair-specific code and data
transdir=jaen

# Source grammar paths
source_grammar_dir=~/grammars/jacy
source_grammar_lexicon="$source_grammar_dir/lexicon.tdl"
source_grammar_image="$source_grammar_dir/jacy.dat"
source_ace_command="ace -g $source_grammar_image -y -n1 --timeout=10"
source_art_options="-Y"  # yy mode

# Transfer grammar paths
transfer_grammar_dir=~/grammars/jaen

# Target grammar paths
target_grammar_dir=~/grammars/erg-1214
target_grammar_lexicon="$target_grammar_dir/lexicon.tdl"
target_grammar_image="$target_grammar_dir/erg.dat"
target_ace_command="ace -g $target_grammar_image -n1 --timeout=10"
target_art_options=

# Bitext paths
source_sentences=corpora/mini.ja
target_sentences=corpora/mini.en

# Relations file; used when creating [incr tsdb()] profiles from the
# bitext sentences
relations="$source_grammar_dir/tsdb/skeletons/Relations"

# The preprocessing functions return on stdout the filename of the
# preprocessed results. If unchanged, just return the original filename.
function preprocess_source() {
	fn="$1.preprocessed"
	cat "$1" | python "$source_grammar_dir/utils/jpn2yy.py" > "$fn"
	echo "$fn"
}
function preprocess_target() { echo "$1"; }

# Anymalign options (e.g. --timeout=86400 to stop after 24hrs)
anymalign="/opt/anymalign2.5/anymalign.py"
anymalign_options="--timeout=300"
