import logging

from tqdm import tqdm


class TqdmToLogger(logging.Handler):
    """Custom logging handler redirecting logs to tqdm.write()."""

    def __init__(self, level=logging.NOTSET):
        super().__init__(level)

    def emit(self, record):
        """Handle the log record."""
        try:
            msg = self.format(record)
            tqdm.write(msg)
            self.flush()
        except Exception:
            self.handleError(record)


def setup_logger(name=None, level=logging.INFO):
    """Setup a logger with a custom logging handler."""
    logger = logging.getLogger(name)

    # Check if the logger already has handlers. If it does, it's already set up.
    if not logger.handlers:
        logger.setLevel(level)

        # Create a custom formatter with the logger's name
        formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

        # Create the TqdmToLogger handler and set its formatter
        handler = TqdmToLogger()
        handler.setFormatter(formatter)

        logger.addHandler(handler)
    return logger
