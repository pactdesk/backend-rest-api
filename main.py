"""Initial main module."""

from loguru import logger


def main() -> None:
    """Log simple hello message."""
    logger.info("Hello from pactdesk-rest-api!")


if __name__ == "__main__":
    main()
