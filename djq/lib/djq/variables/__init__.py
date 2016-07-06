# djq.variables: finding and jsonifying CMOR variables

import djq.low as low

# computing variables
from . import compute
low.publish(__name__, compute)

# jsonifying variable
from . import jsonify
low.publish(__name__, jsonify)
