<!-- (C) British Crown Copyright 2016, 2018, Met Office.
     See LICENSE.md in the top directory for license details. -->

# 20180406
This release adds `cci` which lets you compare `djq` implementations
for computing variables.  It also changes the Travis CI tests,
removing the sanity test that will never pass, and adding some
explicit runs of `djq` & `cci` instead to exercise the program.

`cci` is a new program which can be used to compare two `djq`
implementations, producing a metric of how similar they are.  So, for
instance

```
all-requests | cci -s -1 djq.variables.cv_dreq_example
```

will produce a report describing how similar the DREQ example
implementation (the one which originated from the DREQ documentation)
is to the default one.  You can compare any pair of implementations,
including your own.

`cci` only provides a metric: there is a new sample module which shows
you how to extract sets of labels from replies, which can then be
compared in an interactive session for instance.

It's possible to run comparison tests specifying the number of columns the
spreadsheet has to test old DREQ versions:

```
make compare DREQ_TAG=<old-tag> DREQ_SPREADSHEET_COLS=24
```

will work.  The documentation mentions this.

There are clearer pointers in the documentation on selecting and
writing djq implementations.

Sanity tests are not run, but both `djq` & `cci` are exercised
significantly more in the Travis CI tests.

There were at least two ugly bugs around closing standard output &
error in the commands: these have been fixed.  The symptom was that
they would silendly exit with `EX_IOERR` (which is 74 on my machine).

# 20180326
This release lets you specify the path to the DREQ XML files directly
('direct paths'), and includes some other fixes.

The diagnostic reveiewers script is gone: it was never used and serves
no purpose now.

Support for direct paths.

Update copyright dates.

If there is no ambient metadata don't give up.

Documentation is slightly better.

The xslx sanity checker, which checks djq against what is in the
spreadsheet works again, and supports direct paths at the module
level.  The sanity tests still fail.

# 20180320
This is a catch-up release, just coagulating everything that has
changed.

There is more metadata in replies.

Suppress the manifest when loading the DREQ.

There is better reporting of the root & tag directoeries.

Report the version of the dreq actually loaded rather than the one
asked for (they can be different).

Rename realm to component throughout.

Diagnostic reviewers script.

Support for Travis CI.

# 20160916

## djq
Support for loading the DREQ trunk.  Previously it was only possible
to load tags, which made it impossible to look at any trunk version of
the DREQ.  Now you can load the trunk by the slightly hacky expedient
of setting the tag to `False` (not `None`, which generally means 'use
the ambient default').

Fix a horrible bug in `ensure_dq`: it was not properly defaulting the
tag.

`ensure_dq` can forcibly load the DREQ, by saying `ensure_dq(...,
force=True)`.  This will update the cached copy.

Also some small improvements to documentation and error reporting.

# 20160905
Copyrights and license in all files.

## `djq`
The problem with DREQ betas after `01.beta.32` is due to bugs in the
DREQ spreadsheet: `djq` itself is fine.  See #11.

The names of files produced by `scatter-replies` has changed to
include the project (by default this is `cmip6` but you can set it).

# 20160822
This is the initial release.

## `djq`
This fails its sanity test with any release of the DREQ newer than
`01.beta.32` (currently this means either `01.beta.33` or
`01.beta.34`).  I strongly suspect this is due to problems with the
DREQ, but I haven't checked it in detail.  In the mean time, use it
with `01.beta.32` either explicitly or by setting the `DJQ_DQTAG`
environment variable:

```
DJQ_DQTAG=01.beta.32; export DJQ_DQTAG
```

## `dqi`
This has very little documentation and hasn't been looked after for a
while.