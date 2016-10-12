<!-- (C) British Crown Copyright 2016, Met Office.
     See LICENSE.md in the top directory for license details. -->

# Changes since 20160916
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