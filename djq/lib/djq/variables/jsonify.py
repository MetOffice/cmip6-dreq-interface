"""JSONifying variables

This is extremely incomplete
"""

__all__ = ('jsonify_cmvids',)

from djq.low import whisper

def jsonify_cmvids(dq, cmvids):
    """Return a suitable dict for a bunch of cmv uids.:"""
    results = sorted((jsonify_cmvid(dq, cmvid)
                      for cmvid in cmvids),
                     key=lambda j: j['label'])
    for r in results:
        whisper("     {}", r['label'])
    return results

def jsonify_cmvid(dq, cmvid):
    cmv = dq.inx.uid[cmvid]
    return {'uid': cmvid,
            'label': cmv.label}
