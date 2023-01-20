import inspect
import json


class Event:
    """
    Parent class for logged events

    Subclasses are meant to act as namespaces, providing methods for each
    of their variants.
    """

    def __init__(
        self,
        user_msg: str = "",
        log_msg: str = "",
        error: bool = False,
    ) -> None:
        self.error = error
        self.user_msg = user_msg
        self.log_msg = log_msg

    def __str__(self) -> str:
        return f"{self.log_msg}"

    def unknown_error() -> "Event":
        """An unknown error occured"""

        return Event(
            user_msg="Unknown error, please contact a server admin",
            log_msg="(ask somebody to) check the logs",
            error=True,
        )
