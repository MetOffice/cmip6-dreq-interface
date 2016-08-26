<!-- (C) British Crown Copyright 2016, Met Office.
     See LICENSE.md in the top directory for license details. -->

# Installation
This currently only describes how to install `djq` using Conda.
However, apart from the installation of Conda itself, and the use of
the `conda` package manager to install requirements, installing on top
of other Python environments should be similar.

## Requirements
`djq` requires:

* Python 2.7;
* the Python [nose](https://pypi.python.org/pypi/nose) library for
  tests;
* an installed copy of the DREQ Python interface (so `import dreqPy`
  must work);
* a checkout of the [Subversion
  DREQ](http://proj.badc.rl.ac.uk/svn/exarch/CMIP6dreq/) from the root
  (so tags are available);
* possibly the Python
  [openpyxl](https://pypi.python.org/pypi/openpyxl) library, for some
  comparison checks.

## Installation using Conda
The way I install `djq` is using [Conda](http://conda.pydata.org/),
which provides an encapsulated, controllable environment independent
of the vagaries of whatever version of Python is installed on the
system this week.  I'm not going to describe how to use Conda to
manage and control dependencies in a repeatable and traceable way,
just how to do the minimum to get `djq` working in a Conda
environment.

First of all fetch a copy of
[Miniconda](http://conda.pydata.org/miniconda.html) suitable for your
system.  Assuming you are using Linux fetch a version of the [64-bit
bash
installer](https://repo.continuum.io/miniconda/Miniconda2-latest-Linux-x86_64.sh)
built on Python 2.7 (the 32-bit one would also be fine).  Choose a
suitable toplevel directory and install a Miniconda environment there
by running the installer.

You can now arrange to use this environment by running a command such
as:

```
PATH=/path/to/miniconda/dir/bin:$PATH $SHELL
```

assuming you are using a Bourne-shell family shell.  Everything below
assumes you are in this environment.

(If you know how to drive Conda already, you may want to make a
non-root Conda environment from this environment with, for instance
`conda create -n djq --clone root`, and perhaps to do any updates
(`conda update --all`) or other version controllery that you want to
do in the environment at this point.)

Install nose in the environment: `conda install nose`.

Install openpyxl in the environment: `conda install openpyxl`.

Now checkout the top level of the DREQ to a known directory:

```
svn co http://proj.badc.rl.ac.uk/svn/exarch/CMIP6dreq
```

It is important you fetch the top level, *not* a tag or a branch, as
`djq` wants to be able to specify a tag to use in the request, so you
can select which version of the DREQ to load.  I'll refer to this
directory as `<dqroot>` below.

Install the `dreqPy` library.  It should not be critical which version
of it you install, but it's possible that the API has changed over
time.  Currently, the version from `01.beta.32` is known to work, so
`(cd <dqroot>/tags/01.beta.32 && python setup.py install)` to install
it.

Finally check and install `djq` itself.

* Run the tests: from the toplevel `djq` directory say `make test`:
  everything should be fine.
* Install `djq`: from the same directory run `python setup.py install`
  (or `python setup.py develop` if you might want to make changes or
  do other work on `djq`).

After doing this, you should be able to find `djq`:

```
$ type -p djq
/local/tfb/packages/cmip6-dreq/envs/djq-development/bin/djq
```

(Output will differ, but it should be there).

## Installation smoke tests
`djq` needs to know where the DREQ is: the path I called `<dqroot>`
above.  It has a built-in default but this will always be wrong in
practice.  You either need to tell it with a command-line option, or
by setting the environment variable `DJQ_DQROOT`.

The most basic possible test of `djq` is then to feed it an empty
query and check it returns an empty result:

```
$ echo '[]' | djq -r <dqroot>
[]
$ echo '[]' | djq -r <dqroot> -v -v
root <dqroot> tag latest
from -
[]
```

If this works then it is basically working.

You can also run the sanity checks: from the top-level `djq` directory
say `make sanity`.  This first of all runs the unit tests as above,
and then does a comparison of the results computed by `djq` to the
spreadsheet for the same DREQ version.  If this comparison fails, it
*may* be `djq`'s fault, but it also may be due to a bug in the DREQ
release.  You can test a specific release by, for instance

```
make sanity DREQ_TAG=01.beta.32
```

which should work.  The default tag is `latest`.

## Samples
There are also samples, in the `samples` directory:

* `samples/python` has samples of the Python interface;
* `samples/json` has sample JSON files usable by either interface.

There is at least some documentation for these in the corresponding
`README.md` files.