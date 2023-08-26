import time
from functools import partial
from ..configs import Config


class CoolDownDecorator(object):
    def __init__(self, func):
        self.fn = func
        self.last_run = 0
        self.config = Config.get_instance()

    def __get__(self, obj, obj_type=None):
        if obj is None:
            return self.fn
        return partial(self, obj)

    def __call__(self, *args, **kwargs):
        now = time.time()
        interval = self.config.get('cool_down') / 1000
        if not(now - self.last_run < interval):
            self.last_run = now
            return self.fn(*args, **kwargs)


def cool_down(fn):
    return CoolDownDecorator(fn)
