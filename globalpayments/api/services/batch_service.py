import globalpayments as gp
from globalpayments.api.entities.enums import TransactionType


class BatchService(object):
    @staticmethod
    def close_batch(config_name='default'):
        _response = gp.api.builders.ManagementBuilder(
            TransactionType.BatchClose).execute(config_name)
        return gp.api.entities.BatchSummary()
