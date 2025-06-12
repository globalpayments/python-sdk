"""
Utilities for general use in the SDK
"""

import base64
import enum
import hashlib
import json
import random
import re
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Any, Optional
from typing import Union
from xml.dom import minidom

from globalpayments.api.utils.sensitive_data_utils import ProtectSensitiveData


@dataclass
class ElementTree(object):
    """
    Wraps xml.dom.minidom to provide a simpler et
    """

    doc: Optional[Any] = field(default=None)
    namespaces: Dict[str, str] = field(default_factory=dict)

    def __init__(self):
        self.doc = minidom.Document()
        self.namespaces["soap"] = "http://schemas.xmlsoap.org/soap/envelope/"

    def element(self, tag_name):
        """
        Creates a new element
        """

        element = self._create_element(tag_name)
        return Element(self.doc, element)

    def sub_element(self, parent, tag_name, **kwargs):
        """
        Creates a sub-element on a parent element
        """

        value = ""
        if "value" in kwargs:
            if kwargs["value"] is None:
                return None
            value = kwargs["value"]

        child = self._create_element(tag_name)
        if parent is not None and parent.element is not None and child is not None:
            parent.element.appendChild(child)
            return Element(self.doc, child).text(value)
        return None

    def to_string(self, root):
        """
        Converts an ElementTree object to its string form
        """
        if self.doc is not None and root is not None and root.element is not None:
            self.doc.appendChild(root.element)
            try:
                return self.doc.toxml()
            finally:
                self.doc.removeChild(root)
        return ""

    def get(self, tag_name):
        """
        Gets an element by tag_name
        """
        if self.doc is not None:
            try:
                node = self.doc.getElementsByTagName(tag_name)[0]
                if node is not None:
                    return Element(self.doc, node)
            except IndexError:
                pass
        return None

    def _create_element(self, tag_name):
        if self.doc is None:
            return None

        if tag_name and ":" in tag_name:
            data = tag_name.split(":")
            if len(data) > 1 and data[0] in self.namespaces:
                return self.doc.createElementNS(self.namespaces[data[0]], tag_name)

        return self.doc.createElement(tag_name) if tag_name else None


@dataclass
class Element(object):
    """
    Assists in working with ElementTree elements
    """

    doc: Optional[Any] = field(default=None)
    element: Optional[Any] = field(default=None)

    def __init__(self, doc, element):
        self.doc = doc
        self.element = element

    def first_child(self):
        """
        Gets the first child of the element
        """
        if self.element is not None and hasattr(self.element, "first_child"):
            child = self.element.first_child()
            if child is not None:
                return self.from_node(self.doc, child)
        return None

    def prefix(self, prefix):
        """
        Sets the prefix of the element
        """
        if self.element is not None and hasattr(self.element, "prefix"):
            self.element.prefix(prefix)
        return self

    def remove(self, tag_name):
        """
        Removes the child node by tag_name if it exists
        """
        if self.element is not None:
            child = self.get(tag_name)
            if child is not None and hasattr(self.element, "removeChild"):
                self.element.removeChild(tag_name)
        return self

    def set(self, name, value):
        """
        Sets an attribute by name on the element
        """
        if self.element is not None and hasattr(self.element, "setAttribute"):
            self.element.setAttribute(name, value)
        return self

    def text(self, value):
        """
        Sets the inner text of the element
        """
        if self.element is not None and hasattr(self.element, "innerText"):
            self.element.innerText(value)
        return self

    def append(self, child):
        """
        Adds a child to the element
        """
        if (
            self.doc is not None
            and child is not None
            and hasattr(self.doc, "importNode")
            and self.element is not None
            and hasattr(self.element, "appendChild")
        ):
            self.doc.importNode(child)
            if child.element is not None:
                self.element.appendChild(child.element)
        return self

    def tag(self):
        """
        Gets the element's tag
        """
        if self.element is not None and hasattr(self.element, "tag"):
            return self.element.tag
        return None

    def has(self, tag_name):
        """
        Tests if a child exists with the tag_name
        """
        if self.element is not None and hasattr(self.element, "getElementsByTagName"):
            return len(self.element.getElementsByTagName(tag_name)) > 0
        return False

    def get(self, tag_name):
        """
        Get the first child that matches the tag_name
        """
        if self.element is not None and hasattr(self.element, "getElementsByTagName"):
            elements = self.element.getElementsByTagName(tag_name)
            if elements and len(elements) > 0:
                return elements[0]
        return None

    def get_all(self, tag_name):
        """
        Get all children that match the tag_name
        """
        if self.element is not None and hasattr(self.element, "getElementsByTagName"):
            return self.element.getElementsByTagName(tag_name)
        return []

    def get_value(self, *args):
        """
        Get the value of a child element
        """
        if self.element is not None and hasattr(self.element, "getElementsByTagName"):
            try:
                for tag_name in args:
                    nodes = self.element.getElementsByTagName(tag_name)
                    if nodes and len(nodes) > 0:
                        node = nodes[0]
                        if node is not None and hasattr(node, "innerText"):
                            return node.innerText
            except IndexError:
                pass
        return None

    def get_attribute(self, attribute_name):
        """
        Get an element's attribute value
        """
        if self.element is not None and hasattr(self.element, "getAttribute"):
            return self.element.getAttribute(attribute_name)
        return None

    @staticmethod
    def from_node(doc, node):
        """
        Helper method to create an Element object
        """

        return Element(doc, node)


class GenerationUtils(object):
    """
    Collection of generation tools
    """

    @staticmethod
    def generate_hash(shared_secret, to_hash=None):
        """
        Generates a Realex hash
        """

        if to_hash is None:
            return hashlib.sha1(shared_secret.encode()).hexdigest()  # nosec B324

        first_pass = hashlib.sha1(".".join(to_hash).encode()).hexdigest()  # nosec B324
        return hashlib.sha1(
            (first_pass + "." + shared_secret).encode()
        ).hexdigest()  # nosec B324

    @staticmethod
    def generate_order_id():
        """
        Generates a pseudo-random order id
        """

        return (
            base64.b64encode(bytearray(str(uuid.uuid4()).encode()))
            .decode()
            .replace("=", "")
            .replace("+", "-")
            .replace("/", "_")
        )

    @staticmethod
    def get_uuid() -> str:
        """
        Generates a GUID (Globally Unique Identifier)

        Returns:
            A GUID
        """
        return str(uuid.uuid4())

    @staticmethod
    def generate_recurring_key():
        """
        Generates a pseudo-random recurring key
        """

        return str(uuid.uuid4()).lower()

    @staticmethod
    def generate_timestamp():
        """
        Generates a timestamp in a Realex-compliant format (YYYYMMDDHHMMSS)
        """

        return datetime.now().strftime("%Y%m%d%H%M%S")


class StringUtils:
    """
    Utility methods for string operations.

    """

    @staticmethod
    def convert_enum_value(value: Any) -> Any:
        """
        Converts enum values to their string representation, leaves other values unchanged.
        """
        if isinstance(value, enum.Enum):
            return value.value
        return value

    @staticmethod
    def left_pad(source: Optional[str], length: int, pad_string: str) -> Optional[str]:
        """
        Pads a string on the left with the given pad string to the specified length.

        @param source: The source string to pad
        @param length: The length to pad to
        @param pad_string: The string to use for padding
        @return: The padded string
        """
        if not source:
            return source

        pad = pad_string * length
        return pad[0 : len(pad) - len(source)] + source

    @staticmethod
    def uuid() -> str:
        """
        Generate a UUID in the format xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx.

        @return: A generated UUID
        """
        uuid = ""
        for ii in range(32):
            if ii == 8 or ii == 20:
                uuid += "-"
                uuid += hex(int(random.random() * 16) | 0)[2:]
            elif ii == 12:
                uuid += "-"
                uuid += "4"
            elif ii == 16:
                uuid += "-"
                uuid += hex(int(random.random() * 4) | 8)[2:]
            else:
                uuid += hex(int(random.random() * 16) | 0)[2:]
        return uuid

    @staticmethod
    def btoa(text: str) -> str:
        """
        Base64 encode a string.

        @param text: The text to encode
        @return: Base64 encoded string
        """
        return base64.b64encode(text.encode("ascii")).decode("ascii")

    @staticmethod
    def atob(text: str) -> str:
        """
        Base64 decode a string.

        @param text: The base64 encoded text
        @return: Decoded string
        """
        return base64.b64decode(text.encode("ascii")).decode("ascii")

    @staticmethod
    def validate_to_number(value: str) -> str:
        """
        Strip all non-numeric characters from a string.

        @param value: The input string
        @return: The string with non-numeric characters removed
        """
        return re.sub(r"[^0-9]", "", value)

    @staticmethod
    def to_amount(value: Optional[Union[str, None]]) -> str:
        """
        Convert a string amount in cents to a decimal amount.

        @param value: The amount in cents
        @return: The amount as a decimal string
        """
        if not value:
            return "0"

        return str(float(value) / 100)

    @staticmethod
    def to_dollar_string(value: Optional[float]) -> Optional[str]:
        if value is None:
            return None
        return f"{value:.2f}"

    @staticmethod
    def to_numeric(value: Optional[str]) -> str:
        """
        Convert a decimal amount to cents.

        @param value: The decimal amount
        @return: The amount in cents as a string
        """

        if value is None:
            return ""

        if str(value) == "0":
            return "000"

        try:
            float_value = float(str(value))
        except ValueError:
            raise ValueError("A non well formed numeric value encountered!")

        f = float_value * 100
        formatted = int(f)
        return str(formatted)

    @staticmethod
    def bool_to_string(value: bool) -> Optional[str]:
        """
        Convert a boolean to a string.

        @param value: The boolean value
        @return: String representation of the boolean or None if input is not a boolean
        """
        if not isinstance(value, bool):
            return None

        return str(value).lower()  # Python's json.dumps would return "true"/"false"

    @staticmethod
    def is_json(string: str) -> bool:
        """
        Check if a string is valid JSON.

        @param string: The string to check
        @return: True if the string is valid JSON, False otherwise
        """
        try:
            json.loads(string)
            return True
        except (ValueError, TypeError):
            return False

    @staticmethod
    def two_digit_year(exp_year: str) -> str:
        if exp_year:
            return exp_year.zfill(4)[2:4]
        else:
            return None
