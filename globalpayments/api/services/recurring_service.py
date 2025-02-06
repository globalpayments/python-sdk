import globalpayments as gp
from globalpayments.api.entities.enums import TransactionType


class RecurringService(object):
    @staticmethod
    def create(entity, config_name=None):
        return gp.api.builders.RecurringBuilder(TransactionType.Create, entity).execute(
            config_name
        )

    @staticmethod
    def delete(entity, force=False, config_name=None):
        return (
            gp.api.builders.RecurringBuilder(TransactionType.Delete, entity)
            .with_force(force)
            .execute(config_name)
        )

    @staticmethod
    def edit(entity, config_name=None):
        return gp.api.builders.RecurringBuilder(TransactionType.Edit, entity).execute(
            config_name
        )

    @staticmethod
    def get(entity, config_name=None):
        return gp.api.builders.RecurringBuilder(TransactionType.Fetch, entity).execute(
            config_name
        )

    @staticmethod
    def search(entity=None):
        return gp.api.builders.RecurringBuilder(TransactionType.Search, entity)
