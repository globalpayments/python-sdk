import base64
from typing import List, Optional, Callable, Any, Self

from globalpayments.api.entities.merchant_kvp import MerchantKVP


class MerchantDataCollection:
    def __init__(self):
        self.__collection: List[MerchantKVP] = []

    def add(self, key: str, value: str, visible: bool = True) -> None:
        if self.has_key(key):
            if visible:
                raise ValueError(f"Key {key} already exists in the collection.")
            else:
                index = self.__index_of(key)
                if index != -1:
                    self.__collection.pop(index)

        kvp = MerchantKVP()
        kvp.set_key(key)
        kvp.set_value(value)
        kvp.set_visible(visible)

        self.__collection.append(kvp)

    def get(self, key: str) -> Optional[str]:
        for item in self.__collection:
            if item.get_key() == key and item.is_visible():
                return item.get_value()
        return None

    def get_keys(self) -> List[str]:
        return [item.get_key() for item in self.__collection if item.is_visible()]

    def count(self) -> int:
        return sum(1 for item in self.__collection if item.is_visible())

    def __index_of(self, key: str) -> int:
        for i, item in enumerate(self.__collection):
            if item.get_key() == key:
                return i
        return -1

    def get_hidden_values(self) -> List[MerchantKVP]:
        return [item for item in self.__collection if not item.is_visible()]

    def has_key(self, key: str) -> bool:
        return self.get(key) is not None

    def merge_hidden(self, old_collection: "MerchantDataCollection") -> None:
        hidden_values = old_collection.get_hidden_values()
        for kvp in hidden_values:
            if not self.has_key(kvp.get_key()):
                self.__collection.append(kvp)

    @staticmethod
    def parse(
        kvp_string: str, decoder: Optional[Callable[[str], str]] = None
    ) -> "MerchantDataCollection":
        collection = MerchantDataCollection()

        # Python equivalent of atob is base64.b64decode
        decrypted_kvp = base64.b64decode(kvp_string).decode("utf-8")
        if decoder:
            decrypted_kvp = decoder(decrypted_kvp)

        merchant_data = decrypted_kvp.split("|")
        for kvp in merchant_data:
            data = kvp.split(":")
            collection.add(data[0], data[1], data[2] == "true")

        return collection

    def to_string(
        self, encoder: Optional[Callable[[str], str]] = None
    ) -> Optional[str]:
        sb = ""

        for kvp in self.__collection:
            sb += f"{kvp.get_key()}:{kvp.get_value()}:{kvp.is_visible()}|"

        sb = sb[:-1]  # Remove last pipe character

        try:
            formatted = sb
            if encoder:
                formatted = encoder(sb)
            # Python equivalent of btoa is base64.b64encode
            return base64.b64encode(formatted.encode("utf-8")).decode("utf-8")
        except Exception:
            return None

    def get_value(
        self, key: str, converter: Optional[Callable[[Any], Any]] = None
    ) -> Any:
        for kvp in self.__collection:
            if kvp.get_key() == key:
                if converter is not None:
                    return converter(kvp.get_value())
                else:
                    return kvp.get_value()
        return None
