from typing import Optional

from globalpayments.api.entities.enums import ReportType


# Import inside methods to avoid circular imports


class ReportingService(object):
    @staticmethod
    def activity():
        # Import inside method to avoid circular imports
        from globalpayments.api.builders import TransactionReportBuilder

        return TransactionReportBuilder(ReportType.Activity)

    @staticmethod
    def transaction_detail(transaction_id: Optional[str] = None):
        # Import inside method to avoid circular imports
        from globalpayments.api.builders import TransactionReportBuilder

        if transaction_id is None:
            return TransactionReportBuilder(ReportType.TransactionDetail)
        return TransactionReportBuilder(
            ReportType.TransactionDetail
        ).with_transaction_id(transaction_id)

    @staticmethod
    def find_transactions_paged(
        page: int,
        page_size: int,
        transaction_id: str = None,
    ) -> "TransactionReportBuilder":
        from globalpayments.api.builders import TransactionReportBuilder

        return (
            TransactionReportBuilder(ReportType.FindTransactionsPaged)
            .with_transaction_id(transaction_id)
            .with_paging(page, page_size)
        )

    @staticmethod
    def find_transactions():
        # Import inside method to avoid circular imports
        from globalpayments.api.builders import TransactionReportBuilder

        return TransactionReportBuilder(ReportType.FindTransactions)
