<!-- (C) British Crown Copyright 2016, Met Office.
     See LICENSE.md in the top directory for license details. -->

# `djq`: the CMIP6 Data request JSON Query tool
`djq` is a program which can be used to query the [CMIP6 data
request](https://w3id.org/cmip6dr) (DREQ below): you can hand it requests
specifying MIPs and experiments within those MIPs and it will reply
with lists of variables.

See the [documentation directory](doc/).

There are [some samples](samples/): not yet very complete.

There is some code to compare what `djq` computes with various other
sources of information in [comparisons](comparisons/): there's nothing
installable here, but it may be worth running the tests there to make
sure things make sense.

## Basic sanity checks
To run any checks you will need a DREQ checkout.  Set the environmnent
variable `DJQ_DQROOT` to point at the root of the checkout to tell
everything where it is.  Nothing will work unless this is set.

Running `make sanity` in this directory will run any checks
which are fit to be run.  This currently includes:

* unit tests (run these on their own with `make test`);
* some comparisons (run these on their own with `make compare`).

If any of this fails then something is probably wrong.  However if the
comparisons fail it may be that something is wrong with the DREQ and
not `djq` itself.  If that happens, try `make compare
DREQ_TAG=01.beta.32` to compare against a DREQ tag which should be
good.  There are in fact two options you can give to `make compare`:

* `DREQ_TAG` controls the tag which is loaded;
* `DREQ_SPREADSHEET_COLS` controls the number of columns expected to
  be in the spreadsheet -- this was once 24 but is now 28, so if
  running `make compare` with an old release you may need to force
  this to be 24.

Currently it should be the case that

```
$ make compare DREQ_TAG=01.beta.32 DREQ_SPREADSHEET_COLS=24
```

will work.