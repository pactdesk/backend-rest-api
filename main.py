"""Initial main module.

This module serves as the entry point for the PactDesk REST API application,
handling command line arguments and logger configuration.
"""

import argparse
import sys

from loguru import logger


def main() -> None:
    """Start the application.

    This function parses command line arguments and configures the logging system
    before starting the application.
    """
    parser = argparse.ArgumentParser(description="PactDesk REST API")
    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help="Set the logging level",
    )
    parser.add_argument("--log-file", type=str, help="Path to log file")
    args = parser.parse_args()

    # Remove default logger
    logger.remove()

    # Configure logging based on arguments
    log_format = (
        "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
        "<level>{message}</level>"
    )

    # Add console handler
    logger.add(
        sys.stderr,
        format=log_format,
        level=args.log_level,
        colorize=True,
    )

    # Add file handler if log file is specified
    if args.log_file:
        logger.add(
            args.log_file,
            format=log_format,
            level=args.log_level,
            rotation="10 MB",
            retention="1 week",
        )

    logger.info("Starting pactdesk-rest-api")


if __name__ == "__main__":
    main()
