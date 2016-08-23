# Just do some comparisons to save remembering them
#
# This is experimental code.  Running it as a script does all the
# checks and returns a useful exit code.  Other than that it is just
# messy: it tangles up reporting and tests in a horrid way.
#

from sys import exit
from os import getenv
from djq.low import chatter
from djqxlsx import *

def prune(mtmap):
    # Prune bad things from a map object destructively, reporting if
    # things are being pruned.  Return the object
    #
    # first UIDs which are altogether absent from the dreq
    name = mtmap.name
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
    return mtmap

# report_* functions return true if they found anything bad
#

def report_miptable_differences(m1, m2):
    # report differences in the miptables that exist
    badness = False
    (t1, n1) = (m1.results, m1.name)
    (t2, n2) = (m2.results, m2.name)
    if set(t1.keys()) == set(t2.keys()):
        return 0
    else:
        # failed horribly to even be the same miptables
        chatter("keys differ")
        badness = True
        xrk = set(t2.keys())
        drk = set(t1.keys())
        if len(xrk - drk) > 0:
            chatter("{} extras", n2)
            for k in sorted(xrk - drk):
                chatter(" {}", k)
        if len(drk - xrk) > 0:
            chatter("{} extras", n1)
            for k in sorted(drk - xrk):
                chatter(" {}", k)
        return badness

def report_mt_count_differences(m1, m2):
    # report miptable count differences
    badness = False
    (t1, n1) = (m1.results, m1.name)
    (t2, n2) = (m2.results, m2.name)
    for miptable in sorted(t1.keys()):
        if len(t1[miptable]) != len(t2[miptable]):
            badness = True
            chatter("{}: {} = {}, {} = {}", miptable,
                    n1, len(t1[miptable]), n2, len(t2[miptable]))
    return badness

def vars_consistent_p(m):
    # check a map is consistent: all variables in each miptable should
    # point at the miptable
    inx = m.dq.inx.uid
    for (miptable, uidmap) in m.results.iteritems():
        for uid in uidmap.keys():
            if inx[uid].mipTable != miptable:
                return False
    return True

def report_mt_var_differences(m1, m2):
    # Report differences in vars in each miptable (by assumption the
    # miptable sets are the same by now: the assertion checks this.
    (t1, n1) = (m1.results, m1.name)
    (t2, n2) = (m2.results, m2.name)
    inx = m1.dq.inx.uid

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
            report(t1vs - t2vs, " {}".format(n1))
            report(t2vs - t1vs, " {}".format(n2))
            bad = True
    return bad

def report_mt_varmip_differences(m1, m2):
    # Report mismatched mip sets for each variable.  Miptables are
    # assumed to match: the assertion checks this.

    def report(mips, where):
        for mip in sorted(mips):
            chatter("{} extra {}", where, mip)

    (t1, n1) = (m1.results, m1.name)
    (t2, n2) = (m2.results, m2.name)
    inx = m1.dq.inx.uid
    assert frozenset(t1.keys()) == frozenset(t2.keys()), "madness"
    bad = False
    for mt in sorted(t1.keys()):
        for uid in (frozenset(t1[mt].keys()) & frozenset(t2[mt].keys())):
            lb = inx[uid].label
            t1mips = t1[mt][uid]
            t2mips = t2[mt][uid]
            if t1mips != t2mips:
                chatter("{}/{} ({})", mt, lb, uid)
                report(t1mips - t2mips, " {}".format(n1))
                report(t2mips - t1mips, " {}".format(n2))
                bad = True
    return bad

def load_and_prune_maps(tag=None):
    # load the maps and prune them
    if tag is None:
        tag = getenv("DREQ_TAG")
    if tag is not None:
        chatter("dreq tag {}", tag)

    return(prune(DJQMap(tag=tag)),
           prune(XLSXMap(tag=tag)))

def count_badnesses(dmap, xmap):
    # Find what badnesses there are, and count them
    badnesses = 0

    # check to see if there are the same set of miptables after
    # pruning
    if report_miptable_differences(dmap, xmap):
        # We can't go on from this
        return 1

    # report count of differences in how many variables there are in
    # each table
    if report_mt_count_differences(dmap, xmap):
        badnesses += 1

    # Sanity check that all the variables refer to the miptables they
    # belong to
    #
    for m in (dmap, xmap):
        if not vars_consistent_p(m):
            badnesses += 1
            chatter("{} results are inconsistent", m.name)

    # Check the actual var sets are the same (or not)
    #
    if report_mt_var_differences(dmap, xmap):
        badnesses += 1
        chatter("some miptables don't match")

    # And check the mips
    #
    if report_mt_varmip_differences(dmap, xmap):
        badnesses += 1
        chatter("some mipsets don't match")

    return badnesses

if __name__ == '__main__':
    (dmap, xmap) = load_and_prune_maps()
    badnesses = count_badnesses(dmap, xmap)
    if badnesses == 0:
        chatter("OK")
        exit(0)
    else:
        exit("There is a badness"
             if badnesses == 1
             else "There are many badnesses")
