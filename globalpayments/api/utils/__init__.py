"""
Utilities for general use in the SDK
"""

import base64
from datetime import datetime
import hashlib
import uuid
from xml.dom import minidom


class ElementTree(object):
    """
    Wraps xml.dom.minidom to provide a simpler et
    """

    doc = None
    namespaces = {}

    def __init__(self):
        self.doc = minidom.Document()
        self.namespaces['soap'] = 'http://schemas.xmlsoap.org/soap/envelope/'

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

        value = ''
        if 'value' in kwargs:
            if kwargs['value'] is None:
                return None
            value = kwargs['value']

        child = self._create_element(tag_name)
        parent.element.appendChild(child)
        return Element(self.doc, child).text(value)

    def to_string(self, root):
        """
        Converts an ElementTree object to its string form
        """

        self.doc.appendChild(root.element)
        try:
            return self.doc.toxml()
        finally:
            self.doc.removeChild(root)

    def get(self, tag_name):
        """
        Gets an element by tag_name
        """

        try:
            node = self.doc.getElementsByTagName(tag_name)[0]
            return Element(self.doc, node)
        except IndexError:
            return None

    def parse(self, source):
        """
        Converts a string or bytearray to an ElementTree
        """

        if isinstance(source, str):
            self.doc = minidom.parseString(source)
        elif isinstance(source, bytearray):
            self.doc = minidom.parseString(str(source))

    def _create_element(self, tag_name):
        if tag_name.contains(':'):
            data = tag_name.split(':')
            return self.doc.createElement(data[0], data[1],
                                          self.namespaces[data[0]])
        return self.doc.createElement(tag_name)


class Element(object):
    """
    Assists in working with ElementTree elements
    """

    doc = None
    element = None

    def __init__(self, doc, element):
        self.doc = doc
        self.element = element

    def first_child(self):
        """
        Gets the first child of the element
        """

        return self.from_node(self.doc, self.element.first_child())

    def prefix(self, prefix):
        """
        Sets the prefix of the element
        """

        self.element.prefix(prefix)
        return self

    def remove(self, tag_name):
        """
        Removes the child node by tag_name if it exists
        """

        child = self.get(tag_name)
        if child is not None:
            self.element.removeChild(tag_name)
        return self

    def set(self, name, value):
        """
        Sets an attribute by name on the element
        """

        self.element.setAttribute(name, value)
        return self

    def text(self, value):
        """
        Sets the inner text of the element
        """

        self.element.innerText(value)
        return self

    def append(self, child):
        """
        Adds a child to the element
        """

        self.doc.importNode(child)
        self.element.appendChild(child.element)
        return self

    def tag(self):
        """
        Gets the element's tag
        """

        return self.element.tag

    def has(self, tag_name):
        """
        Tests if a child exists with the tag_name
        """

        return len(self.element.getElementsByTagName(tag_name)) > 0

    def get(self, tag_name):
        """
        Get the first child that matches the tag_name
        """

        return self.element.getElementsByTagName(tag_name)[0]

    def get_all(self, tag_name):
        """
        Get all children that match the tag_name
        """

        return self.element.getElementsByTagName(tag_name)

    def get_value(self, *args):
        """
        Get the value of a child element
        """

        try:
            for tag_name in args:
                node = self.element.getElementsByTagName(tag_name)[0]
                if node is not None:
                    return node.innerText
        except IndexError:
            return None

    def get_attribute(self, attribute_name):
        """
        Get an element's attribute value
        """

        return self.element.getAttribute(attribute_name)

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
            return hashlib.sha1(shared_secret.encode()).hexdigest()

        first_pass = hashlib.sha1('.'.join(to_hash).encode()).hexdigest()
        return hashlib.sha1(
            (first_pass + '.' + shared_secret).encode()).hexdigest()

    @staticmethod
    def generate_order_id():
        """
        Generates a pseudo-random order id
        """

        return base64.b64encode(bytearray(str(uuid.uuid4()).encode())).decode() \
            .replace('=', '') \
            .replace('+', '-') \
            .replace('/', '_')

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

        return datetime.now().strftime('%Y%m%d%H%M%S')
