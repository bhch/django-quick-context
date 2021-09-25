class ContextRegistry:
    _registry = []

    @classmethod
    def get_registry(cls):
        return cls._registry.copy()

    @classmethod
    def register(cls, name, value):
        if hasattr(cls, name):
            raise DuplicateContextEntry(
                'An entry with the name "%s" already exists in the context registry.'
                'To update a variable, use ContextRegistry.update method.'
                % name)

        setattr(cls, name, value)
        cls._registry.append(name)

    @classmethod
    def register_model(cls, name, model, lookup_field):
        value = ContextModelEntry(model, lookup_field)
        cls.register(name, value)

    @classmethod
    def update(cls, name, value):
        if name not in cls.get_registry():
            raise EntryNotFound(
                'Can\'t update entry "%s" because it had not been registered.'
                'To register a new entry, use the ContextRegistry.register method.'
            % name)

        setattr(cls, name, value)


class ContextModelEntry:
    """This class allows for fetching model objects from the database
    using a uninque field value. 

    For example, to get a user whose username is 'root', this class 
    allows doing {{ quick.user.root }}. 
    """
    def __init__(self, model, lookup_field):
        self.model = model
        self.lookup_field = lookup_field
        self.filter_exp = None

    def __getattr__(self, attr):
        if attr.startswith('filter__'):
            self.filter_exp = attr.split('__')[1]
            return self
        
        if self.filter_exp:
            return self.model.objects.filter(**{
                '%s__%s' % (self.lookup_field, self.filter_exp): attr,
                })
        else:
            try:
                return self.model.objects.get(**{self.lookup_field: attr})
            except self.model.DoesNotExist:
                return None


class DuplicateContextEntry(Exception):
    pass


class EntryNotFound(Exception):
    pass
