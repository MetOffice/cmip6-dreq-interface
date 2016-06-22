"""JSONifying variables

This is extremely incomplete
"""

__all__ = ('jsonify_cmvids',)

def jsonify_cmvids(dq, cmvids):
    """Return a suitable dict for a bunch of cmv uids.:"""
    return sorted((jsonify_cmvid(dq, cmvid)
                   for cmvid in cmvids),
                  key=lambda j: j['label'])

def jsonify_cmvid(dq, cmvid):
    cmv = dq.inx.uid[cmvid]
    return {'uid': cmvid,
            'label': cmv.label}
