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

    def __init__(self, human: str | None, event_name: str, **kwargs) -> None:
        self.human = human or ""
        self.event_name = event_name
        self.custom_attrs = kwargs

    def __str__(self) -> str:
        formatted_attrs = ", ".join(
            map(lambda attr: f'"{attr[0]}":"{attr[1]}"', self.custom_attrs.items())
        )
        return f"{self.event_name} | {{{formatted_attrs}}}"

    @staticmethod
    def _create_named_event(human: str | None = None, **kwargs) -> str:
        """
        Create a new event with the given kwargs and a name based on the
        called methods name and parent class
        """

        class_name = inspect.currentframe().f_back.f_locals["cls"].__name__
        event_name = inspect.currentframe().f_back.f_code.co_name
        return Event(human=human, event_name=f"{class_name}.{event_name}", **kwargs)