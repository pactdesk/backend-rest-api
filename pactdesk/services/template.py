"""Module for handling template loading and processing in contract generation.

This module provides services for loading and processing contract templates from
JSON files. It includes error handling and logging for template loading operations.
"""

import json
from json import JSONDecodeError
from pathlib import Path
from typing import Any, cast

from loguru import logger

from pactdesk.models.domain.base import BaseText


class TemplateService:
    """Service for loading and processing contract templates.

    This class handles the loading of contract templates from JSON files and
    provides methods for accessing specific template types.

    Attributes
    ----------
        base_path (Path): The base directory for template files.
    """

    def __init__(self, base_path: Path = Path("templates")) -> None:
        """Initialise the template service with a base path.

        Args:
            base_path (Path): The base directory for template files.
        """
        self.base_path = base_path

    def load(self, path: Path) -> dict[str, Any]:
        """Load a template from a JSON file.

        Args:
            path (Path): The path to the template file.

        Returns
        -------
            dict[str, Any]: The loaded template data.

        Raises
        ------
            FileNotFoundError: If the template file does not exist.
            JSONDecodeError: If the template file contains invalid JSON.
            Exception: For any other error during template loading.
        """
        logger.debug(f"Loading template from path: {path}")
        try:
            with Path.open(path) as f:
                content = f.read()
                logger.debug(f"File content length: {len(content)}")
                if not content:
                    logger.error(f"Empty file at path: {path}")
                    return {}

                return cast(dict[str, Any], json.loads(content))

        except FileNotFoundError:
            logger.error(f"Template file not found: {path}")
            raise

        except JSONDecodeError as err:
            logger.error(f"JSON decode error in file {path}: {err!s}")
            raise

        except Exception as err:
            logger.error(f"Error loading template from {path}: {err!s}")
            raise

    def load_legal_entity(self) -> BaseText:
        """Load the template for a legal entity party.

        Returns
        -------
            BaseText: The loaded legal entity template.
        """
        template = self.load(self.base_path / "general" / "parties" / "legal_entity.json")
        return BaseText(**template)

    def load_natural_person(self) -> BaseText:
        """Load the template for a natural person party.

        Returns
        -------
            BaseText: The loaded natural person template.
        """
        template = self.load(self.base_path / "general" / "parties" / "natural_person.json")
        return BaseText(**template)
