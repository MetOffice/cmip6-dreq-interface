"""Default JSONify implementation
"""

__all__ = ('jsonify_cmvids',)

from varmip import mips_of_cmv, priority_of_cmv_in_mip

def jsonify_cmvids(dq, cmvids):
    """Convert a bunch of CMORvar IDs to JSON."""
    return tuple(jsonify_cmvid(dq, cmvid) for cmvid in cmvids)

def jsonify_cmvid(dq, cmvid):
    cmv = dq.inx.uid[cmvid]
    return {'uid': cmvid,
            'label': cmv.label,
            'miptable': cmv.mipTable,
            'priority': cmv.defaultPriority,
            'mips': mipinfo_of_cmv(dq, cmv)}

def mipinfo_of_cmv(dq, cmv):
    # compute the mipinfo for a variable.  This could easily be cached
    # as it gets called many many times for the same MIPs
    return tuple({'mip': mip,
                  'objectives': tuple(o.description
                                      for o in dq.coll['objective'].items
                                      if o.mip == mip),
                  'priority': priority_of_cmv_in_mip(dq, cmv, mip)}
                 for mip in mips_of_cmv(dq, cmv))
