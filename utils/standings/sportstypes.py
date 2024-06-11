def constant(f):
    def fset(self, value):
        raise TypeError
    def fget(self):
        return f()
    return property(fget, fset)

class _SportsTypes(object):
    @constant
    def HANDBALL():
        return 4
    @constant
    def FOOTBALL():
        return 1

SPORTSTYPES = _SportsTypes()