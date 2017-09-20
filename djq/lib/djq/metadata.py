# (C) British Crown Copyright 2017, Met Office.
# See LICENSE.md in the top directory for license details.
#

"""Metadata for a request
"""

# Package interface: nothing (this is shared by several modules but
# not used outside djq)
#
__all__ = ()

# Interface
# - reply_metadata
# - note_reply_metadata

from low import fluid, boundp, Disaster

# Metadata added to a reply.  This has no global value
reply_metadata = fluid()

class MetadataUnbound(Disaster):
    """Raised if metadata is unbound"""
    pass

def note_reply_metadata(**kv):
    # append everything in kv to the current metadata, canonicalising
    # names (hyphens not underscores)
    if not boundp(reply_metadata):
        raise MetadataUnbound()
    metadata = reply_metadata()
    for (k, v) in kv.iteritems():
        metadata[k.replace("_", "-")] = v
