class MerchantKVP:
    def __init__(self):
        self.__key: str = ""
        self.__value: str = ""
        self.__visible: bool = False

    def get_key(self) -> str:
        return self.__key

    def set_key(self, key: str) -> None:
        self.__key = key

    def get_value(self) -> str:
        return self.__value

    def set_value(self, value: str) -> None:
        self.__value = value

    def is_visible(self) -> bool:
        return self.__visible

    def set_visible(self, visible: bool) -> None:
        self.__visible = visible
