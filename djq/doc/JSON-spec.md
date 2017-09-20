<!-- (C) British Crown Copyright 2016, Met Office.
     See LICENSE.md in the top directory for license details. -->

# DREQ JSON interface
This document describes the [JSON](http://json.org/) syntax that `djq` understands.

## Notes
Everything should be case-insensitive unless that is not possible.  Case should be preserved unless that is hard.  All the syntactical details are [JSON](http://json.org/): if this conflicts with that, then this is wrong.

While this document describes the JSON syntax, `djq` uses the standard Python [JSON](https://docs.python.org/2/library/json.html) interface with no special options set, so the Python-level data structures used by the Python interface correspond to the structures described here in a fairly straightforward way as defined by that interface.

For replies, the specification below applies to the default JSONifier.

In the syntax below nonterminals are in *italics*, optional things are in (parentheses).  The formatting leaves much to be desired, but it's all I could manage given the contstraints of Markdown.

## Request
|||
|---:|:---|
| *request*|array of *single-requests* |
| *single-request*|object, with keys as follows |
||(`"dreq"`): identifies the DREQ version: this is the SVN tag in the implementation |
||`"mip"`: the name of the MIP, a string |
||`"experiment"`: the name of experiment within the MIP, a string, or `true` meaning 'all experiments in the MIP', or `false` or `null` meaning 'just the direct MIP variables', with the normal stringy case returning the variables specified by the MIP *and* the experiment |
||other keys may be present, and must have names which begin with the string `"request-"` |

### Example requests
A request for a single MIP and experiment

```JSON
[{"dreq": "b27",
  "mip": "DECK",
  "experiment": "control"}]
```

A request for for just direct MIP variables

```JSON
[{"dreq": "b27",
  "mip": "DECK",
  "experiment": null}]
```

(in this case, the experiment could also be given as `false`).

### Notes
The reason that *requests* are arrays of *single-requests* is to allow multiple requests to be bundled, and to allow extra data to be provided in due course.

## Reply
A reply is either an array of *single-reply*s, or a single *catastrophic-reply* object, if something horrible went wrong.  These two cases are immediately distinguishable: if you get an array then all is basically well, if you don't then a catastrophe has happened.

What is described here is what the default JSONifier does.  The JSONifier is responsible for returning an object which is used as the value of the `"reply-variables"` field, which by default is an array of *single-reply-variables*: any alternative JSONifier may alter what appears here.

|||
|---:|:---|
| *reply*|**either** array of *single-reply*s, **or** a *catastrophic-reply* |
| *single-reply*|object with keys as follows |
||`"dreq"`: the DREQ version.  This is the actual version of the DREQ which was loaded: if it's different than what was in the request there is usually a problem.  However note that if you asked for `"latest"` you will get a specific version back. |
||`"mip"`: as in request |
||`"experiment"`: as in request |
||`"reply-variables"`: an array of *single-reply-variable*s, or `null`, in which case `"reply-status"` will not be `"ok"` |
||`"reply-status"`: one of `"ok"` (normal reply), `"not-found"` (MIP or experiment not found), `"bad-request"` (request was ill-formed) or `"error"` (something went wrong).  In anything but the first case there may be more information in `"reply-status-detail"` |
||(`"reply-status-detail"`): a string providing additional information if something went wrong: this is only present if `"reply-status"` is not `"ok"` |
||`"reply-metadata"`: an object containing some metadata about the reply, useful for debugging.  There are a number of fields in this object, none of which are stable. |
||possible additional keys: any additional keys must begin with the string `"reply-"`, except that any additional keys and values from the request will be returned unaltered |
| *single-reply-variable*|object with keys as follows |
||`"label"`: the label of the variable, a string |
||`"miptable"`: the miptable name, a string |
||`"priority"`: the highest priority across all MIPs, a number (probably an integer?) |
||`"mips"`: an array of *variable-mip-information*s |
||possibly other keys TBD |
| *variable-mip-information*|an object describing MIP-related information for a *single-reply-variable*, with keys as follows |
||`"mip"`: the name of the MIP, a string |
||`"priority"`: the priority in the MIP, a number |
||`"objectives"`: an array of strings describing MIP objectives |
| *catastrophic-reply*|an object with keys as follows |
||`"catastrophe"`: a string describing the catastrophe |
||other keys which may describe the nature of the catastrophe |

### Notes
Each *single-request* will have exactly one *single-reply* and the `"dreq"`, `"mip`" and `"experiment`" as well as any additional request keys will be the same as in the request.  *single-reply*s should be in the same order as the *single-request*s they are replies to.

### Examples
An example successful reply might look like:

```JSON
[{"mip": "DECK",
  "experiment": "control",
  "dreq": "b27",
  "reply-status": "ok",
  "reply-metadata": {...},
  "reply-variables": [{"label": ...,
                       "miptable": ...,
                       "priority": ...,
                       "mips": [{"mip": ...,
                                 "priority": ...,
                                 "objectives: [...]},
                                ...]},
                      ...]}]
```

An error response would be:

```JSON
[{"mip": "DECK",
  "dreq": "b27",
  "experiment": "control",
  "reply-status": "error",
  "reply-status-detail": "computer on fire",
  "reply-metadata": {...},
  "reply-variables": null}]
```

Finally, a catastrophic response might be:

```JSON
{"catastrophe": "your JSON isn't JSON"}
```
