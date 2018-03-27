import globalpayments.api
from globalpayments.api.builders.validations.validation_target import ValidationTarget


class Validations(object):
    rules = None

    def __init__(self):
        self.rules = {}

    def of(self, type_name):
        '''
        Creates a new `ValidationTarget` for the given
        transaction type mask.

        @type type_name: TransactionType
        @param type_name: Mask of transaction types
        @rtype: ValidationTarget
        @return: The current validation
        '''
        if type_name not in self.rules:
            self.rules[type_name] = []

        target = ValidationTarget(self, type_name)
        self.rules[type_name].append(target)
        return target

    def validate(self, builder):
        '''
        Validates a given builder with the defined validation rules

        :type builder: BaseBuilder
        :param builder: The builder
        '''

        for key in self.rules:
            value = self._get_property_value(builder, 'transaction_type')

            if value != key & value:
                continue

            for validation in self.rules[key]:
                if validation.clause is None:
                    continue

                #  modifier
                if validation.constraint_name is not None:
                    modifier = self._get_property_value(
                        builder, validation.constraint_name)
                    if validation.constraint_value is not modifier:
                        continue

                # check precondition
                if validation.precondition is not None:
                    if not validation.precondition.callback(builder):
                        continue

                if not validation.clause.callback(builder):
                    raise globalpayments.api.entities.exceptions.BuilderException(
                        validation.clause.message)

    @staticmethod
    def _get_property_value(obj, comp):
        if obj is None:
            return None

        try:
            return getattr(obj, comp)
        except AttributeError as _exc:
            return None
