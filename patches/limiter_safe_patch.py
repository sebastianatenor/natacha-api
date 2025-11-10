"""
Hotfix temporal: evita crash si limiter == None.
"""
def safe_limit(limiter):
    if limiter is None:
        def no_limit(*_args, **_kwargs):
            def decorator(f):
                return f
            return decorator
        return no_limit
    return limiter.limit
