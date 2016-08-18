# `djq`: the CMIP6 Data request JSON Query tool
`djq` is a program which can be used to query the [CMIP6 data
request](w3id.org/cmip6dr) (DREQ below): you can hand it requests
specifying MIPs and experiments within those MIPs and it will reply
with lists of variables.

See the [documentation directory](doc/).

There are [some samples](samples/): not yet very complete.

There is some code to compare what `djq` computes with various other
sources of information in [comparisons](comparisons/): there's nothing
installable here, but it may be worth running the tests there to make
sure things make sense.

## Basic sanity checks
If you run `make sanity` in this directory it will run any checks
which are fit to be run.  This currently includes:

* unit tests (run these on their own with `make test`);
* some comparisons (run these on their own with `make compare`).

If any of this fails then something is probably wrong.  However if the
comparisons fail it may be that something is wrong with the DREQ and
not `djq` itself.  If that happens, try `make compare
DREQ_TAG=01.beta.32` to compare against a DREQ tag which should be
good.
