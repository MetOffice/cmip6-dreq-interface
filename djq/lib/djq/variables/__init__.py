# djq.variables: finding and jsonifying CMOR variables

# computing variables
from . import compute
from .compute import *

# Implementations
#
# The example back end
from . import impl_dreq_example

cv_implementation(impl_dreq_example)

# jsonifying variable
from . import jsonify
from .jsonify import *
