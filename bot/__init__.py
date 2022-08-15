import logging

root_logger = logging.getLogger()

format_string = "%(asctime)s | %(name)s | %(levelname)s | %(message)s"
log_format = logging.Formatter(format_string)

stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.INFO)
stream_handler.setFormatter(log_format)

root_logger.setLevel(logging.INFO)
root_logger.addHandler(stream_handler)
