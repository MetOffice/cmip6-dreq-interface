<!-- (C) British Crown Copyright 2016, 2018 Met Office.
     See LICENSE.md in the top directory for license details. -->

# Command line interfaces for `djq`
There are three command line programs ('scripts') associated with `djq`:

* `djq` is the main thing: you can use it to make queries and get
  answers;
* `all-requests` is a little program which reads the DREQ, and then
  generates a request for every experiment in every MIP, which can be
  fed to `djq` to run a really comprehensive set of queries;
* `scatter-replies` is another little program which will read a set of
  replies from `djq` and spit them out into files named after the MIPs
  and experiments.

The result of all this is that you can run something like this (do
this in a scratch directory as it will make a large number of files):

```
$ all-requests | djq | scatter-replies
```

This pipeline takes perhaps five minutes to run (the default
`djq.variables.cv_invert_varmip` implementation is pretty inefficient
when given a lot of nearly-identical requests) and needs a reasonably
significant amount of memory (4GB seems to be enough, 1GB is not).
For the current request (`01.beta.32`) it produces nearly 900MB in 284
files.

## `djq`: a command line interface to querying the DREQ
`djq` is the original interface: in it's simplest form it reads a
query from a file, or standard input if none is given, and prints the
results on standard output.  There are options to specify how verbose
it should be, what back end to use and so on.  `djq -h` will print a
usage message:

```
usage: djq [-h] [-r DQROOT] [-t DQTAG] [-u] [-p DQPATH] [-i IMPLEMENTATION]
           [-j JSONIFY_IMPLEMENTATION] [-v] [-d] [-b] [-c CHECK_PRIORITY]
           [-o OUTPUT]
           [request]
```

Here are some details:

* *request* is a file containing a request.  If no file is given then
  it will read from standard input.  This means that `djq` on its own
  will simply wait for you to type something.
* `-o` *OUTPUT* specifies where output should be written, with the
  default being standard output.
* `-r` *DQROOT* lets you specify where the DREQ checkout is.  By
  default it will listen to the `DJQ_DQROOT` environment variable (and
  there is a fallback default which will never be right).
* `-t` *DQTAG* allows you to specify the tag.  This is defaulted from
  the `DJQ_DQTAG` environment variable, with a fallback to `latest`
  (which often is right).
* `-u` will load the DREQ from the trunk rather than from a tag.
* `-p` *PATH* is an alternative way of specifying where the XML files
  are: if given it should be a directory containing the XML files for
  the DREQ (in the DREQ distribution this is a directory which looks
  like `.../dreqPy/docs/`).  If this option is given then the root and
  tag options are ignored.
* `-i` *IMPLEMENTATION* lets you set the implementation for computing
  variables.  See the [the API documentation](Pythin-interface.md) and
  [the implementations documentation](Implementations.md).
* `-j` *JSONIFY_IMPLEMENTATION* does the same for JSONifiers.  Note
  that there is only one such provided at present (although you can
  easily write your own).
* `-v` increases the verbosity.  You can repeat this to make it
  increasingly verbose: twice is useful, and three times might be;
  more than that probably is not.
* `-d` turns on debugging output, which is probably only interesting
  to me.
* `-b` doesn't suppress backtraces if some error propagates to the
  top-level, and is again mostly for debugging.
* `-c` *CHECK_PRIORITY* sets the level of various internal checks
  which will run: again, this is a debugging switch really.  The
  default level lets all checks run, which is right.
* And finally `-h` gives some help.

### An example of `djq`
```
$ djq -v -o deck-all-out.json samples/json/deck-all.json
root /local/tfb/packages/CMIP6dreq tag latest
from samples/json/deck-all.json to deck-all-out.json
* single-request
  mip DECK experiment True implementation djq.variables.cv_default
[pruned 21 invalid vars]
[pruned 87 dubious vars]
  -> 1943 variables
$ wc deck-all-out.json
 147695  925526 7646536 deck-all-out.json
```

### Notes on `djq`
All 'noise' output -- debugging and verbosity -- appears on standard
error.  However some versions of the DREQ interface have been noisy on
standard output.  You can deal with this by using `-o` to cause it to
explicitly put the results in a file.

## `all-requests`: create all requests for `djq`
`all-requests` is a program which reads the DREQ and then emits a JSON
request for every experiment in every MIP, including requests for all
and no experiments for each MIP.  It has some of the same options that
`djq` has.

```
usage: all-requests [-h] [-r DQROOT] [-t DQTAG] [-u] [-p DQPATH] [-v] [-d]
                    [-b] [-c CHECK_PRIORITY]
                    [output]```

* *output* tells it where the output should go: by default it is
standard output.
* `-r` *DQROOT* sets the root, as for `djq`.
* `-t` *DQTAG* sets the tag.
* `-u` loads from the trunk rather than from a tag.
* `-p` *PATH* specifies where the XML files are explicitly.
* `-v` makes it more verbose.
* `-d` prints internal debugging output.
* `-b` does not suppress backtraces.
* `-c` *CHECK_PRIORITY* controls internal checks.
* `-h` prints some help.

All of these options are equivalent to those for `djq`.  However
`all-requests` has much less to it than `djq` and, while some of them
set thresholds for checks, for instance, there are no actual checks to
run.

### An example of `all-requests`
```
$ all-requests -v -t 01.beta.20| wc
root /local/tfb/packages/CMIP6dreq tag 01.beta.20
to -
   1078    1616   14994
```

This asking it to produce all the requests for the `01.beta.20` tag.

### Notes on `all-requests`
If you specify a tag you want to specify the *same* tag to the
corresponding `djq` run.

## `scatter-replies`: scatter replies from `djq` into files
`scatter-replies` is a program which reads a reply from `djq` and
scatters its individual *single-reply*s into files, named after the
MIP and experiment.  The files are named as `<project>_<mip>_<experiment>.json`
where:

* `<project>` is the name of the project, which is `cmip6` by default;
* `<mip>` is the name of the MIP, in lower case;
* `<experiment>` is the name of the experiment, in lower case, *or*
  `ALL` meaning 'all experiments' or `NONE` meaning 'no experiments'.

It has some of the same options as `djq`:

```
usage: scatter-replies [-h] [-v] [-d] [-b] [-c CHECK_PRIORITY]
                       [-o OUTPUT_DIRECTORY] [-p PROJECT]
                       [replies]
```

* *replies* is a file of replies, with standard input being the
   default.
* `-o` *OUTPUT_DIRECTORY* specifies the directory where the scattered
  files should live, with the default being the current directory.
  This directory (and all its parents) is created if it does not
  exist.
* `-p` *PROJECT* specifies the project name, which is `cmip6` by
  default.

The remaining options are as for `djq`, but again there is less to
`scatter-replies` than `djq` so some of them don't actually do
anything.

### An example of `scatter-replies`
This example shows it being run in a pipeline with `all-requests` and
`djq`.

```
$ all-requests | djq | scatter-replies -v -o /tmp/replies
scattering from - to /tmp/replies
scattered 284 replies
$ ls /tmp/replies|wc
    284     284    6537
$ du -sh /tmp/replies
872M   	/tmp/replies
```

This pipeline takes several minutes to run.

### Notes on `scatter-replies`

Surprisingly, `scatter-replies` requires more resources than the other
two programs: significantly it requires more memory.  This is because
it has to read a (generally very large) JSON stream into memory, and
the Python JSON reader is not very efficient (in particular the
structures it produces are much larger than the equivalent structure
that `djq` wrote).  There is some interning code in it to make it
smaller, and this allows it to run on machines with modest memory (4GB
is fine).

The program creates a lot of files: you almost certainly want to run
it in a scratch directory or use the `-o` option.