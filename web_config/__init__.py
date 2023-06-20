import logging
from logging import Formatter, StreamHandler

root_logger = logging.getLogger()

format_string = "%(asctime)s | %(levelname)7s | %(name)s | %(message)s"

stream_handler = StreamHandler()
stream_handler.setFormatter(Formatter(format_string))

root_logger.setLevel(logging.INFO)
root_logger.addHandler(stream_handler)
