import pkgutil
import importlib
import inspect
from typing import Iterator, NoReturn

from bot import tasks, root_logger


task_logger = root_logger.getChild("task")


def walk_tasks() -> Iterator[str]:
    """Yield all task names from the bot.tasks package"""

    def on_error(name: str) -> NoReturn:
        raise ImportError(name=name)

    for module in pkgutil.walk_packages(
        tasks.__path__, f"{tasks.__name__}.", onerror=on_error
    ):
        if module.ispkg:
            imported = importlib.import_module(module.name)
            if not inspect.isfunction(getattr(imported, "setup", None)):
                # Skip tasks without a setup function
                continue

        yield module.name


TASKS = frozenset(walk_tasks())
