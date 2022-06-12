from __future__ import absolute_import

from functools import wraps

from django_ratelimit import ALL, UNSAFE
from django_ratelimit.exceptions import Ratelimited
from django_ratelimit.core import get_usage

__all__ = ['ratelimit']


def ratelimit(group=None, key=None, rate=None, method=ALL, block=False):
    def decorator(fn):
        @wraps(fn)
        def _wrapped(view, *args, **kw):
            request = view.request
            old_limited = getattr(request, 'limited', False)
            usage = get_usage(request=request, group=group, fn=fn,
                              key=key, rate=rate, method=method,
                              increment=True)

            if usage:
                limited = usage['should_limit']
                count = usage['count']
            else:
                limited = False
                count = 0

            request.limited = limited or old_limited
            request.count = count

            if limited and block:
                raise Ratelimited()

            return fn(view, *args, **kw)

        return _wrapped

    return decorator


ratelimit.ALL = ALL
ratelimit.UNSAFE = UNSAFE
