class SingletonMeta(type):
    """Singleton metaclass.
    This metaclass can be used to create singleton classes.

    Returns:
        instance: Singleton instance.
    """
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]
