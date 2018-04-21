<!-- (C) British Crown Copyright 2016, 2018, Met Office.
     See LICENSE.md in the top directory for license details. -->

# CMIP6 DREQ interfaces

## `djq`
`djq` is the DREQ JSON Query tool which allows you to query the DREQ
for variable mappings, and also provides an interface to explore
algorithms to implement such mappings.  You can hand it requests
specifying MIPs and experiments within those MIPs and it will reply
with lists of variables.  You should be able to install it from its
`setup.py`.  It requires the `dreqPy` package from the DREQ (but is
not fussy about version), nose to run tests, and will also need access
to the a SVN checkout of the DREQ itself: you will almost certainly
need to teach it where this is.

Because the mapping from MIPs and experiments to variables is not very
well-defined by the DREQ, `djq` also provides a simple interface which
allows you to define your own mapping function: this function doesn't
need to know anything about `djq` at all other than how it is called, and
can be loaded dynamically from a module at run time, so no modifications
are needed to `djq` in order to provide an alternative mapping function . It
is possible to specify which function or module to use both from the Python API
and from the command line. Multiple such functions / modules can exist
concurrently. These functions / modules are called 'implementations' in the
code.

Once the set of variables is computed, it needs to be elaborated in various ways
before being turned into JSON.  This is done by a 'JSONifier', and these are
also components which can be plugged in to `djq` dynamically.

A tool is included, `cci`, which allows you to directly compare
implementations.

There are four command line programs associated with `djq`.

* `djq` is the main thing: you can use it to make queries and get
  answers;
* `cci` compares implementations -- you can give it the names of one
  or two implementation modules and will tell you whether they differ
  in the variables they compute, giving a metric of similarity going
  from 0.0 (completely different) to 1.0 (identical);
* `all-requests` is a little program which reads the DREQ, and then
  generates a request for every experiment in every MIP, which can be
  fed to djq to run a really comprehensive set of queries;
* `scatter-replies` is another little program which will read a set of
  replies from `djq` and spit them out into files named after the MIPs
  and experiments.

As an example, using `cci` to compare the two implementations bundled
with `djq`, which correspond to what Martin described in his document
and what he used at to generate his spreadsheets, both at the time
`djq` was originally written, the results vary from 0.0 to 1.0 for
different pairs of MIP and experiment.

## `dqi`
`dqi` is the DREQ Query Interface.  You do not need this to use `djq`,
although some `djq` back ends may need it (they do not currently).

## `small`
`small` contains some small, more-or-less ad-hoc programs which are
related to the CMIP6 DREQ.  These are almost entirely undocumented and
may or may not work.

See [the change log](Changes.md), which contains at least an entry for
each release, and often also any changes which matter since the most
recent release.

## Pointers
* [`djq`](djq/README.md)
* [Some general documentation](doc/README.md)
* (No documentation for `dqi` yet)

## References
* [The CMIP6 data request](https://w3id.org/cmip6dr) or DREQ (redirection page)
* [Subversion repo for the DREQ](http://proj.badc.rl.ac.uk/svn/exarch/CMIP6dreq/), also browsable

## Builds and tests
[![Build Status](https://travis-ci.org/tfeb/cmip6-dreq-interface.svg)](https://travis-ci.org/tfeb/cmip6-dreq-interface)

This status corresponds to
[`github.com/tfeb/cmip6-dreq-interface`](https://github.com/tfeb/cmip6-dreq-interface)
and may not completely correspond to the status of the [Met Office
repo](https://github.com/MetOffice/cmip6-dreq-interface).  Almost all
of the tests are for `djq`: `dqi` has no tests at all.

The tests should pass unless there are serious bugs in `djq` itself.
It formerly ran a hairy sanity test which compared what it computes
against spreadsheets included with the DREQ.  Unfortunately the DREQ
is so unstable that these essentially never passed, so these are no
longer included in the Travis CI tests.

If the build status link is dead, that's probably because
[`github.com/tfeb/cmip6-dreq-interface`](https://github.com/tfeb/cmip6-dreq-interface)
has gone away.

## Browsing the documentation
All the documentation is in
[Markdown](http://daringfireball.net/projects/markdown/) (and
specifically [GitHub flavoured
Markdown](https://help.github.com/categories/writing-on-github/)):
this should be fairly readable as plain text.  `README.md` files are
the entry points, and any extended documentation is in subdirectories
called `doc`.

You can use [grip](https://github.com/joeyespo/grip) to view the
pretty version of the documentation locally.  It can be installed with
`pip`:

```
$ pip install grip
[...]
$ grip
 * Running on http://localhost:6419/ (Press CTRL+C to quit)
```

`grip -b` is also useful (opens a browser tab).

See [its
documentation](https://github.com/joeyespo/grip/blob/master/README.md). Note
that `grip` works by using GitHub's API to format the markdown files,
and so sends their content to GitHub: it's not suitable for sensitive data.

---

&copy; British Crown Copyright 2016, 2018, Met Office.  See
[LICENSE.md](LICENSE.md) for license details.
