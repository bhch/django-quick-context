class ContextModelEntry:
    def __init__(self, model, lookup_field):
        self.model = model
        self.lookup_field = lookup_field

    def __getattr__(self, attr):
        try:
            return self.model.objects.get(**{self.lookup_field: attr})
        except self.model.DoesNotExist:
            return None


class ContextRegistry:
    _registry = []

    @classmethod
    def get_registry(cls):
        return cls._registry.copy()

    @classmethod
    def register(cls, name, entry):
        if hasattr(cls, name):
            raise DuplicateContextEntry('An entry with the name "%s" already exists' % name)

        setattr(cls, name, entry)
        cls._registry.append(name)

    @classmethod
    def register_model(cls, name, model, lookup_field):
        entry = ContextModelEntry(model, lookup_field)
        cls.register(name, entry)


class DuplicateContextEntry(Exception):
    pass
