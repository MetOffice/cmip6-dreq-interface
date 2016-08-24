# 20160822
This is the initial release.

## `djq`
This fails its sanity test with any release of the DREQ newer than
`01.beta.32` (currently this means either `01.beta.33` or
`01.beta.34`).  I strongly suspect this is due to problems with the
DREQ, but I haven't checked it in detail.  In the mean time, use it
with `01.beta.32` either explicitly or by setting the `DJQ_DQTAG`
environment variable:

```
DJQ_DQTAG=01.beta.32; export DJQ_DQTAG
```

## `dqi`
This has very little documentation and hasn't been looked after for a
while.