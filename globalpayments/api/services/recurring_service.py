from globalpayments.api.entities.enums import TransactionType

# Import RecurringBuilder inside the methods to avoid circular imports


class RecurringService(object):
    @staticmethod
    def create(entity, config_name=None):
        # Import inside method to avoid circular imports
        from globalpayments.api.builders import RecurringBuilder

        return RecurringBuilder(TransactionType.Create, entity).execute(config_name)

    @staticmethod
    def delete(entity, force=False, config_name=None):
        # Import inside method to avoid circular imports
        from globalpayments.api.builders import RecurringBuilder

        builder = RecurringBuilder(TransactionType.Delete, entity)
        # Use set_property_if_exists instead of with_force which doesn't exist
        if hasattr(builder, "force"):
            builder.force = force
        return builder.execute(config_name)

    @staticmethod
    def edit(entity, config_name=None):
        # Import inside method to avoid circular imports
        from globalpayments.api.builders import RecurringBuilder

        return RecurringBuilder(TransactionType.Edit, entity).execute(config_name)

    @staticmethod
    def get(entity, config_name=None):
        # Import inside method to avoid circular imports
        from globalpayments.api.builders import RecurringBuilder

        return RecurringBuilder(TransactionType.Fetch, entity).execute(config_name)

    @staticmethod
    def search(entity=None):
        # Import inside method to avoid circular imports
        from globalpayments.api.builders import RecurringBuilder

        return RecurringBuilder(TransactionType.Search, entity)
