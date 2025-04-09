import json
from pathlib import Path
from typing import Any, cast

from loguru import logger

from pactdesk.models.domain.base import BaseText


class TemplateService:
    def __init__(self, base_path: Path = Path("templates")) -> None:
        self.base_path = base_path

    def load(self, path: Path) -> dict[str, Any]:
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

        except json.JSONDecodeError as err:
            logger.error(f"JSON decode error in file {path}: {err!s}")
            raise

        except Exception as err:
            logger.error(f"Error loading template from {path}: {err!s}")
            raise

    def load_legal_entity(self) -> BaseText:
        template = self.load(self.base_path / "general" / "parties" / "legal_entity.json")
        return BaseText(**template)

    def load_natural_person(self) -> BaseText:
        template = self.load(self.base_path / "general" / "parties" / "natural_person.json")
        return BaseText(**template)
