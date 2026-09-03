"""Record/replay harness for CI tests."""

import json
import os
import time
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional, cast
from urllib.parse import quote

from freezegun import freeze_time

_TIMESTAMP_KEY = "_fixedTimestamp"


class CacheMode(str, Enum):
    """Cache mode for the CI testing harness."""

    Locked = "LOCKED"
    Unlocked = "UNLOCKED"


class CiTestingHarness(object):
    _proxy_base: str
    _target_service_url: str
    _cache_mode: CacheMode
    _test_name: str
    _generated_ids: Dict[str, str]
    _language: Optional[str]
    _category: Optional[str]
    _subcategory: Optional[str]
    _current_function: Optional[str]
    _variable_fields: Dict[str, List[str]]
    _fixed_timestamp_millis: int
    _freezer: Any

    def __init__(
        self, target_service_url: str, cache_mode: CacheMode, test_name: str
    ) -> None:
        proxy_host = os.environ.get("PROXY_ENDPOINT")
        if not proxy_host:
            raise RuntimeError(
                "PROXY_ENDPOINT environment variable is not set. "
                'Set it to the proxy hostname (e.g. PROXY_ENDPOINT="your-proxy-host.example.com").'
            )
        self._proxy_base = "https://" + proxy_host + "/proxy"
        self._target_service_url = target_service_url
        self._cache_mode = cache_mode
        self._test_name = test_name
        self._generated_ids: Dict[str, str] = {}
        self._language: Optional[str] = "python"
        self._category: Optional[str] = None
        self._subcategory: Optional[str] = None
        self._current_function: Optional[str] = None
        self._variable_fields = self._default_variable_fields_for(target_service_url)

        if cache_mode == CacheMode.Locked:
            self._generated_ids = self._load_ids(required=True)
        else:
            self._generated_ids = self._load_ids(required=False)
            self._generated_ids[_TIMESTAMP_KEY] = str(int(time.time() * 1000))
            self._write_ids()
        self._fixed_timestamp_millis = int(self._generated_ids[_TIMESTAMP_KEY])

        fixed_dt = datetime.fromtimestamp(
            self._fixed_timestamp_millis / 1000.0, tz=timezone.utc
        )
        self._freezer = freeze_time(fixed_dt)
        self._freezer.start()

    def set_function(self, function_path: Optional[str]) -> None:
        if function_path is None:
            self._category = self._subcategory = self._current_function = None
            return
        parts = function_path.split("|", 2)
        if len(parts) == 3:
            self._category, self._subcategory, self._current_function = parts
        else:
            self._category = self._subcategory = None
            self._current_function = function_path

    def set_language(self, language: Optional[str]) -> None:
        self._language = language

    def set_variable_fields(
        self, payload: List[str], query: Optional[List[str]] = None
    ) -> None:
        self._variable_fields = {"payload": payload, "query": query or []}

    def get_testing_url(self) -> str:
        cache_returns = "true" if self._cache_mode == CacheMode.Locked else "false"
        target_host = self._target_service_url
        for prefix in ("https://", "http://"):
            if target_host.startswith(prefix):
                target_host = "https:/" + target_host[len(prefix) :]
                break

        args = "cacheReturns:" + cache_returns

        vars_parts: List[str] = []
        for f in self._variable_fields["payload"]:
            vars_parts.append("payload." + f)
        for f in self._variable_fields["query"]:
            vars_parts.append("query." + f)
        if vars_parts:
            args += ",vars:" + "|".join(vars_parts)

        if (
            self._language is not None
            and self._category is not None
            and self._subcategory is not None
            and self._current_function is not None
        ):
            args += (
                ",language:"
                + self._encode(self._language)
                + ",category:"
                + self._encode(self._category)
                + ",subcategory:"
                + self._encode(self._subcategory)
                + ",function:"
                + self._encode(self._current_function)
            )

        return self._proxy_base + "/(" + args + ")/" + target_host

    def get_current_time(self) -> datetime:
        return datetime.fromtimestamp(
            self._fixed_timestamp_millis / 1000.0, tz=timezone.utc
        )

    def generate_random_id(self, key: str) -> str:
        if key in self._generated_ids:
            return self._generated_ids[key]
        if self._cache_mode == CacheMode.Locked:
            raise RuntimeError(
                "Harness is locked but no cached ID found for key: "
                + key
                + ". Run tests in Unlocked mode first to generate IDs."
            )
        import random

        value = str(random.randint(1000000, 99999998))
        self._generated_ids[key] = value
        self._write_ids()
        return value

    @staticmethod
    def _default_variable_fields_for(_target_service_url: str) -> Dict[str, List[str]]:
        return {"payload": [], "query": []}

    @staticmethod
    def _encode(value: str) -> str:
        return quote(value, safe="")  # space -> %20

    def _resource_dir(self) -> str:
        return os.path.join(os.path.dirname(__file__), "citesting")

    def _write_ids(self) -> None:
        directory = self._resource_dir()
        if not os.path.isdir(directory):
            os.makedirs(directory)
        with open(os.path.join(directory, self._test_name + ".json"), "w") as handle:
            json.dump(self._generated_ids, handle, indent=4)

    def _load_ids(self, required: bool) -> Dict[str, str]:
        path = os.path.join(self._resource_dir(), self._test_name + ".json")
        if not os.path.exists(path):
            if required:
                raise RuntimeError(
                    "Harness is locked but ID file not found: "
                    + path
                    + ". Run tests in Unlocked mode first to generate the file."
                )
            return {}
        with open(path, "r") as handle:
            decoded = json.load(handle)
        return cast(Dict[str, str], decoded) if isinstance(decoded, dict) else {}
