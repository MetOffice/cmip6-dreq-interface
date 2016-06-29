# djq.variables: finding and jsonifying CMOR variables

def _publish(mod):
    g = globals()
    for var in getattr(mod, '__published__',
                       getattr(mod, '__all__', ())):
        g[var] = getattr(mod, var)

# computing variables
from . import compute
_publish(compute)

# jsonifying variable
from . import jsonify
_publish(jsonify)
