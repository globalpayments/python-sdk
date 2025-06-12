from globalpayments.api.entities.enums import TransactionType


class BatchService(object):
    @staticmethod
    def close_batch(config_name="default"):
        # Import inside method to avoid circular imports
        import globalpayments as gp
        from globalpayments.api.builders import ManagementBuilder
        from globalpayments.api.entities import BatchSummary

        _response = ManagementBuilder(TransactionType.BatchClose).execute(config_name)
        return BatchSummary()
