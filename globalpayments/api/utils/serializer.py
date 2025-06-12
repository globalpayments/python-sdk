from typing import Any

import jsonpickle


def object_serialize(ob: Any) -> str:
    return str(jsonpickle.encode(ob, False, False, False))
