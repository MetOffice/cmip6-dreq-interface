# Implementations for `djq`
In [the Python interface notes](Python-interface.md) I described how `djq` lets you switch between various methods of computing variables, and in fact of generating the JSON objects corresponding to them.  The reason for this is that there seem to be several different ways of doing the computation of variables, and I could not decide which was the right one, if indeed there *is* a right one.  Although the same confusion doesn't exist for the JSONification process, it was easier to do it the same way: there's only one implementation for this at present.

`djq` ships with two different implementations for variable computation, both based on things that come with the DREQ, and what I want to do here is to describe where they came from, so there's some chance of selecting between them, or writing a third.

Both of these implementations exist as modules in `djq.variables`:

* `djq.variables.cv_dreq_example` was the original default implementation;
* `djq.variables.cv_invert_varmip` is an implementation which tries to reproduce the results of the spreadsheet, and is now the default (the change in default happened in commit 25e53a1731901a3d9b49ff3bd99688ab8c1b30cb).

The following two sections give some provenance for these two implementations.

The DREQ home page can be found [here](https://w3id.org/cmip6dr) (this is a redirection page which points to wherever its home really is).  The top of the SVN repo is [here](http://proj.badc.rl.ac.uk/svn/exarch/CMIP6dreq/).  I've tried to make links below point at a tag corresponding to the version I actually used: this means that things may have changed in the trunk of course.

## `djq.variables.cv_dreq_example`
This is the original implementation, and was formerly the default.  It originates from two places:

* The [DREQ examples document](http://proj.badc.rl.ac.uk/svn/exarch/CMIP6dreq/tags/01.beta.32/dreqPy/docs/dreqExamples.pdf) (link is to `01.beta.32` version), and in particular section 3;
* [`scope.py`](http://proj.badc.rl.ac.uk/svn/exarch/CMIP6dreq/tags/01.beta.32/dreqPy/scope.py) (link is to `01.beta.32` version).

The examples document shows how to find the `CMORvar`s corresponding to a MIP by:

1. finding `requestLink` objects which refer to the MIP;
2. finding `requestVarGroup` objects which talk about the `requestLink`s;
3. finding the `requestVar`s for these groups, and then the `CMORvar`s for these.

This solves part of the problem, but it doesn't deal with experiments at all.  Dealing with experiments is much more complicated and less well-founded.

1. First of all, given an `experiment`, it finds `requestLink`s that refer to it.  This is based on code in `scope.py` again.
2. For those `requestLink`s it finds the `requestVarGroup`s they refer to.
3. For the `requestVarGroup`s it then finds the `requestVar`'s that refer to them and hence the `CMORvar`s.

The implementation essentially then takes the union of the results of these two processes.  In various releases of the DREQ things have turned up in this set which are not `CMORvar`s, so it then prunes the result set by checking for bogons and removing them, muttering as it does so (if `verbosity_level()` is 1 or higher it will report the total number of things pruned; if it is 2 or higher it will report each thing pruned as well).

## `djq.variables.cv_invert_varmip`
This implementation is based on the code which produces the spreadsheet.  The code that does this computation lives in [`vrev.py`](http://proj.badc.rl.ac.uk/svn/exarch/CMIP6dreq/tags/01.beta.32/dreqPy/vrev.py) (link is to `01.beta.32` version) and the particular method is `vrev.chkCmv`.  There are two problems with this code as it stands:

* the spreadsheet knows nothing about experiments;
* The spreadsheet maps `CMORvar`s to their MIPs, whereas I need to map MIPs (and experiments) to their `CMORvar`s.

The experiment problem isn't that hard to deal with: the code in `vrev.py` already deals with finding MIPs which are requesting a variable through experiments, as well as ones which request it directly.  I have just modified that code to be fussy about *which* experiments it accepts: rather than anything, it checks for the experiments given as arguments, and in the case of experiment groups (`exptgroup`s) it iterates over all their experiments for ones which match.  I am reasonably but not completely sure this approach works: it certainly gives results which don't look silly.

The mapping problem is dealt with by simply computing the sets of MIPs for *all* `CMORvar`s, and then inverting that mapping.  This makes it rather slow (this could easily be sped up by caching and inverting the map just once, and then probing it for each MIP -- that would be fairly easy to implement but given the likely use of this code there seemed no reason to worry about the performance), but it's easy to understand.

There are two bad cases which can occur here (in both cases the number of variables pruned is reported if `verbosity_level()` is 1 or greater with details reported if it is 2 or greater):

* sometimes there are `CMORvar`s which belong to *no* MIPs: these can never be used;
* there can be invalid `CMORvar`s -- typically variables which are placeholders or are otherwise incomplete -- which are excised.

This implementation has been tested against the spreadsheet fairly extensively, and, with the caveat that the spreadsheet does not deal with experiments so this can't be tested, produces the same mappings.