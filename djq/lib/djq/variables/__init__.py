# djq.variables: finding and jsonifying CMOR variables

# computing variables
from . import compute
from .compute import *

# Back end: just import the default back end (which is a symlink) and
# set it up.  Note that this sets the fallback, as it is the first
# call.
#
from . import cv_default
cv_implementation(cv_default)

# jsonifying variables
from . import jsonify
from .jsonify import *

# Again, import the default back end and set it, and note that this
# sets the fallback as well.
#
from . import jsonify_default
jsonify_implementation(jsonify_default)
