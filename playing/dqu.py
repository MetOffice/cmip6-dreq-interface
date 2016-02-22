__all__ = ['dqi']

def dqi(thing):
    # information on something
    something = False
    if hasattr(thing, '__info__'):
        something = True
        thing.__info__()
    if hasattr(thing, '_h') and hasattr(thing._h, '__info__'):
        something = True
        thing._h.__info__()
    if not something:
        print "no"

def memoize(f):
    cache = {}
    def call(key, *args):
        if key not in cache:
            result = f(key, *args)
            cache[key] = (result, args)
            return result
        else:
            (cached_result, cached_args) = cache[key]
            if cached_args == args:
                return cached_result
            else:
                result = f(key, *args)
                cache[key] = (result, args)
                return result
    return call
            

