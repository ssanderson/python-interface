class default(object):
    """Default implementation of a function in terms of interface methods.
    """
    def __init__(self, implementation):
        self.implementation = implementation

    def __repr__(self):
        return "{}({})".format(type(self).__name__, self.implementation)
