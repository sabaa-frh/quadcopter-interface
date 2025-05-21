#logging_setup.py

import logging
import sys

def setup_logging() -> None:
    """Setup logging configuration."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)]
    )

if __name__ == "__main__":
    setup_logging()
    logging.info("Logging is set up.")
