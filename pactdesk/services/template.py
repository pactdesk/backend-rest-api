"""
Template service for the PactDesk system.

This module provides services for loading and managing template files used in
contract generation. It handles JSON templates for different contract components
such as party information, clauses, and sections.
"""

import json
from pathlib import Path
from typing import Any, cast


class TemplateService:
    """
    Service for loading and managing template files.

    This class provides methods for loading JSON template files used in contract
    generation. It handles templates for different contract components such as
    party information, clauses, and sections.

    Attributes
    ----------
        base_path: The base path for template files, defaults to "templates".
    """

    base_path: Path = Path("templates")

    def load(self, path: Path) -> dict[str, Any]:
        """
        Load a template file from the specified path.

        This method opens and reads a JSON template file, casting the result
        to a dictionary with string keys and any values.

        Parameters
        ----------
            path: The path to the template file.

        Returns
        -------
            The loaded template as a dictionary.
        """
        with Path.open(path) as f:
            return cast(dict[str, Any], json.load(f))

    def load_legal_entity(self) -> dict[str, Any]:
        """
        Load the legal entity party template.

        This method loads the template for legal entity parties, which includes
        fields for company information such as name, registration number, and
        registered address.

        Returns
        -------
            The legal entity template as a dictionary.
        """
        return self.load(self.base_path / "general" / "parties" / "legal_entity.json")

    def load_natural_person(self) -> dict[str, Any]:
        """
        Load the natural person party template.

        This method loads the template for natural person parties, which includes
        fields for personal information such as name, date of birth, and address.

        Returns
        -------
            The natural person template as a dictionary.
        """
        return self.load(self.base_path / "general" / "parties" / "natural_person.json")
