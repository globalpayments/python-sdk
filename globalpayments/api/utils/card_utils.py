"""
Utility class for card-related operations
"""

import re
from typing import Dict, Any, Optional

from globalpayments.api.entities.enums import (
    CvnPresenceIndicator,
    TransactionType,
    PaymentMethodType,
    TrackNumber,
    EmvLastChipRead,
)
from globalpayments.api.entities.gp_api.DTO.card import Card
from globalpayments.api.payment_methods import CreditTrackData
from globalpayments.api.utils.enum_mapping import EnumMapping
from globalpayments.api.utils.sensitive_data_utils import ProtectSensitiveData


class CardUtils:
    """Utility class for card-related operations"""

    # Regular expression patterns for track data parsing
    _track_one_pattern = r"%?[B0]?([\d]+)\\^[^\\^]+\\^([\\d]{4})([^?]+)?"
    _track_two_pattern = r";?([\d]+)=([\d]{4})([^?]+)?"

    # Fleet BIN ranges mapping
    _fleet_bin_map = {
        "Visa": [
            ["448460", "448611"],
            ["448613", "448615"],
            ["448617", "448674"],
            ["448676", "448686"],
            ["448688", "448699"],
            ["461400", "461421"],
            ["461423", "461499"],
            ["480700", "480899"],
        ],
        "MC": [
            ["553231", "553380"],
            ["556083", "556099"],
            ["556100", "556599"],
            ["556700", "556999"],
        ],
        "Wex": [
            ["690046", "690046"],
            ["707138", "707138"],
        ],
        "Voyager": [["708885", "708889"]],
    }

    # Card type regex patterns
    _card_types = {
        "Visa": re.compile(r"^4"),
        "MC": re.compile(
            r"^(?:5[1-6]|222[1-9]|22[3-9][0-9]|2[3-6][0-9]{2}|27[01][0-9]|2720)"
        ),
        "Amex": re.compile(r"^3[47]"),
        "DinersClub": re.compile(r"^3(?:0[0-5]|[68][0-9])"),
        "EnRoute": re.compile(r"^2(014|149)"),
        "Discover": re.compile(r"^6(?:011|5[0-9]{2})"),
        "Jcb": re.compile(r"^(?:2131|1800|35\d{3})"),
        "Wex": re.compile(r"^(?:690046|707138)"),
        "Voyager": re.compile(r"^70888[5-9]"),
    }

    @staticmethod
    def generate_card(
        builder: Any,  # AuthorizationBuilder
        gateway_provider: Any,
        masked_values: Dict[str, str],
    ) -> Card:
        """
        Generates a Card object from the builder data

        Args:
            builder: The authorization builder
            gateway_provider: The gateway provider
            masked_values: Dictionary to store masked sensitive values

        Returns:
            A Card object
        """
        payment_method = builder.payment_method
        transaction_type = builder.transaction_type

        card = Card()

        if hasattr(payment_method, "is_track_data") and payment_method.is_track_data:
            card.track = payment_method.value
            if transaction_type == TransactionType.Sale:
                if not card.track:
                    card.number = payment_method.pan
                    masked_values.update(
                        ProtectSensitiveData.hide_value(
                            "payment_method.card.number",
                            payment_method.pan,
                            4,
                        )
                    )
                    if hasattr(payment_method, "expiry") and payment_method.expiry:
                        card.expiry_month = payment_method.expiry[2:4]
                        card.expiry_year = payment_method.expiry[0:2]
                        masked_values.update(
                            ProtectSensitiveData.hide_values(
                                {
                                    "payment_method.card.expiry_month": (
                                        str(card.expiry_month)
                                        if card.expiry_month
                                        else ""
                                    ),
                                    "payment_method.card.expiry_year": (
                                        str(card.expiry_year)
                                        if card.expiry_year
                                        else ""
                                    ),
                                }
                            )
                        )

                if (
                    builder.transaction_type == TransactionType.Sale
                    or builder.transaction_type == TransactionType.Refund
                ) and not hasattr(builder, "tag_data"):
                    chip_condition = (
                        builder.emv_chip_condition
                        if hasattr(builder, "emv_chip_condition")
                        else None
                    )
                    if chip_condition is not None:
                        card.chip_condition = EnumMapping.map_emv_last_chip_read(
                            gateway_provider,
                            chip_condition,
                        )

                if builder.transaction_type == TransactionType.Sale:
                    card.funding = (
                        "DEBIT"
                        if payment_method.payment_method_type == PaymentMethodType.Debit
                        else "CREDIT"
                    )

        elif hasattr(payment_method, "is_card_data") and payment_method.is_card_data:
            card.number = payment_method.number
            masked_values.update(
                ProtectSensitiveData.hide_value(
                    "payment_method.card.number",
                    payment_method.number,
                    4,
                    6,
                )
            )

            if hasattr(payment_method, "exp_month") and payment_method.exp_month:
                card.expiry_month = str(payment_method.exp_month).zfill(2)
                masked_values.update(
                    ProtectSensitiveData.hide_value(
                        "payment_method.card.expiry_month",
                        card.expiry_month,
                    )
                )

            if hasattr(payment_method, "exp_year") and payment_method.exp_year:
                card.expiry_year = str(payment_method.exp_year).zfill(4)[2:4]
                masked_values.update(
                    ProtectSensitiveData.hide_value(
                        "payment_method.card.expiry_year",
                        card.expiry_year,
                    )
                )

            if hasattr(payment_method, "cvn") and payment_method.cvn:
                card.cvv = payment_method.cvn
                masked_values.update(
                    ProtectSensitiveData.hide_value(
                        "payment_method.card.cvv",
                        payment_method.cvn,
                    )
                )
                cvn_presence_indicator = (
                    CvnPresenceIndicator.Present
                    if payment_method.cvn
                    else (
                        payment_method.cvn_presence_indicator
                        if hasattr(payment_method, "cvn_presence_indicator")
                        else CvnPresenceIndicator.NotRequested
                    )
                )
                card.cvv_indicator = CardUtils.get_cvv_indicator(cvn_presence_indicator)

            if (
                hasattr(builder, "emv_chip_condition")
                and builder.emv_chip_condition
                and not hasattr(builder, "tag_data")
            ):
                if builder.emv_chip_condition is not None:
                    card.chip_condition = EnumMapping.map_emv_last_chip_read(
                        gateway_provider,
                        builder.emv_chip_condition,
                    )

        if (
            hasattr(payment_method, "is_pin_protected")
            and payment_method.is_pin_protected
        ):
            card.pin_block = payment_method.pin_block

        billing_address = (
            builder.billing_address.street_address1
            if hasattr(builder, "billing_address")
            and builder.billing_address
            and hasattr(builder.billing_address, "street_address1")
            else None
        )

        postal_code = (
            builder.billing_address.postal_code
            if hasattr(builder, "billing_address")
            and builder.billing_address
            and hasattr(builder.billing_address, "postal_code")
            else None
        )

        card.tag = builder.tag_data if hasattr(builder, "tag_data") else None
        card.avs_address = billing_address
        card.avs_postal_code = postal_code
        card.authcode = (
            builder.offline_auth_code if hasattr(builder, "offline_auth_code") else None
        )

        return card

    @staticmethod
    def get_cvv_indicator(cvn_presence_indicator: CvnPresenceIndicator) -> str:
        """
        Gets the CVV indicator string from the CVN presence indicator

        Args:
            cvn_presence_indicator: The CVN presence indicator

        Returns:
            The CVV indicator string
        """
        if cvn_presence_indicator == CvnPresenceIndicator.Present:
            return "PRESENT"
        elif cvn_presence_indicator == CvnPresenceIndicator.Illegible:
            return "ILLEGIBLE"
        elif cvn_presence_indicator == CvnPresenceIndicator.NotOnCard:
            return "NOT_ON_CARD"
        else:
            return "NOT_PRESENT"

    @staticmethod
    def parse_track_data(payment_method: CreditTrackData) -> CreditTrackData:
        """
        Parses track data from a payment method

        Args:
            payment_method: The payment method

        Returns:
            The payment method with parsed track data
        """
        track_data = payment_method.value
        track_two_pattern = re.compile(CardUtils._track_two_pattern)
        track_one_pattern = re.compile(CardUtils._track_one_pattern)

        matches = track_two_pattern.search(track_data or "")
        if matches and matches.group(1) and matches.group(2):
            pan = matches.group(1)
            expiry = matches.group(2)
            discretionary = matches.group(3) if matches.group(3) else None

            if discretionary:
                if len(
                    pan + expiry + discretionary
                ) == 37 and discretionary.lower().endswith("f"):
                    discretionary = discretionary[:-1]

                payment_method.discretionary_data = discretionary

            payment_method.track_number = TrackNumber.TRACK_TWO
            payment_method.pan = pan
            payment_method.expiry = expiry
            payment_method.track_data = f"{pan}={expiry}{discretionary}?"
        else:
            matches = track_one_pattern.search(track_data or "")
            if matches and matches.group(1) and matches.group(2):
                payment_method.track_number = TrackNumber.TRACK_ONE
                payment_method.pan = matches.group(1)
                payment_method.expiry = matches.group(2)

                payment_method.track_data = matches.group(0).replace("%", "")

        return payment_method

    @staticmethod
    def get_card_type(number: str) -> str:
        """
        Gets the card type from a card number

        Args:
            number: The card number

        Returns:
            The card type
        """
        number = number.replace(" ", "").replace("-", "")

        card_type = "Unknown"
        for type_name, regex in CardUtils._card_types.items():
            if regex.search(number):
                card_type = type_name

        if card_type != "Unknown":
            if CardUtils.is_fleet(card_type, number):
                card_type += "Fleet"

        return card_type

    @staticmethod
    def is_fleet(card_type: str, pan: str) -> bool:
        """
        Determines if a card is a fleet card

        Args:
            card_type: The card type
            pan: The card number

        Returns:
            True if the card is a fleet card, False otherwise
        """
        if pan:
            compare_value = pan[:6]
            base_card_type = card_type.replace("Fleet", "")

            if base_card_type in CardUtils._fleet_bin_map:
                bin_ranges = CardUtils._fleet_bin_map[base_card_type]
                for lower_range, upper_range in bin_ranges:
                    if lower_range <= compare_value <= upper_range:
                        return True

        return False
