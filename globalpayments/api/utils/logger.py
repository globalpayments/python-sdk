import json
import logging
import os
from datetime import datetime
from typing import Dict, Any


class Logger:
    INFO_LOG_LEVEL = "info"

    def __init__(self, log_directory: str = "logs"):
        self.log_levels = {
            "info": "info",
            "warn": "warn",
            "error": "error",
            "fatal": "fatal",
        }

        self.options = {
            "extension": "txt",
            "dateFormat": "Y-m-d G:i:s.u",
            "filename": False,
            "flushFrequency": False,
            "prefix": "log_",
            "logFormat": False,
            "appendContext": True,
        }

        self.queue = {}  # Dictionary to store queued logs by request ID
        self.log_file_path = ""
        self.log_line_count = 0
        self.last_line = ""

        # Remove trailing slashes
        log_directory = log_directory.rstrip("/\\")

        # Create directory if it doesn't exist
        if not os.path.exists(log_directory):
            os.makedirs(log_directory, exist_ok=True)

        self.set_log_file_path(log_directory)

        # Check if file is writable
        if os.path.exists(self.log_file_path) and not os.access(
            self.log_file_path, os.W_OK
        ):
            raise PermissionError(
                "The file could not be written to. Check that appropriate permissions have been set."
            )

        # Setup the native Python logger
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)

        # Create a file handler
        file_handler = logging.FileHandler(self.log_file_path, mode="a")
        self.logger.addHandler(file_handler)

    def set_log_to_std_out(self, std_out_path: str) -> None:
        self.log_file_path = std_out_path

    def set_log_file_path(self, log_directory: str) -> None:
        if self.options["filename"]:
            filename = self.options["filename"]
            extension = self.options["extension"]

            if ".log" in filename or ".txt" in filename:
                self.log_file_path = f"{log_directory}/{filename}"
            else:
                self.log_file_path = f"{log_directory}/{filename}.{extension}"
        else:
            prefix = self.options["prefix"]
            date_obj = datetime.now()
            date = f"{date_obj.year}-{date_obj.month:02d}-{date_obj.day:02d}"

            self.log_file_path = (
                f"{log_directory}/{prefix}{date}.{self.options['extension']}"
            )

    def set_date_format(self, date_format: str) -> None:
        self.options["dateFormat"] = date_format

    def queue_log(
        self, level: str, request_id: int, message: str, context: Dict[str, Any] = {}
    ) -> None:
        formatted_message = self.format_message(level, message, context)
        self.push_to_queue_log(request_id, formatted_message)

    async def log(self, request_id: int) -> None:
        if request_id in self.queue:
            await self.write("".join(self.queue[request_id]))

    def push_to_queue_log(self, request_id: int, formatted_message: str) -> None:
        if request_id not in self.queue:
            self.queue[request_id] = [formatted_message]
            return

        self.queue[request_id].append(formatted_message)

    async def write(self, message: str) -> None:
        try:
            with open(self.log_file_path, "a") as f:
                f.write(message)

            self.last_line = message.strip()
            self.log_line_count += 1

            # Handle flush frequency
            if (
                self.options["flushFrequency"]
                and self.log_line_count % self.options["flushFrequency"] == 0
            ):
                # In Python, files are automatically flushed when closed
                pass
        except Exception as e:
            raise PermissionError(
                "The file could not be written to. Check that appropriate permissions have been set."
            )

    def get_log_file_path(self) -> str:
        return self.log_file_path

    def get_last_log_line(self) -> str:
        return self.last_line

    def format_message(self, level: str, message: str, context: Dict[str, Any]) -> str:
        if self.options["logFormat"]:
            parts = {
                "date": self.get_timestamp(),
                "level": str(level).upper(),
                "level-padding": " " * (9 - len(str(level))),
                "priority": self.log_levels.get(level, level),
                "message": message,
                "context": json.dumps(context),
            }

            formatted_message = self.options["logFormat"]

            for part, value in parts.items():
                formatted_message = formatted_message.replace(f"{{{part}}}", str(value))
        else:
            formatted_message = f"[{self.get_timestamp()}] [{level}] {message}"

        if self.options["appendContext"] and context:
            formatted_message += f"\n{self.indent(self.context_to_string(context))}"

        return f"{formatted_message}\n"

    def get_timestamp(self) -> str:
        date_obj = datetime.now()

        # Format the date according to the specified format
        date = (
            f"{date_obj.year}-{date_obj.month:02d}-{date_obj.day:02d} "
            f"{date_obj.hour:02d}:{date_obj.minute:02d}:{date_obj.second:02d}"
        )

        return date

    def context_to_string(self, context: Dict[str, Any]) -> str:
        export_string = ""

        for key, value in context.items():
            export_string += f"{key}: "

            # Convert value to string and format it
            value_str = str(value)
            value_str = (
                value_str.replace("=> ", "=> ")
                .replace("array( )", "array()")
                .replace("array (", "array(")
            )

            # Apply indentation
            value_str = "    ".join(value_str.splitlines(True))

            export_string += value_str
            export_string += "\n"

        # Remove backslashes and trailing whitespace
        return export_string.replace("\\\\", "\\").replace("\\'", "'").rstrip()

    def indent(self, string: str, indent: str = "    ") -> str:
        return indent + string.replace("\n", f"\n{indent}")

    async def info(
        self,
        message: str,
        request_id: int,
        context: Dict[str, Any] = {},
        queue: bool = True,
    ) -> None:
        self.queue_log("INFO_LOG_LEVEL", request_id, message, context)
        if not queue:
            await self.log(request_id)
