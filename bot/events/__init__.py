import inspect
import json


class Event:
    """
    Parent class for logged events

    Subclasses are meant to act as namespaces, providing classmethods for each
    of their variants.

    These variant methods can then call `Event.create_named_event` with their
    own arguments to create a new `Event` containing their namespace and name,
    alongside the passed values.
    """

    scope = "unknown"

    def __init__(
        self,
        error: bool,
        event_scope: str,
        event_name: str,
        user_msg: str,
        log_msg: str,
        **kwargs,
    ) -> None:
        self.error = error
        self.event_scope = event_scope
        self.event_name = event_name
        self.user_msg = user_msg
        self.log_msg = log_msg
        self.custom_attrs = kwargs

    def __str__(self) -> str:
        formatted_attrs = json.dumps(self.custom_attrs, default=str)

        return f"{self.event_scope} | {self.event_name} | {formatted_attrs}"

    @staticmethod
    def _create_named_event(
        error: bool = False, user_msg: str = "", log_msg: str = "", **kwargs
    ) -> "Event":
        """
        Create a new event with the given kwargs and a name based on the
        called methods name and parent class
        """

        event_scope = inspect.currentframe().f_back.f_locals["cls"].scope

        event_name = inspect.currentframe().f_back.f_code.co_name
        event_name = event_name.replace("_", " ")

        return Event(
            error=error,
            event_scope=event_scope,
            event_name=event_name,
            user_msg=user_msg,
            log_msg=log_msg,
            **kwargs,
        )

    @classmethod
    def unknown_error(cls) -> "Event":
        """An unknown error occured"""

        return cls._create_named_event(
            error=True,
            user_msg="Unknown error, please contact a server admin",
            log_msg="(ask somebody to) check the logs",
        )
