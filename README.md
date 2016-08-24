# CMIP6 DREQ interfaces
`djq` is the DREQ JSON Query tool, which you should be able to install
from its `setup.py`.  It requires the `dreqPy` package from the DREQ
(but is not fussy about version), nose to run tests, and will also
need access to the a SVN checkout of the DREQ itself: you will almost
certainly need to teach it where this is.

`dqi` is the DREQ Query Interface.  You do not need this to use `djq`,
although some `djq` back ends may need it.

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
