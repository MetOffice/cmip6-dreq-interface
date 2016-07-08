# djq.variables: finding and jsonifying CMOR variables

# computing variables
from . import compute
from .compute import *

# Implementations
#
# The example back end
from . import impl_dreq_example

# A back end which tries to invert the variable->mip map
from . import impl_invert_varmip

# Set the default implementation
cv_implementation(impl_dreq_example)

# jsonifying variable
from . import jsonify
from .jsonify import *
