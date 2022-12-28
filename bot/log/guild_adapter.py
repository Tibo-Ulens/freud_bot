import inspect
import gc
from logging import LoggerAdapter
from typing import Any, MutableMapping


class GuildAdapter(LoggerAdapter):
    """
    Logger adapter which, depending on whether the log was created in a command
    or an app command, adds an extra `__context__`, or `__interaction__` field
    to the extra arguments of the log record
    """

    def process(
        self, msg: Any, kwargs: MutableMapping[str, Any]
    ) -> tuple[Any, MutableMapping[str, Any]]:
        # LoggerAdapter's process method gets called by its `.log` method,
        # this in turn gets called by its debug/info/... methods
        # this function -> adapter.log -> adapter.{level} -> caller
        log_caller_frame = inspect.currentframe().f_back.f_back.f_back
        log_caller_code = log_caller_frame.f_code

        # Iterate over all objects that refer to the `log_caller_code` object
        # This should just be this function and the actual function that called
        # the logging function
        for func in gc.get_referrers(log_caller_code):
            # Find the actual calling function by comparing its code object to
            # the one on the stack frame
            if getattr(func, "__code__", None) is log_caller_code:
                if "__interaction__" in func.__dict__.keys():
                    interaction = func.__dict__["__interaction__"]
                    kwargs["extra"] = {"__interaction__": interaction}
                elif "__context__" in func.__dict__.keys():
                    context = func.__dict__["__context__"]
                    kwargs["extra"] = {"__context__": context}

        return (msg, kwargs)
