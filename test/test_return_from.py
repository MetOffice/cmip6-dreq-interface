# just to see if it works to finish walks early

from dqi import (walk_dq, walk_linked, dqtype, 
                 return_from_thing, return_from_walk)
from dqi.util import load_from_dqroot, walk_from_dqroot

def explode(*junk, **kws):
    return_from_walk(1)

ruleset = {'CMORvar': (('all', (walk_linked,)),),
           None: explode}
    
