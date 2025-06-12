"""
Request builder factory for creating request builders
"""

from typing import Dict, List, Optional, Any, Union

from globalpayments.api.builders.request_builder.GpApi.GpApiAuthorizationRequestBuilder import (
    GpApiAuthorizationRequestBuilder,
)
from globalpayments.api.builders.request_builder.GpApi.GpApiManagementRequestBuilder import (
    GpApiManagementRequestBuilder,
)
from globalpayments.api.builders.request_builder.GpApi.GpApiMiCRequestBuilder import (
    GpApiMiCRequestBuilder,
)
from globalpayments.api.builders.request_builder.GpApi.GpApiReportRequestBuilder import (
    GpApiReportRequestBuilder,
)
from globalpayments.api.builders.request_builder.GpApi.GpApiSecureRequestBuilder import (
    GpApiSecureRequestBuilder,
)
from globalpayments.api.builders.request_builder.GpEcom.GpEcomAuthorizationRequestBuilder import (
    GpEcomAuthorizationRequestBuilder,
)
from globalpayments.api.builders.request_builder.GpEcom.GpEcomManagementRequestBuilder import (
    GpEcomManagementRequestBuilder,
)
from globalpayments.api.entities.enums import GatewayProvider


class RequestBuilderFactory:
    """
    Factory for creating request builders based on gateway provider
    """

    supplementary_data: Dict[str, Union[str, List[str]]] = {}

    # Dictionary of gateway providers and their associated request builders
    _processes: Dict[GatewayProvider, List[Any]] = {
        GatewayProvider.GpApi: [
            GpApiAuthorizationRequestBuilder(),
            GpApiManagementRequestBuilder(),
            GpApiReportRequestBuilder(),
            GpApiSecureRequestBuilder(),
            GpApiMiCRequestBuilder(),
        ],
        GatewayProvider.GpEcom: [
            GpEcomAuthorizationRequestBuilder(),
            GpEcomManagementRequestBuilder(),
        ],
        GatewayProvider.Portico: [],
    }

    def get_request_builder(
        self, builder: Any, gateway_provider: GatewayProvider
    ) -> Optional[Any]:
        """
        Get the appropriate request builder for the given builder and gateway provider

        Args:
            builder: The builder to process
            gateway_provider: The gateway provider to use

        Returns:
            The appropriate request builder or None if not found
        """
        if gateway_provider not in self._processes:
            return None

        for process_name in self._processes[gateway_provider]:
            if process_name.can_process(builder):
                return process_name

        return None
