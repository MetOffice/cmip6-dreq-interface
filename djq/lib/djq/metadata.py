# (C) British Crown Copyright 2017, 2018, Met Office.
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

from low import fluid, boundp, mutter

# Metadata added to a reply.  This has no global value
reply_metadata = fluid()

def metadata_bound_p():
    return boundp(reply_metadata)

def note_reply_metadata(**kv):
    # append everything in kv to the current metadata, if there is
    # any, canonicalising names (hyphens not underscores)
    if boundp(reply_metadata):
        metadata = reply_metadata()
        for (k, v) in kv.iteritems():
            metadata[k.replace("_", "-")] = v
    else:
        mutter("no ambient reply metadata")
