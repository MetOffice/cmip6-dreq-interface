# Just do some comparisons to save remembering them
#
# This is experimental code
#

from djq.low import chatter
from djqxlsx import *

dmap = DJQMap()
xmap = XLSXMap()

def prune(mtmap, name):
    # Prune destructively
    #
    # first UIDs which are altogether absent from the dreq
    badness = mtmap.missing_uids()
    if len(badness) > 0:
        chatter("{}: pruning {} missing variables", name, len(badness))
        mtmap.results = mtmap.prune_missing_uids()
    # now remove variables with empty mipsets
    badness = mtmap.miptables_with_empty_mipsets()
    if len(badness) > 0:
        chatter("{}: pruning empty mipsets from", name)
        for mt in sorted(badness):
            chatter(" {}", mt)
        mtmap.results = mtmap.prune_empty_mipsets()
    # prune any miptables which are either newly empty or were already
    # empty
    badness = mtmap.empty_miptables()
    if len(badness) > 0:
        chatter("{}: pruning empty miptables", name)
        for mt in sorted(badness):
            chatter(" {}", mt)
        mtmap.results = mtmap.prune_empty_miptables()
    return mtmap.results

dresults = prune(dmap, "dmap")
xresults = prune(xmap, "xmap")

def rtcounts(rt):
    return tuple(sorted(((mt, len(vs)) for (mt, vs) in rt.iteritems()),
                        key=lambda x: x[0]))

drcounts = rtcounts(dresults)
xrcounts = rtcounts(xresults)

if set(dresults.keys()) != set(xresults.keys()):
    # failed horribly to even be the same miptables
    chatter("keys differ")
    xrk = set(xresults.keys())
    drk = set(dresults.keys())
    if len(xrk - drk) > 0:
        chatter("xresults extras")
        for k in sorted(xrk - drk):
            chatter(" {}", k)
    if len(drk - xrk) > 0:
        chatter("dresults extras")
        for k in sorted(drk - xrk):
            chatter(" {}", k)
else:
    # miptables are OK, so we know we can go through drcounts and
    # xrcounts
    assert len(drcounts) == len(xrcounts), "madness"
    for i in range(len(drcounts)):
        dc = drcounts[i]
        xc = xrcounts[i]
        assert dc[0] == xc[0], "more madness"
        if dc[1] != xc[1]:
            chatter("{}: dc = {}, xc = {}", dc[0], dc[1], xc[1])

def rtvars(rt):
    return {mt: set(vs.keys()) for (mt, vs) in rt.iteritems()}

dvars = rtvars(dresults)
xvars = rtvars(xresults)
