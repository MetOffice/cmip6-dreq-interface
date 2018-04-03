<!-- (C) British Crown Copyright 2016, Met Office.
     See LICENSE.md in the top directory for license details. -->

# CMIP6 DREQ interfaces
`djq` is the DREQ JSON Query tool which allows you to query the DREQ
for variable mappings, and also provides an interface to explore
algorithms to implement such mappings.  You should be able to install
it from its `setup.py`.  It requires the `dreqPy` package from the
DREQ (but is not fussy about version), nose to run tests, and will
also need access to the a SVN checkout of the DREQ itself: you will
almost certainly need to teach it where this is.

`dqi` is the DREQ Query Interface.  You do not need this to use `djq`,
although some `djq` back ends may need it.

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
repo](https://github.com/MetOffice/cmip6-dreq-interface).  Almost all of the tests are for `djq`: `dqi` has no tests at all.

There are two reasons for the `djq` tests failing:

* there are bugs in `djq`;
* there are problems which causes `djq` to fail its sanity test.

In the second case it is often initially obscure where the problem
which is causing the sanity tests lies, but it has often been due to
problems with the DREQ itself.

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

&copy; British Crown Copyright 2016, Met Office.  See
[LICENSE.md](LICENSE.md) for license details.