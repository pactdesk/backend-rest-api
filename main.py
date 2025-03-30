"""Initial main module."""

from loguru import logger


def main() -> None:
    """Log simple hello message."""
    logger.info("Hello from draftmaster-rest-api!")


if __name__ == "__main__":
    main()
