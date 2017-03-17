
The Ja↔En Machine-translation System contains two transfer grammars: one
for each translation direction:

* [JaEn][] for Japanese-to-English
* Enja for English-to-Japanese

These transfer grammars map [Minimal Recursion Semantic][MRS] ([MRS][])
representations to/from the [Jacy][] Japanese grammar and the
[English Resource Grammar][ERG] ([ERG][]).

# Setup

In order to use these transfer grammars, you will need either the
[ACE][] or [LKB][] (by itself or as part of [LOGON][]) processor
installed. You'll also want to install [Jacy][] and the [ERG][]
(binaries are available at the [ACE][] website, or the grammar source
is available in [LOGON][] at `$LOGONROOT/lingo/erg/`). For extending
JaEn with automatically extracted transfer rules (see below), you'll
need to install [PyDelphin][] (for Python 2.7).

# Grammars

## JaEn

There are two flavors to JaEn: a core transfer grammar containing
hand-built and dictionary-extracted transfer rules, and a larger grammar
using transfer rules extracted from bilingual corpora.

**Note**: The following have been removed, as they were not actively
used by the ACE-compiled version of JaEn:

- `mrs.binlm` language model (used by the [LKB][])
- `perl/` tools for extracting transfer rules from [EDICT][]

If they are needed, you can get them from the original [LOGON][]
repository at `$LOGONROOT/uio/tm/jaen/`.

### JaEn Core

Compile the core JaEn grammar as follows (from the top-level directory):

    ace -g jaen/ace/config-core.tdl -G jaen-core.dat

This grammar may not have good coverage, but it can be useful for
debugging.

### Extended JaEn

If you want to use the
[automatically extracted](http://moin.delph-in.net/MtRuleExtraction)
transer rules for JaEn, you use the
[`utils/select-rule.py`](utils/select-rule.py) script to generate a
subset of the rules that only includes those useful for some given
sentences. The rules extracted by [Haugereid and Bond 2012][] are
available in the [data/](data) directory. It is called as follows:

    python2 utils/select-rule.py WORKDIR [OPTION..] ITEM [ITEM..]

The `WORKDIR` parameter is a path to a working directory, which is where
the output files are written. If you don't supply the `--data` and
`--jacy` options (for the data and Jacy directories, respectively), it
assumes they are at `$WORKDIR/data` and `$WORKDIR/jacy` respectively.
Thus, the easiest way to get started is to use the top-level directory
of this repository as `WORKDIR` and to symlink Jacy. E.g.:

    ln -s ~/grammars/jacy jacy
    python2 utils/select-rule.py . jacy/tsdb/skeletons/tanaka/tc-000/item

If all goes well, the `single.selected.mtr` and `mwe.selected.mtr` files
are created. Move these under the `jaen/` subdirectory and compile:

    mv single.selected.mtr jaen/
    mv mwe.selected.mtr jaen/
    ace -g jaen/ace/config.tdl -G jaen.dat

You can use many more item files to get a more robust transfer grammar,
but if it is too big, ACE may fail to compile it.

    python2 utils/select-rule.py . jacy/tsdb/skeletons/tanaka/tc-{000..100}/item


## EnJa

There has not been any development on EnJa for a while, so it currently
does not have an [ACE][] config file. It may work with the [LKB][], but
we have not tested this. We include the EnJa files so that we may update
them in the future.


# History

The JaEn and EnJa grammars were copied from the LOGON repository and
now exist separately to encourage development.  The original README is
below:

> this directory contains the LOGON Transfer Matrix (TM), an attempt
> at providing a reusable, basic infrastructure for the creation of
> new, language-specific transfer grammars.  as of mid-2010, the core
> of the Transfer Matrix is straight from the original LOGON
> Norwegian--English MT system, with some additions from the
> experience of building Japanese--English and German--English
> prototypes.
> 
> between 2004 and 2010, the Transfer Matrix was maintained at the
> University of Oslo, predominantly by Stephan Oepen, Jan Tore
> Lønning, and Petter Haugereid.  with the completion of the Paris
> release of the LOGON tree, TM maintenance is transferred to Nanyang
> Technological University (NTU), where Francis Bond and Petter
> Haugereid are actively working on transfer-based MT.

# Citation

Francis Bond, Stephan Oepen, Eric Nichols, Dan Flickinger, Erik Velldal
and Petter Haugereid (2011)
[Deep Open Source Machine Translation](http://www.springerlink.com/openurl.asp?genre=article&id=doi:10.1007/s10590-011-9099-4).
In Machine Translation 25(2) 87-105
([bib](citation.bib))

[JaEn]: http://moin.delph-in.net/MtJaen
[MRS]: http://moin.delph-in.net/RmrsTop
[Jacy]: https://github.com/delph-in/jacy
[ERG]: http://www.delph-in.net/erg
[ACE]: http://sweaglesw.org/linguistics/ace
[LKB]: http://moin.delph-in.net/LkbTop
[LOGON]: http://moin.delph-in.net/LogonTop
[EDICT]: http://www.edrdg.org/jmdict/edict.html
[PyDelphin]: https://github.com/delph-in/pydelphin
[Haugereid and Bond 2012]: http://www.aclweb.org/website/old_anthology/W/W12/W12-4208.pdf
