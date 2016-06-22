# Samples for `djq`
The samples in this directory are things I used during the development of `djq`.  Unfortunately you can't put comments in JSON so they're not very self-descriptive.

A good way to run `djq` on one of these files is to turn on all the debugging and verbosity you can, and don't suppress backtraces if it falls over horribly.  You do this with an incantation like

```
djq -b -v -v -d <input-file.json >output-file.json
```

Some of the samples produce a *lot* of output as you'd expect.

Here's what it should look like with everything turned on:

```
$ djq -b -v -v -d <acm-compare-tags.json >/dev/null
enabled True minpri 0
root /local/tfb/packages/CMIP6dreq tag latest
from -
* single-request tag 01.beta.29
missed 01.beta.29, loading dreq
  mip AerChemMIP experiment HISTghg
[passed variables.compute/0/preset-safety]
      HISTghg
  -> 786 variables
* single-request tag latest
missed latest, loading dreq
  mip AerChemMIP experiment HISTghg
[passed variables.compute/0/preset-safety]
      HISTghg
  -> 786 variables
```

It is generally more useful with just one `-v` and certainly without `-d`:

```
$ djq -v  <acm-compare-tags.json >/dev/null
root /local/tfb/packages/CMIP6dreq tag latest
from -
* single-request tag 01.beta.29
  mip AerChemMIP experiment HISTghg
  -> 786 variables
* single-request tag latest
  mip AerChemMIP experiment HISTghg
  -> 786 variables
```

## The current samples
The `acm-*.json` files look experiments from `AerChemMIP` (because it is at the start of the alphabet):

* `acm-single.json` is one request which should work;
* `acm-miponly.json` just asks for the variables the MIP itself wants;
* `acm-all.json` asks for the variables for all experiments (and the MIP);
* `acm-badexpt.json` asks for a non-existent experiment and should elicit a `not-found` reply;
* `acm-notag.json` asks for a non-existent DREQ tag and should get an error response;
* `acm-compare-tags.json` asks for the same MIP and experiment from two DREQ tags and will make a lot of output.

The `bogus-*.json` files are all syntactically bogus (the unit tests should catch this, but you can point at them as well).  Apart from the last one -- `bogus-almost-ok.json` -- these should all cause catastrophes (and if you use `-b` backtraces): the last should elicit a `bad-request` reply.