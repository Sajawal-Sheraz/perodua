def from_env(config, key, cast=str, default=None):
    if key in config:
        return cast(config[key])
    elif default is None:
        return None
    else:
        return default
