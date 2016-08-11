# Just do some comparisons to save remembering them
#
# This is experimental code.  Running it as a script does all the
# checks and returns a useful exit code.
#

from sys import exit
from djq.low import chatter
from djqxlsx import *

dmap = DJQMap()
xmap = XLSXMap()
assert dmap.dq == xmap.dq, "mismatched dqs"
dq = dmap.dq

badnesses = 0

def prune(mtmap, name):
    # Prune bad things from a map object destructively, reporting if things
    # are being pruned
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

# Report on miptable sets matching, and any differences in variable
# lists

if set(dresults.keys()) != set(xresults.keys()):
    # failed horribly to even be the same miptables
    chatter("keys differ")
    badnesses += 1
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
    for miptable in sorted(dresults.keys()):
        if len(dresults[miptable]) != len(xresults[miptable]):
            badnesses += 1
            chatter("{}: dc = {}, xc = {}", miptable,
                    len(dresults[miptable]), len(xresults[miptable]))

# Sanity check that all the variables refer to the miptables they belong to
#
def vars_consistent_p(varmap, dq):
    inx = dq.inx.uid
    for (miptable, uidmap) in varmap.iteritems():
        for uid in uidmap.keys():
            if inx[uid].mipTable != miptable:
                return False
    return True

if not vars_consistent_p(dresults, dq):
    badnesses += 1
    chatter("DJQ results are inconsistent")
if not vars_consistent_p(xresults, dq):
    badnesses += 1
    chatter("XLSX results are inconsistent")

# Check the actual var sets are the same (or not)
#

def report_mt_var_differences(t1, t2, dq):
    # Report differences in vars in each miptable (by assumption the
    # miptable sets are the same by now)
    inx = dq.inx.uid

    def report(vs, where):
        for (v, uid) in sorted(((inx[uid].label, uid) for uid in vs),
                               key=lambda x: x[0]):
            chatter("{} extra {} ({})", where, v, uid)

    assert frozenset(t1.keys()) == frozenset(t2.keys()), "madness"
    bad = False
    for mt in sorted(t1.keys()):
        t1vs = frozenset(t1[mt].keys())
        t2vs = frozenset(t2[mt].keys())
        if t1vs != t2vs:
            chatter("{}", mt)
            report(t1vs - t2vs, " lhs")
            report(t2vs - t1vs, " rhs")
            bad = True
    return bad

if report_mt_var_differences(dresults, xresults, dq):
    badnesses += 1
    chatter("some miptables don't match")

# And check the mips
#

def report_mt_varmip_differences(t1, t2, dq):
    # Report mismatched mip sets

    def report(mips, where):
        for mip in sorted(mips):
            chatter("{} extra {}", where, mip)

    inx = dq.inx.uid
    assert frozenset(t1.keys()) == frozenset(t2.keys()), "madness"
    bad = False
    for mt in sorted(t1.keys()):
        for uid in (frozenset(t1[mt].keys()) & frozenset(t2[mt].keys())):
            lb = inx[uid].label
            t1mips = t1[mt][uid]
            t2mips = t2[mt][uid]
            if t1mips != t2mips:
                chatter("{}/{} ({})", mt, lb, uid)
                report(t1mips - t2mips, " lhs")
                report(t2mips - t1mips, " rhs")
                bad = True
    return bad

if report_mt_varmip_differences(dresults, xresults, dq):
    badnesses += 1
    chatter("some mipsets don't match")

if __name__ == '__main__':
    if badnesses == 0:
        chatter("OK")
        exit(0)
    else:
        exit("a badness"
             if badnesses == 1
             else "many badnesses")
