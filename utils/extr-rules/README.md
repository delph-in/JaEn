
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

    sudo apt-get install mecab mecab-ipadic-utf8

You will need to download the [Anymalign][] phrase aligner and extract
it somewhere (e.g., in this directory, or under `/opt/`, etc.).
To get more results, you should also use the [MOSES][] system, but
that is not a part of this procedure.

This directory contains a shell script that runs through the whole
procedure of rule extraction. A run can be configured by modifying the
`parameters.bash` file. I suggest that you copy `parameters.bash` and
modify the copy. The script then can be run with the path of the new
parameters file as an argument:

    bash extr-rule.bash my-parameters.bash

If you don't give any arguments, it will use the default parameters:

    bash extr-rule.bash

For more information abour each program run by the script, see
comments in `extr-rule.bash` and `parameters.bash`.

To add MOSES, use it to align the MRS files and then use
`phrtab-thin.py` to combine its phrase table with the one from
Anymalign.

[Anymalign]: https://anymalign.limsi.fr
[MOSES]: http://www.statmt.org/moses/
