class DotDict(dict):
    def __getattr__(self, attr):
        if type(self.get(attr)) == list and len(self.get(attr)) == 4:
            return tuple(self.get(attr))
        return self.get(attr)
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__