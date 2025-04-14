"""Module for handling template loading and processing in contract generation.

This module provides services for loading and processing contract templates from
JSON files. It includes error handling and logging for template loading operations.
"""

import json
from json import JSONDecodeError
from pathlib import Path
from typing import Any, cast

from loguru import logger

from pactdesk.models.domain.base import BaseText, Clause


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
        try:
            with Path.open(path) as f:
                content = f.read()
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

    def load_clause(self, path: Path) -> Clause:
        """Load a clause template and properly handle its structure.

        This method handles the complex structure of clauses with paragraphs and subparagraphs.

        Args:
            path (Path): The path to the clause template file.

        Returns
        -------
            Clause: The loaded and structured clause.
        """
        template_data = self.load(path)

        # Process the clause data to ensure it matches our model structure
        processed_data = self._process_clause(template_data)

        return Clause(**processed_data)

    def _process_clause(self, data: dict[str, Any]) -> dict[str, Any]:
        """Process clause data to ensure it fits our model structure.

        Args:
            data (Dict[str, Any]): The raw clause data from the template.

        Returns
        -------
            Dict[str, Any]: Processed data that fits our Clause model.
        """
        # Ensure 'content' is present (defaults to empty string if not provided)
        if "content" not in data:
            data["content"] = ""

        # Process paragraphs if they exist
        if data.get("paragraphs"):
            processed_paragraphs = []

            for paragraph in data["paragraphs"]:
                processed_paragraph = self._process_paragraph(paragraph)
                processed_paragraphs.append(processed_paragraph)

            data["paragraphs"] = processed_paragraphs

        return data

    def _process_paragraph(self, data: dict[str, Any]) -> dict[str, Any]:
        """Process paragraph data to ensure it fits our model structure.

        Args:
            data (Dict[str, Any]): The raw paragraph data from the template.

        Returns
        -------
            Dict[str, Any]: Processed data that fits our Paragraph model.
        """
        # Process subparagraphs if they exist
        if data.get("subparagraphs"):
            processed_subparagraphs = []

            for subparagraph in data["subparagraphs"]:
                # If subparagraph is already a dict with 'content', convert to BaseText
                if isinstance(subparagraph, dict) and "content" in subparagraph:
                    processed_subparagraphs.append(BaseText(**subparagraph))
                # If it's a string, wrap it in a BaseText
                elif isinstance(subparagraph, str):
                    processed_subparagraphs.append(BaseText(content=subparagraph))

            data["subparagraphs"] = processed_subparagraphs

        return data
