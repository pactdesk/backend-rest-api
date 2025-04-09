"""Initial main module."""

import argparse
from pathlib import Path

from loguru import logger

from pactdesk.logging import setup_logging


def main() -> None:
    """Main entry point for the application."""
    parser = argparse.ArgumentParser(description="PactDesk REST API")
    parser.add_argument("--log-level", default="INFO", choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
                        help="Set the logging level")
    parser.add_argument("--log-file", type=str, help="Path to log file")
    args = parser.parse_args()
    
    # Set up logging
    setup_logging(log_level=args.log_level, log_file=args.log_file)
    
    logger.info("Hello from pactdesk-rest-api!")


if __name__ == "__main__":
    main()
