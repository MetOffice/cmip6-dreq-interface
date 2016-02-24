# See makeTables.py

from collections import defaultdict
from dreqPy.dreq import loadDreq

dq = loadDreq()

cmvs = sorted(dq.coll['CMORvar'].items, cmp=lambda x,y: cmp(x.label, y.label))
miptables = sorted(set(v.mipTable for v in cmvs))

def validp(thing):
    # Missing pointers have headers with label 'remarks' (I think)
    return thing._h.label != 'remarks'

def dict_of(thing, attrs):
    return {attr: getattr(thing.attr) for attr in attrs}

def mips_of(cmv):
    # This is a simplified version of vrev.checkVar.chkCmv (in
    # vrev.py) But it is simpler in the sense that I do not understand
    # what the original code really does, so I have just tried to make
    # something which is a bit less horrible and which might do
    # something useful.  In particular it does not deal with any of
    # the experiment stuff.

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
    for vgid in vgpri:
        if dq.inx.iref_by_sect[vgid].a.has_key('requestLink'):
            for rlid in dq.inx.iref_by_sect[vgid].a['requestLink']:
                rl = dq.inx.uid[rlid] # requestLink
                if rl.opt == 'priority':
                    # if it has a priority, add it if it is high enough
                    p = int(float(rl.opar)) # this is what he does: rounding?
                    if vgpri[vgid] <= p:
                        linkids.add(rlid)
                else:
                    # no priority, just add it
                    linkids.add(rlid)

    return set(dq.inx.uid[rlid].mip for rlid in linkids)

for table in miptables:
    for cmv in cmvs:
        if cmv.mipTable == table:
            var = dq.inx.uid[cmv.vid]   # var of the CMOR var
            strc = dq.inx.uid[cmv.stid] # structure of the CMOR var
            if validp(var) and validp(strc):
                sshp = dq.inx.uid[strc.spid] # spatial shape
                tshp = dq.inx.uid[strc.tmid] # temporal shape
                if validp(sshp) and validp(tshp):
                    # grovel out the dimensions
                    dims = (sshp.dimensions.split("|")
                            + tshp.dimensions.split("|")
                            + strc.odims.split("|"))

                    out = (var.label, var.title, cmv.defaultPriority, var.units,
                           var.description, var.sn,
                           strc.cell_methods,
                           cmv.positive, cmv.type, dims,
                           cmv.modeling_realm, cmv.frequency,
                           strc.cell_measures,
                           cmv.prov, cmv.provNote,
                           cmv.rowIndex,
                           mips_of(cmv))

                    print out
