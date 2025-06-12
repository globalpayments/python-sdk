def get_error_message(e: Exception) -> str:
    return getattr(e, "message", repr(e))
