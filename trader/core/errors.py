class Error(Exception):
    msg = None

    def __init__(self, **kwargs):
        self.kwargs = kwargs

    def __str__(self):
        return self.msg.format(**self.kwargs)

    __unicode__ = __str__
    __repr__ = __str__
