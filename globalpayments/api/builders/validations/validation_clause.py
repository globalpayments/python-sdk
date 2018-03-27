class ValidationClause(object):
    parent = None
    target = None
    property_name = None
    callback = None
    message = None
    precondition = None

    def __init__(self, parent, target, property_name, precondition=False):
        self.parent = parent
        self.target = target
        self.property_name = property_name
        self.precondition = precondition

    def is_not_none(self, message=None):
        self.callback = (
            lambda builder: self._get_property_value(builder, self.property_name) is not None
        )
        self.message = message if message is not None else 'property `{}` is None'.format(
            self.property_name)

        if self.precondition:
            return self.target

        return self.parent.of(self.target.type_name) \
            .with_constraint(self.target.constraint_name, self.target.constraint_value)

    def is_none(self, message=None):
        self.callback = (
            lambda builder: self._get_property_value(builder, self.property_name) is None
        )
        self.message = message if message is not None else 'property `{}` is not None'.format(
            self.property_name)

        if self.precondition:
            return self.target

        return self.parent.of(self.target.type_name) \
            .with_constraint(self.target.constraint_name, self.target.constraint_value)

    def equals(self, expected, message=None):
        self.callback = (
            lambda builder: self._get_property_value(builder, self.property_name) is expected
        )
        self.message = message if message is not None else 'property `{}` does not equal `{}`'.format(
            self.property_name, str(expected))

        if self.precondition:
            return self.target

        return self.parent.of(self.target.type_name) \
            .with_constraint(self.target.constraint_name, self.target.constraint_value)

    def does_not_equal(self, expected, message=None):
        self.callback = (
            lambda builder: self._get_property_value(builder, self.property_name) is not expected
        )
        self.message = message if message is not None else 'property `{}` is equals `{}`'.format(
            self.property_name, str(expected))

        if self.precondition:
            return self.target

        return self.parent.of(self.target.type_name) \
            .with_constraint(self.target.constraint_name, self.target.constraint_value)

    @staticmethod
    def _get_property_value(obj, comp):
        if obj is None:
            return None

        try:
            return getattr(obj, comp)
        except AttributeError as _exc:
            return None
