"""Default JSONify implementation
"""

__all__ = ('jsonify_cmvids',)

def jsonify_cmvids(dq, cmvids):
    return tuple(jsonify_cmvid(dq, cmvid) for cmvid in cmvids)

def jsonify_cmvid(dq, cmvid):
    cmv = dq.inx.uid[cmvid]
    return {'uid': cmvid,
            'label': cmv.label,
            'miptable': cmv.mipTable}
