# See makeTables.py

from dreqPy.dreq import loadDreq

dq = loadDreq()

cmvs = sorted(dq.coll['CMORvar'].items, cmp=lambda x,y: cmp(x.label, y.label))
miptables = sorted(set(v.mipTable for v in cmvs))

def valid(thing):
    # Missing pointers have headers with label 'remarks' (I think)
    return thing._h.label != 'remarks'

def dict_of(thing, attrs):
    return {attr: getattr(thing.attr) for attr in attrs}

for table in miptables:
    for cmv in cmvs:
        if cmv.mipTable == table:
            var = dq.inx.uid[cmv.vid]   # var of the CMOR var
            strc = dq.inx.uid[cmv.stid] # structure of the CMOR var
            if valid(var) and valid(strc):
                sshp = dq.inx.uid[strc.spid] # spatial shape
                tshp = dq.inx.uid[strc.tmid] # temporal shape
                if valid(sshp) and valid(tshp):
                    # grovel out the dimensions
                    dims = (sshp.dimensions.split("|")
                            + tshp.dimensions.split("|")
                            + strc.odims.split("|")
                            + strc.coords.split("|"))
                    out = (var.label, var.title, cmv.defaultPriority, var.units,
                           var.description, var.sn,
                           strc.cell_methods,
                           cmv.positive, cmv.type, dims,
                           cmv.modeling_realm, cmv.frequency,
                           strc.cell_measures,
                           cmv.prov, cmv.provNote,
                           cmv.rowIndex)

                    print out
