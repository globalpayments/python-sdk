"""
Base request builder for Global Payments Ecommerce
"""

import xml.etree.ElementTree as ET
from abc import ABC
from typing import Any, Dict, List, Union

from globalpayments.api.utils import ElementTree
from globalpayments.api.utils import GenerationUtils, StringUtils


class GpEcomRequestBuilder(ABC):
    """
    Base class for building requests for the Global Payments Ecommerce gateway
    """

    def build_supplementary_data(
        self, supplementary_data: Dict[str, Union[str, List[str]]], request: ET.Element
    ) -> None:
        """
        Builds supplementary data for a request

        Args:
            supplementary_data: Dictionary of supplementary data
            request: The XML request element to add to
        """
        supplementary_data_elem = ET.SubElement(request, "supplementaryData")

        for key in supplementary_data:
            item = ET.SubElement(supplementary_data_elem, "item", {"type": key})

            items = []
            value = supplementary_data[key]
            if isinstance(value, str):
                items = value.split(" ")
            elif isinstance(value, list):
                items = value
            else:
                items = [str(supplementary_data[key])]

            for index, item_split in enumerate(items):
                field = ET.SubElement(item, f"field{index}")
                field.text = item_split

    def build_envelope(self, transaction: ET.Element) -> str:
        """
        Builds an XML envelope for a transaction

        Args:
            transaction: The transaction element

        Returns:
            The XML envelope as a string
        """
        tree = ElementTree()
        return ET.tostring(transaction, encoding="utf-8").decode("utf-8")

    def number_format(self, amount: Union[float, str]) -> str:
        """
        Formats a number for the request

        Args:
            amount: The amount to format

        Returns:
            The formatted amount as a string
        """
        f = float(amount) * 100
        return str(round(f, 2))

    def generate_hash(
        self,
        config: Any,
        timestamp: str,
        order_id: str,
        amount: str,
        currency: str,
        payment_data: str,
        verify: bool = False,
    ) -> str:
        """
        Generates a hash for the request

        Args:
            config: The GP Ecom configuration
            timestamp: The request timestamp
            order_id: The order ID
            amount: The transaction amount
            currency: The transaction currency
            payment_data: The payment data
            verify: Whether this is a verification request

        Returns:
            The generated hash
        """
        data = [timestamp, config.merchant_id, order_id]

        if not verify:
            data.append(amount)
            data.append(currency)

        data.append(payment_data)

        return GenerationUtils.generate_hash(config.shared_secret, data)

    def build_customer(self, customer: Any) -> ET.Element:
        """
        Builds customer data for a request

        Args:
            customer: The customer data

        Returns:
            The customer element
        """
        payer = ET.Element(
            "payer",
            {
                "ref": (
                    customer.key
                    if hasattr(customer, "key") and customer.key
                    else StringUtils.uuid()
                ),
                "type": "Retail",
            },
        )

        # Add customer details
        title_elem = ET.SubElement(payer, "title")
        title_elem.text = customer.title if hasattr(customer, "title") else ""

        firstname_elem = ET.SubElement(payer, "firstname")
        firstname_elem.text = (
            customer.first_name if hasattr(customer, "first_name") else ""
        )

        surname_elem = ET.SubElement(payer, "surname")
        surname_elem.text = customer.last_name if hasattr(customer, "last_name") else ""

        company_elem = ET.SubElement(payer, "company")
        company_elem.text = customer.company if hasattr(customer, "company") else ""

        # Add address if available
        if hasattr(customer, "address") and customer.address:
            address = ET.SubElement(payer, "address")

            line1_elem = ET.SubElement(address, "line1")
            line1_elem.text = (
                customer.address.street_address1
                if hasattr(customer.address, "street_address1")
                else ""
            )

            line2_elem = ET.SubElement(address, "line2")
            line2_elem.text = (
                customer.address.street_address2
                if hasattr(customer.address, "street_address2")
                else ""
            )

            line3_elem = ET.SubElement(address, "line3")
            line3_elem.text = (
                customer.address.street_address3
                if hasattr(customer.address, "street_address3")
                else ""
            )

            city_elem = ET.SubElement(address, "city")
            city_elem.text = (
                customer.address.city if hasattr(customer.address, "city") else ""
            )

            county_elem = ET.SubElement(address, "county")
            county_elem.text = (
                customer.address.province
                if hasattr(customer.address, "province")
                else ""
            )

            postcode_elem = ET.SubElement(address, "postcode")
            postcode_elem.text = (
                customer.address.postal_code
                if hasattr(customer.address, "postal_code")
                else ""
            )

            if hasattr(customer.address, "country") and customer.address.country:
                country_elem = ET.SubElement(address, "country", {"code": "GB"})
                country_elem.text = customer.address.country

        # Add phone numbers
        phone = ET.SubElement(payer, "phonenumbers")

        home_elem = ET.SubElement(phone, "home")
        home_elem.text = customer.home_phone if hasattr(customer, "home_phone") else ""

        work_elem = ET.SubElement(phone, "work")
        work_elem.text = customer.work_phone if hasattr(customer, "work_phone") else ""

        fax_elem = ET.SubElement(phone, "fax")
        fax_elem.text = customer.fax if hasattr(customer, "fax") else ""

        mobile_elem = ET.SubElement(phone, "mobile")
        mobile_elem.text = (
            customer.mobile_phone if hasattr(customer, "mobile_phone") else ""
        )

        # Add email
        email_elem = ET.SubElement(payer, "email")
        email_elem.text = customer.email if hasattr(customer, "email") else ""

        return payer
