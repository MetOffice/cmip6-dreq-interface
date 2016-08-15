# `djq`: the CMIP6 Data request JSON Query tool
`djq` is a program which can be used to query the [CMIP6 data
request](w3id.org/cmip6dr) (dreq below): you can hand it requests
specifying MIPs and experiments within those MIPs and it will reply
with lists of variables.

See the [documentation directory](doc/).

There is some code to compare what `djq` computes with various other
sources of information in [comparisons](comparisons/): there's nothing
installable here, but it may be worth running the tests there to make
sure things make sense.
