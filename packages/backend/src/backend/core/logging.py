import logging
import sys


def configure_logging() -> logging.Logger:
    """
    Configures basic application logging.
    In future, this can be extended to use structured JSON logging for production.
    """
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
    )
    return logging.getLogger("backend")


logger = configure_logging()
