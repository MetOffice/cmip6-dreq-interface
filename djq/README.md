# `djq`: the CMIP6 Data request JSON Query tool
`djq` is a program which can be used to query the [CMIP6 data
request](w3id.org/cmip6dr) (dreq below): you can hand it requests
specifying MIPs and experiments within those MIPs and it will reply
with lists of variables.

This documentaton only currently deals with the requirements to
install `djq`: the specifications of the JSON queries and the
behaviour of the program itself is missing so far, as are any
examples.

This is all extremely incomplete and preliminary.

## Installation
### Requirements
`djq` requires:

* Python 2.7;
* the Python [nose](https://pypi.python.org/pypi/nose) library for
  tests;
* an installed copy of the dreq Python interface (so `import dreqPy`
  must work);
* a checkout of the [Subversion
  dreq](http://proj.badc.rl.ac.uk/svn/exarch/CMIP6dreq/) from the root
  (so tags are available);

### Installation using Conda
The way I install `djq` is using [Conda](http://conda.pydata.org/),
which provides an encapsulated, controllable environment independent
of the vagaries whatever of version of Python is installed on the
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

Now checkout the top level of the dreq to a known directory:

```
svn co http://proj.badc.rl.ac.uk/svn/exarch/CMIP6dreq
```

It is important you fetch the top level, *not* a tag or a branch, as
`djq` wants to be able to specify a tag to use in the request, so you
can select which version of the dreq to load.  I'll refer to this
directory as `<dqroot>` below.

Install the `dreqPy` library.  It should not be critical which version
of it you install, but it's possible that the API has changed over
time.  Currently, the version from `01.beta.29` is known to work, so
`(cd <dqroot>/tags/01.beta.29 && python setup.py install)` to install
it.

Finally check and install `djq` itself.

* Run the tests: from the directory containing this file say
  `nosetests`: they should all pass.
* Install `djq`: from the same directory run `python setup.py install`
  (or `python setup.py develop` if you might want to make changes or
  do other work on `djq`).

After doing this, you should be able to find `djq`:

```
$ type -p djq
/local/tfb/packages/cmip6-dreq/envs/djq-development/bin/djq
```

(Output will differ, but it should be there).

### Installation smoke test
`djq` needs to know where the dreq is: the path I called `<dqroot>`
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

If you are in the toplevel directory of the `djq` distribution you can
also point it at sample files in the `samples` directory which
represent various queries.  See the `README.md` in that directory.