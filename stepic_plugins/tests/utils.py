import functools

from stepic_plugins import settings


def override_settings(**settings_kwargs):
    def decorator(f):
        @functools.wraps(f)
        def wrapped(*args, **kwargs):
            orig_settings = {}
            absent_settings = []
            for k, v in settings_kwargs.items():
                if hasattr(settings, k):
                    orig_settings[k] = getattr(settings, k)
                else:
                    absent_settings.append(k)
                setattr(settings, k, v)
            try:
                return f(*args, **kwargs)
            finally:
                # Revert settings to the original values
                for k, v in orig_settings.items():
                    setattr(settings, k, v)
                for k in absent_settings:
                    delattr(settings, k)
        return wrapped

    return decorator
