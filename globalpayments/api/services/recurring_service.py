import globalpayments as gp
from globalpayments.api.entities.enums import TransactionType


class RecurringService(object):
    @staticmethod
    def create(entity, config_name=None):
        return gp.api.builders.RecurringBuilder(TransactionType.Create,
                                                entity).execute(config_name)

    @staticmethod
    def delete(entity, force=False, config_name=None):
        return gp.api.builders.RecurringBuilder(TransactionType.Delete, entity) \
            .with_force(force) \
            .execute(config_name)

    @staticmethod
    def edit(entity, config_name=None):
        return gp.api.builders.RecurringBuilder(TransactionType.Edit,
                                                entity).execute(config_name)

    @staticmethod
    def get(key, config_name=None):
        entity = gp.api.entities.RecurringEntity()
        entity.key = key

        return gp.api.builders.RecurringBuilder(TransactionType.Fetch,
                                                entity).execute(config_name)

    @staticmethod
    def search():
        return gp.api.builders.RecurringBuilder(TransactionType.Search)
