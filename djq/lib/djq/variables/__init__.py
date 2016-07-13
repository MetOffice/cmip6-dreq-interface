# djq.variables: finding and jsonifying CMOR variables

# computing variables
from . import compute
from .compute import *

# Back ends: just import the default back end (which is a symlink)
# and set it up.
#
from . import cv_default
cv_implementation(cv_default)

# jsonifying variable
from . import jsonify
from .jsonify import *

from . import jsonify_default
jsonify_implementation(jsonify_default)
