# Some general tools
#
# None of this is relied on by anything else
#

__all__ = ['dqi']

def dqi(thing, h=True, t=True):
    # information on something
    something = False
    if t and hasattr(thing, '__info__'):
        something = True
        thing.__info__()
    if h and hasattr(thing, '_h') and hasattr(thing._h, '__info__'):
        something = True
        thing._h.__info__()
    if not something:
        print "no"

            

