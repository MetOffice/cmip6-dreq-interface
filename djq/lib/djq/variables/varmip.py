"""Working from variables to MIPs.  None of this code is an interface in djq.
"""

# This is meant to be functionality which several modules might use
#
# Note that some of this originated in dqi.
#

__all__ = ('mips_of_cmv', 'priority_of_cmv_in_mip',
           'validp', 'dqtype')

from djq.low import DJQException

class BadDreq(DJQException):
    # bad dreq (is this internal or external?)
    pass

def dqtype(item):
    # an item's type in the request
    return item._h.label

def validp(item):
    # something is valid if its dqt is not 'remarks'
    return dqtype(item) != 'remarks'

def mips_of_cmv(dq, cmv, exids=True):
    # Return a set of the mips of a CMORvar in dq.  If exids is given
    # it should be a set of experiment IDs, and only MIPs for those
    # experiments are included.  If it is True (specifically True, not
    # just something which is not false) then all experiments are
    # included, and if it is false then no experiments are included.
    #
    # This is a simplified version of vrev.checkVar.chkCmv (in
    # vrev.py) But it is simpler in the sense that I do not understand
    # what the original code really does, so I have just tried to make
    # something which is a bit less horrible and which might do
    # something useful.
    #
    # This originated in dqi.walker but has been changed since then.
    # The argument convention is slightly mutant (cmv as an object,
    # but ids of experiments).
    #

    # requestVar ids which refer to cmv and whose groups are valid
    rvids = set(rvid for rvid in dq.inx.iref_by_sect[cmv.uid].a['requestVar']
                if validp(dq.inx.uid[dq.inx.uid[rvid].vgid]))

    # construct a dict mapping from variable group id to the highest
    # priority in that group
    vgpri = dict()
    for rvid in rvids:
        rv = dq.inx.uid[rvid]   # the requestVar
        rvp = rv.priority       # its priority
        vgid = rv.vgid          # its group
        if vgid not in vgpri or rvp > vgpri[vgid]:
            vgpri[vgid] = rvp

    linkids = set()
    for (vgid, pri) in vgpri.iteritems():
        if dq.inx.iref_by_sect[vgid].a.has_key('requestLink'):
            for rlid in dq.inx.iref_by_sect[vgid].a['requestLink']:
                rl = dq.inx.uid[rlid] # requestLink
                if rl.opt == 'priority':
                    # if it has a priority, add it if it is high
                    # enough. This is what he does: rounding?
                    if int(float(rl.opar)) > pri:
                        linkids.add(rlid)
                else:
                    # no priority, just add it
                    linkids.add(rlid)

    # OK, so here is the first chunk of mips: just the mip fields of
    # all these requestLink objects
    mips = set(dq.inx.uid[rlid].mip for rlid in linkids)

    if exids:
        # Now deal with experiments, if asked
        #

        # The IDs of all the experimenty things corresponding to the
        # requestLinks, I think
        esids = set(dq.inx.uid[u].esid
                    for rlid in linkids
                    for u in dq.inx.iref_by_sect[rlid].a['requestItem'])

        # Empty IDs can leak in (which is looks like is a bug?)
        esids.discard('')

        for esid in (esid for esid in esids
                     if validp(dq.inx.uid[esid])):
            # what sort of thing is this
            dqt = dqtype(dq.inx.uid[esid])
            if dqt == 'mip':
                # it's a MIP, directly, just add this
                mips.add(esid)
            elif dqt == 'experiment':
                # It's an experiment
                if exids is True or esid in exids:
                    mips.add(dq.inx.uid[esid].mip)
            elif dqt == 'exptgroup':
                # It's a group
                for exid in dq.inx.iref_by_sect[esid].a['experiment']:
                    if exids is True or exid in exids:
                       mips.add(dq.inx.uid[exid].mip)
            else:
                raise BadDreq("{} isn't an experiment, group or mip"
                              .format(dqt))
    return mips

def priority_of_cmv_in_mip(dq, cmv, mip):
    # Compute the priority of a CMV in a MIP.
    #
    # Find all the requestVars which refer to cmv and whose groups are
    # valid and which refer to mip, and compute the maximum priority
    # of that set.  If the set is empty (which it can be), just use
    # the default from the variable.
    #
    priorities = tuple(rv.priority
                       for rv in (dq.inx.uid[rvid]
                                  for rvid in
                                  dq.inx.iref_by_sect[cmv.uid].a['requestVar'])
                       if (validp(dq.inx.uid[rv.vgid])
                           and rv.mip == mip))
    if len(priorities) > 0:
        return max(priorities)
    else:
        return cmv.defaultPriority
