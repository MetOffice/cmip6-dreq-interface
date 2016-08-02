# Implementations for `djq`
In [the implementation notes](Python-interface.md) I described how `djq` lets you switch between various methods of computing variables, and in fact of generating the JSON objects corresponding to them.  The reason for this is that there seem to be several different ways of doing the computation of variables, and I could not decide which was the right one, if indeed there *is* a right one.  Although the same confusion doesn't exist for the JSONification process, it was easier to do it the same way: there's only one implementation for this at present.

`djq` ships with two different implementations for variable computation, both based on things that come with the DREQ, and what I want to do here is to describe where they came from, so there's some chance of selecting between them, or writing a third.

Both of these implementations exist as modules in `djq.variables`:

* `djq.variables.cv_dreq_example` is the current default implementation;
* `djq.variables.cv_invert_varmip` is an implementation which tries to reproduce the results of the spreadsheet.

The following two sections give some provenance for these two implementations.

The DREQ home page can be found [here](https://w3id.org/cmip6dr) (this is a redirection page which points to wherever its home really is).  The top of the SVN repo is [here](http://proj.badc.rl.ac.uk/svn/exarch/CMIP6dreq/).  I've tried to make links below point at a tag corresponding to the version I actually used: this means that things may have changed in the trunk of course.

## `djq.variables.cv_dreq_example`
This is the original implementation.  It originates from two places:

* The [DREQ examples document](http://proj.badc.rl.ac.uk/svn/exarch/CMIP6dreq/tags/01.beta.32/dreqPy/docs/dreqExamples.pdf) (link is to `01.beta.32` version), and in particular section 3;
* [`scope.py`](http://proj.badc.rl.ac.uk/svn/exarch/CMIP6dreq/tags/01.beta.32/dreqPy/scope.py) (link is to `01.beta.32` version)