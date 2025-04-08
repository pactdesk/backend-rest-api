"""
Main entry point for the PactDesk REST API.

This module serves as the entry point for the PactDesk REST API application.
It initializes the application and starts the server when executed directly.
"""

from loguru import logger


def main() -> None:
    """Log simple hello message."""
    logger.info("Hello from pactdesk-rest-api!")


if __name__ == "__main__":
    main()
