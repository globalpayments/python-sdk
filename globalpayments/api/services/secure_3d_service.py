from typing import Any

from globalpayments.api.builders.threeD_secure_builder import Secure3dBuilder
from globalpayments.api.entities import ThreeDSecure
from globalpayments.api.entities.enums import TransactionType


class Secure3dService:
    """
    Secure 3D service implementation to support 3DS authentication operations
    """

    @staticmethod
    def check_enrollment(payment_method: Any) -> Secure3dBuilder:
        """
        Check if a payment method is enrolled in the 3DS program.

        Args:
            payment_method: The payment method to verify enrollment for

        Returns:
            A Secure3dBuilder instance with the VerifyEnrolled transaction type
        """
        return Secure3dBuilder(TransactionType.VerifyEnrolled).with_payment_method(
            payment_method
        )

    @staticmethod
    def initiate_authentication(
        payment_method: Any, secure_ecom: ThreeDSecure
    ) -> Secure3dBuilder:
        """
        Initiates the authentication process for a 3D Secure transaction.

        Args:
            payment_method: The payment method to be authenticated
            secure_ecom: The ThreeDSecure object returned from check_enrollment

        Returns:
            A Secure3dBuilder instance with the InitiateAuthentication transaction type
        """
        if payment_method.is_secure_3d:
            payment_method.three_d_secure = secure_ecom

        return Secure3dBuilder(
            TransactionType.InitiateAuthentication
        ).with_payment_method(payment_method)

    @staticmethod
    def get_authentication_data() -> Secure3dBuilder:
        """
        Gets the authentication data for a 3D Secure transaction after completion.

        Returns:
            A Secure3dBuilder instance with the VerifySignature transaction type
        """
        return Secure3dBuilder(TransactionType.VerifySignature)
