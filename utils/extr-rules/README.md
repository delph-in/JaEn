
# Transfer Rule Extraction

This directory contains a tool (`extr-rule.bash`) for extracting
transfer rules from parallel MRS corpora, developed at Nanyang
Technological University (NTU) by Petter Haugereid (2010-2012). More
detailed instructions on how to use it can be found at
http://moin.delph-in.net/MtRuleExtraction

In order to make it work you need to have the LOGON system installed:

http://moin.delph-in.net/LogonInstallation

You need a parallel corpus in two files. If one of the languages is
Japanese, you will need to install the MeCab tagger:

    sudo apt-get install python-yaml
    sudo apt-get install mecab-ipadic-utf8 python-mecab

You will need to download the [Anymalign][] phrase aligner, and place
the `anymalign.py` script in the same directory as `extr-rule.bash`.

To get more results, you should also use the [MOSES][] system, but
that is not a part of this procedure.  This directory contains a shell
script that runs through the whole procedure of rule extraction. It
can be executed with:

    bash extr-rule.bash SRCGRM XFRGRM TGTGRM SRCSNT TGTSNT CORPUS TRANSDIR

e.g.

    bash extr-rule.bash ~/jacy/ ~/jaen/ ~/erg/ \
                        corpora/mini.ja corpora/mini.en \
                        mini jaen

The arguments are defined as follows:

| Argument   | Description                                            |
| ---------- | ------------------------------------------------------ |
| `SRCGRM`   | path to the source grammar                             |
| `XFRGRM`   | path to the transfer grammar                           |
| `TGTGRM`   | path to the target grammar                             |
| `SRCSNT`   | path to a file of aligned source sentences             |
| `TGTSNT`   | path to a file of aligned target sentences             |
| `CORPUS`   | the name given to a run of the extraction code         |
| `TRANSDIR` | directory with resources specific to the language pair |

The resulting transfer rule files are written into the `TRANSDIR`

For more information abour each program run by the script, see
comments in `extr-rule.bash`.

To add MOSES, use it to align the MRS files and then use
`phrtab-thin.py` to combine its phrase table with the one from
Anymalign.

[Anymalign]: https://anymalign.limsi.fr
[MOSES]: http://www.statmt.org/moses/
